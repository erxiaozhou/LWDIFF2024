from extract_dump import load_results_from_one_dumped_data_dir


def load_log_from_one_tc_result(one_tc_result_dir):
    results = load_results_from_one_dumped_data_dir(one_tc_result_dir)
    return load_log_from_dumped_results(results)

def load_log_from_dumped_results(dumped_results):
    name_log = {}
    for r in dumped_results:
        if 'log_content' in r.__dict__ and r.log is None:
            name_log[r.name] = r.log_content
        else:
            name_log[r.name] = r.log
    return name_log
