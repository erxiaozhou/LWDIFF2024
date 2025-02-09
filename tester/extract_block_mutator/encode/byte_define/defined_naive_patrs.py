import struct
from ..util import FailedDecodeException
from .NoNameDecoder import NoNameDecoder
from util.encoding_util import read_next_leb_int_num, read_next_leb_num
from singleton_decorator import singleton
import leb128


class OneValPart(NoNameDecoder):
    def __init__(self):
        pass

    def prefix_info(self) -> memoryview:
        return memoryview(bytes())


@singleton
class U32(OneValPart):
    def byte_decode_and_generate(self, ba_view:memoryview):
        try:
            val, offset = read_next_leb_num(ba_view, 0)
            return val, offset
        except:
            raise FailedDecodeException(f'Failure during decode an UINT')

    def encode(self, val):
        return leb128.u.encode(val)



# @singleton
class IN(OneValPart):
    def __init__(self, n):
        self.mod = 2 ** (n-1)
    def byte_decode_and_generate(self, ba_view:memoryview):
        try:
            val, offset = read_next_leb_int_num(ba_view, 0)
            return val, offset
        except Exception as e:
            raise FailedDecodeException(f'Failure during decode an UINT')
        
    def encode(self, val:int):
        val = val % self.mod
        return leb128.i.encode(val)

I32 = IN(32)
I33 = IN(33)
I64 = IN(64)

        
@singleton
class BytePart(OneValPart):
    def byte_decode_and_generate(self, ba_view:memoryview):
        try:
            return ba_view[0], 1
        except:
            raise FailedDecodeException(f'Failure during decode an UINT')
    def encode(self, val:int):
        return val

@singleton
class F32Part(OneValPart):
    def byte_decode_and_generate(self, ba_view:memoryview):
        decoded, = struct.unpack('<f', ba_view[:4])
        return decoded, 4
    def encode(self, val):
        return bytearray(struct.pack('<f', val)) 
    
@singleton
class F64Part(OneValPart):
    def byte_decode_and_generate(self, ba_view:memoryview):
        decoded, = struct.unpack('<d', ba_view[:8])
        return decoded, 8

    def encode(self, val):
        return bytearray(struct.pack('<d', val)) 

@singleton
class EmptyPart(OneValPart):
    def byte_decode_and_generate(self, ba_view:memoryview):
        return None, 0

    def encode(self, val):
        if val is None:
            return bytearray()
        raise Exception(f'The encoder {self.__class__.__name__} can only encode None')  # ，
        return bytearray()

@singleton
class ByteVec(OneValPart):
    # ! 。，

    def byte_decode_and_generate(self, ba_view:memoryview):
        try:
            len_, offset = read_next_leb_num(ba_view, 0)
            end_idx = len_ + offset
            target_ba = bytearray(ba_view[offset:len_ + offset])
            return target_ba, end_idx
        except:
            raise FailedDecodeException(f'Failure during decode an UINT')

    def encode(self, val:bytearray):
        if isinstance(val, str):
            raise Exception('WWW wrong type of val', val)
        len_ = len(val)
        result = leb128.u.encode(len_)
        result.extend(val)
        return result


@singleton
class UTF8str(OneValPart):
    # ! 。，

    def byte_decode_and_generate(self, ba_view:memoryview):
        try:
            len_, offset = read_next_leb_num(ba_view, 0)
            end_idx = len_ + offset
            target_bytes = bytes(ba_view[offset:len_ + offset])
            utf8_s = target_bytes.decode('utf-8')
            return utf8_s, end_idx
        except:
            raise FailedDecodeException(f'Failure during decode an UINT')
        
    def encode(self, val:str):
        utf8_bytearray =  val.encode('utf-8')
        len_ = len(utf8_bytearray)
        result = leb128.u.encode(len_)
        result.extend(utf8_bytearray)
        return result