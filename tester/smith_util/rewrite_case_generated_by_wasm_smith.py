from random import choice, randint
from typing import Optional
from extract_block_mutator.DefShell import gen_export_desc, gen_export_funcidx_part
from extract_block_mutator.InstGeneration.InstFactory import InstFactory
from extract_block_mutator.InstUtil.Inst import Inst
from extract_block_mutator.InstUtil.InstFactory_util import generate_randon_common_i32, generate_randon_f32, generate_randon_i64, generate_randon_f64
from extract_block_mutator.InstGeneration.padding_input_type import get_inst_by_require_ty_const
import leb128
from extract_block_mutator.encode.byte_define.encode_main import encode_data_payload_with_name
from extract_block_mutator.WasmParser import  WasmParser
from extract_block_mutator.parser_to_file_util import parser2wasm

from extract_block_mutator.watFunc import watFunc
from extract_block_mutator.funcType import funcType
from file_util import generate_vec_bytes, print_ba
from extract_block_mutator.funcType import funcType, get_func_type_from_ba
from generate_tcs_by_mutation_util.generate_wasm_tc_util import read_next_leb_num, write_wasm_from_dict
from util.prepare_template import prepare_template
from util.value_encoder import value_holder, i32_holder, ref_null_holder, i64_holder, f32_holder, f64_holder, v128_holder

def is_expected_case(parser: WasmParser):
    if len(parser.defined_funcs) == 0:
        return False
    return True


def _detect_the_longest_func(parser: WasmParser):
    max_func_len = -1
    max_len_defined_func_idx = 0
    if len(parser.defined_funcs) == 0:
        return None
    for func_idx, func in enumerate(parser.defined_funcs):
        cur_inst_num = len(func.insts)
        if cur_inst_num > max_func_len:
            max_func_len = cur_inst_num
            max_len_defined_func_idx = func_idx
    # max_func_len_idx = max_func_len_idx + import_func_num
    return max_len_defined_func_idx


# generate func to call the longest func
def _generate_entry_func(parser: WasmParser, longest_func_idx: int):
    raise NotImplementedError
    longest_func_type = parser.defined_funcs[longest_func_idx].func_ty
    new_func_type = funcType([], longest_func_type.result_types)
    ori_paras = parser.defined_funcs[longest_func_idx].param_types
    # generate inst to set operands
    insts = [get_inst_by_require_ty_const(ty) for ty in ori_paras]
    # generate call
    call_inst = InstFactory.gen_binary_info_inst_high_single_imm('call', longest_func_idx)
    insts.append(call_inst)
    insts_part = "\n".join(str(inst) for inst in insts)
    func_fext = f'(func {new_func_type.as_code()}\n{insts_part}\n)'
    return watFunc.from_text(func_fext, new_func_type)


def rewrite_a_case(parser: WasmParser, new_path):
    longest_defined_func_idx = _detect_the_longest_func(parser)
    assert longest_defined_func_idx is not None
    new_func = _generate_entry_func(parser, longest_defined_func_idx)
    parser.defined_funcs.append(new_func)
    export_func_idx = len(parser.defined_funcs) + parser.import_func_num - 1
    export_func_name = 'to_test'
    idx_part = gen_export_funcidx_part(func_idx=export_func_idx)
    export_dec = gen_export_desc(name=export_func_name, desc=idx_part)

    parser.exports.append(export_dec)
    parser2wasm(parser, new_path)

ty2encoder = {
    'i32': i32_holder,
    'i64': i64_holder,
    'f32': f32_holder,
    'f64': f64_holder,
    'v128': v128_holder,
    'funcref': ref_null_holder,
    'externref': ref_null_holder
}

def get_entry_func_byte(params, to_call_func_idx):
    # print(params)
    encoders = []
    for ty in params:
        if ty == 'i32':
            val = generate_randon_common_i32()
            encoder = i32_holder(val, 'i32')
        elif ty == 'i64':
            val = generate_randon_i64()
            encoder = i64_holder(val, 'i64')
        elif ty == 'f32':
            val = generate_randon_f32()
            encoder = f32_holder(val, 'f32')
        elif ty == 'f64':
            val = generate_randon_f64()
            encoder = f64_holder(val, 'f64')
        elif ty == 'v128':
            val = [randint(0, 255) for _ in range(16)]
            encoder = v128_holder(val, 'v128')
        elif ty in ['funcref', 'externref']:
            val = 0x70 if ty == 'funcref' else 0x6F
            encoder = ref_null_holder(val)
        encoders.append(encoder)
    insts_ba = bytearray()
    insts_ba.extend(leb128.u.encode(0))
    for encoder in encoders:
        insts_ba.extend(encoder.const_line)
    insts_ba.append(0x10)
    insts_ba.extend(leb128.u.encode(i=to_call_func_idx))
    insts_ba.append(0x0B)
    # print_ba(insts_ba)
    # print(params)
    func_code_ba = leb128.u.encode(len(insts_ba)) + insts_ba
    return func_code_ba
    

class ByteSmithRewriter:
    def __init__(self, p):
        # ba = Path(p).read_bytes()
        self.ori_p = p
        # result = prepare_template(p)
        try:
            self.sec_dict = prepare_template(p)
        except Exception as e:
            print('|||==>p', p)
            print(e)
            raise e

    def is_expected_case(self):
        has_zero_import = sure_import_func_num_is_zero(self.sec_dict.get('import'))
        # print('==>has_zero_import', has_zero_import, self.ori_p)
        if not has_zero_import:
            return False
        # if self.no_func_in_code_sec():
        #     return False
        no_func_in_func_sec = self._no_func_in_func_sec()
        no_func_in_code_sec = self._no_func_in_code_sec()
        if no_func_in_func_sec != no_func_in_code_sec:
            raise Exception(
                'no_func_in_func_sec != no_func_in_code_sec; Maybe invalid case')
        return not no_func_in_func_sec

    def _no_func_in_func_sec(self):
        function_sec_bas = self.sec_dict.get('function')
        return function_sec_bas is None or (len(function_sec_bas) == 1 and int(function_sec_bas[0]) == 0)

    def _no_func_in_code_sec(self):
        code_sec_bas = self.sec_dict.get('code')
        return code_sec_bas is None or (len(code_sec_bas) == 1 and int(code_sec_bas[0]) == 0)

    def rewrite_to_path(self, p):
        write_wasm_from_dict(p, self.sec_dict)

    def rewrite_main(self, p):
        pass
        # 1. determine the largest func
        # 2. add a new function call the largest func
        # 3. add export
        # 4. write to path
        max_func_idx = get_max_func_idx(self.sec_dict['code'])
        function_sec = _FunctionSection.from_ba(self.sec_dict['function'])
        func_ty_idxs = function_sec.func_ty_idxs
        type_sec = _typeSection.from_ba(self.sec_dict['type'])
        # print(func_ty_idxs)
        func_types = type_sec.types
        max_func_type = func_types[func_ty_idxs[max_func_idx]]
        params = max_func_type.param_types
        # encoders
        func_code_byte = get_entry_func_byte(params, max_func_idx)
        new_func_type = funcType([], max_func_type.result_types)
        type_idx = type_sec.get_func_idx_and_insert(new_func_type)
        function_sec.func_ty_idxs.append(type_idx)
        # code
        code_sec = _CodeSectionInfo.from_ba(self.sec_dict['code'])
        code_sec.add_raw_func_ba(func_code_byte)
        # import num
        # print('==>p', self.ori_p)
        import_func_num = 0
        assert sure_import_func_num_is_zero(self.sec_dict.get('import'))
        # export
        # print_ba(self.sec_dict.get('export'))
        export_sec = _ExportForAppend.from_ba(self.sec_dict.get('export'))
        new_export_func_ba = generate_export_func_entry_ba(code_sec.func_num + import_func_num - 1, 'to_test')
        export_sec.append_export_func_ba(new_export_func_ba)
        # print_ba(export_sec.as_ba)
        # 
        self.sec_dict['type'] = type_sec.as_bytes_without_length
        self.sec_dict['function'] = function_sec.as_bytes_without_length
        self.sec_dict['code'] = code_sec.as_ba
        self.sec_dict['export'] = export_sec.as_ba
        self.rewrite_to_path(p)


def get_max_func_idx(conde_section_ba):
    offsets = _CodeSectionInfo.from_ba(conde_section_ba).func_lengths
    max_len = max(offsets)
    possible_idxs = [i for i, l in enumerate(offsets) if l == max_len]
    assert len(possible_idxs)
    return choice(possible_idxs)


class _typeSection:
    def __init__(self, types):
        self.types = types

    def get_func_idx_and_insert(self, func_type)->int:
        if func_type in self.types:
            return self.types.index(func_type)
        else:
            self.types.append(func_type)
            return len(self.types) - 1
    @classmethod
    def from_ba(cls, ba):
        ba = bytearray(ba)
        type_num, offset = read_next_leb_num(byte_seq=ba, offset=0)
        types = []
        type_bas = []
        type_ba_start_idxs = [i+1 for i, b in enumerate(ba) if b==0x60]
        type_ba_end_idxs = [x-1 for x in type_ba_start_idxs[1:]] + [len(ba)]
        # print_ba(ba)
        # print(type_ba_start_idxs)
        func_types = []
        assert type_num == len(type_ba_start_idxs)
        for type_ba_start_idx, type_ba_end_idx in zip(type_ba_start_idxs, type_ba_end_idxs):
            # type_bas.append(ba[type_ba_start_idx: type_ba_end_idx])
            func_types.append(get_func_type_from_ba(ba[type_ba_start_idx: type_ba_end_idx]))
        #     type_ba 
        # print(func_types)
        return cls(func_types)


    @property
    def as_bytes_without_length(self):
        func_type_bytes = [x.as_bytes for x in self.types]
        return generate_vec_bytes(func_type_bytes)

class _FunctionSection:
    def __init__(self, func_ty_idxs):
        self.func_ty_idxs = func_ty_idxs

    @classmethod
    def from_ba(cls, ba):
        idx_num, offset = read_next_leb_num(byte_seq=ba, offset=0)
        idxs = []
        for i in range(idx_num):
            type_idx, offset = read_next_leb_num(ba, offset=offset)
            idxs.append(type_idx)
        return cls(idxs)

    @property
    def as_bytes_without_length(self):
        type_idx_bytes = [leb128.u.encode(x) for x in self.func_ty_idxs]
        return generate_vec_bytes(type_idx_bytes)

class _CodeSectionInfo:
    def __init__(self, func_lengths, func_bodys, raw_func_code_ba):
        # ! func body， ，
        self.func_lengths = func_lengths
        self.func_bodys = func_bodys
        self.raw_func_code_ba:bytearray = raw_func_code_ba
        self.func_num = len(func_lengths)

    def add_raw_func_ba(self,ba):
        self.raw_func_code_ba.extend(ba)
        self.func_num += 1

    @classmethod
    def from_ba(cls, ba):
        ba = bytearray(ba)
        func_num, offset = read_next_leb_num(byte_seq=ba, offset=0)
        start_code_ba_idx = offset
        func_lengths = []
        func_bodys = []
        for i in range(func_num):
            func_len, offset = read_next_leb_num(ba, offset=offset)
            func_lengths.append(func_len)
            func_bodys.append(ba[offset:offset + func_len])
            offset += func_len
        return cls(func_lengths, func_bodys, ba[start_code_ba_idx:])
    @property
    def as_ba(self):
        ba = leb128.u.encode(self.func_num)
        ba.extend(self.raw_func_code_ba)
        return ba
        

class _ExportForAppend:
    def __init__(self,export_num, raw_ba):
        self.export_num:int = export_num
        self.raw_ba: bytearray = raw_ba
        # print(self.export_num)

    def append_export_func_ba(self, ba):
        self.export_num += 1
        self.raw_ba.extend(ba)
        
    @classmethod
    def from_ba(cls, ba):
        if ba is not None:
            ba = bytearray(ba)
            export_num, offset = read_next_leb_num(byte_seq=ba, offset=0)
            ba = ba[offset:]
        else:
            ba = bytearray()
            export_num = 0
        return cls(export_num, ba)
    @property
    def as_ba(self):
        ba = leb128.u.encode(self.export_num)
        ba.extend(self.raw_ba)
        return ba

def generate_export_func_entry_ba(func_idx, name):
    idx_part = gen_export_funcidx_part(func_idx)
    data = gen_export_desc(name=name, desc=idx_part)
    return encode_data_payload_with_name(data)

def get_import_func_num(ba:Optional[bytearray]):
    if ba is None:
        return 0
    num, offset = read_next_leb_num(ba,0)
    if num == 0:
        return 0
    # print_ba(ba)
    raise NotImplementedError

def sure_import_func_num_is_zero(ba:Optional[bytearray]):
    if ba is None:
        return True
    num, offset = read_next_leb_num(ba,0)
    if num == 0:
        return True
    
    return False
