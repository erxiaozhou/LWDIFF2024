from extract_block_mutator.encode.byte_define.DecoderID import DecoderMemory
from .defined_naive_patrs import I32, I33, I64, U32, BytePart, ByteVec, F32Part, F64Part,EmptyPart, UTF8str
from .structure_decoder import AllSizeG, ArrayPart, UnionPart, VecPartG
from .FixPart import FixPart
from ..util import InvalidTypeDescException, hexstr2int
from .NGDecoderP import NGDecoderP
from ..util import is_hex_str


def common_desc_validation(desc_str):
    # if not (desc_str.startswith('<') and desc_str.endswith('>')):
    #     raise InvalidTypeDescException(desc_str)
    if ' ' in desc_str:
        raise InvalidTypeDescException(f'There should not be space in {desc_str}')

class UnionDecoderFactory:
    @staticmethod
    def support(desc_str:str)->bool:
        core_str = desc_str[1:-1]
        if not core_str.startswith('Union:'):
            return False
        return True

    # @staticmethod
    # def is_byt_may_ill_formatted

    @staticmethod
    def get_decoder(desc_str:str)->NGDecoderP:
        # print('SSS s1', desc_str)
        core_str = desc_str[1:-1]
        # print('SSS s2', core_str)
        sub_reprs = _get_sub_decoder_repr(core_str[6:])
        print('||==>> sub_reprs', sub_reprs)
        sub_decoders = [type_desc_parser(sub_repr) for sub_repr in sub_reprs]
        return UnionPart(sub_decoders)
        raise NotImplementedError

def _get_sub_decoder_repr(core_str: str) -> list[str]:
    # print('XXXX _get_sub_decoder_repr   core_str', core_str)
    # raise NotImplementedError
    # * now, only support the union of naive defined types
    if _check_no_nested(core_str):
        return core_str.split(':')
    result_strs = []
    depth = 0
    cur_chars = []
    last_depth_is_zero = False
    for ch in core_str:
        if ch == '<':
            depth += 1
        elif ch == '>':
            depth -= 1
        if len(cur_chars) == 0 and ch == ':':
            continue
        cur_chars.append(ch)
        if depth == 0:
            # print(cur_chars)
            inferred_str = ''.join(cur_chars)
            if inferred_str and inferred_str != ':' and (not last_depth_is_zero):
                result_strs.append(inferred_str)
                cur_chars = []
            last_depth_is_zero = True
        else:
            last_depth_is_zero = False
    # assert len(cur_chars) == 0, cur_chars
    if cur_chars:
        result_strs.append(''.join(cur_chars))
    return result_strs
    
def _check_no_nested(desc_str:str)->bool:
    depth = 0
    for ch in desc_str:
        if ch == '<':
            depth += 1
        elif ch == '>':
            depth -= 1
        if depth > 0:
            return False
        if depth < 0:
            raise InvalidTypeDescException(f'Invalid desc: {desc_str}')
    return True

class ArrayDecoderFactory:
    @staticmethod
    def support(desc_str:str)->bool:
        common_desc_validation(desc_str)
        core_str = desc_str[1:-1]
        if not core_str.startswith('Array:'):
            return False
        all_parts = core_str.split(':')
        sub_decoder_repr = ':'.join(all_parts[1:-1])
        assert_valid_type_desc(sub_decoder_repr)
        
        if not core_str.split(':')[-1].isdigit():
            raise InvalidTypeDescException(f'Invalid para: {core_str.split(":")[-1]} in {desc_str}')
        return True

    @staticmethod
    def get_decoder(desc_str:str)->NGDecoderP:
        core_str = desc_str[1:-1]
        all_parts = core_str.split(':')
        para_parts = all_parts[1:]
        length = int(para_parts[-1])
        sub_decoder_repr = ':'.join(para_parts[:-1])
        sub_decoder = type_desc_parser(sub_decoder_repr)
        return ArrayPart(length, sub_decoder)

class VecDecoderFactory:
    @staticmethod
    def support(desc_str:str)->bool:
        common_desc_validation(desc_str)
        core_str = desc_str[1:-1]
        if not core_str.startswith('Vec:'):
            return False
        sub_decoder_repr = core_str.split(':')[1]
        assert_valid_type_desc(sub_decoder_repr)
        return True

    @staticmethod
    def get_decoder(desc_str:str)->NGDecoderP:
        core_str = desc_str[1:-1]
        all_parts = core_str.split(':')
        para_parts = all_parts[1:]
        sub_decoder_repr = ':'.join(para_parts)
        sub_decoder = type_desc_parser(sub_decoder_repr)
        return VecPartG(sub_decoder)


class OptionalDecoderFactory:
    @staticmethod
    def support(desc_str:str)->bool:
        common_desc_validation(desc_str)
        core_str = desc_str[1:-1]
        if not core_str.startswith('Optional:'):
            return False
        sub_decoder_repr = core_str.split(':')[1]
        assert_valid_type_desc(sub_decoder_repr)
        return True
    @staticmethod
    def get_decoder(desc_str:str)->NGDecoderP:
        core_str = desc_str[1:-1]
        all_parts = core_str.split(':')
        para_parts = all_parts[1:]
        sub_decoder_repr = ':'.join(para_parts)
        sub_decoder = type_desc_parser(sub_decoder_repr)
        empty_one = EmptyPart()
        return UnionPart([sub_decoder, empty_one])
    

class AllSizeGDecoderFactory:
    @staticmethod
    def support(desc_str:str)->bool:
        common_desc_validation(desc_str)
        core_str = desc_str[1:-1]
        if not core_str.startswith('AllSizeG:'):
            return False
        sub_decoder_repr = core_str.split(':')[1]
        assert_valid_type_desc(sub_decoder_repr)
        return True

    @staticmethod
    def get_decoder(desc_str:str)->NGDecoderP:
        core_str = desc_str[1:-1]
        all_parts = core_str.split(':')
        para_parts = all_parts[1:]
        sub_decoder_repr = ':'.join(para_parts)
        sub_decoder = type_desc_parser(sub_decoder_repr)
        return AllSizeG(sub_decoder)
    
class FixPartDecoderFactory:
    @staticmethod
    def support(desc_str:str)->bool:
        # assert desc_str.startswith('<') and desc_str.endswith('>'), desc_str
        common_desc_validation(desc_str)
        core_str = desc_str[1:-1]
        if not core_str.startswith('Fix'):
            return False
        # check whether the paras are valid
        if not(core_str.count(':') == 2):
            raise InvalidTypeDescException(f'Wrong para count in {desc_str}; Required: 2, but got: {core_str.count(":")}')
        all_parts = core_str.split(':')
        para_parts = all_parts[1:]
        # if not is_hex_str(para_parts[0]):
        #     raise InvalidTypeDescException(f'Invalid para0: {para_parts[0]} in {desc_str}')
        if para_parts[1] not in {'u32', 'hex', 'bytes'}:
            raise InvalidTypeDescException(f'Invalid para0: {para_parts[1]} in {desc_str}')
        if para_parts[1] == 'u32' or para_parts[1] == 'hex':
            if not is_hex_str(para_parts[0]):
                raise InvalidTypeDescException(f'Invalid para0: {para_parts[0]} in {desc_str}')
        return True

    @staticmethod
    def get_decoder(desc_str:str)->NGDecoderP:
        core_str = desc_str[1:-1]
        all_parts = core_str.split(':')
        para_parts = all_parts[1:]
        if para_parts[1] == 'u32':
            return FixPart(U32().encode(int(para_parts[0])))
        elif para_parts[1] == 'hex':
            val = hexstr2int(para_parts[0])
            # print('val', val)
            return FixPart(bytes([val]))
        elif para_parts[1] == 'bytes':
            hex_strs = para_parts[0].split('_')
            ints = [hexstr2int(hex_str) for hex_str in hex_strs]
            return FixPart(bytes(ints))
            # return FixPart(eval(para_parts[0]))
        raise NotImplementedError('Not implemented yet: desc_str')


DecoderMemory.register_decoder('u32', U32())
DecoderMemory.register_decoder('i33', I33)
DecoderMemory.register_decoder('i32', I32)
DecoderMemory.register_decoder('i64', I64)
DecoderMemory.register_decoder('f32', F32Part())
DecoderMemory.register_decoder('f64', F64Part())
DecoderMemory.register_decoder('utf8str', UTF8str())
DecoderMemory.register_decoder('byte', BytePart())
DecoderMemory.register_decoder('bytevec', ByteVec())
DecoderMemory.register_decoder('empty', EmptyPart())
# InstD

def type_desc_parser(type_desc_str:str)->NGDecoderP:
    if DecoderMemory.existed(type_desc_str):
        return DecoderMemory.get_decoder(type_desc_str)
    elif FixPartDecoderFactory.support(type_desc_str):
        return FixPartDecoderFactory.get_decoder(type_desc_str)
    elif AllSizeGDecoderFactory.support(type_desc_str):
        return AllSizeGDecoderFactory.get_decoder(type_desc_str)
    elif VecDecoderFactory.support(type_desc_str):
        return VecDecoderFactory.get_decoder(type_desc_str)
    elif ArrayDecoderFactory.support(type_desc_str):
        return ArrayDecoderFactory.get_decoder(type_desc_str)
    elif UnionDecoderFactory.support(type_desc_str):
        return UnionDecoderFactory.get_decoder(type_desc_str)
    elif OptionalDecoderFactory.support(type_desc_str):
        return OptionalDecoderFactory.get_decoder(type_desc_str)
    else:
        raise NotImplementedError(f'Unrecgonized type desc: {type_desc_str}; supported generated ones: {DecoderMemory.support_decoder_ids()}')

def assert_valid_type_desc(type_desc_str:str)->None:
    if DecoderMemory.existed(type_desc_str):
        return
    elif FixPartDecoderFactory.support(type_desc_str):
        return
    elif VecDecoderFactory.support(type_desc_str):
        return
    elif ArrayDecoderFactory.support(type_desc_str):
        return
    elif UnionDecoderFactory.support(type_desc_str):
        return
    elif AllSizeGDecoderFactory.support(type_desc_str):
        return
    elif (':' not in type_desc_str):
        return
    else:
        raise InvalidTypeDescException(f'Invalid type desc: {type_desc_str}')
