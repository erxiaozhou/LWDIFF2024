from collections import Counter
from functools import lru_cache
from pathlib import Path
import re
from .extract_keyword_from_content_util import func_sec_size_mismatch
from .extract_keyword_from_content_util import runtime_self_unsupport
from get_impls_util.impl_features_para import support_ref, support_v128
from .load_log_from_one_tc_result_util import load_log_from_one_tc_result
from .load_log_from_one_tc_result_util import load_log_from_dumped_results
from .log_dict2key_util import log_dict2key
from .one_runtime_log_util import get_one_runtime_log_from_paras, oneManualRuntimeLog, oneRuntimeLog
from .one_runtime_log_util import get_one_runtime_log
from extract_dump.data_comparer import diffResult
from file_util import get_logger

logger = get_logger(__name__, f'/tmp/{__name__}.log')

def _get_statu_dict_from_key_repr(key_repr):
    diff_reason = eval(f'diffResult({key_repr})')
    status = diff_reason.status_diff
    if status is None:
        status = {}
    return status

supported_strategies = ['all', 's3', 'only_interesting', 'only_highlight']


def group_tc_names_by_log_key(tc_result_dirs, strategy, reason_key_repr: str):
    assert reason_key_repr is not None
    # print('*********** reason_key_repr', reason_key_repr)
    statu_diff = _get_statu_dict_from_key_repr(reason_key_repr)
    # print('*********** statu_diff', statu_diff, type(statu_diff.get('iwasm_aot_dump')))
    runtime_logs2tc_names = {}
    for tc_result_dir in tc_result_dirs:
        tc_name = Path(tc_result_dir).name
        try:
            runtime_logs: runtimeLogs = get_runtime_logs_from_dir(tc_result_dir, strategy)
        except Exception as e:
            # raise e
            # print(f'Error in {tc_result_dir}')
            logger.debug(f'Error in {tc_result_dir}')
            continue
            
        runtime_logs2tc_names.setdefault(runtime_logs, []).append(tc_name)
    # print('vbfdvnjfd====', [len(v) for v in runtime_logs2tc_names.values()])
    if strategy == 'only_highlight':
        tmp_log_key2tc_names = rewrite_dict(runtime_logs2tc_names)
        log_key2tc_names = {}
        for logs_key, tc_names in tmp_log_key2tc_names.items():
            logs_key.update_processed_log_dict(statu_diff)
            log_key2tc_names[logs_key.processed_key] = tc_names
    else:
        log_key2tc_names = {}
        for runtime_logs, tc_names in runtime_logs2tc_names.items():
            runtime_logs.update_processed_log_dict(statu_diff)
            logs_key = repr(runtime_logs)
            log_key2tc_names.setdefault(logs_key, []).extend(tc_names)
    # print('vb*******************====', [len(v) for v in log_key2tc_names.values()])
    return log_key2tc_names


def get_runtime_logs_from_dir(tc_result_dir, strategy):
    strategy2class = {
        'all': rawRuntimeLogs,
        's3': s3RuntimeLogs,
        'only_interesting': onlyInterestingRuntimeLogs,
        'only_highlight': onlyHighlightRuntimeLogs
    }
    assert strategy in strategy2class
    return strategy2class[strategy].from_tc_result_dir(tc_result_dir)


class runtimeLogs:
    def __init__(self, log_dict: dict[str, str]) -> None:
        log_dict = {runtime_name: get_one_runtime_log(log, runtime_name) for runtime_name, log in log_dict.items()}
        self.log_dict = self._process_log_dict(log_dict)

    def _process_log_dict(self, log_dict):
        raise NotImplementedError

    def update_processed_log_dict(self, new_processed_log_dict):
        to_update_dict = new_processed_log_dict.copy()
        for runtime_name, log in to_update_dict.items():
            if runtime_name not in self.log_dict:
                self.log_dict[runtime_name] = oneManualRuntimeLog(log, runtime_name)

    def __repr__(self) -> str:
        return log_dict2key(self.log_dict)

    def __hash__(self) -> int:
        return hash(repr(self.log_dict))

    def __eq__(self, o) -> bool:
        return self.log_dict == o.log_dict

    def all_empty(self):
        return all([log.is_empty() for log in self.log_dict.values()])

    def as_str_dict(self):
        return {k: str(v) for k, v in self.log_dict.items()}

    # def all_not_empty(self):
    #     return all([not log.is_empty() for log in self.log_dict.values()])

    @classmethod
    def from_tc_result_dir(cls, tc_result_dir):
        return cls(load_log_from_one_tc_result(tc_result_dir))

    @classmethod
    def from_dumped_results(cls, dumped_results):
        return cls(load_log_from_dumped_results(dumped_results))


class rawRuntimeLogs(runtimeLogs):
    def _process_log_dict(self, log_dict):
        paras_str_dict = {runtime_name: log.as_paras_str() for runtime_name, log in log_dict.items()}
        para_str_dict_repr = repr(paras_str_dict)
        return _process_raw_log_dict_repr(para_str_dict_repr)

_num_p = re.compile(r'\d+')
@lru_cache(maxsize=4096*4, typed=False)
def _process_raw_log_dict_repr(para_str_dict_repr):
    paras_str_dict = eval(para_str_dict_repr)
    log_dict = {runtime_name: get_one_runtime_log_from_paras(eval(paras_str)) for runtime_name, paras_str in paras_str_dict.items()}
    for k in log_dict.keys():
        assert isinstance(log_dict[k], oneRuntimeLog)
        log_dict[k].describor = log_dict[k].summary_key
    return log_dict


class s3RuntimeLogs(runtimeLogs):
    def _process_log_dict(self, log_dict):
        paras_str_dict = {runtime_name: log.as_paras_str() for runtime_name, log in log_dict.items()}
        para_str_dict_repr = repr(paras_str_dict)
        return _process_s3_log_dict_repr(para_str_dict_repr)

@lru_cache(maxsize=4096*4, typed=False)
def _process_s3_log_dict_repr(para_str_dict_repr):
    paras_str_dict = eval(para_str_dict_repr)
    log_dict = {runtime_name: get_one_runtime_log_from_paras(eval(paras_str)) for runtime_name, paras_str in paras_str_dict.items()}
    for k in log_dict.keys():
        assert isinstance(log_dict[k], oneRuntimeLog)
        log_dict[k].describor = log_dict[k].summary_key
    return log_dict


class onlyInterestingRuntimeLogs(runtimeLogs):
    def _process_log_dict(self, log_dict):
        paras_str_dict = {runtime_name: log.as_paras_str() for runtime_name, log in log_dict.items()}
        para_str_dict_repr = repr(paras_str_dict)
        return _process_interesting_log_dict_repr(para_str_dict_repr)

@lru_cache(maxsize=4096*4, typed=False)
def _process_interesting_log_dict_repr(para_str_dict_repr):
    paras_str_dict = eval(para_str_dict_repr)
    log_dict = {runtime_name: get_one_runtime_log_from_paras(eval(paras_str)) for runtime_name, paras_str in paras_str_dict.items()}
    # 
    for k in log_dict.keys():
        assert isinstance(log_dict[k], oneRuntimeLog)
        log_dict[k].describor = log_dict[k].summary_key
    # 
    log_objs = list(log_dict.values())
    size_mismatch_logs_num = len(
        [1 for log_obj in log_objs if log_obj.is_size_missmatch])
    if 0 < size_mismatch_logs_num < len(log_objs):
        for runtime_name in log_dict.keys():
            log_dict[runtime_name].describor = func_sec_size_mismatch
    # ====================================

    # logruntime
    runtime_names = list(log_dict.keys())
    # fd =======================================================
    has_fd = _has_fd(log_dict)
    if has_fd:
        for log in log_dict.values():
            if log.is_illegal_type:
                log.describor = runtime_self_unsupport
        for runtime_name, log in log_dict.items():
            if not support_v128(runtime_name):
                log.describor = runtime_self_unsupport
    # ref =======================================================
    # reference
    has_ref = _has_ref(log_dict)
    if has_ref:
        for log in log_dict.values():
            if log.is_illegal_type:
                log.describor = runtime_self_unsupport
        for runtime_name, log in log_dict.items():
            if not support_ref(runtime_name):
                log.describor = runtime_self_unsupport
    # some features are not supported by some runtimes, which is as expected
    for runtime_name in runtime_names:
        if log_dict[runtime_name].describor == runtime_self_unsupport:
            log_dict.pop(runtime_name)
        elif log_dict[runtime_name].self_unsupport:
            log_dict.pop(runtime_name)
    return log_dict


def _has_ref(log_dict):
    has_ref = False
    for log in log_dict.values():
        if log.ref_unsupport:
            has_ref = True
            break
    return has_ref


def _has_fd(log_dict):
    # rule1: fd_opcode
    # rule2: SIMD_unsupport
    has_fd = False
    for v in log_dict.values():
        if v.fd_or_SIMD_related:
            has_fd = True
            break
    # rule3: special runtimes
    if not has_fd:
        for runtime_name, log in log_dict.items():
            if not support_v128(runtime_name):
                if log_dict.get(runtime_name).fd_or_SIMD_related:
                    has_fd = True
                    break
    return has_fd


class onlyHighlightRuntimeLogs(onlyInterestingRuntimeLogs):
    pass


def rewrite_dict(log_key2tc_names):
    # ! disabled now
    assert 0
    log_key2log_key_freq = {}

    log_kwds = set()
    for log_key in log_key2tc_names.keys():
        cur_log_kwds = list(eval(log_key.log_dict).values())
        log_kwds.update(cur_log_kwds)
        log_key2log_key_freq[log_key] = {
            kwd: v/len(cur_log_kwds) for kwd, v in Counter(cur_log_kwds).items()}

    to_save_log_keys = set()
    if '{}' in log_key2log_key_freq:
        to_save_log_keys.add('{}')
    for kwd in log_kwds:
        max_v = -1
        for log_key, c in log_key2log_key_freq.items():
            if c.get(kwd, -5) >= max_v:
                max_v = c[kwd]
        # if max_v < 0.5:
        #     continue
        for log_key, c in log_key2log_key_freq.items():
            if c.get(kwd, -5) == max_v:
                to_save_log_keys.add(log_key)
    log_key2tc_names = {k: log_key2tc_names[k] for k in to_save_log_keys}
    return log_key2tc_names
