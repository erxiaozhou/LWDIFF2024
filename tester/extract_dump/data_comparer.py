from functools import lru_cache
from file_util import read_json, save_json
from get_impls_util.impl_features_para import registered_runtime_names, support_score
from .dump_data_util import dumpData, get_diff_attr_names, no_exec_state_attrs
from typing import Dict, List, Optional
from util import execStatus
from enum import Enum


class DiffStrategy(Enum):
    ALL = 1
    ExecStatus = 2
    Variable = 3


class diffResult:
    def __init__(self, no_diff, status_diff=None, variable_diff=None, canrun_cannot_init=None) -> None:
        self.no_diff: bool = no_diff
        self.status_diff: Optional[Dict[str, str]] = status_diff
        self.variable_diff: Optional[Dict[str, List[str]]] = variable_diff
        if canrun_cannot_init is None:
            canrun_cannot_init = []
        self.canrun_cannot_init = canrun_cannot_init

    def _repr_str(self):
        return f'diffResult(no_diff={self.no_diff}, status_diff={self.status_diff}, variable_diff={self.variable_diff}, canrun_cannot_init={self.canrun_cannot_init})'

    def __eq__(self, __value: object) -> bool:
        assert isinstance(__value, diffResult)
        return self.no_diff == __value.no_diff and self.status_diff == __value.status_diff and self.variable_diff == __value.variable_diff

    # ! 
    def as_unique_key(self, diff_strategy: DiffStrategy) -> str:
        no_diff_part = f'no_diff={self.no_diff}'
        ordered_status_diff = None
        ordered_variable_diff = None

        if diff_strategy in [DiffStrategy.ALL, DiffStrategy.ExecStatus]:
            if self.status_diff is None:
                ordered_status_diff = 'None'
            else:
                ordered_status_diff = _as_ordered_dict_str(
                    registered_runtime_names, self.status_diff)
        if diff_strategy in [DiffStrategy.ALL, DiffStrategy.Variable]:
            if self.variable_diff is None:
                ordered_status_diff = 'variable_diff=None'
            else:
                ordered_variable_diff = _as_ordered_dict_str(
                    registered_runtime_names, self.variable_diff)
        if diff_strategy == DiffStrategy.ExecStatus:
            key = f'{no_diff_part}, status_diff={ordered_status_diff}'
        elif diff_strategy == DiffStrategy.Variable:
            key = f'{no_diff_part}, variable_diff={ordered_variable_diff}'
        elif diff_strategy == DiffStrategy.ALL:
            key = f'{no_diff_part}, status_diff={ordered_status_diff}, variable_diff={ordered_variable_diff}'
        else:
            raise Exception(f'Unknown diff_strategy: {diff_strategy}')
        return key

    def __repr__(self) -> str:
        return self._repr_str()

    def __hash__(self) -> int:
        # ，dict
        return hash(self._repr_str())

    def save_as_json(self, path):
        # save_json(path, self.to_dict)
        d = {}
        d['no_diff'] = self.no_diff
        d['status_diff'] = self.status_diff
        d['variable_diff'] = self.variable_diff
        d['canrun_cannot_init'] = self.canrun_cannot_init
        save_json(path, d)

    @property
    def canrun_cannot_dump(self):
        return len(self.canrun_cannot_init) > 0

    @classmethod
    def from_json(cls, path):
        # print(path)
        try:
            d = read_json(path)
        except Exception as e:
            print(f'Error when reading {path}')
            raise e
        return cls(**d)


def _as_ordered_dict_str(runtime_names, dict_: Dict):
    item_strs = []
    for existing_name in dict_.keys():
        assert existing_name in runtime_names
    for runtime_name in runtime_names:
        if runtime_name not in dict_:
            continue
        item_strs.append(f"{repr(runtime_name)}: {repr(dict_[runtime_name])}")
    return '{' + ', '.join(item_strs) + '}'


def are_different(dumped_results: List[dumpData]) -> diffResult:
    # ，difference
    # ， simd / reference / multi memoryruntime，difference ()
    # run，dump，，
    # Timeout

    # all runtimes fail to run
    dumped_results = _sort_results_by_support_score(dumped_results)
    names = tuple(r.name for r in dumped_results)
    exec_statuss: list[execStatus] = []
    for r in dumped_results:
        assert r.cli_result is not None
        exec_status = r.cli_result.exec_status
        exec_statuss.append(exec_status)
    #
    # initialize canrun_cannot_init
    canrun_cannot_init = []
    for exec_status, dump_result in zip(exec_statuss, dumped_results):
        if exec_status.is_success and (not dump_result.can_initialize):
            canrun_cannot_init.append(dump_result.name)

    if all(r in [execStatus.Timeout, execStatus.Exception] for r in exec_statuss):
        # no_diff = (len(canrun_cannot_init) == 0)
        assert len(canrun_cannot_init) == 0
        return diffResult(no_diff=True)
    # Then, compare. First, we select a base runtime
    base_index = -1
    for i, exec_status in enumerate(exec_statuss):
        if exec_status.is_success:
            base_index = i
            break
    if base_index == -1:
        # meaning that there is no need to compare the variables
        status_diff = {}
        for name, exec_status in zip(names, exec_statuss):
            assert not exec_status.is_success
            if exec_status == execStatus.Timeout or exec_status == execStatus.Crash:
                status_diff[name] = exec_status.name
        assert len(status_diff)
        return diffResult(no_diff=False, status_diff=status_diff, canrun_cannot_init=canrun_cannot_init)
    else:
        other_indexs = [i for i in range(len(exec_statuss)) if i != base_index]
        base_dump_result = dumped_results[base_index]
        assert exec_statuss[base_index].is_success
        status_diff = {}
        variable_diff = {}
        for index in other_indexs:
            cur_dump_result = dumped_results[index]
            cur_exec_status = exec_statuss[index]
            if not cur_exec_status.is_success:
                # assert 0, print(cur_dump_result.name)
                status_diff[cur_dump_result.name] = cur_exec_status.name
            else:
                cur_different_attrs = get_diff_attr_names(
                    base_dump_result, cur_dump_result, no_exec_state_attrs)
                if len(cur_different_attrs):
                    variable_diff[cur_dump_result.name] = cur_different_attrs
                    if base_dump_result.name not in variable_diff:
                        variable_diff[base_dump_result.name] = []
                    for _ in cur_different_attrs:
                        variable_diff[base_dump_result.name].append(_)
        if len(status_diff) == 0 and len(variable_diff) == 0:
            assert all(s == execStatus.Success for s in exec_statuss), print(
                exec_statuss)
            return diffResult(no_diff=True)
        if len(status_diff) == 0:
            status_diff = None
        if len(variable_diff) == 0:
            variable_diff = None
        return diffResult(no_diff=False, status_diff=status_diff, variable_diff=variable_diff, canrun_cannot_init=canrun_cannot_init)


def _sort_results_by_support_score(results):
    # sort runtimes according to the result of support_score, from high to low
    # runtimes = sorted(results, key=lambda x: support_score(x.name), reverse=True)
    names = tuple(r.name for r in results)
    assert names_are_unique(names)
    index_list = _get_index_list(names)
    results = [results[i] for i in index_list]
    return results


@lru_cache(maxsize=8192, typed=False)
def names_are_unique(names):
    return len(names) == len(set(names))


@lru_cache(maxsize=8192, typed=False)
def _get_index_list(names):
    sorted_names = sorted(names, key=lambda x: support_score(x), reverse=True)
    index_list = [names.index(n) for n in sorted_names]
    return index_list
