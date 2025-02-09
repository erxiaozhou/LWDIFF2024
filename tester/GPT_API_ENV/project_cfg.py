from pathlib import Path
from file_util import check_dir
project_path = Path(__file__).parent.absolute()

# def get_abs_path(relevant_path):
    

doc_core_folder_path = project_path / 'spec/document/core'
default_core_dict_p = project_path / 'parsing_spec_data/core_dict_new.pkl'
default_tags_p = project_path / 'parsing_spec_data/tags_new.pkl'
default_tags2cnodes_p = project_path / 'parsing_spec_data/tags2cnode.pkl'

default_env_store_path = project_path / 'parsing_spec_data/env.pickle'
default_tar_names_p = project_path / 'parsing_spec_data/tar_names.json'
default_titles_p = project_path / 'parsing_spec_data/titles.json'
default_op_name2exec_fmt_json_path = project_path / 'parsing_spec_data/op_name2exec_fmt.json'
default_cexec_name_query_result_demo_path = project_path / 'parsing_spec_data/cexec_name_query_result_demo.json'
cexec_name2fexec_name_json_path = project_path / 'parsing_spec_data/cexec_name2fexec_name.json'

raw_cp910_jsons_dir = project_path / 'pre_data/combined_inst_data_3'
# text embedding
text2embedding_dim = 3072
text2embedding_model_name = "text-embedding-3-large"
# text embedding dirs
# project_path / '

text2embedding_data_base_dir = check_dir(project_path / 'text2embedding_data')
text2embedding_data_text_dir = check_dir(text2embedding_data_base_dir / 'texts')
text2embedding_data_embedding_dir = check_dir(text2embedding_data_base_dir / 'embeddings')

result_dir = check_dir(project_path / 'results')
cfg_result_dir = check_dir(result_dir / 'cfg')
module_def_result_dir = check_dir(result_dir / 'module_def')
inst_result_dir = check_dir(result_dir / 'inst')

# inst op info path
inst_op_info_path = project_path / 'parsing_spec_data/inst_op_info.pkl'
last_inst_op_info_json_path = project_path / 'parsing_spec_data/last_inst_op_info.pkl'

op_name2exec_fmt_json_path = project_path / 'pre_data/op_name2exec_fmt.json'


# inst related
inst_template_path = project_path / 'prompt_util/inst_ptemplate_init.txt'
global_set_exmaple_path = project_path / 'prompt_util/inst_result_examples/global_set.txt'
i32_store_example_path = project_path / 'prompt_util/inst_result_examples/i32_store.txt'

module_name2path_name_ori = {
    'data count section': 'data_count',
    'global variable': 'global_variable',
    'memory section': 'memory_section',
    'type': 'type',
    'start section': 'start',
    'import section': 'import_section',
    'function section': 'function_section',
    'table section': 'table_section',
    'passive element segment': 'passive_element_segment',
    'active element segment': 'active_element_segment',
    'declarative element segment': 'declarative_element_segment',
    'active data segment': 'active_data_segment',
    'passive data segment': 'passive_data_segment',
    'export section': 'export_section',
    'custom section': 'custom_section',
}


module_name2path_name = {
    'data count section': 'data_count',
    'one global variable': 'global_variable',
    'one memory': 'memory_section',
    # 'one type': 'type',
    'start section': 'start',
    'one import': 'import_section',
    'one function': 'function_section',
    'one table': 'table_section',
    'one passive element segment': 'passive_element_segment',
    'one active element segment': 'active_element_segment',
    'one declarative element segment': 'declarative_element_segment',
    'one active data segment': 'active_data_segment',
    'one passive data segment': 'passive_data_segment',
    'one export': 'export_section',
    'custom section': 'custom_section',
}



module_names_to_ask = list(module_name2path_name.keys()) + [
    'memory section',
    'function section',
    'table section',
    'import section',
    'export section',
    'custom section',
    'start section',
    'type section',
    'global section',
    'data section',
    'element section',
    'code section',
    'data count section',
]


module_names_to_ask = [
    'memory section',
    'function section',
    'table section',
    'import section',
    'export section',
    'custom section',
    'start section',
    'type section',
    'global section',
    'data section',
    'element section',
    'code section',
    'data count section',
]
