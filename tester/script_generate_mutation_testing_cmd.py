import sys
from pathlib import Path


argv = sys.argv
assert len(argv) == 13, '''
Usage: python script_generate_mutation_testing_cmd.py 
    <rename_result_dir:bool> 
    <remove_result_dir:bool> 
    <time_out_str:str> <seed_dir:str> <result_base_dir:str> <impl_mode:str> <seed_scheduler_name:str> <mutation_selector_name:str> <suffix:str> <post_process:bool> <mutation_config_path:str> <structure_name:str>

'''
assert argv[1] in ['True', 'False']
rename_result_dir: bool = True if argv[1] == 'True' else False
assert argv[2] in ['True', 'False']
remove_result_dir: bool = True if argv[2] == 'True' else False
time_out_str: str = argv[3]
seed_dir: str = argv[4]
result_base_dir: str = argv[5]
impl_mode: str = argv[6]
seed_scheduler_name: str = argv[7]
mutation_selector_name: str = argv[8]
suffix: str = argv[9]
assert argv[10] in ['True', 'False']
post_process: bool = True if argv[10] == 'True' else False
mutation_config_path = argv[11]
structure_name = argv[12]


tester_name_prefix = f'{impl_mode}_{seed_scheduler_name}_{mutation_selector_name}_{time_out_str}_{structure_name}_{suffix}'
if rename_result_dir:
    result_base_dir = Path(result_base_dir)
    ori_sub_dir_name = result_base_dir.name
    new_name = f'{ori_sub_dir_name}_{tester_name_prefix}'
    result_base_dir = result_base_dir.parent / new_name


# remove base dir cmd
if remove_result_dir:
    remove_result_dir_cmd = f'rm -rf {result_base_dir}'
else:
    remove_result_dir_cmd = ''


# main testing cmd
# cmd = f'timeout {time_out_str} python run_dir_tester_main.py mutation_testing {seed_dir} {result_base_dir} {mutation_config_path} {seed_scheduler_name} {mutation_selector_name} {impl_mode} {tester_name_prefix} {structure_name}'  # the original one
cmd = f'python run_dir_tester_main.py mutation_testing {seed_dir} {result_base_dir} {mutation_config_path} {seed_scheduler_name} {mutation_selector_name} {impl_mode} {tester_name_prefix} {structure_name} {time_out_str}'

# post process cmd
if post_process:
    post_process_cmd = f' ./post_analyze_result_base_dir.sh {result_base_dir}'
else:
    post_process_cmd = ''


cmds = [remove_result_dir_cmd, cmd, post_process_cmd]
cmds = [cmd for cmd in cmds if cmd != '']
final_cmd = ' ; '.join(cmds)
print(final_cmd)
