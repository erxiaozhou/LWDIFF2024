from math import inf
from pathlib import Path
import subprocess
from typing import Set, Union
from file_util import default_exec_cmd_without_return
from .process_dump_data_util import get_int, get_u16
from .process_dump_data_util import get_u64
from collections import Counter
from config import EXEC_TIMEOUT
# /home/anonymous/CP912/iwasm_pg/wamr_cov/jit_coverage


coverage_paras = {
    'cmd': '/home/anonymous/CP912/iwasm_pg/wamr_cov_v1/install_jit/bin/iwasm --heap-size=0 --llvm-jit -f {func_name} {case_path}',
    'dumped_coverage_path': './jit_coverage'
}

def exec_to_dump_coverage(case_path, func_name='to_test'):
    default_exec_cmd_without_return(f'rm {coverage_paras["dumped_coverage_path"]}')
    cmd = coverage_paras['cmd'].format(func_name=func_name, case_path=case_path)
    try:
        default_exec_cmd_without_return(cmd, timeout=EXEC_TIMEOUT)
    except subprocess.TimeoutExpired as e:
        print(f'Timeout when exec the coommand {cmd} to dump coverage!')
    return True

def get_coverage_from_default_path():
    coverage = oneExecCoverage.from_v1_path(coverage_paras['dumped_coverage_path'])
    
    return coverage

def collect_a_cov(p, func_name='to_test'):
    exec_to_dump_coverage(p, func_name=func_name)
    cov = get_coverage_from_default_path()
    return cov

class oneExecCoverage:
    def __init__(self, unique_visited_guard_num, total_visited_guard_num, unique_visited_guard_list, guard_hit_num_list, total_guard_num, name=None):
        self.unique_visited_guard_num = unique_visited_guard_num
        self.total_visited_guard_num = total_visited_guard_num
        self.total_guard_num = total_guard_num
        self.guard_hit_num_list = guard_hit_num_list
        self.name = name
        # self.hit_num_dict = {idx: hit for idx, hit in zip(
        #     unique_visited_guard_list, guard_hit_num_list)}
        # self.hit_num_dict = Counter(self.hit_num_dict)
        self.unique_visited_guards = set(unique_visited_guard_list)
        if self.total_visited_guard_num > 0:
            self.cov_rate = self.unique_visited_guard_num / self.total_visited_guard_num
        else:
            self.cov_rate = 0
    @property
    def meaningless(self):
        return self.total_visited_guard_num == self.unique_visited_guard_num == 0
            
    def copy(self):
        return oneExecCoverage(self.unique_visited_guard_num, self.total_visited_guard_num, self.unique_visited_guards, self.guard_hit_num_list, self.total_guard_num, name=self.name)
    
    @classmethod
    def from_v1_path(cls, path: Union[Path, str]):
        # unique_visited_guard_num: [8 byte]: number of unique guards
        # unique_visited_guard_list: [8 byte * unique_visited_guard_num]: list of unique guards
        # guard_hit_num_list: [2 byte * unique_visited_guard_num]: list of hit number of unique guards
        path = Path(path)
        if path.exists():
            bas = path.read_bytes()
            total_guard_num = get_int(bas[:8])
            assert get_u64(bas[:8]) == total_guard_num
            total_visited_guard_num = get_int(bas[16:24])
            assert get_u64(bas[16:24]) == total_visited_guard_num
            unique_visited_guard_num = get_int(bas[8:16])
            assert get_u64(bas[8:16]) == unique_visited_guard_num
            bas = bas[24:]
            assert len(bas) == unique_visited_guard_num * (8 + 2), \
                (len(bas), unique_visited_guard_num)
            offset = 0
            unique_visited_guard_list = []
            for i in range(unique_visited_guard_num):
                unique_visited_guard_list.append(get_int(bas[offset:offset+8]))
                offset += 8
            # guard_hit_num_list = []
            # for i in range(unique_visited_guard_num):
            #     guard_hit_num_list.append(get_int(bas[offset:offset+2]))
            #     assert get_u16(bas[offset:offset+2]) == guard_hit_num_list[-1]
            #     offset += 2
            assert len(unique_visited_guard_list) == unique_visited_guard_num
        else:
            total_guard_num = 0
            total_visited_guard_num = 0
            unique_visited_guard_num = 0
            unique_visited_guard_list = []
        return oneExecCoverage(unique_visited_guard_num, total_visited_guard_num, unique_visited_guard_list, [], total_guard_num=total_guard_num)

    @classmethod
    def from_ori_path_full(cls, path: Union[Path, str]):
        # unique_visited_guard_num: [8 byte]: number of unique guards
        # unique_visited_guard_list: [8 byte * unique_visited_guard_num]: list of unique guards
        # guard_hit_num_list: [2 byte * unique_visited_guard_num]: list of hit number of unique guards
        bas = Path(path).read_bytes()
        # print('len(bas)', len(bas))
        total_guard_num = get_int(bas[:8])
        assert get_u64(bas[:8]) == total_guard_num
        total_visited_guard_num = get_int(bas[16:24])
        assert get_u64(bas[16:24]) == total_visited_guard_num
        unique_visited_guard_num = get_int(bas[8:16])
        assert get_u64(bas[8:16]) == unique_visited_guard_num
        bas = bas[24:]
        assert len(bas) == unique_visited_guard_num * (8 + 2), \
            (len(bas), unique_visited_guard_num)
        offset = 0
        unique_visited_guard_list = []
        for i in range(unique_visited_guard_num):
            unique_visited_guard_list.append(get_int(bas[offset:offset+8]))
            offset += 8
        guard_hit_num_list = []
        for i in range(unique_visited_guard_num):
            guard_hit_num_list.append(get_int(bas[offset:offset+2]))
            assert get_u16(bas[offset:offset+2]) == guard_hit_num_list[-1]
            offset += 2
        assert len(unique_visited_guard_list) == unique_visited_guard_num
        return oneExecCoverage(unique_visited_guard_num, total_visited_guard_num, unique_visited_guard_list, guard_hit_num_list, total_guard_num=total_guard_num)

#  case，，，（，），
# 38069 39392 39396 39392 39394 39389 38196 39396 39395 39392



class CoverageAll:
    def __init__(self) -> None:
        self.total_guard_num = None
        self.guard_visit_couner = Counter()
        self.visited_guards = set()
        # some status info
        self.update_times = 0
        self.cur_avg_unique_visited_guard_num = 0
        self.min_unique_visited_guard_num = inf
        self.common_guards = set()

    def update_common_guards(self):
        if len(self.visited_guards) == 0:
            return
        guards_and_freqs = self.guard_visit_couner.most_common()
        guards = [x[0] for x in guards_and_freqs]
        # guards = guards[:len(guards) * 3//4]
        guards = guards[:int(len(guards) * 0.9)]
        self.common_guards = set(guards)


    @property
    def cov_rate(self):
        assert self.total_guard_num is not None
        return len(self.visited_guards) / self.total_guard_num

    def update_coverage_info(self, coverage: oneExecCoverage):
        if coverage.meaningless:
            return
        if coverage.total_guard_num is not None:
            if self.total_guard_num is None:
                self.total_guard_num = coverage.total_guard_num
            else:
                assert self.total_guard_num == coverage.total_guard_num
        self.guard_visit_couner.update(coverage.unique_visited_guards)
        self.visited_guards.update(coverage.unique_visited_guards)
        # new status info
        self.update_times += 1
        self.cur_avg_unique_visited_guard_num = (self.cur_avg_unique_visited_guard_num * (self.update_times - 1) + coverage.unique_visited_guard_num) / self.update_times
        # the mini case
        if self.min_unique_visited_guard_num > coverage.unique_visited_guard_num:
            self.min_unique_visited_guard_num = coverage.unique_visited_guard_num

    def update_by_unique_visited_guards(self, unique_visited_guards:Set):
        self.guard_visit_couner.update(unique_visited_guards)
        self.visited_guards.update(unique_visited_guards)

        

    @property
    def total_visited_guard_num(self):
        return len(self.visited_guards)

def trigger_new_guards(one_exec_cov:oneExecCoverage, summary_cov:CoverageAll) -> int:
    new_guards = one_exec_cov.unique_visited_guards - summary_cov.visited_guards
    return len(new_guards)
    
