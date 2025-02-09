from GPT_API_ENV.prompt_util.control_flow_related import query_control_flow_and_save_result


if __name__ == '__main__':
    query_control_flow_and_save_result(
        False,
        result_dir='./GPT_API_ENV/results/cfg_base1_test',
        max_idx=3,
        skip_exist=False
        )
