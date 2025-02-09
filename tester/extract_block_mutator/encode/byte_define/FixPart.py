from typing import Union
from ..util import FailedDecodeException
from .NGDecoderP import NGDecoderP
import leb128


class FixPart(NGDecoderP):
    def __init__(self, expected_ba:Union[bytes, bytearray]):
        self.expected_ba = memoryview(expected_ba)
        self.byte_len = len(self.expected_ba)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.expected_ba})'

    @classmethod
    def require_uint(cls, expected_uint:int):
        expected_ba = bytes(leb128.u.encode(expected_uint))
        return cls(expected_ba)

    def byte_decode_and_generate(self, ba_view:memoryview):
        # * check
        
        if not all(self.expected_ba[i] == ba_view[i] for i in range(self.byte_len)):
            # raise FailedDecodeException(f'Failed to decode;')
            raise FailedDecodeException(f'Failed to decode; self.expected_ba: {bytearray(self.expected_ba)}, ba_view: {[x for x in ba_view[:self.byte_len]]}, self.byte_len: {self.byte_len}')
        return None,  self.byte_len

    def encode(self, *args, **kwds):
        return self.expected_ba

    def prefix_info(self):
        return self.expected_ba
