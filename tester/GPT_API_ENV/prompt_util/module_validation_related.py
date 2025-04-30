from enum import Enum

from tqdm import tqdm

from GPT_API_ENV.prompt_util.module_def_related import _get_file_name, get_names_in_a_response_txt_path, requirement_core
from extract_block_mutator.model_gen.naive_type_desc import _a_field_exist
from ..ResponseChecker.each_def_checker import InvalidTypeDescException, extract_terms_from_desc, type_desc_is_valid
from file_util import check_dir, get_json_fmt_str, path_read, read_json
from ..get_active_element_example import get_active_element_example
from ..parsing_spec_util.customNode import customNode
from ..prepare_data_env.get_background import SpecSearchEngine
from util.util import FailedParsingException, MayWrongSyntaxWraning
from ..project_cfg import module_def_result_dir
from ..project_cfg import module_names_to_ask
from ..check_module_def_response_struc import content_as_final_kv
from .util import OneTaskQueryFileNames, QueryFileNames, ask_core_ng
from ..message_util import AttachedChatsFactory
from typing import NoReturn, Union, Optional
from pathlib import Path
from WasmInfoCfg import naive_module_component_types


class DefInfo:
    def __init__(self, cur_def:list[dict], ref_dicts:dict[str, list[dict]]):
        self.cur_def = cur_def
        self.ref_dicts = ref_dicts

def query_all_module_def_validation_and_save_result(sub_dir_name, query_num=1, debug=False, skip_exist=False, max_iter_num=15, def_names=module_names_to_ask):
    pass
    defname2components = read_json('GPT_API_ENV/results/final/module_def_all_sub_type.json')
    defs = read_json('GPT_API_ENV/results/final/module_def_trimmed_list.json')
    search_engine = SpecSearchEngine.get_all_valid_default()
    result_dir = check_dir(module_def_result_dir / sub_dir_name)
    
    
    introduced_names = []
    mentioned_names = []
    naive_ones = naive_module_component_types
    naive_ones = set(naive_ones)
    uncovered_names = set(def_names) - naive_ones

    for i in range(10):
        if len(uncovered_names) == 0:
            break
        for module_name in tqdm(uncovered_names):
            # init def info
            module_name_repr = module_name.replace(' ', '_')
            cur_def = defs[module_name_repr]
            all_ref_def_names = defname2components[module_name_repr]
            cur_ref_names = [x for x in all_ref_def_names if x in defs]
            ref_dicts = {n: defs[n] for n in cur_ref_names}
            def_info = DefInfo(cur_def, ref_dicts)
            # 
            module_file_name = _get_file_name(module_name)
            query_module_valid_and_save_result(
                def_info,
                search_engine,
                result_dir,
                query_num,
                module_name,
                module_file_name,
                max_iter_num=max_iter_num,
                skip_exist=skip_exist,
                debug=debug)
            introduced_names.append(module_file_name)
            mentioned_names.extend(cur_ref_names)
        uncovered_names = set(mentioned_names) - set(introduced_names)
        uncovered_names = uncovered_names - naive_ones
        # uncovered_names = list(uncovered_names)
        print('uncovered_names', uncovered_names)
        print('introduced_names', introduced_names)
        print(f'Result dir: {result_dir}')


def query_module_valid_and_save_result(
        def_info:DefInfo,
        search_engine,
        result_dir,
        query_num,
        module_name,
        module_file_name,
        skip_exist=False,
        max_iter_num=15,
        debug=False)->tuple[list[str], list[str]]:
    cur_module_def_names = OneTaskQueryFileNames(
        result_dir, 
        module_file_name, 
        max_iter_num
    )
    exist_epoch_num = cur_module_def_names.exist_epoch_num
    print('|||=== exist_epoch_num', exist_epoch_num)
    if skip_exist:
        start_idx = exist_epoch_num
    else:
        start_idx = 0
    for query_iter_idx in range(start_idx, max_iter_num):
        print(f'query_iter_idx: {query_iter_idx}')
        if query_iter_idx > 0:
            last_fpaths = cur_module_def_names.get_query_names(idx=query_iter_idx-1)
            if is_well_formatted_mod_def(last_fpaths.response_txt_path, def_info):

                break
        next_fpaths = cur_module_def_names.get_query_names(query_iter_idx)
        prompt = get_prompt(
        def_info,search_engine, query_num, query_iter_idx, module_name, cur_module_def_names)
        print('Try get response')
        ask_core_ng(
            next_fpaths,
            prompt,
            debug=debug,
            skip_exist=skip_exist
            )


def is_well_formatted_mod_def(response_path:Path, def_info:DefInfo)->bool:
    try:
        check_a_response_txt_path(response_path, def_info)
    except FailedParsingException as e:
        return False
    except InvalidTypeDescException as e:
        return False
    return True


def _get_refine_info(response_path, def_info):
    if is_well_formatted_mod_def(response_path, def_info):
        raise ValueError('According to the expected logic, the last response should not be well-formatted. Please check the implementation.')

    msg = None
    try:
        check_a_response_txt_path(response_path, def_info)
    except FailedParsingException as e:
        msg = f'{e}'
    except InvalidTypeDescException as e:
        msg = f'{e}'
    except MayWrongSyntaxWraning as e:
        msg = f'{e}'
    assert msg is not None
    s = f'''The last response of the query is as follows: \n\n{path_read(response_path)}\n\nHowever, there are some errors in the response: {msg}. Please refine the response. Furthermore, you may loss variations of the definition.Please check the background information carefully.Please refine the response. Note it, you should finish all the tasks again, not just the ill-formatted one.'''

    return s


def check_a_response_txt_path(fpath:Path, def_info:DefInfo):
    result = content_as_final_kv(fpath)

    # def_is_list_result = _check_def_is_list(result)
    # if def_is_list_result is not None:
    #     raise FailedParsingException(def_is_list_result)
    _check_c(result)
    constraints = []
    for cs in result:
        if isinstance(cs, dict):
            constraints.append(cs)
        elif isinstance(cs, list):
            constraints.extend(cs)
        else:
            raise FailedParsingException(f'The response should be a list of mappings and the keys of a mapping should be `v1`, `v2`, `relation`. However, the following part is not a list: {cs}')
    check_are_dict_result = _check_def_are_dict_cs(constraints, def_info)
    if check_are_dict_result is not None:
        raise FailedParsingException(check_are_dict_result)
    # check each constraint
        
    # raise NotImplementedError

def _check_c(result:list):
    if not isinstance(result, list):
        raise FailedParsingException(f'The response should be a list of mappings and the keys of a mapping should be `v1`, `v2`, `relation`. However, the following part is not a list: {result}') 
    for c in result:
        if not isinstance(c, dict):
            raise FailedParsingException(f'The constraint should be a mapping. However, the following part is not a mapping: {c}')
        keys = set(c.keys())
        if keys != {'v1', 'v2', 'relation'}:
            raise FailedParsingException(f'The keys of the constraint should be `v1`, `v2`, and `relation`. However, the following keys are found: {keys} in the constraint {c}.')


def _check_def_is_list(result:list)->Optional[str]:
    msgs = []
    for one_part in result:
        if not isinstance(one_part, list):
            msg = f'The response should be a list of constraints. However, the following part is not a list: {one_part}'
            msgs.append(msg)
    if len(msgs) == 0:
        return None
    return '\n'.join(msgs)

def _check_def_are_dict_cs(cs:list, def_info)->Optional[str]:
    msgs = []
    for c in cs:
        if not isinstance(c, dict):
            msg = f'The constraint should be a mapping. However, the following part is not a mapping: {c}'
            msgs.append(msg)
            
        else:
            msg = _check_keys_of_each_cs(c,def_info )
            if msg is not None:
                msgs.append(msg)
    if len(msgs) == 0:
        return None
    return '\n'.join(msgs)


def _check_keys_of_each_cs(c:dict, def_info:DefInfo)->Optional[str]:
    keys = set(c.keys())
    # if keys == {'name', 'predicate'}:
    #     return _check_each_field_in_c(c, def_info)
    if keys == {'v1', 'v2', 'relation'}:
        return _check_each_field_in_c(c, def_info)
    
        
    
    return f'The keys of the constraint should be `v1`, `v2`, and `relation`. However, the following keys are found: {keys} in the constraint {c}.'

def _check_each_field_in_c(c:dict, def_info:DefInfo)->Optional[str]:
    keys = set(c.keys())
    result = []
    # if keys == {'name', 'predicate'}:
    #     if c['predicate'] != 'always_valid':
    #         result.append(f'The predicate should be `always_valid`. However, the following predicate is found: {c["predicate"]}')
    #     check_name_result = _check_field_name_is_valid(c['name'], def_info)
    #     if check_name_result is not None:
    #         result.append(check_name_result)
    if keys == {'v1', 'v2', 'relation'}:
        v1_check_result = _check_val_in_c(c['v1'], def_info)
        if v1_check_result is not None:
            result.append(v1_check_result)
        v2_check_result = _check_val_in_c(c['v2'], def_info)
        if v2_check_result is not None:
            result.append(v2_check_result)
        relation_check_result = _check_relation_in_c(c['relation'])
        if relation_check_result is not None:
            result.append(relation_check_result)
    else:
        result.append(f'The keys of the constraint should be `v1`, `v2`, and `relation`. However, the following keys are found: {keys} in the constraint {c}.')

    if len(result) == 0:
        return None
    return '\n'.join(result)
        
def _check_val_in_c(val_repr:str, def_info:DefInfo)->Optional[str]:
    if not isinstance(val_repr, str):
        return f'The value should be a string. However, the following value is not a string: {val_repr}'
    if val_repr.isdigit():
        return None
    if val_repr.startswith('context.'):
        return None
    is_valid_field_info = _check_field_name_is_valid(val_repr, def_info)
    if is_valid_field_info is None:
        return None
    else:
        return is_valid_field_info
    raise NotImplementedError

def _check_relation_in_c(val_repr:str)->Optional[str]:
    if not isinstance(val_repr, str):
        return f'The relation should be a string. However, the following value is not a string: {val_repr}'
    if val_repr in {'eq', 'neq', 'ne', 'ge', 'gt', 'le', 'lt', 'in'}:
        return None
    else:
        return f'The relation should be one of the following predicates: `eq`, `neq`, `ne`, `ge`, `gt`, `le`, `lt`, `in`. However, the following relation is found: {val_repr}'

def _check_field_name_is_valid(name:str, def_)->Optional[str]:
    exists = _a_field_exist(def_.cur_def, def_.ref_dicts, name)
    if exists:
        return None
    return f'The field name {name} is not found in the definition. Please re-check the field name.'
    raise NotImplementedError

def get_prompt(
    def_info:DefInfo,
    search_engine, 
    query_num, 
    query_iter_idx, 
    module_name, 
    cur_module_def_names)->list:
    main_instruction = get_main_prompt(
        def_info,
        search_engine,
        module_name
    )
    if query_iter_idx == 0:
        return AttachedChatsFactory.generate_common_query_msg(main_instruction).release_messages()
    else:
        last_fpath = cur_module_def_names.get_query_names(query_iter_idx-1)
        refine_info = _get_refine_info(last_fpath.response_txt_path, def_info)
        # print('refine_info', refine_info)
        prompt = AttachedChatsFactory.generate_query_msg_with_refine(main_instruction, refine_info).release_messages()
    return prompt


def get_main_prompt(
    def_info:DefInfo,
    search_engine, 
    module_name)->str:
    template = get_template_prompt()
    # validation
    # get background
    query_instruction = f'validation of {module_name}'
    result_texts, cnodes, distances = search_engine.search_with_cnodes(query_instruction, k=1)
    background = '\n\n'.join(result_texts)
    # 
    return template.replace('{module_name}', module_name) .replace('{requirement_core}', requirement_core()).replace('{module_format}', get_get_fomrat_desc(def_info)).replace('{validation_desc}', background)
    


def get_get_fomrat_desc(def_info:DefInfo):
    format_ = def_info.cur_def
    format_str = get_json_fmt_str(format_)
    if len(def_info.ref_dicts) == 0:
        return format_str
    sub_components_part = get_json_fmt_str(def_info.ref_dicts)
    final_repr = f'{format_str}\nThe format of its fields are as follow\n{sub_components_part}'
    return final_repr


def get_template_prompt():
    return '''
# Task instruction:
# Please summarize the validation rules for the definition **{module_name}** according to the given background knowledge and return the result in the expected format.

# Background knowledge:
I will introduce the definition of **{module_name}** and the description of the validation of **{module_name}**

## Fefinition of **{module_name}**:
Here, I first introduce how to understand the given definition information and the then provide the definition information.

### How to understand the definition information:
The definition information is represented by the following way:

{requirement_core}

### definition information:
The definition of **{module_name}** is represented as follows:

{module_format}

## Description of the validation of **{module_name}**:
Here is the description of the validation of **{module_name}** from the WebAssembly specification.

{validation_desc}

# Expected format:
Your response should be organized in the following way:

1. Your response should be in JSON format.
2. If a definition has multiple variants, you should provide the validation rules for each variant.
3. The validation rules for each variant should be represented as a list of constraints for each component / field in the module definition.
4. Each constraint should be represented in the expected format:
    - The constraint should be represented as a mapping. 
    - You can skip the constraints on some fields:
        1. You do not need to infer the constraints for the fields with fixed values.
        2. You can skip the constraints for the fields that are always valid.
    - A constraint should be a mapping with the keys `v1`, `v2`, `relation`.
        - For the constraint that can be represented as a relation between two variables, you should represent the constraint as a mapping with the following keys and values:
            `v1`: the first variable
            `v2`: the second variable
            `relation`: it should be a string representing the relation between `v1` and `v2`, and it should be one of the following predicates 'eq', 'neq', 'ne', 'ge', 'gt', 'le', 'lt', 'in'. If the relation cannot be represented by the above predicates, you can use an appropriate predicate to represent the relation.
            The encoding rule of `v1` and `v2`: 
                1. If the variable is a constant (e.g., 0, 1, 2), you can use the constant value directly.
                2. If the variable is a field in the definition, you can represent it with the filed's name. For example, for the following definition `memtype`, which contains a field `limits`: 
                    {
                        "memtype": [
                            {
                                "name": "lim",
                                "type": "limits",
                                "description": "The limits of the memory type."
                            }
                        ]
                    }
                    {
                        "limits": [
                            {
                                "name": "flag",
                                "type": "<Fix:01:hex>",
                                "description": "A flag indicating that there is a maximum limit. The flag is fixed at 0x01."
                            },
                            {
                                "name": "min",
                                "type": "u32",
                                "description": "The minimum limit."
                            },
                            {
                                "name": "max",
                                "type": "u32",
                                "description": "The maximum limit."
                            }
                        ]
                    }
                you can represent the filed `lim` with the string `lim` and represent the filed named 'min' with the string `lim.min`.
                3. If the variable is a variable indicateed by the context. You can represent it like `context.var_name.attr`. For example, you can use 'context.tables.length' to represent the number of tables in the context.
5. Just summarize the constraints. Don't repeat the definition again.
'''
