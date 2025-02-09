import json
from pathlib import Path
from typing import Optional
from tqdm import tqdm
from SInst.RuleInst.GptInst2GRule import extract_and_parse, extract_from_one_response

from extract_LLM_spec.extract_data_from_GPT_response import GptResponseData, _get_inst_name_from_raw_file_path, extract_a_text_to_json
from ..ResponseChecker.each_def_checker import InvalidTypeDescException
from ..op_related.generate_op_cnode_desc import get_inst_name2op_desc_practical
from file_util import check_dir, path_read, path_write, save_json
from ..message_util import AttachedChatsFactory
from ..parsing_spec_util.customNode import customNode
from util.util import FailedParsingException
from .util import OneTaskQueryFileNames, get_inst_name2exec_inst_name
from .util import QueryFileNames
from ..prepare_data_env.get_background import SpecSearchEngine
from .util import ask_core_ng
from ..project_cfg import inst_result_dir
import numpy as np
from ..project_cfg import inst_template_path
from ..project_cfg import global_set_exmaple_path
from ..project_cfg import i32_store_example_path
from ..api_util import MODEL_VERSION

class InstInfo:
    def __init__(self, 
                 valid_info, 
                 exec_info, 
                 debug_info=None
                 ):
        self.valid_info = valid_info
        self.exec_info = exec_info
        self.valid_info_append = None
        self.exec_info_append = None
        self.op_background_info = None
        self.debug_info = debug_info

    def set_op_background_info(self, op_background_info):
        self.op_background_info = op_background_info

    def released_info(self):
        d = {
            'validation_description': self.valid_info,
            'execution_description': self.exec_info,
        }
        if self.op_background_info is not None:
            d['op_background_info'] = self.op_background_info
        return d



def query_insts_info_and_save_result4(
        sub_dir_name,
        considered_insts_names=None, 
        skip_exist=True,
        use_op_background_info=False, 
        with_example=False,
        debug=False,
        max_idx=5,
        model_name=MODEL_VERSION
    ):

    inst_name2exec_inst_name = get_inst_name2exec_inst_name()
    search_engine = SpecSearchEngine.get_default()
    result_dir = check_dir(inst_result_dir / sub_dir_name)
    inst_name2op_desc = get_inst_name2op_desc_practical()
    failed_inst_names = []
    for inst_name, exec_inst_name in tqdm(inst_name2exec_inst_name.items()):
        if considered_insts_names is not None and inst_name not in considered_insts_names:
            continue
        try:
            if use_op_background_info:
                op_background_info = inst_name2op_desc.get(inst_name)
            else:
                op_background_info = None
            cur_inst_task_fnames = OneTaskQueryFileNames(
                result_dir, 
                inst_name,
                max_idx
                )
            query_one_inst_and_save_result(
                search_engine,
                cur_inst_task_fnames,
                inst_name,
                exec_inst_name,
                with_example=with_example,
                op_background_info=op_background_info,
                skip_exist=skip_exist, 
                debug=debug,
                model_name=model_name
            )
        except Exception as e:
            # raise e
            failed_inst_names.append(inst_name)
    save_json('tt/failed_inst_names4.json', failed_inst_names)
    print(failed_inst_names)

def query_one_inst_and_save_result(
        search_engine,
        cur_inst_task_fnames:OneTaskQueryFileNames,
        inst_name,
        exec_inst_name,
        skip_exist,
        op_background_info=None,
        with_example=False,
        debug=False,
        model_name=MODEL_VERSION
):
    exist_epoch_num = cur_inst_task_fnames.exist_epoch_num
    print('|||=== exist_epoch_num', exist_epoch_num)
    max_idx = cur_inst_task_fnames.max_idx
    if skip_exist:
        start_idx = exist_epoch_num
    else:
        start_idx = 0
    for query_iter_idx in range(start_idx, max_idx):
        print(f'query_iter_idx: {query_iter_idx}')
        if query_iter_idx > 0:
            last_fpaths = cur_inst_task_fnames.get_query_names(query_iter_idx-1)
            if is_well_formatted_inst_response(last_fpaths.response_txt_path):
                structured_json_path = get_structured_json_path(last_fpaths)
                if not structured_json_path.exists():
                    extract_txt_as_json(last_fpaths)
                break
        prompt = get_prompt(search_engine, inst_name, exec_inst_name, op_background_info, with_example, cur_inst_task_fnames, query_iter_idx)
        
        next_fpaths = cur_inst_task_fnames.get_query_names(query_iter_idx)
        print('|||==>> next_fpaths.response_txt_path', next_fpaths.response_txt_path)
        ask_core_ng(
            next_fpaths,
            prompt,
            debug=debug,
            skip_exist=skip_exist,
            mode_name=model_name
        )


def extract_txt_as_json(last_fpaths:QueryFileNames):
    responst_txt_path = last_fpaths.response_txt_path
    json_path =get_structured_json_path(last_fpaths)
    extract_a_text_to_json(responst_txt_path, json_path)

def get_structured_json_path(last_fpaths:QueryFileNames):
    responst_txt_path = last_fpaths.response_txt_path
    base_dir = last_fpaths.base_dir
    stem = _get_inst_name_from_raw_file_path(responst_txt_path)
    json_path = base_dir / f'{stem}.json'
    return json_path


def is_well_formatted_inst_response(response_txt_path:Path):
    try:
        _check_inst_response(response_txt_path)
    except FailedParsingException as e:
        return False
    except InvalidTypeDescException as e:
        return False
    return True

def _check_inst_response(response_txt_path):
    print('The response_txt_path under check:', response_txt_path)
    extract_and_parse(response_txt_path)
    # TODO
    # raise NotImplementedError('Not implemented yet.')

def get_prompt(search_engine, inst_name, exec_inst_name, op_background_info, with_example, cur_inst_task_fnames, prompt_idx):
    main_question = get_init_prompt(search_engine, inst_name, exec_inst_name, op_background_info, with_example, cur_inst_task_fnames)
    if prompt_idx == 0:
        prompt = AttachedChatsFactory.generate_inst_query_msg(json.dumps(main_question, indent=4)).release_messages()
    else:
        last_fpath = cur_inst_task_fnames.get_query_names(prompt_idx-1)
        refine_info = _get_inst_refine_info(last_fpath.response_txt_path)
        prompt = AttachedChatsFactory.generate_query_msg_with_refine(main_question, refine_info).release_messages()
    return prompt

def _get_inst_refine_info(response_txt_path:Path):
    
    if is_well_formatted_inst_response(response_txt_path):
        raise ValueError('According to the expected logic, the last response should not be well-formatted. Please check the implementation.')
    try:
        _check_inst_response(response_txt_path)
    except FailedParsingException as e:
        msg = f'{e}'
    except InvalidTypeDescException as e:
        msg = f'{e}'
    s = f'''The last response of the query is as follows: \n\n{path_read(response_txt_path)}\n\nHowever, there are some errors in the response: {msg}.Please refine the response. Note it, you should finish all the tasks again, not just the ill-formatted one.'''
    return s

def get_init_prompt(search_engine, inst_name, exec_inst_name, op_background_info, with_example, cur_inst_task_fnames):
    result_dir = cur_inst_task_fnames.base_dir
    inst_info: InstInfo = _get_inst_info(
        search_engine,
        exec_inst_name
        )
    inst_info.set_op_background_info(op_background_info)
    inst_info_dict = {
        'concrete instruciton name': inst_name,
        'instruction format': exec_inst_name,
    }
    inst_info_dict.update(inst_info.released_info())
    _save_inst_info_for_debug(result_dir, inst_name, inst_info_dict)
    
    example = _get_exmaples(with_example)
    # get main question
    template = path_read(inst_template_path)
    main_question = template.replace(
        '{data}', str(inst_info_dict)).replace(
        '{example}', example)    # 
    # msg = AttachedChatsFactory.generate_inst_query_msg(
    #     main_question
    # ).release_messages()
    
    return main_question


def _save_inst_info_for_debug(result_dir, inst_name, data:dict):
    fname = f'{inst_name}_info.txt'
    fpath = result_dir / fname
    path_write(fpath, str(data))
    save_json(result_dir / f'{inst_name}_info.json', data)

def _get_exmaples(with_example):
    if with_example:
        example = f'''
# Example :
# Example :
## Example 1:
{path_read(global_set_exmaple_path)}


## Example 2:
{path_read(i32_store_example_path)}
'''
    else:
        example = ''

    return example

def _get_inst_info(
        search_engine: SpecSearchEngine,
        exec_inst_name) -> InstInfo:
    valid_info_q = f'validation (valid) of the instruction {exec_inst_name}'
    exec_info_q = f'execution (exec) of the instruction {exec_inst_name}'
    valid_infos, valid_cnodes, valid_distances = search_engine.search_with_cnodes(valid_info_q, k=5)
    exec_infos, exec_cnodes, exec_distances = search_engine.search_with_cnodes(exec_info_q, k=5)
    # 
    valid_info = valid_infos[0]
    exec_info = exec_infos[0]
    # 
    # determine debug info
    valid_titles = _get_titles_from_cnodes(valid_cnodes)
    exec_titles = _get_titles_from_cnodes(exec_cnodes)
    valid_distances = _process_distance(valid_distances)
    exec_distances = _process_distance(exec_distances) 
    debug_info = {
        'valid_titles': valid_titles,
        'exec_titles': exec_titles,
        'valid_distances': valid_distances,
        'exec_distances': exec_distances
    }
    inst_info = InstInfo(valid_info, exec_info, debug_info=debug_info)
    return inst_info


def _get_titles_from_cnodes(cnodes:list[customNode]):
    titles = [cnode.all_title_repr for cnode in cnodes]
    return titles


def _process_distance(distances:np.ndarray):
    d = distances.tolist()
    return d
