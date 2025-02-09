from enum import Enum

from tqdm import tqdm
from ..ResponseChecker.each_def_checker import InvalidTypeDescException, _is_valid_fix_part, extract_terms_from_desc, type_desc_is_valid
from file_util import check_dir, path_read
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


class FmtKind(Enum):
    binary = 1
    text = 2

    def to_str(self):
        return self.name


class ModuleDefQueryFileNames(OneTaskQueryFileNames):
    def __init__(self, base_dir:Union[str, Path], fmt_type:FmtKind, module_file_name:str, max_idx:int):
        self.fmt_type: FmtKind = fmt_type
        self.module_name = module_file_name
        self.fmt_name = fmt_type.to_str()
        name_base = f'{module_file_name}_{self.fmt_name}'
        super().__init__(base_dir, name_base, max_idx)

    
def query_all_module_def_related_and_save_result(sub_dir_name, query_num=1, debug=False, skip_exist=False, max_iter_num=15, def_names=module_names_to_ask):
    # query_num = 1  # 1, 8
    # search_engine =   SpecSearchEngine.get_default()
    search_engine = SpecSearchEngine.get_all_binary_default()
    result_dir = check_dir(module_def_result_dir / sub_dir_name)
    introduced_names = []
    mentioned_names = []
    naive_ones = naive_module_component_types
    naive_ones = set(naive_ones)
    uncovered_names = def_names
    for i in range(5):
        if len(uncovered_names) == 0:
            break
        for fmt_kind in {FmtKind.binary}:
            for module_name in tqdm(uncovered_names):
                module_file_name = _get_file_name(module_name)
                cur_introduced_names, cur_mentioned_names = query_module_def_and_save_result(
                    search_engine,
                    result_dir,
                    query_num,
                    module_name,
                    module_file_name,
                    fmt_kind,
                    max_iter_num=max_iter_num,
                    skip_exist=skip_exist,
                    debug=debug)
                introduced_names.extend(cur_introduced_names)
                mentioned_names.extend(cur_mentioned_names)
        uncovered_names = set(mentioned_names) - set(introduced_names)
        uncovered_names = uncovered_names - naive_ones
        # uncovered_names = list(uncovered_names)
        print('uncovered_names', uncovered_names)
        print('introduced_names', introduced_names)
    print(f'Result dir: {result_dir}')


def _get_file_name(ori_desc):
    # if ori_desc in module_name2path_name:
    #     return module_name2path_name[ori_desc]
    return ori_desc.replace(' ', '_').replace('/', '_')


def query_module_def_and_save_result(
        search_engine,
        result_dir,
        query_num,
        module_name,
        module_file_name,
        fmt_kind: FmtKind,
        skip_exist=False,
        max_iter_num=15,
        debug=False):
    cur_module_def_names = ModuleDefQueryFileNames(
        result_dir, 
        fmt_kind, 
        module_file_name, 
        max_iter_num
    )
    exist_epoch_num = cur_module_def_names.exist_epoch_num
    # if exist_epoch_num !=0 and skip_exist:
    #     raise NotImplementedError('Not implemented yet.')
    # 
    print('|||=== exist_epoch_num', exist_epoch_num)
    if skip_exist:
        start_idx = exist_epoch_num
    else:
        start_idx = 0
    for query_iter_idx in range(start_idx, max_iter_num):
        print(f'query_iter_idx: {query_iter_idx}')
        if query_iter_idx == 0:
            last_fpaths = None
        else:
            last_fpaths = cur_module_def_names.get_query_names(idx=query_iter_idx-1)
        if is_well_formatted_mod_def(last_fpaths):
            def_names, mentioned_names = get_names_in_a_response_txt_path(last_fpaths.response_txt_path)
            return def_names, mentioned_names
            break
        print('is_well_formatted_mod_def(last_fpaths)', is_well_formatted_mod_def(last_fpaths), last_fpaths)
        next_fpaths = cur_module_def_names.get_query_names(query_iter_idx)
        prompt = get_prompt(search_engine, query_num, query_iter_idx, module_name, fmt_kind, cur_module_def_names)
        print('Try get response')
        ask_core_ng(
            next_fpaths,
            prompt,
            debug=debug,
            skip_exist=skip_exist
            )
    return [], []
            

def is_well_formatted_mod_def(fnames_result:Optional[QueryFileNames]):
    if fnames_result is None:
        return False
    # 
    try:
        check_a_response_txt_path(fnames_result.response_txt_path)
    except FailedParsingException as e:
        return False
    except InvalidTypeDescException as e:
        return False
    except MayWrongSyntaxWraning as e:
        return False
    return True


def check_a_response_txt_path(fpath:Path, required_name:Optional[str]=None):
    result = content_as_final_kv(fpath)
    all_dicts = []
    for definition_desc in result:
        if isinstance(definition_desc, list):
            all_dicts.extend(definition_desc)
        elif isinstance(definition_desc, dict):
            all_dicts.append(definition_desc)
        else:
            raise FailedParsingException(f'The description should be a dict or a list, rather than {type(definition_desc)}')
    for d in all_dicts:
        if len(d) != 1:
            raise FailedParsingException(f'The description for a definition should be a dict with a single key-value pair, mapping definiiton name to its components, rather than {d}, which has {len(d)} key-value pairs.')
        _check_a_component_is_well_formatted(d)
    all_names = []
    for d in all_dicts:
        all_names.extend(d.keys())
    if required_name is not None and required_name not in all_names:
        raise FailedParsingException(f'Please check the response the response and ensure there is a definition whose name is {required_name}.')


def get_names_in_a_response_txt_path(fpath:Path):
    result = content_as_final_kv(fpath)
    defined_names = []
    mentioned_names = []
    meitioned_types=  []
    for definition_descs in result:
        # assert len(definition_desc) == 1, definition_desc 
        print('definition_descs', definition_descs, type(definition_descs))
        # assert isinstance(definition_descs, list)
        if not isinstance(definition_descs, list):
            definition_descs = [definition_descs]
        for definition_desc in definition_descs:
            assert len(definition_desc) == 1, definition_desc 
            cur_component_name = list(definition_desc.keys())[0]
            self_introduce = False
            for component_desc in list(definition_desc.values())[0]:
                # print('XXX component_desc', component_desc)
                type_def = component_desc['type']
                if type_def == cur_component_name:
                    self_introduce = True
                    continue
                meitioned_types.append(type_def)
                # print('||| type_def', type_def)
                sub_mentioned_names = extract_terms_from_desc(type_def)
                mentioned_names.extend(sub_mentioned_names)
            if not self_introduce:
                defined_names.append(cur_component_name)
            # if type_def.startswith('<Union:'):
            # if 
    return defined_names, mentioned_names  # , meitioned_types



def _check_a_component_is_well_formatted(d:dict)->None:
    # if len()
    for component_name, component_desc in d.items():
        if not isinstance(component_desc, list):
            raise FailedParsingException(f'The description of the {component_name} should be a list, rather than {type(component_desc)}')
        has_union = False
        for each_desc in component_desc:
            if not isinstance(each_desc, dict):
                raise FailedParsingException(f'The description of the {component_name} should be a dict, rather than {type(each_desc)}')
            # if not _check_a_desc_is_well_formatted(each_desc):
            #     return False
            # for component_attr
            # if len()
            component_attr_names = set(each_desc.keys())
            if {'type',  'description', 'name'} - component_attr_names:
                raise FailedParsingException(f'The component should have the following keys: type,  description')
            check_name_is_not_type_desc(each_desc['name'])
            type_desc = each_desc['type']
            if not type_desc_is_valid(type_desc):
                raise FailedParsingException(f'The type description {type_desc} is invalid.')
        # 
        all_descs = [d['type'] for d in component_desc]
        if all([_is_valid_fix_part(d) for d in all_descs]) and len(all_descs) > 1:
            raise MayWrongSyntaxWraning(f'The for description for component {component_name} indicates that {component_name} consists of a sequence of constant bytes. However, it is a rare situation. Please check the relationship between the constant parts to confirm whether they exist at the same time or only one of them exists at a time (i.e. union relationship).')
            # print('all_descs', all_descs)
        # 
            # if '<Union:' in type_desc:
            #     has_union = True
        # if has_union and len(component_desc) != 1:
        #     raise FailedParsingException(f'The component {component_name} is currently described with a union type, but it also includes additional component descriptions. This approach is incorrect because a definition of {component_name} that has multiple representations should only include one union-type component. The union should represent the possible variations with a union type, and the individual components of each variation should be detailed separately. Please revise the definition {component_name} accordingly, ensuring that the union component accurately captures the variations of {component_name}, while other details are moved to describe each variation explicitly.')


def check_name_is_not_type_desc(name:str):
    if '<' in name or '>' in name:
        raise FailedParsingException(f'The name {name} should not be a type description.')


def get_prompt(search_engine, 
               query_num, 
               prompt_idx, 
               module_name, 
               fmt_kind: FmtKind, 
               cur_module_def_names:ModuleDefQueryFileNames
    ):

    background = _get_background(search_engine,
                                    query_num,
                                    module_name,
                                    fmt_kind)
    # 
    
    if fmt_kind == FmtKind.binary:
        example_text = get_two_binary_example()
    else:
        raise NotImplementedError('Not implemented yet.')
    main_question = _get_base_main_question_text_core(
        background_info=background,
        module_name=module_name,
        example_info=example_text,
        format_requirement=get_format_requirement_text(),
        fmt_kind=fmt_kind
    )
    if prompt_idx == 0:
        prompt = AttachedChatsFactory.generate_common_query_msg(main_question).release_messages()
    else:
        print('|||||||||| last prompt_idx', prompt_idx-1)
        last_fpath = cur_module_def_names.get_query_names(prompt_idx-1)
        refine_info = _get_refine_info(module_name, fmt_kind, last_fpath)
        # print('refine_info', refine_info)
        prompt = AttachedChatsFactory.generate_query_msg_with_refine(main_question, refine_info).release_messages()
    return prompt
        # The last 

def _get_refine_info(module_name, fmt_kind: FmtKind, last_fpaths)-> str:
    # assert last_fpaths is not None
    if is_well_formatted_mod_def(last_fpaths):
        raise ValueError('According to the expected logic, the last response should not be well-formatted. Please check the implementation.')

    s = _get_refine_info_core(last_fpaths.response_txt_path)
    assert s != ''
    return s

def _get_refine_info_core(response_path)-> str:
    msg = None
    try:
        check_a_response_txt_path(response_path)
    except FailedParsingException as e:
        msg = f'{e}'
    except InvalidTypeDescException as e:
        msg = f'{e}'
    except MayWrongSyntaxWraning as e:
        msg = f'{e}'
    if msg is None:
        return ''
    s = f'''The last response of the query is as follows: \n\n{path_read(response_path)}\n\nHowever, there are some errors in the response: {msg}. Please refine the response. Furthermore, you may loss variations of the definition.Please check the background information carefully.Please refine the response. Note it, you should finish all the tasks again, not just the ill-formatted one.'''

    return s

def _get_background(search_engine: SpecSearchEngine, query_num, module_name, fmt_kind: FmtKind):
    question_template_dict: dict[FmtKind, str] = {
        FmtKind.binary: 'The binary definition of {}',
        FmtKind.text: 'The text definition of {}',
        # FmtKind.binary: 'The binary syntax module definition of {}',
        # FmtKind.text: 'The text syntax module definition of {}'
    }
    query_instruction = question_template_dict[fmt_kind].format(module_name)
    print('background_q', query_instruction)
    result_texts, cnodes, distances = search_engine.search_with_cnodes(query_instruction, k=query_num)
    background = _combine_text(result_texts)

    print('distances', distances)

    all_titles = []
    for n in cnodes:
        assert isinstance(n, customNode)
        title = n.all_title_repr
        all_titles.append(title)
    print('all_titles', all_titles)
    return background


def _combine_text(texts):
    return '\n\n'.join(texts)


def _get_base_main_question_text_core(
    background_info:str,
    module_name:str,
    example_info:str,
    format_requirement:str,
    fmt_kind: FmtKind
):
    if fmt_kind == FmtKind.text:
        template = '''Please summarize the text definition of **{module_name}** in both natural language and JSON format. Use the attached background information, which includes the text definition syntax and other relevant details from the WebAssembly specification, to ensure accuracy and completeness.

**Formatting Requirements**:  
{format_requirement}

**Background Information**:  
{background_info}

**Example of a Binary Definition**:  
{example_info}'''
    elif fmt_kind == FmtKind.binary:
        template = '''Please summarize the binary definition of **{module_name}** in both natural language and JSON format. Use the attached background information, which includes the binary definition syntax and other relevant details from the WebAssembly specification, to ensure accuracy and completeness.

**Formatting Requirements**:  
{format_requirement}

**Background Information**:  
{background_info}

**Example of a Definition**:  
{example_info}'''
    else:
        raise ValueError(f'Unsupported fmt_kind: {fmt_kind}')
    return template.format(
        module_name=module_name,
        background_info=background_info,
        format_requirement=format_requirement,
        example_info=example_info
    )


def get_format_requirement_text():
    s = '''
You are tasked with identifying and describing each part of the definition in detail. The output should be provided in JSON format, following these guidelines:

''' + requirement_core() + '''

For example:


- If a type `<type1>` can be represented as either `<type2>` or `<type3>`, and these definitions have distinct formats, the output should:
  - Include a union representation of `<type1>` that combines `<type2>` and `<type3>`.
  - Provide detailed descriptions of `<type2>` and `<type3>` separately, immediately following the description of `<type1>`.

The JSON output must adhere to the following structure:

```json
[
    {
        "<type1>": [
            {
                "name": "...",
                "type": "<Union:<type2>:<type3>>",
                "description": "A description explaining that <type1> can be either <type2> or <type3>."
            }
        ]
    },
    {
        "<type2>": [
            {
                "name": "...",
                "type": "...",
                "description": "A detailed description of <type2>."
            },
            ...
        ]
    },
    {
        "<type3>": [
            {
                "name": "...",
                "type": "...",
                "description": "A detailed description of <type3>."
            },
            ...
        ]
    }
]
```
Please ensure the response is correct and complete. The response should include all variations of the definition. Ensure the response does not misuse the `list` and (misuse meaning represent a Union as a list).'''
    return s


def requirement_core()->str:
    s = '''
1. Each key in the JSON represents the name of a definition.
2. The value is a **list** of the definition's components.  
3. Each component in the list must include the following fields:
   - **`name`**: Specifies the name of the component.
   - **`type`**: Specifies the type of the component. If a type has multiple varaints, you must explicitly define it as a union using `<Union:...>`.
   - **`description`**: Provides a detailed description of the component.
4. **You must first point out all variantions of the definitions and include all of them in the JSON and represent the definition using <Union:Variant1:...:VariantN>**

### Rules for Representing Types

1. **Basic Types**: Use a single token such as `u32`, `i32`, `blocktype`, `valtype`, `utf8str`, `byte`, etc.
2. **Constant Values**: Represent fixed values using `<Fix:<val>:<type1>>`, where `val` is the constant value and `type1` is the type. For example, a constant `0x60` of type `hex` is written as `<Fix:60:hex>`. Please note to use hexadecimal notation when representing results, rather than decimal.
3. **Complex Types**:
   - `<Union:<type1>:<type2>:...>`: Represents a type that can be one of multiple varaints (`type1`, `type2`, etc.).
   - `<Array:<type1>:<n>>`: Represents an array of `n` elements, all of type `type1`.
   - `<Vec:<type1>>`: Represents a vector of elements, all of type `type1`.
   - `<Optional:<type1>>`: Represents an optional type `type1`.

### Structured and Hierarchical Descriptions

1. **Hierarchical Relationships**: If a component `<type1>` is described using another type `<type2>`, and the description for `<type2>` is included in the provided information, the LLM must:
   - First describe `<type1>` as a single component.
   - Provide the descriptions of `<type2>` and `<type3>` in subsequent entries, explicitly detailing their structure.
    '''
    return s.strip('\n ')

def get_data_count_sample():
    return '''The binary syntax of data count section is 
{
    "data_count_section": [
        {
            "name": "section_id",
            "type": "<Fix:0C:hex>",
            "description": "The ID of the data count section, which is fixed at 0x0C."
        },
        {
            "name": "section_len",
            "type": "u32",
            "description": "The length of the data count section in bytes."
        },
        {
            "name": "n",
            "type": "<Optional:u32>",
            "description": "An optional u32 value representing the number of data segments in the data section. If present, it must match the length of the data segment vector; otherwise, the module is malformed."
        }
    ]
}

    It consists of a single field n, which is a u32 value, and its value is the length of the data section.
    '''

def get_two_binary_example():
    return f'''#### First example:
{get_data_count_sample()}


#### Second example:
{get_active_element_example()}
'''
