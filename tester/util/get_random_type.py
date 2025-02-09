from random import choice
from WasmInfoCfg import val_type_strs_list

def get_random_type() -> str:
    return choice(val_type_strs_list)
