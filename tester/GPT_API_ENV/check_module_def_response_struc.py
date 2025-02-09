import json
from pathlib import Path

from file_util import check_dir, path_read
from file_util import read_json, save_json
from .process_response_util.extract_json_util import match_md_json_start_idxs, track_lines_of_a_dict
from .process_response_util.extract_json_util import match_md_json_end_idxs
from .process_response_util.extract_json_util import detect_line_idxs
from util.util import FailedParsingException
# =============== extract content start ===============


def _is_one_json_part(content:str):
    lines = content.split('\n')
    start_idxs = match_md_json_start_idxs(lines)
    end_idxs = match_md_json_end_idxs(lines)
    # print('start_idxs, end_idxs', start_idxs, end_idxs)
    if len(start_idxs) == 1 and len(end_idxs) == 1:
        return True
    return False


def _extract_data_from_one_json_part(content:str):
    lines = content.split('\n')
    start_idxs = match_md_json_start_idxs(lines)
    end_idxs = match_md_json_end_idxs(lines)
    start_idx = start_idxs[0]
    end_idx = end_idxs[0]
    content = '\n'.join(lines[start_idx+1:end_idx])
    # print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
    # print(content)
    # print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
    
    if '...' in content:
        raise FailedParsingException('The response should be a valid json. Do not use "..." in the response, though you do not know some components.')
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise FailedParsingException('The response should be a valid json. The current response is invalid')
    return data


def _detect_json_part_in_file(file_name):
    print(file_name)
    content = path_read(file_name)
    if _is_one_json_part(content):
        return [_extract_data_from_one_json_part(content)]
    else:
        paragraph_texts = track_lines_of_a_dict(content.split('\n'))
        return [json.loads(p) for p in paragraph_texts]
        if len(paragraph_texts) == 1:
            return json.loads(paragraph_texts[0])
        else:
            raise FailedParsingException('The response should be origanized in a single json part')
    raise NotImplementedError('Not implemented yet ;; TBD: process other cases')
    # return data


def _remove_repeated_lists(data):
    assert isinstance(data, list)
    if len(data) == 1 and isinstance(data[0], list):
        return _remove_repeated_lists(data[0])
    return data


def content_as_final_kv(file_path):
    print('In content_as_kv', file_path)
    # is_text_desc = _is_text_file(file_path)
    try:
        content = _detect_json_part_in_file(file_path)
        content = _remove_repeated_lists(content)
    except json.decoder.JSONDecodeError as e:
        raise FailedParsingException(f'The response should be a valid json. The current JSON in the response is ill-formatted: {e}')
    # expected_key_name:str = 'wat_syntax' if is_text_desc else 'bin_syntax'
    # assert is_text_desc
    if len(content) == 0:
        raise FailedParsingException('The response does not contain a description in JSON format.')
    assert isinstance(content, list)
    return content
    

        

def _is_text_file(file_name:str):
    file_name = Path(file_name).name
    if file_name.endswith('.txt'):
        file_name = file_name[:-4]
    if file_name.endswith('_result'):
        file_name = file_name[:-7]
    assert '_' in file_name
    query_type = file_name.split('_')[-1]
    assert query_type in ['binary', 'text']
    return query_type == 'text'
        
def _get_module_name(file_name:str):
    file_name = Path(file_name).name
    if file_name.endswith('.txt'):
        file_name = file_name[:-4]
    if file_name.endswith('_result'):
        file_name = file_name[:-7]
    if file_name.endswith('_text'):
        file_name = file_name[:-5]
    if file_name.endswith('_binary'):
        file_name = file_name[:-7]
    return file_name
    # assert '_' in file_name
    

# =============== extract content end ===============



def get_results(raw_result_dir, structured_result_dir):
    # raw_result_dir = Path('./results/module_def/base_with_example_fixing')
    # structured_result_dir = check_dir('./results/module_spec')
    result_files = list(raw_result_dir.glob('*result.txt'))
    summary_dict = {}
    for p in result_files:
        module_name = _get_module_name(p.stem)
        if module_name not in summary_dict:
            summary_dict[module_name] = {}
        summary_dict[module_name].update(content_as_final_kv(p))
    for module_name, content in summary_dict.items():
        save_json(structured_result_dir/f'{module_name}.json', content)
        
