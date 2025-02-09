from .seed_select_info_util import Path2SeedSelectInfoClass, SeedSelectInfo
import random
from pathlib import Path
from typing import List, Tuple
from extract_dump.retrieve_coverage import CoverageAll
from logging import Logger


def get_init_seeds(seeds):
    sizes = [Path(p).stat().st_size for p in seeds]
    path_and_size = list(zip(seeds, sizes))
    from_short_to_large = sorted(path_and_size, key=lambda x:x[1])
    # print(from_short_to_large)
    sorted_paths = [p for p, _ in from_short_to_large]
    return sorted_paths


def cal_selected_time_factor(seedPath2SeedSelectInfo:Path2SeedSelectInfoClass, proper_max_selected_time, seed_path):
    selected_num = seedPath2SeedSelectInfo[seed_path].selected_num
    raw_f = proper_max_selected_time // (2**selected_num)
    selected_time_factor = max(raw_f, 1)
    return selected_time_factor


def cal_coverage_length_factor(seedPath2SeedSelectInfo:Path2SeedSelectInfoClass, logger:Logger, seed_path, coverage_summary:CoverageAll):  # bitmap factor
    seed_select_info = seedPath2SeedSelectInfo[seed_path]
    unique_visited_guard_num = seed_select_info.unique_visited_guard_num
    min_unique_visited_guard_num = coverage_summary.min_unique_visited_guard_num
    if coverage_summary.update_times == 0:
        ratio = 1
    else:
        avg_cocd_cov = coverage_summary.cur_avg_unique_visited_guard_num
        # ratio =unique_visited_guard_num / min_unique_visited_guard_num
        ratio = (unique_visited_guard_num - min_unique_visited_guard_num) / (avg_cocd_cov-min_unique_visited_guard_num)
    return min(max(0.5, ratio), 30)


def select_a_seed_randomly(seed_pool: List[str]) -> Tuple[int, str]:
    seed_idx = random.randint(0, len(seed_pool)-1)
    seed_path = str(seed_pool[seed_idx])
    return seed_idx, seed_path


# cov related

def get_rare_guard_factor(seedPath2SeedSelectInfo:Path2SeedSelectInfoClass, logger:Logger, seed_path, coverage_summary: CoverageAll):
    seed_path = str(seed_path)
    assert seed_path in seedPath2SeedSelectInfo
    rarest_guards_in_the_seed = get_rarest_guard(coverage_summary, seedPath2SeedSelectInfo[seed_path].unique_visited_guards)
    if rarest_guards_in_the_seed is None:
        return 1
    else:
        median = p25_rarest_guard_freq(coverage_summary)
        freq = coverage_summary.guard_visit_couner[rarest_guards_in_the_seed]
        raw_factor = median / freq
        logger.debug(f'freq: {freq} median: {median}, median/freq: {raw_factor}')
    return min(max(raw_factor, 0.1), 20000)


def p25_rarest_guard_freq(coverage_summary: CoverageAll):
    guard_visit_couner = coverage_summary.guard_visit_couner
    freqs = guard_visit_couner.most_common()
    freqs = [x[1] for x in freqs]
    len_ = len(freqs)
    return freqs[(len_*3)//4]


def get_rarest_guard(coverage_summary: CoverageAll, filter_guards=None):
    if len(coverage_summary.visited_guards) == 0:
        return None
    guard_visit_couner = coverage_summary.guard_visit_couner
    most_rare_guards = guard_visit_couner.most_common()[::-1]
    for guard, freq in most_rare_guards:
        if filter_guards is not None:
            if guard in filter_guards:
                return guard
        else:
            return guard


def can_replace_ori_seed(new_case_result: SeedSelectInfo, ori_case_result: SeedSelectInfo):
    from file_util import get_logger
    # logger = get_logger('can_replace_ori_seed', '/tmp/can_replace_ori_seed.log')
    # assert new_case_result.dumped_results is not None
    assert ori_case_result.case_can_be_seed and new_case_result.case_can_be_seed
    # logger.info(f'new_case_result.can_success_num {new_case_result.can_success_num} ori_case_result.can_success_num {ori_case_result.can_success_num};')
    if new_case_result.can_success_num >= ori_case_result.can_success_num:
        new_case_guards = new_case_result.unique_visited_guards
        ori_case_guards = ori_case_result.unique_visited_guards
        if len(new_case_guards - ori_case_guards) > 0 and len(ori_case_guards - new_case_guards) == 0:
            return True
        # print(len(ori_case_guards - new_case_guards))
        # logger.info(f'len(ori_case_guards - new_case_guards): {len(ori_case_guards - new_case_guards)}')
    return False
