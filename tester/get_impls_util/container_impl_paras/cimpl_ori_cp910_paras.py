


cimpl_ori_cp910_paras = {
    'wasmer_default_dump':{
        'bin_cmd': 'docker exec ori_wasmer_cp910_debug /root/.cargo/bin/wasmer',
        'std_cmd': '{}  {} -i to_test',
        'container_name': 'ori_wasmer_cp910_debug',
        # 'std_cmd': '{} run {}  --enable-all -e to_test',
        'err_channel': 'stderr',
    },
    'wasmi_interp': {
        'bin_cmd': 'docker exec ori_wasmi_cp910_debug /usr/local/cargo/bin/wasmi_cli',
        'std_cmd': '{} {}  to_test',
        'container_name': 'ori_wasmi_cp910_debug',
        'err_channel': 'stderr',
    },
    'iwasm_classic_interp_dump':{
        'bin_cmd': 'docker exec ori_iwasm_classic_cp910_debug /usr/local/bin/iwasm',
        'std_cmd': '{} --heap-size=0 -f to_test {}',
        'container_name': 'ori_iwasm_classic_cp910_debug',
        'err_channel': 'stdout',
    },
    'iwasm_fast_interp_dump':{
        'bin_cmd': 'docker exec ori_iwasm_fast_cp910_debug /usr/local/bin/iwasm',
        'std_cmd': '{} --heap-size=0 -f to_test {}',
        'container_name': 'ori_iwasm_fast_cp910_debug',
        'err_channel': 'stdout',
    },
    'wasm3_dump':{
        'bin_cmd': 'docker exec ori_wasm3_cp910_debug /usr/local/bin/wasm3',
        'std_cmd': '{} --func to_test {}',
        'container_name': 'ori_wasm3_cp910_debug',
        'err_channel': 'stderr',
    },
    'WasmEdge_disableAOT_newer':{
        'bin_cmd': 'docker exec ori_wasmedge_disableaot_debug /usr/local/bin/wasmedge',
        'std_cmd': '{} --reactor {} to_test',
        'container_name': 'ori_wasmedge_disableaot_debug',
        'err_channel': 'stdout',
    },
    'WAVM_default':{
        'bin_cmd': 'docker exec ori_wavm_cp910_debug /usr/local/bin/wavm',
        'std_cmd': '{} run --function=to_test {}',
        'container_name': 'ori_wavm_cp910_debug',
        'err_channel': 'stderr',
    }
}