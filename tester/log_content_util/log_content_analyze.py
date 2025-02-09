import re
from pathlib import Path
from tqdm import tqdm
from file_util import check_dir, read_json, save_json
from .get_key_util import group_tc_names_by_log_key
from .get_key_util import supported_strategies


def log_content_categorize_by_one_reason_path(reason_json_path, dumped_data_base_dir, log_categorize_dir, strategy_mode):
    # print(f'({reason_json_path}, {dumped_data_base_dir}, {log_categorize_dir}, {strategy_mode})')
    # return
    assert strategy_mode in supported_strategies
    reason_key2tc_result_dirs = get_reason_key2dumped_data_dirs_from_reason_json(
        reason_json_path, dumped_data_base_dir)
    assert isinstance(reason_key2tc_result_dirs, dict)
    # 
    # for k, v in reason_key2tc_result_dirs.items():
    #     print(k, len(v))
    # assert 0
    log_categorize_dir = check_dir(log_categorize_dir)
    path2reason_content_pair = {}
    sigs = set()
    for file_idx, (reason_key, tc_result_dirs) in enumerate(reason_key2tc_result_dirs.items(), start=1):
        # print(len(tc_result_dirs))
        log_key2tc_names = group_tc_names_by_log_key(
            tc_result_dirs, strategy_mode, reason_key)
        assert isinstance(log_key2tc_names, dict)
        # print([len(v) for v in log_key2tc_names.values()])
        log_key2tc_names_path = str(log_categorize_dir / f'{file_idx}.json')
        save_json(log_key2tc_names_path, log_key2tc_names)
        # print(log_key2tc_names_path)
        # assert 0
        for log_key in tqdm(log_key2tc_names.keys(), total=len(log_key2tc_names)):
            # TODO clean，，，
            reason_key_path = f'{log_key2tc_names_path}<-->{reason_key}'
            path2reason_content_pair.setdefault(
                reason_key_path, []).append(log_key)
            sigs.add(log_key)

    save_json(log_categorize_dir /
              '0_reason_content_pair_inv_log.json', path2reason_content_pair)
    save_json(log_categorize_dir / '0_sigs.json', list(sigs))


def get_reason_key2dumped_data_dirs_from_reason_json(reason_json_path, dumped_data_base_dir):
    dumped_data_base_dir = Path(dumped_data_base_dir)
    reason_tc_names = read_json(reason_json_path)
    # assert 0, print(list(reason_tc_names.keys()))
    # ! 
    return {reason_key: [dumped_data_base_dir/tc_name for tc_name in tc_names] for reason_key, tc_names in reason_tc_names.items() if "variable_diff=None" not in reason_key}
