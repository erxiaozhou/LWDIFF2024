from extract_dump import are_different
from extract_dump import load_results_from_one_dumped_data_dir
from file_util import read_json, save_json, check_dir
from pathlib import Path
from functools import lru_cache
from tqdm import tqdm
from extract_dump.data_comparer import DiffStrategy, diffResult


# ! not used
def dumped_data_base_dir2reason_summary_json(result_json_path, dumped_data_base_dir, except_log, diff_strategy:DiffStrategy):
    reason_summary = {}
    except_tc_names = []
    for dumped_data_dir in tqdm(Path(dumped_data_base_dir).iterdir(), desc='In dumped_data_base_dir2reason_summary_json'):
        tc_name = dumped_data_dir.name
        try:
            dumped_results = load_results_from_one_dumped_data_dir(dumped_data_dir)
            difference_reason = are_different(dumped_results)
            if not difference_reason.no_diff:
                reason_key = _get_key_from_reason_content(difference_reason, diff_strategy)
                if reason_key not in reason_summary:
                    reason_summary[reason_key] = []
                reason_summary[reason_key].append(tc_name)
        except Exception:
            except_tc_names.append(tc_name)
    save_json(result_json_path, reason_summary)
    save_json(except_log, except_tc_names)


def dumped_data_base_dir2reason_base_dir(dumped_data_base_dir, reason_base_dir):
    reason_base_dir = check_dir(reason_base_dir)
    dumped_data_base_dir = Path(dumped_data_base_dir)
    for tc_dumped_data_dir in tqdm(dumped_data_base_dir.iterdir(), desc='In dumped_data_base_dir2reason_base_dir'):
        tc_name = tc_dumped_data_dir.name
        
        dumped_results = load_results_from_one_dumped_data_dir(tc_dumped_data_dir)
        difference_reason = are_different(dumped_results)
        if  not difference_reason.no_diff:
            difference_reason.save_as_json(reason_base_dir / f'{tc_name}.json')


def reason_base_dir2reason_summary_json(reason_base_dir, save_path, diff_strategy:DiffStrategy):
    reason_summary = {}
    dir_path = Path(reason_base_dir)
    for p in tqdm(dir_path.iterdir(), desc='In reason_base_dir2reason_summary_json'):
        tc_name = p.stem
        diff_result = diffResult.from_json(p)
        diff_result_key = _get_key_from_reason_content(diff_result, diff_strategy)
        reason_summary.setdefault(diff_result_key, []).append(tc_name)

    save_json(save_path, reason_summary)


@lru_cache(maxsize=4096 * 4, typed=False)
def _get_key_from_reason_content(diff_result:diffResult, diff_strategy:DiffStrategy):
    return diff_result.as_unique_key(diff_strategy)

