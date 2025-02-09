from GPT_API_ENV.prompt_util.inst_related import query_insts_info_and_save_result4
from GPT_API_ENV.prompt_util.util import get_all_inst_names
from file_util import read_json


def sample_some_insts(p=0.1):
    all_inst_names = get_all_inst_names()
    import random
    names = random.sample(all_inst_names, int(len(all_inst_names) * p))
    return names


if __name__ == '__main__':
    considered_insts_names = None
    considered_insts_names = read_json('considered_names.json')

    sub_dir_name='std43'
    debug = True
    debug = False
    if debug:
        sub_dir_name += '_debug'
    skip_exist = True
    # skip_exist = False

    query_insts_info_and_save_result4(
        sub_dir_name=sub_dir_name,
        considered_insts_names = considered_insts_names,
        use_op_background_info=False, 
        with_example=True,
        skip_exist=skip_exist,
        debug=debug,
        max_idx=3
    )
