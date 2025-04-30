from typing import Any, Optional
import leb128

from extract_block_mutator.encode.NGDataPayload import DataPayloadwithName
from extract_block_mutator.encode.byte_define.DecoderID import DecoderMemory
from .FixPart import FixPart
from ..util import FailedDecodeException
from .NGDecoderP import NGDecoderP
from typing import List
from util.encoding_util import read_next_leb_num
from .NoNameDecoder import NoNameDecoder

def _get_a_batch_encode_resule(encoder, vals):
    result_ba = bytearray()
    for one_val in vals:

        
        cur_result = encoder.encode(one_val)
        if isinstance(cur_result, int):
            result_ba.append(cur_result)
        else:
            result_ba.extend(cur_result)
    return result_ba


class StructuredDecoder(NoNameDecoder):

    def prefix_info(self) -> memoryview:
        return memoryview(bytes())

class VecPartG(StructuredDecoder):
    def __init__(self, sub_decoder:NGDecoderP):
        self.sub_decoder =  sub_decoder

    def byte_decode_and_generate(self, ba_view:memoryview)->tuple[Any, int]:
        vec = []
        num, offset = read_next_leb_num(ba_view, 0)
        total_offset = offset
        for idx in range(num):
            obj, cur_offset = self.sub_decoder.byte_decode_and_generate(ba_view[total_offset:])
            vec.append(obj)
            total_offset += cur_offset
        return vec, total_offset

    def encode(self, val: Any ):
        len_ = len(val)
        result_ba = leb128.u.encode(len_)
        vals_encoding = _get_a_batch_encode_resule( self.sub_decoder, val)
        result_ba.extend(vals_encoding)
        return result_ba


class AllSizeG(StructuredDecoder):
    def __init__(self, sub_decoder:NGDecoderP):
        self.sub_decoder = sub_decoder
        
    def byte_decode_and_generate(self, ba_view:memoryview)->tuple[list[Any], int]:
        results = []
        cur_offset = 0
        target_all_offset = len(ba_view)
        while cur_offset < target_all_offset:
            obj, offset = self.sub_decoder.byte_decode_and_generate(ba_view[cur_offset:])
            cur_offset += offset
            results.append(obj)
        return results, cur_offset


    def encode(self, val: Any ):
        return _get_a_batch_encode_resule( self.sub_decoder, val)
        

class ArrayPart(StructuredDecoder):
    def __init__(self, 
                 length:int,
                 sub_decoder:NGDecoderP
        ) -> None:
        self.length = length
        self.sub_decoder = sub_decoder

    def byte_decode_and_generate(self, ba_view:memoryview)->tuple[list[Any], int]:
        result=  []
        cur_offset = 0
        for i in range(self.length):
            obj, _offsert = self.sub_decoder.byte_decode_and_generate(ba_view[cur_offset:])
            cur_offset += _offsert
            result.append(obj)
        return result, cur_offset

    def encode(self, val: Any ):
        return _get_a_batch_encode_resule( self.sub_decoder, val)

class UnionPart(StructuredDecoder):
    def __init__(self, sub_decoders:List[NGDecoderP]):
        self.sub_decoders =  sub_decoders

        prefix_tree = {}
        meta_data:list[tuple[memoryview, int]] = [(d.prefix_info(), idx) for idx, d in enumerate(sub_decoders)]
        for prefix, idx in meta_data:
            cur_tree = prefix_tree
            for byte in prefix:
                if byte not in cur_tree:
                    cur_tree[byte] = {}
                cur_tree = cur_tree[byte]
            cur_tree.setdefault('idx', []).append(idx)
        self.prefix_tree = prefix_tree
        

    def _get_possible_decoder_idxs(self, ba_view:memoryview)->List[int]:
        return _get_possible_idx_in_tree( self.prefix_tree, ba_view)

    def encode(self, val):
        if isinstance(val, DataPayloadwithName):
            payload_name = val.inner_name.name
            encoder = DecoderMemory.get_decoder(payload_name)
            return encoder.encode(val)
        else:
            for sub_decoder in self.sub_decoders:
                if isinstance(sub_decoder, FixPart):
                    raise Exception('FixPart should not be in UnionPart')
                try:
                    return sub_decoder.encode(val)
                except FailedDecodeException:
                    continue
     
         
        raise FailedDecodeException(f'UnionPart does not support encode yet: {val}, type(val): {type(val)} ;; self.sub_decoders: {self.sub_decoders}')
        

    def byte_decode_and_generate(self, ba_view:memoryview)->tuple[Any, int]:
        possible_decoder_idxs = self._get_possible_decoder_idxs(ba_view)
        if len(possible_decoder_idxs) == 0:
            raise FailedDecodeException(f'Failed to decode;')
            raise FailedDecodeException(f'Failed to decode; The sub decoders are {self.sub_decoders[:10]} ... Bytes: {[int(x) for x in ba_view[:10]]}')
        for idx in possible_decoder_idxs:
            sub_decoder = self.sub_decoders[idx]
            try:
                result, offset = sub_decoder.byte_decode_and_generate(ba_view)
                return result, offset
            except FailedDecodeException:
              
                continue
            
        raise FailedDecodeException(f'Failed to decode;')
        raise FailedDecodeException(f'Failed to decode; The sub decoders are {self.sub_decoders[:10]} ... Bytes: {[int(x) for x in ba_view[:10]]}')


def _get_possible_idx_in_tree(prefix_tree, ba_view:memoryview):
    if len(ba_view) == 0:
        return prefix_tree.get('idx', [])
    else:
        cur_b = ba_view[0]
        if cur_b in prefix_tree:
            to_append_idxs = _get_possible_idx_in_tree(prefix_tree[cur_b], ba_view[1:])
        else:
            to_append_idxs = []
        cur_idxs = prefix_tree.get('idx', [])
        return to_append_idxs + cur_idxs
