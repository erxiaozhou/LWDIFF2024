import json
from file_util import path_read
from util.util import FailedParsingException
from ..prepare_data_env.get_background import SpecSearchEngine
from ..project_cfg import cfg_result_dir
from .util import OneTaskQueryFileNames, ask_core_ng, QueryFileNames
from ..message_util import AttachedChatsFactory



def query_control_flow_and_save_result(
    debug=False, 
    result_dir=None, 
    max_idx=3, 
    skip_exist=False
):
    query_num = 1  # 1, 8
    main_question = '''
# Task description
Please summary the control flow construct grammar, considering the attached background imformation. Note it, here, control flow constrct refers to the nested instruction, which contains the other instructions. An instruction does not contain the other instructions is a non-control flow construct instruction, even it is a contrl instruction. 

- you should group the instructions that do not contains the control flow construct and represent them as  non-control flow construct instructions.
- Note it, the back
Note it, the background information just contains the control instrucitons. Therefore, you should include a tokento represent the non-control flow construct instructions.

# Format requirement
- First, you summary the control flow construct grammar in natural language.
- Then, you should summary it in a structured way, such as a BNF grammar. 
- You should organize the BNF grammar as a JSON mapping. An expansion rule should looks like
```
"<control_flow_name>": ['control_flow_start', '<blocktype>', '<insts>', 'end']
- Your response should include the following necessary information: 
    - Each kind of control flow construct should be represented as a expaonsion rule.
    - There should be a token named "other-instruction" to represent the non-control Wasm instructions, which are not included in the background.
    - There should be a token named "non-contrl-flow-instruction" to represent the non-control flow construct instructions, including the non control flow instructions in the background and the other instructions.
```
    '''
    # 
    if result_dir is None:
        result_dir = cfg_result_dir
    cur_task_fnames = OneTaskQueryFileNames(
    result_dir, 
    'cfg_grammar',
    max_idx
    )
    # 
    exist_epoch_num = cur_task_fnames.exist_epoch_num
    print('|||=== exist_epoch_num', exist_epoch_num)
    max_idx = cur_task_fnames.max_idx
    if skip_exist:
        start_idx = exist_epoch_num
    else:
        start_idx = 0
    # 
    
    for query_iter_idx in range(start_idx, max_idx):
        print(f'query_iter_idx: {query_iter_idx}')
        if query_iter_idx > 0:
            last_fpaths = cur_task_fnames.get_query_names(query_iter_idx-1)
            if is_well_formatted_response(last_fpaths.response_txt_path):
                break
        prompt = get_prompt(query_num, main_question, query_iter_idx, cur_task_fnames)
        
        next_fpaths = cur_task_fnames.get_query_names(query_iter_idx)
        print('|||==>> next_fpaths.response_txt_path', next_fpaths.response_txt_path)
        ask_core_ng(
            next_fpaths,
            prompt,
            debug=debug,
            skip_exist=skip_exist
        )

def get_prompt(query_num, main_question, prompt_idx, cur_inst_task_fnames):
    background = _get_control_flow_info(query_num)
    if prompt_idx == 0:
        print(f'Result dir: {cfg_result_dir}')
        message = AttachedChatsFactory.generate_cfg_query_msg(main_question, background).release_messages()
        return message
    else:
        last_fpath = cur_inst_task_fnames.get_query_names(prompt_idx-1)
        try:
            _check_inst_response(last_fpath.response_txt_path)
            refine_info = ''
        except FailedParsingException as e:
            refine_info =f'''The last response of the query is as follows: \n\n{path_read(last_fpath.response_txt_pat)}\n\nHowever, there are some errors in the response: {e}.Please refine the response. Note it, you should finish all the tasks again, not just the ill-formatted one.'''
        main_question = main_question + refine_info
        message = AttachedChatsFactory.generate_cfg_query_msg(main_question, background).release_messages()
        return message

            
def _check_inst_response(response_txt_path):
    obj = _get_data_part_texts(path_read(response_txt_path))
    if not isinstance(obj, dict):
        raise FailedParsingException('The response should be a mapping.')
    return True



def _get_data_part_texts(content):
    a_data_part_in_process = False
    cur_lines = []
    data_part_texts = []
    for line in content.split('\n'):
        if line.strip() == '```json':
            a_data_part_in_process = True
        elif line.strip() == '```':
            a_data_part_in_process = False
            if cur_lines:
                data_part_texts.append('\n'.join(cur_lines))
                cur_lines = []
        elif a_data_part_in_process:
            cur_lines.append(line)
    
    # print(data_part_texts)
    # data_part_texts = [
    #     x for x in data_part_texts if 'validation_description' not in x]
    final_text = '\n'.join(data_part_texts)
    try:
        obj = json.loads(final_text)
    except json.JSONDecodeError as e:
        raise FailedParsingException(f'The response should be a valid json. The current JSON \n\n{final_text}\n\n in the response is ill-formatted: {e}')
    return obj



def is_well_formatted_response(response_txt_path):
    try:
        return _check_inst_response(response_txt_path)
    except FailedParsingException as e:
        return False

def _combine_text(texts):
    return '\n\n'.join(texts)


def _get_control_flow_info(query_num):
    search_engine = SpecSearchEngine.get_default()
    q = 'control flow construct syntex indicated by the control instructions'
    result_texts, idxs, distances = search_engine.search_with_cnodes(q, k=query_num)
    info_text = _combine_text(result_texts)
    return info_text
