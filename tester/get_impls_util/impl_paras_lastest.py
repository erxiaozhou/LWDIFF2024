from extract_dump import wasmedgeHalfDumpData
from extract_dump import wasmerHalfDumpData
from extract_dump import iwasmHalfDumpDataCore
from pathlib import Path

from extract_dump.wasmtime_extract_dump import wasmtimeHalfDumpData


runtimes_base_dir = '/home/std_runtime_test/lastest_runtimes'
runtimes_base_dir = Path(runtimes_base_dir)

impl_paras_lastest = {
    'iwasm_classic_interp_dump':{
        'bin_path': '/home/anonymous/CP912/iwasm_pg/ori_wamr/install_classic_interpreter/bin/iwasm',
        'dump_vstack_rpath': '/home/anonymous/CP912/iwasm_pg/wamr_classic/install/dump_vstack',
        'dump_instante_rpath': '/home/anonymous/CP912/iwasm_pg/wamr_classic/install/dump_instantiation',
        'std_cmd': '/home/anonymous/CP912/iwasm_pg/ori_wamr/install_classic_interpreter/bin/iwasm --heap-size=0 -f {func_name} {case_path}',
        'dump_cmd': '/home/anonymous/CP912/iwasm_pg/wamr_classic/install/bin/iwasm --heap-size=0 -f {func_name} {case_path}',
        'err_channel': 'stdout',
        'dump_extractor': iwasmHalfDumpDataCore,
    },
    'iwasm_fast_interp_dump':{
        'bin_path': '/home/anonymous/CP912/iwasm_pg/ori_wamr/install_fast_interpreter/bin/iwasm',
        'dump_vstack_rpath': '/home/anonymous/CP912/iwasm_pg/wamr_fast/install/dump_vstack',
        'dump_instante_rpath': '/home/anonymous/CP912/iwasm_pg/wamr_fast/install/dump_instantiation',
        'std_cmd': '/home/anonymous/CP912/iwasm_pg/ori_wamr/install_fast_interpreter/bin/iwasm --heap-size=0 -f {func_name} {case_path}',
        'dump_cmd': '/home/anonymous/CP912/iwasm_pg/wamr_fast/install/bin/iwasm --heap-size=0 -f {func_name} {case_path}',
        'err_channel': 'stdout',
        'dump_extractor': iwasmHalfDumpDataCore,
    },
    'iwasm_mt_jit_dump':{
        'bin_path': '/home/anonymous/CP912/iwasm_pg/ori_wamr/install_mt_jit/bin/iwasm',
        'dump_vstack_rpath': '/home/anonymous/CP912/iwasm_pg/wamr_mt_jit/install/dump_vstack',
        'dump_instante_rpath': '/home/anonymous/CP912/iwasm_pg/wamr_mt_jit/install/dump_instantiation',
        'std_cmd': '/home/anonymous/CP912/iwasm_pg/ori_wamr/install_mt_jit/bin/iwasm --heap-size=0 --multi-tier-jit -f {func_name} {case_path}',  #
        'dump_cmd': '/home/anonymous/CP912/iwasm_pg/wamr_mt_jit/install/bin/iwasm --heap-size=0 --multi-tier-jit -f {func_name} {case_path}',
        'err_channel': 'stdout',
        'dump_extractor': iwasmHalfDumpDataCore,
    },
    'iwasm_jit_dump':{
        'bin_path': '/home/anonymous/CP912/iwasm_pg/ori_wamr/install_jit/bin/iwasm',
        'dump_vstack_rpath': '/home/anonymous/CP912/iwasm_pg/wamr_jit/install/dump_vstack',
        'dump_instante_rpath': '/home/anonymous/CP912/iwasm_pg/wamr_jit/install/dump_instantiation',
        'std_cmd': '/home/anonymous/CP912/iwasm_pg/ori_wamr/install_jit/bin/iwasm --heap-size=0 --llvm-jit -f {func_name} {case_path}',
        'dump_cmd': '/home/anonymous/CP912/iwasm_pg/wamr_jit/install/bin/iwasm --heap-size=0 --llvm-jit -f {func_name} {case_path}',
        'err_channel': 'stdout',
        'dump_extractor': iwasmHalfDumpDataCore,
    },
    'iwasm_fast_jit_dump':{
        'bin_path': '/home/anonymous/CP912/iwasm_pg/ori_wamr/install_fast_jit/bin/iwasm',
        'dump_vstack_rpath': '/home/anonymous/CP912/iwasm_pg/wamr_fast_jit/install/dump_vstack',
        'dump_instante_rpath': '/home/anonymous/CP912/iwasm_pg/wamr_fast_jit/install/dump_instantiation',
        'std_cmd': '/home/anonymous/CP912/iwasm_pg/ori_wamr/install_fast_jit/bin/iwasm --heap-size=0  --fast-jit -f {func_name} {case_path}',
        'dump_cmd': '/home/anonymous/CP912/iwasm_pg/wamr_fast_jit/install/bin/iwasm --heap-size=0  --fast-jit -f {func_name} {case_path}',
        'err_channel': 'stdout',
        'dump_extractor': iwasmHalfDumpDataCore,
    },
        
        

    
    'WasmEdge_disableAOT_newer':{
        'bin_path': '/home/anonymous/CP912/WasmEdge/install/bin/wasmedge',
        'dump_vstack_rpath': '/home/anonymous/CP912/ld_WasmEdge_disableAOT_lastest/dump_result/dump_vstack',
        'dump_instante_rpath': '/home/anonymous/CP912/ld_WasmEdge_disableAOT_lastest/dump_result/dump_instantiation',
        'dump_cmd': '/home/anonymous/CP912/ld_WasmEdge_disableAOT_lastest/install/bin/wasmedge run --reactor {case_path} {func_name}',
        'std_cmd': '/home/anonymous/CP912/WasmEdge/install/bin/wasmedge run --reactor {case_path} {func_name}',
        'err_channel': 'stdout_stderr',
        'dump_extractor': wasmedgeHalfDumpData,
    },
    
    'wasmtime':{
        'bin_path': '/home/anonymous/CP912/wasmtime2/install/bin/wasmtime',
        'dump_vstack_rpath': '/home/anonymous/CP912/wasmtime2/dump_vstack',
        'dump_instante_rpath': '/home/anonymous/CP912/wasmtime2/dump_instantiation',
        'dump_cmd': '/home/anonymous/CP912/wasmtime2/install/bin/wasmtime run {case_path} --invoke {func_name}',
        'std_cmd': '/home/anonymous/CP912/wasmtime/install/bin/wasmtime run {case_path} --invoke {func_name}',
        'err_channel': 'stderr',
        'dump_extractor': wasmtimeHalfDumpData,
    },
    'wasmer_default_dump':{
        'bin_path': '/home/anonymous/CP912/for_testing/ori_wasmer_lastest/target/release/wasmer',
        'dump_vstack_rpath': '/home/anonymous/CP912/for_testing/ld_wasmer_lastest/dump_vstack',
        'dump_instante_rpath': '/home/anonymous/CP912/for_testing/ld_wasmer_lastest/dump_instantiation',
        'dump_cmd': '/home/anonymous/CP912/for_testing/ld_wasmer_lastest/target/release/wasmer {case_path}  --enable-all -e {func_name}',
        'std_cmd': '/home/anonymous/CP912/for_testing/ori_wasmer_lastest/target/release/wasmer {case_path}  --enable-all -e {func_name}',
        'err_channel': 'stderr',
        'dump_extractor': wasmerHalfDumpData,
    },

}