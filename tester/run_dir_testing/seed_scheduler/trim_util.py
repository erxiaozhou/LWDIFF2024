from collections import Counter
from logging import Logger
from pathlib import Path
from typing import List, Optional
from file_util import check_dir, cp_file, save_json

from ..seed_scheduler.seed_select_info_util import SeedSelectInfo, Path2SeedSelectInfoClass


def trim_seed(seeds:list[str], seeds_info:Path2SeedSelectInfoClass, logger:Optional[Logger]=None):
    # rule1: un exec seeds
    print('ORI len(seeds)', len(seeds))
    print('ORI len(seeds_info)', len(seeds_info))
    unexec_seeds = [s for s in seeds if s not in seeds_info]
    # for seed, seed_info in seeds_info.items():
    #     if seed_info.selected_num == 0:
    #         unexec_seeds.append(seed)
    print('len(unexec_seeds)', len(unexec_seeds))
    
    # can_success_num = [seed_info.can_success_num for seed_info in seeds_info.inner_dict.values()]
    seed_info_for_sort:list[tuple[str, SeedSelectInfo]] = list(seeds_info.items())
    seed_info_for_sort = _get_sorted_seed_info_for_trim(seed_info_for_sort)
    print('len(seed_info_for_sort)', len(seed_info_for_sort))
    if logger is not None:
        logger.info(f'len(seed_info_for_sort): {len(seed_info_for_sort)}')
        # logger.info(f'{[Path(seed_info[0]).stem for seed_info in seed_info_for_sort]}')
    # rule2: by cov
    info_num = len(seed_info_for_sort)
    for idx in range(info_num-1):
        assert seed_info_for_sort[idx][1].can_success_num >= seed_info_for_sort[idx+1][1].can_success_num,print(seed_info_for_sort[idx][1].can_success_num, seed_info_for_sort[idx+1][1].can_success_num) 
    to_store_idxs = []
    # ================================
    all_success_guards = set()
    # all_success_visited_guards = set()
    ths = [10, 5, 2, 0]
    for phase_num, th in enumerate(ths):
        for idx, (seed, seed_info) in enumerate(seed_info_for_sort):
            if idx in to_store_idxs:
                continue
            if not seed_info.all_can_success:
                continue
            cur_visited_guards = seed_info.unique_visited_guards
            if len(cur_visited_guards-all_success_guards) > th:
                to_store_idxs.append(idx)
                all_success_guards.update(cur_visited_guards)
        print(f'Phase {phase_num}: len(to_store_idxs)', len(to_store_idxs))
        print(f'Phase {phase_num}: len(all_success_guards)', len(all_success_guards))
        if logger is not None:
            logger.info(f'Phase {phase_num}: len(to_store_idxs) {len(to_store_idxs)}')
            logger.info(f'Phase {phase_num}: len(all_success_guards) {len(all_success_guards)}')
    # ================================
    visited_guards = all_success_guards
    # all_visited_guards = set()
    
    for phase_num, th in enumerate(ths):
        for idx, (seed, seed_info) in enumerate(seed_info_for_sort):
            if idx in to_store_idxs:
                continue
            cur_visited_guards = seed_info.unique_visited_guards
            if len(cur_visited_guards-visited_guards) > th:
                to_store_idxs.append(idx)
                visited_guards.update(cur_visited_guards)
        print(f'Phase {phase_num}: len(to_store_idxs)', len(to_store_idxs))
        print(f'Phase {phase_num}: len(all_success_guards)', len(visited_guards))
        if logger is not None:
            logger.info(f'Phase {phase_num}: len(to_store_idxs) {len(to_store_idxs)}')
            logger.info(f'Phase {phase_num}: len(all_success_guards) {len(visited_guards)}')
    # rule 3: max cov
    unique_visited_guard_nums = [seed_info[1].unique_visited_guard_num for seed_info in seed_info_for_sort]
    max_guard_num = max([seed_info[1].unique_visited_guard_num for seed_info in seed_info_for_sort])
    max_cov_idxs = [idx for idx, num in enumerate(unique_visited_guard_nums) if num == max_guard_num]
    print('len(max_cov_idxs)', len(max_cov_idxs))
    
    
    for idx in max_cov_idxs:
        if idx not in to_store_idxs:
            to_store_idxs.append(idx)
    print('len(to_store_idxs)', len(to_store_idxs))
    seeds_to_store = [seed_info_for_sort[i] for i in to_store_idxs]
    trimmed_can_success_num = [seed_info[1].can_success_num for seed_info in seeds_to_store]
    print(Counter(trimmed_can_success_num))
    _to_store_seeds = [seed_info[0] for seed_info in seeds_to_store]
    save_json('tt/seed_to_store_by_cov.json', _to_store_seeds)
    all_to_store_seeds = set(unexec_seeds)
    print('len(unexec_seeds)', len(unexec_seeds))
    all_to_store_seeds.update(_to_store_seeds)
    print('Final seed pool size', len(all_to_store_seeds))
    final_seeds = list(all_to_store_seeds)
    print('len(final_seeds)', len(final_seeds))
    if logger is not None:
        logger.info(f'len(to_store_idxs): {len(to_store_idxs)}')
        logger.info(f'len(final_seeds): {len(final_seeds)}')
        logger.info(f'Expected Final seed pool size: {len(final_seeds)}')
    for _ in final_seeds:
        assert _ in seeds
    removed_num = 0
    removed_paths = []
    for seed in seeds.copy():
        if seed not in final_seeds:
            removed_num += 1
            assert seed in seeds_info
            # assert seed in 
            seeds.remove(seed)
            seeds_info.pop(seed)
            removed_paths.append(seed)
    print('len(seeds)', len(seeds), 'len(set(seeds))', len(set(seeds)))
    print('Removed num', removed_num)
    if logger is not None:
        logger.info(f'len(seeds) {len(seeds)} len(set(seeds)) {len(set(seeds))}')
        logger.info(f'Removed num {removed_num}')
    return removed_paths


def _get_sorted_seed_info_for_trim(seed_info_for_sort:list[tuple[str, SeedSelectInfo]]):
    sorted_list = [seed_info_for_sort[0]]
    # 
    for item in seed_info_for_sort[1:]:
        for i, sorted_item in enumerate(sorted_list):
            if first_seed_is_prefered_for_trim_consider_path(item, sorted_item):
                sorted_list.insert(i, item)
                break
        else:
            sorted_list.append(item)
    return sorted_list

def first_seed_is_prefered_for_trim_consider_path(seed_with_info:tuple[str, SeedSelectInfo], seed_with_info2:tuple[str, SeedSelectInfo]):
    seed_info1 = seed_with_info[1]
    seed_info2 = seed_with_info2[1]
    seed_path1 = seed_with_info[0]
    seed_path2 = seed_with_info2[0]
    
    seed1_has_more_success_num = seed_info1.can_success_num - seed_info2.can_success_num
    if seed1_has_more_success_num != 0:
        return seed1_has_more_success_num > 0
    # print('Using rule 2')
    seed1_has_more_size = Path(seed_path1).stat().st_size - Path(seed_path2).stat().st_size
    if seed1_has_more_size != 0:
        return seed1_has_more_size < 0
    seed1_has_more_guards = seed_info1.unique_visited_guard_num - seed_info2.unique_visited_guard_num
    # ! 
    if seed1_has_more_guards != 0:
        return seed1_has_more_guards < 0
    return seed_info1.selected_num < seed_info2.selected_num
