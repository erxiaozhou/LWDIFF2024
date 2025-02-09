python script_analyze_in_result_base_dir.py "$1"
python script_run_bug_counter.py result_base_dir "$1" skip_key
python script_prepare_unseen_maybe_bug_cases.py "$1"
# python run_dir_tester_main.py no_mutation_halfdump "$1/to_recheck_cases"  "$1/to_recheck_cases_result"
python script_analyze_in_result_base_dir.py "$1/to_recheck_cases_result"  # this line is useful
# script_extract_smith_case_name_from_exec_log.py