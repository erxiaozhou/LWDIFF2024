from extract_block_mutator.WasmParser import WasmParser
from taint_analysis.ICFGConstructor import ICFGConstructor, DEBUG_OUTPUT
from pathlib import Path
import sys

def debug_icfg_construction(wasm_file_path: Path):
    """ICFG"""
    print(f": {wasm_file_path}")
    
    # 
    global DEBUG_OUTPUT
    DEBUG_OUTPUT = True
    
    # WASM
    parzer = WasmParser.from_wasm_path(wasm_file_path)
    
    # ICFG
    icfg = ICFGConstructor.init_ICFG_from_parzer(parzer)
    
    # ICFG
    print(f"\n==================== ICFG ====================")
    print(f": {icfg.func_num}")
    print(f": {icfg.node_num}")
    print(f": {icfg.edge_num}")
    
    # 
    for func_idx, func_cfg in icfg.idx2func.items():
        print(f"\n {func_idx} :")
        print(f"  : {func_cfg.node_num}")
        print(f"  : {len(func_cfg.callsites)}")
        
        # 
        node_types = {}
        for node in func_cfg.graph.nodes:
            node_type = node.__class__.__name__
            node_types[node_type] = node_types.get(node_type, 0) + 1
            
        print(f"  :")
        for node_type, count in node_types.items():
            print(f"    {node_type}: {count}")
    
    return icfg

if __name__ == "__main__":
    # WASM
    data_base_dir = Path('tests/taint_analysis/data')
    wasm_file = data_base_dir / 'try_build_icfg3.wasm'
    
    # ，
    if len(sys.argv) > 1:
        wasm_file = Path(sys.argv[1])
        
    # ICFG
    icfg = debug_icfg_construction(wasm_file)
    
    # 
    print(f"\n====================  ====================")
    print(f":")
    print(f"  : 2")
    print(f"  : 8")
    print(f"  : 7")
    print(f":")
    print(f"  : {icfg.func_num}")
    print(f"  : {icfg.node_num}")
    print(f"  : {icfg.edge_num}") 