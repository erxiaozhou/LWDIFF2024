features_paras = {
    'wasmer_default_dump':{
        'support_multi_mem': True,
        'support_ref': True,
        'support_v128': True
    },
    'wasmi_interp': {
        'support_multi_mem': False,
        'support_ref': False,
        'support_v128': False
    },
    'iwasm_classic_interp_dump':{
        'support_multi_mem': False,
        'support_ref': True,
        'support_v128': False
    },
    'iwasm_fast_interp_dump':{
        'support_multi_mem': False,
        'support_ref': True,
        'support_v128': False 
    },
    'wasm3_dump':{
        'support_multi_mem': True,
        'support_ref': True,
        'support_v128': False
    },
    'WasmEdge_disableAOT_newer':{
        'support_multi_mem': True,
        'support_ref': True,
        'support_v128': True
    },
    'WAVM_default':{
        'support_multi_mem': True,
        'support_ref': True,
        'support_v128': True
    },
    'iwasm_mt_jit_dump':{
        'support_multi_mem': True,
        'support_ref': True,
        'support_v128': True
    },
    'iwasm_jit_dump':{
        'support_multi_mem': True,
        'support_ref': True,
        'support_v128': True
    },
    'iwasm_fast_jit_dump':{
        'support_multi_mem': True,
        'support_ref': True,
        'support_v128': False
    },
    'iwasm_aot_dump':{
        'support_multi_mem': True,
        'support_ref': True,
        'support_v128': True
    },
    'wasmtime':{
        'support_multi_mem': True,
        'support_ref': True,
        'support_v128': True
    }
}


def support_all_features(impl_name):
    return all(features_paras[impl_name].values())

def support_multi_mem(impl_name):
    return features_paras[impl_name]['support_multi_mem']

def support_ref(impl_name):
    return features_paras[impl_name]['support_ref']

def support_v128(impl_name):
    return features_paras[impl_name]['support_v128']

def support_score(impl_name):
    return sum([1 for v in features_paras[impl_name].values() if v])

registered_runtime_names = sorted([name for name in features_paras.keys()])
