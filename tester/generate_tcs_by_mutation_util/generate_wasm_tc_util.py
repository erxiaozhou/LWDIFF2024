'''
wasm，
<code><0A><code><><><><>
<code>type section（section id : 1）
type，type0x60，pararesult，
func，，section id, ，，
'''
import random
import leb128
from file_util import write_bytes
from .byte_seq_nomask_mutator import mutate_without_mask
from util.encoding_util import read_next_leb_num
from util.prepare_template import id_name_dict

class BAwithLen:
    def __init__(self, ba:bytearray, length:int) -> None:
        self.ba: bytearray = ba
        self.length: int = length

    def as_vec_encoding(self):
        return leb128.u.encode(self.length) + self.ba

    @classmethod
    def from_ba_without_length(cls, ba:bytearray):
        length = len(ba)
        return cls(ba, length)
        

def mutate_BAwithLen(ba_with_length:BAwithLen, section_name:str):
    # 
    ba = mutate_without_mask(ba_with_length.ba)
    len_ = len(ba)
    len_ = random.choices([-1, 0, 1], [0.01, 0.98, 0.01], k=1)[0] + len_
    if len_ <= 0:
        len_ = 0
    return BAwithLen(ba, len_)
    

def _get_wasm_bytes_from_dict(section_dict):
    result = bytearray()
    result.extend(section_dict['pre'])
    idxs = [1,2,3,4,5,6,7,8,9,12,10,11]
    for i in idxs:
        content = section_dict.get(id_name_dict[i])
        if content is None:
            continue
        result.extend(leb128.u.encode(i))
        section_len = len(content)
        result.extend(leb128.u.encode(section_len))
        result.extend(content)
    return result


def write_wasm_from_dict(path, section_dict):
    # assert not Path(path).exists()
    wasm_bytes = _get_wasm_bytes_from_dict(section_dict)
    write_bytes(path, wasm_bytes)


def prepare_template2(template_path):
    with_table_template = {}
    # 
    # ba = Path(template_path).read_bytes()
    with open(template_path, 'rb') as f:
        ba = f.read()
        # size = os.path.getsize(template_path)
        # ba = mmap.mmap(f.fileno(), size, mmap.PROT_READ)
    with_table_template['pre'] = ba[:0x8]
    offset_ = 8
    ba_len = len(ba)
    while offset_ < ba_len:
        cur_section_id_raw_content = ba[offset_:offset_+1].hex()
        offset_ += 1
        cur_section_id = int(cur_section_id_raw_content, 16)
        cur_section_name = id_name_dict[cur_section_id]
        section_length, offset_ = read_next_leb_num(ba, offset_)
        with_table_template[cur_section_name] = ba[offset_:offset_+section_length]
        offset_ += section_length
        

    return with_table_template
