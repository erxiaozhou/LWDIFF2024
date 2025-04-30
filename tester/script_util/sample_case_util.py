from pathlib import Path
import random
from debug_util.debug_util import validate_wasm


def sample_500_cases_from_case_dir(case_num=500, case_dir='/media/hdd8T1/testing_time3/seed_v3_halfdump_V3_MAB_90000s_SOPS_less_wrap4/test_std_new_tcs'):
    case_dir = Path(case_dir)
    ps = list(case_dir.iterdir())
    selected_case_num = 0
    sample_paths = []
    while selected_case_num < case_num:
        p_idx = random.randint(0, len(ps)-1)
        p = ps[p_idx]
        ps.pop(p_idx)
        if validate_wasm(p):
            selected_case_num += 1
            sample_paths.append(p)
    return sample_paths
