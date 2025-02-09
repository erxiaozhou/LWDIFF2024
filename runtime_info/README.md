Here, we introduce the information about the runtimes under test, including the the commit id and the patch to collect return value.
  - the commit id
  - the patch to collect return value


- wasmtime
    - commit id: 37300d3f4b51e0e3374e3c4fc382b7603b065c8b
    - We hook the runtime to collect the return value of wasmtime
        - patch file: wasmtime.patch
-  WAMR
    - commit id: 0b8a90419309a5db65c65127d7a86aedf36240f1
    - We hook the runtime to collect the return value of WAMR
        - patch file: WAMR.patch
    - building scripts for different modes:
        - build_wamr_classic_interpreter.sh
        - build_wamr_fast_interpreter.sh
        - build_wamr_jit.sh
        - build_wamr_fast_jit.sh
        - build_wamr_mt_jit.sh
- wasmer
    - commit id: 69c0aa256eedc23cc51247db7bbaa79d7a8bd1db
    - We hook the runtime to collect the return value of wasmer
        - patch file        : wasmer.patch
    - building script       : build_wasmer.sh
- WasmEdge
    - commit id: 0f9153fc553d0b5c22a654ffd7d3177ff7b90874
    - We hook the runtime to collect the return value of WasmEdge
        - patch file        : WasmEdge.patch
    - building script       : build_wasmedge.sh
