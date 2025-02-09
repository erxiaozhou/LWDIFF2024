import re
from functools import lru_cache

# hex_p = r'0[xX][0-9a-fA-F]+'
# num_p = r'^[\-\+]?(?:(?:\d+)|(?:[\.\+\d]+e[\-\+]?\d+)|(?:\d+\.\d+)|(?:nan)|(?:inf))\n?$'
# wasm_path_p = r' [^ ]+\.wasm'
# offset_p = r'\(at offset (?:(?:\d+)|(?:0[xX][0-9a-fA-F]+))\)'
# time_p = r'\[[\-0-9]+ [\.:0-9]+\]'

hex_p = re.compile(r'0[xX][0-9a-fA-F]+')
num_p = re.compile(r'^[\-\+]?(?:(?:\d+)|(?:[\.\+\d]+e[\-\+]?\d+)|(?:\d+\.\d+)|(?:nan)|(?:inf))\n?$')
wasm_path_p = re.compile(r' [^ ]+\.wasm')
offset_p = re.compile(r'\(at offset (?:(?:\d+)|(?:0[xX][0-9a-fA-F]+))\)')
time_p = re.compile(r'\[[\-0-9]+ [\.:0-9]+\]')
nan_p = re.compile(r'[\-\+]?nan')
inf_p = re.compile(r'[\-\+]?inf')
@lru_cache(maxsize=8192, typed=False)
def _oneWasmerRuntimeLog_filter_normal_output(s):
    s = re.sub(offset_p, '', s)
    s = re.sub(wasm_path_p, '', s)
    return s


wamr_p1 = re.compile(r'^\n*$')
wamr_p2 = re.compile(r'Create AoT compiler with.*target triple.*was generated.\s*', flags=re.S)
wamr_p3 = re.compile(r'^0x[a-f\d]+:i(?:(?:64)|(?:32))$')
wamr_p4 = re.compile(r'^.*:f(?:(?:64)|(?:32))$')
wamr_pf = re.compile(r'(?:<float>)|(?:<int>)|(?:<ExternNull>)|(?:<FuncrefNull>)|(?:<v128>)|,')
# @lru_cache(maxsize=8192, typed=False)
def _oneIwasmRuntimeLog_filter_normal_output(s):
    # print('XXXX ==>', s)
    s = re.sub(wamr_p1, '', s)
    s = re.sub(wamr_p2, '', s)
    s = re.sub(wamr_p3, '', s)
    s = re.sub(wamr_p4, '', s)
    p = r'\d:ref\.func'
    s = re.sub(p, '', s)
    p = r'^(?:(?:func)|(?:extern)):ref\.null$'
    s = re.sub(p, '', s)
    p = r'^<0x[a-f0-9]{16} 0x[a-f0-9]{16}>:v128$'
    s = re.sub(p, '', s)
    # token
    p = r'<0x[a-f0-9]{16} 0x[a-f0-9]{16}>:v128'
    s = re.sub(p, '<v128>', s)
    p = r'0x[a-f\d]+:i(?:(?:64)|(?:32))'
    s = re.sub(p, '<int>', s)
    p = r'extern:ref.null'
    s = re.sub(p, '<ExternNull>', s)
    p = r'func:ref.null'
    s = re.sub(p, '<FuncrefNull>', s)
    p = r'[\+\-]?\d+\.\d+e[\+\-]?\d*:f(?:(?:64)|(?:32))'
    s = re.sub(p, '<float>', s)
    p = r'[\+\-]?\d*:f(?:(?:64)|(?:32))'
    s = re.sub(p, '<float>', s)
    s = re.sub(nan_p, '', s)
    s = re.sub(inf_p, '', s)
    s = re.sub(wamr_pf, '', s)
    # p = r'\d*:f(?:(?:64)|(?:32))'
    # s = re.sub(p, '<float>', s)
    # print('YYYY ==>', s)
    return s


@lru_cache(maxsize=8192, typed=False)
def _oneWasmiRuntimeLog_filter_normal_output(s):
    s = re.sub(offset_p, '', s)
    s = re.sub(wasm_path_p, '', s)
    return s


def _get_wasmtime_warning_p():
    raw_s = r'''warning: this CLI invocation of Wasmtime will be parsed differently in future
         Wasmtime versions -- see this online issue for more information:
         https://github.com/bytecodealliance/wasmtime/issues/7384

         Wasmtime will now execute with the old (<= Wasmtime 13) CLI parsing,
         however this behavior can also be temporarily configured with an
         environment variable:

         - WASMTIME_NEW_CLI=0 to indicate old semantics are desired and silence this warning, or
         - WASMTIME_NEW_CLI=1 to indicate new semantics are desired and use the latest behavior'''
    # raw_s = raw_s.replace('<num>', r'\d+')
    # raw_s = raw_s.replace(r'[ \n]+', '[ \n]+')
    # return re.compile(raw_s, re.S)
    return re.compile(re.escape(raw_s))
    

wasmtime_warning_p = _get_wasmtime_warning_p()

@lru_cache(maxsize=8192, typed=False)
def _oneWasmtimeRuntimeLog_filter_normal_output(s):
    # assert 0
    # print(f'raws||{s}||')
    s = re.sub(wasmtime_warning_p, '', s)
    return s




@lru_cache(maxsize=8192, typed=False)
def _oneWAVMRuntimeLog_filter_normal_output(s):
    return s

wasmedge_p1 = re.compile(r'Bytecode offset: 0[xX][0-9a-fA-F]+')
wasmedge_p2 = re.compile(r' Code: 0[xX][0-9a-fA-F]+')
@lru_cache(maxsize=8192, typed=False)
def _oneWasmEdgeRuntimeLog_filter_normal_output(s):
    # print('Wasmedge', s)
    s = re.sub(time_p, '', s)
    s = re.sub(wasm_path_p, '', s)
    s = re.sub(wasmedge_p1, '', s)
    s = re.sub(wasmedge_p2, '', s)
    s = re.sub(nan_p, '', s)
    s = re.sub(num_p, '', s)
    s = re.sub(inf_p, '', s)
    return s


@lru_cache(maxsize=8192, typed=False)
def _oneWasm3RuntimeLog_filter_normal_output(s):
    p = r' *Result: *\-?[0-9\.]+$'
    s = re.sub(p, '', s)
    p = r' *Result: *\-?0[xX][0-9a-fA-F]+$'
    s = re.sub(p, '', s)
    p = r' *Result: *\-?(?:(?:nan)|(?:inf))'
    s = re.sub(p, '', s)
    if 'Empty Stack' in s:
        s = ''
    return s
