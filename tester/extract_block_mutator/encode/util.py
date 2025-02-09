from typing import Any, Callable
import re


hex_p = re.compile(r'(?:0[xX])?[0-9a-fA-F]+')
u32_imm_types = {
    'funcidx',
    'tableidx',
    'localidx',
    'typeidx',
    'elemidx',
    'offset',
    'dataidx',
    'globalidx',
    'labelidx',
    'laneidx',
    'align',
}

def is_hex_str(s:str)->bool:
    return bool(hex_p.fullmatch(s))

def hexstr2int(s:str)->int:
    # print('s', s)
    return int(s, 16)

def is_imm_u32(s:str)->bool:
    return (s in u32_imm_types) or (s == 'u32')


def get_default_prefix_name(idx):
    return f'prefix_{idx}'

def is_prefix_name(name:str)->bool:
    if name.startswith('prefix_'):
        num_part = name[7:]
        if num_part.isdigit():
            raise Exception('To remove the fucntion')
            return True
    return False

class FailedDecodeException(Exception): pass
class InvalidTypeDescException(Exception): pass

