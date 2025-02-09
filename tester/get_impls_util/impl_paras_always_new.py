from pathlib import Path


# iwasm  https://bytecodealliance.github.io/wamr.dev/blog/introduction-to-wamr-running-modes/

runtimes_base_dir = '/home/std_runtime_test/lastest_runtimes'
runtimes_base_dir = Path(runtimes_base_dir)

impl_paras_always_new = {
    'iwasm_classic_interp_dump':{
        'bin_path': '/home/anonymous/CP912/iwasm_pg/lastest_wamr2/install_classic_interpreter/bin/iwasm',
        'std_cmd': '/home/anonymous/CP912/iwasm_pg/lastest_wamr2/install_classic_interpreter/bin/iwasm --heap-size=0 -f {func_name} {case_path}',
        'err_channel': 'stdout',
    },
    'iwasm_fast_interp_dump':{
        'bin_path': '/home/anonymous/CP912/iwasm_pg/lastest_wamr2/install_fast_interpreter/bin/iwasm',
        'std_cmd': '/home/anonymous/CP912/iwasm_pg/lastest_wamr2/install_fast_interpreter/bin/iwasm --heap-size=0 -f {func_name} {case_path}',
        'err_channel': 'stdout',
    },
    'iwasm_mt_jit_dump':{
        'bin_path': '/home/anonymous/CP912/iwasm_pg/lastest_wamr2/install_mt_jit/bin/iwasm',
        'std_cmd': '/home/anonymous/CP912/iwasm_pg/lastest_wamr2/install_mt_jit/bin/iwasm --heap-size=0 --multi-tier-jit -f {func_name} {case_path}',  #
        'err_channel': 'stdout',
    },
    'iwasm_jit_dump':{
        'bin_path': '/home/anonymous/CP912/iwasm_pg/lastest_wamr2/install_jit/bin/iwasm',
        'std_cmd': '/home/anonymous/CP912/iwasm_pg/lastest_wamr2/install_jit/bin/iwasm --heap-size=0 --llvm-jit -f {func_name} {case_path}',
        'err_channel': 'stdout',
    },
    'iwasm_fast_jit_dump':{
        'bin_path': '/home/anonymous/CP912/iwasm_pg/lastest_wamr2/install_fast_jit/bin/iwasm',
        'std_cmd': '/home/anonymous/CP912/iwasm_pg/lastest_wamr2/install_fast_jit/bin/iwasm --heap-size=0  --fast-jit -f {func_name} {case_path}',
        'err_channel': 'stdout',
    },
    
    'WasmEdge_disableAOT_newer':{
        'bin_path': '/home/anonymous/CP912/WasmEdge_always_new/install/bin/wasmedge',
        'std_cmd': '/home/anonymous/CP912/WasmEdge_always_new/install/bin/wasmedge run --reactor {case_path} {func_name}',
        'err_channel': 'stdout_stderr',
    },
    
    'wasmtime':{
        'bin_path': '/home/anonymous/CP912/wasmtime_always_new/install/bin/wasmtime',
        'std_cmd': '/home/anonymous/CP912/wasmtime_always_new/install/bin/wasmtime run {case_path} --invoke {func_name}',
        'err_channel': 'stderr',
    },
    #  error: There are no available compilers for your architecture
    'wasmer_default_dump':{
        'bin_path': '/home/anonymous/CP912/for_testing/wasmer_always_new/target/release/wasmer',
        'std_cmd': '/home/anonymous/CP912/for_testing/wasmer_always_new/target/release/wasmer {case_path}  --enable-all -e {func_name}',
        'err_channel': 'stderr',
    },
    # wasmi_interp
    'wasmi_interp':{
        'bin_path': '/home/anonymous/CP912/for_testing/wasmi_always_new/install/bin/wasmi_cli',
        'std_cmd': '/home/anonymous/CP912/for_testing/wasmi_always_new/install/bin/wasmi_cli {case_path} --invoke {func_name}',
        'err_channel': 'stderr',
    },

}