from extract_dump.retrieve_coverage import trigger_new_guards


def trigger_new_cov_tc_idxs(case_exec_info_list, coverage_summary, can_be_seed_tc_indexs):
    new_can_be_seed_tc_indexs = []
    for can_be_seed_tc_index in can_be_seed_tc_indexs:
        if trigger_new_guards(case_exec_info_list[can_be_seed_tc_index].caseCoverage, coverage_summary):
            new_can_be_seed_tc_indexs.append(can_be_seed_tc_index)
    return new_can_be_seed_tc_indexs
