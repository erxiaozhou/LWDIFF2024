from GPT_API_ENV.prompt_util.module_def_related import query_all_module_def_related_and_save_result
from GPT_API_ENV.project_cfg import module_names_to_ask

if __name__ == '__main__':
    sub_dir_name = '1107_v74import'
    debug = False
    if not debug:
        sub_dir_name += '_nodebug'
    target_names = list(module_names_to_ask)
    query_all_module_def_related_and_save_result(sub_dir_name=sub_dir_name, query_num=1, debug=debug, skip_exist=True, max_iter_num=10, def_names=target_names)
    