from pathlib import Path
from .prompt_util.util import get_inst_name2exec_inst_name


if __name__ == '__main__':
    # get all names
    inst_name2exec_inst_name = get_inst_name2exec_inst_name()
    all_inst_names = list(inst_name2exec_inst_name.keys())
    # get generated files' name
    generated_file_dir = Path('./results/inst/with_example_v1_without_background_re_gen/')
    suffix_len = len('_result.txt')
    generated_file_names = [f.name[:-suffix_len] for f in generated_file_dir.glob('*_result.txt')]
    # 
    un_generated_insts = set(all_inst_names) - set(generated_file_names)
    print(f'un_generated_insts: {un_generated_insts}')
