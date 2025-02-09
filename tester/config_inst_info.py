from pathlib import Path
from file_util import read_json


all_inst_names:set[str] = set(read_json('inst_ty_info/inst_names.json'))
easy_sound_strategy_need_transfer_result = read_json('inst_ty_info/easy_sound_strategy_need_transfer_result.json')
raw_binary_info = read_json('inst_ty_info/collected_binary_info.json')
inst_bynary_type_desc_path = Path('inst_ty_info/inst_bynary_type_desc.json')

control_inst_names = {'loop', 'call', 'nop', 'call_indirect', 'br', 'return', 'br_if', 'br_table', 'if', 'unreachable', 'block'}
poly_control_inst_names = {'loop', 'call', 'call_indirect', 'br', 'return', 'br_if', 'br_table', 'if', 'unreachable', 'block'}

gpt_data_v2_dir = Path('./openai_data/syned_openai_demo_v2_spec_fixed')

desc_path = Path('GPT_API_ENV/results/final/module_def_trimmed_list.json')