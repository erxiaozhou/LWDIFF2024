
from typing_extensions import runtime

from .filter_normal_output_util import _oneWasmEdgeRuntimeLog_filter_normal_output
from .filter_normal_output_util import _oneWasm3RuntimeLog_filter_normal_output

from .filter_normal_output_util import _oneWAVMRuntimeLog_filter_normal_output
from .filter_normal_output_util import _oneWasmiRuntimeLog_filter_normal_output
from .filter_normal_output_util import _oneIwasmRuntimeLog_filter_normal_output
from .filter_normal_output_util import _oneWasmtimeRuntimeLog_filter_normal_output
from .filter_normal_output_util import _oneWasmerRuntimeLog_filter_normal_output
from .extract_keyword_from_content_util import ExceptionInfo, extract_keyword_from_content, get_categorize_info_fine_summary
from functools import lru_cache
import re


def get_runtime_name2class():
    runtime_name2class = {
        'wasm3_dump': oneWasm3RuntimeLog,
        'WasmEdge_disableAOT_newer': oneWasmEdgeRuntimeLog,
        'wasmi_interp': oneWasmiRuntimeLog,
        'wasmer_default_dump': oneWasmerRuntimeLog,
        'WAVM_default': oneWAVMRuntimeLog,
        'iwasm_fast_interp_dump': oneIwasmRuntimeLog,
        'iwasm_classic_interp_dump': oneIwasmRuntimeLog,
        'iwasm_fast_jit_dump': oneIwasmRuntimeLog,
        'iwasm_classic_interp_dump': oneIwasmRuntimeLog,
        'iwasm_mt_jit_dump': oneIwasmRuntimeLog,
        'iwasm_aot_dump': oneIwasmRuntimeLog,
        'iwasm_jit_dump': oneIwasmRuntimeLog,
        'wasmtime': onewasmtimeRuntimeLog
    }
    return runtime_name2class

def get_pre_normal_func(runtime_name):
    # print('VVVVV runtime_name', runtime_name)
    # assert runtime_name != 'wasmtime'
    runtime_name_pre_normal_func = {
        'wasm3_dump': _oneWasm3RuntimeLog_filter_normal_output,
        'WasmEdge_disableAOT_newer': _oneWasmEdgeRuntimeLog_filter_normal_output,
        'wasmi_interp': _oneWasmiRuntimeLog_filter_normal_output,
        'wasmer_default_dump': _oneWasmerRuntimeLog_filter_normal_output,
        'WAVM_default': _oneWAVMRuntimeLog_filter_normal_output,
        'iwasm_fast_interp_dump': _oneIwasmRuntimeLog_filter_normal_output,
        'iwasm_classic_interp_dump': _oneIwasmRuntimeLog_filter_normal_output,
        'iwasm_fast_jit_dump': _oneIwasmRuntimeLog_filter_normal_output,
        'iwasm_mt_jit_dump': _oneIwasmRuntimeLog_filter_normal_output,
        'iwasm_aot_dump': _oneIwasmRuntimeLog_filter_normal_output,
        'iwasm_jit_dump': _oneIwasmRuntimeLog_filter_normal_output,
        'wasmtime': _oneWasmtimeRuntimeLog_filter_normal_output
    }
    return runtime_name_pre_normal_func.get(runtime_name, None)


def get_one_runtime_log(s, runtime_name):
    runtime_name2class = get_runtime_name2class()
    assert runtime_name in runtime_name2class
    return runtime_name2class[runtime_name].from_raw_log_str(s, runtime_name)

def get_one_runtime_log_from_paras(para_dict):
    runtime_name2class = get_runtime_name2class()
    runtime_name = para_dict['runtime_name']
    assert runtime_name in runtime_name2class
    return runtime_name2class[runtime_name](**para_dict)


class oneRuntimeLog():
    _num_p = re.compile(r'\d{1,}')
    _num_p1 = re.compile(r'[\-\+]?<num>[ \.e]')
    _num_p2 = re.compile(r'(?:<num>)+')
    _num_p3 = re.compile(r'<num>(?:\s*[\-\+]?<num>)*')
    def __init__(self, runtime_name, filter_normal, describor=None, s=None) -> None:
        self.s = s
        self.runtime_name = runtime_name
        self.filter_normal = filter_normal
        self.keyword_part = extract_keyword_from_content(self.filter_normal)
        self.summary_key = self._init_summary_key()
        self.describor = describor

    @lru_cache(maxsize=8192, typed=False)
    def _init_summary_key(self):
        s = get_categorize_info_fine_summary(self.keyword_part)
        # print('#@$@!%$#%@#$%$================================', self.runtime_name)
        # print(s)
        if isinstance(s, str):
            s = re.sub(oneRuntimeLog._num_p, '<num>', s)
            s = re.sub(oneRuntimeLog._num_p1, '<num>', s)
            s = re.sub('type code: <num>', '<num>', s)
            s = re.sub(oneRuntimeLog._num_p2, '<num>', s)
            s = re.sub(oneRuntimeLog._num_p3, '<num>', s)
            if s == '<num>':
                s = ''
            # print('s is str', s)
        # else:
        #     print('s is not str', s)
        # if 
        return s

    def __str__(self) -> str:
        return str(self.describor)

    def is_empty(self):
        return self.describor == ''

    def as_paras_str(self):
        return repr({
            'runtime_name': self.runtime_name,
            'filter_normal': self.filter_normal,
            'describor': self.describor
        })

    @classmethod
    def from_paras_str(cls, s):
        paras = eval(s)
        return cls(**paras)

    @classmethod
    def from_raw_log_str(cls, s, runtime_name, describor=None):
        pre_norla_func = get_pre_normal_func(runtime_name)
        if pre_norla_func is None:
            pre_norla_func = lambda x: x
        filter_normal = pre_norla_func(s)
        filter_normal = re.sub('\n', ' ', filter_normal)
        filter_normal = filter_normal.strip('\'"\n\\ ')
        # print('------------------------------------------- ', runtime_name)
        # print(describor)
        return cls(s=s, runtime_name=runtime_name, filter_normal=filter_normal, describor=describor)

    @property
    def is_size_missmatch(self):
        if isinstance(self.summary_key, ExceptionInfo):
            return self.summary_key.is_size_missmatch()
        return False

    def __hash__(self) -> int:
        return hash(self.filter_normal)

    def __eq__(self, o) -> bool:
        return isinstance(o, oneRuntimeLog) and self.filter_normal == o.filter_normal

    @property
    def fd_or_SIMD_related(self):
        return self.summary_key in [ExceptionInfo.FDOpcode, ExceptionInfo.SIMDUnsupport]

    @property
    def is_illegal_type(self):
        return self.summary_key in [ExceptionInfo.IllegalLocalType, ExceptionInfo.IllegalType]

    @property
    def ref_unsupport(self):
        return self.summary_key == ExceptionInfo.ReferenceUnsupport

    @property
    def self_unsupport(self):
        return self.summary_key in [ExceptionInfo.ReferenceUnsupport,
                                    ExceptionInfo.MultiMemUnsupport,
                                    ExceptionInfo.TooManyLocal,
                                    ExceptionInfo.StackOperandOverflow,
                                    ExceptionInfo.SIMDUnsupport]


class oneManualRuntimeLog(oneRuntimeLog):
    def __init__(self, comment, runtime_name) -> None:
        self.runtime_name = runtime_name
        if not isinstance(comment, str):
            print('the length of input is greater than 1 in oneManualRuntimeLog', comment, type(comment))
            comment = str(comment)
        # assert isinstance(comment, str), print(comment, type(comment))

        self.s = comment
        self.keyword_part = comment
        self.summary_key = comment
        self.describor = comment
        self.filter_normal = comment



class oneWasmerRuntimeLog(oneRuntimeLog): pass
class oneIwasmRuntimeLog(oneRuntimeLog): pass
class oneWasmiRuntimeLog(oneRuntimeLog): pass
class oneWAVMRuntimeLog(oneRuntimeLog): pass
class oneWasmEdgeRuntimeLog(oneRuntimeLog): pass
class oneWasm3RuntimeLog(oneRuntimeLog): pass
class onewasmtimeRuntimeLog(oneRuntimeLog): pass
