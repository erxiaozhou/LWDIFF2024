from typing import Any, Union
from extract_block_mutator.encode.NGDataPayload import DataPayloadName, DataPayloadwithName
from extract_block_mutator.encode.byte_define.DecoderID import DecoderMemory

from extract_block_mutator.encode.byte_define.FixPart import FixPart
from extract_block_mutator.encode.byte_define.defined_naive_patrs import U32
from extract_block_mutator.encode.byte_define.structure_decoder import UnionPart

from file_util import bytes2f32, print_ba
from .NGDecoderP import NGDecoderP
from ..PartDesc import PartDesc



# def the_one_non_prefix_name_optional(attribute_name2decoders):
#     fix_num = 0
#     possible_name = None
#     for name, desc  in attribute_name2decoders.items():
#         if not FixPartDecoderFactory.support(desc):
#             fix_num += 1
#             possible_name= name
#     if fix_num == 1:
#         return possible_name
#     return None

class CommonBehaviorPart(NGDecoderP):
    part_desc: PartDesc
    
    def __init__(self, part_desc) -> None:
        self.decoder_name = part_desc.decoder_name
        self.part_desc = part_desc
        self.all_fix_part_names = self.part_desc.all_fix_part_names
        not_fix_part_names = self.part_desc.not_fix_part_names
        prefix_num = self.part_desc.prefix_num

        if prefix_num == 0:
            self.prefix_ba = self.prefix_ba = memoryview(bytes())
        else:
            prefix_ba = bytes()
            for i in range(prefix_num):
                prefix_ba += self.part_desc.attribute_names2init_decoder[self.part_desc.attribute_names[i]].expected_ba
            self.prefix_ba = memoryview(prefix_ba)
        # 
        self.is_section = part_desc.is_section
        self.the_only_not_fix_name = None
        if len(not_fix_part_names) == 1:
            self.the_only_not_fix_name = not_fix_part_names[0]
        if len(not_fix_part_names) == 2 and self.is_section:
            self.the_only_not_fix_name = not_fix_part_names[1]
        self.has_one_not_fix = self.the_only_not_fix_name is not None

        # prefix
        all_decoder_are_fix = True
        for decoder in self.part_desc.attribute_names2init_decoder.values():
            if not isinstance(decoder, FixPart):
                all_decoder_are_fix = False
                break
        self.all_decoder_are_fix = all_decoder_are_fix
            
    def prefix_info(self) -> memoryview:
        return self.prefix_ba

    def byte_decode_and_generate(self, ba_view:memoryview)->tuple[Any, int]:
        total_offset = 0
        data = {}
        for attribute_name in self.part_desc.attribute_names:
            
            cur_init_func = self.part_desc.attribute_names2init_decoder[attribute_name].byte_decode_and_generate

            # obj, cur_offset = cur_init_func(ba_view[total_offset:])
            # 
            if self.part_desc.lasy_attribute:
                _, cur_offset = cur_init_func(ba_view[total_offset:])
                obj = ba_view[total_offset:total_offset+cur_offset]
            else:
                # print('VVVVVVVVVVVVVVVVVV self.part_desc', self.part_desc.decoder_name)
                # print('VVVVVVVVVVVVVVVVVV cur_init_func', cur_init_func)
                obj, cur_offset = cur_init_func(ba_view[total_offset:])
            # 
                
            # 
            total_offset += cur_offset
            data[attribute_name] = obj
        result = self.part_desc.to_wat_component_func(data)
        return  result,  total_offset

    def encode(self, val):
        # print(f'------- Cur decoder name: {self.decoder_name}  -----------------------------------------------')
        # print(self.part_desc.attribute_names)
        attribute_names2init_decoder = {}
        for name in self.part_desc.attribute_names:
            attribute_names2init_decoder[name] = self.part_desc.attribute_names2init_decoder[name]
        # first 
        actual_union_decodername_mapping:dict = {}
        # if return_is_self_payload:
        
        if self.part_desc.to_payload_func is not None:
            # print('self.decoder_name', self.decoder_name, val, type(val))
            val = self.part_desc.to_payload_func(val)
            # print('after to_payload_func', val)
            # print('P6P6P6PP6P6PP6PP6PP6PP66')
        if self.all_decoder_are_fix:
            data_dict = {}
        elif  self.the_only_not_fix_name is not None:
            # if not isinstance(val, DataPayloadwithName):
            cocresponding_decoder = attribute_names2init_decoder[self.the_only_not_fix_name]
            # print('self.the_only_not_fix_name : ', self.the_only_not_fix_name, val,  self.the_only_not_fix_name, cocresponding_decoder)
            if isinstance(val, DataPayloadwithName):
                
                if isinstance(cocresponding_decoder, UnionPart):
                    actual_union_decodername_mapping[self.the_only_not_fix_name] = val.inner_name.name
                # else:
                #     assert self.part_desc.return_is_self_payload == (val.inner_name.name == self.decoder_name), print(self.decoder_name, val.inner_name.name, self.part_desc.return_is_self_payload)

                if self.part_desc.return_is_self_payload:
                    data_dict  = val.data
                    if self.part_desc.support_one_attr_inference:  # !   ！ 
                        if len(data_dict) == 1:
                            # print('p6p6p6p6p6')
                            data_dict = {self.the_only_not_fix_name: val.x}
                        
                    # print('P2P2P2P2P2P2P2')
                # elif isinstance(cocresponding_decoder, UnionPart):
                #     # actual_union_decodername_mapping[self.the_only_not_fix_name] = val.inner_name.name
                #     data_dict = {self.the_only_not_fix_name:val}
                #     print('P1P1PP1P1P1')
                elif self.decoder_name == val.inner_name.name:
                    data_dict = val.data
                else:
                    # print('P3P3P3P3P3')
                    data_dict = {self.the_only_not_fix_name:val}

            else:
                # print('P5P5P5 type(val)', type(val))
                data_dict = {self.the_only_not_fix_name:val}
                
        else:
            if not isinstance(val, DataPayloadwithName):
                raise Exception(f'val is not DataPayloadwithName: {val} ;; {self.decoder_name};; {self.part_desc.attribute_names}  ;; {self.part_desc.attribute_names2init_decoder} ;; It should be parsed by the code related to all_decoder_are_fix')
            # inner_name_str = val.inner_name.name
            if isinstance(val, DataPayloadwithName):
                data_dict = val.data
        # print('PPPPPPPPPPPP Determined data_dict', data_dict)
        # print()
        for key in actual_union_decodername_mapping:
            if DecoderMemory.existed(actual_union_decodername_mapping[key]):
                if self.decoder_name != actual_union_decodername_mapping[key]:
                    # actual_union_decoder_mapper[key] = DecoderMemory.get_decoder(actual_union_decodername_mapping[key])
                    assert isinstance(attribute_names2init_decoder[key], UnionPart)
                    # print('In replacing =====================', key, '\nxx', actual_union_decodername_mapping[key], '\nyy', attribute_names2init_decoder[key], '\nzz',  DecoderMemory.get_decoder(actual_union_decodername_mapping[key]), '\nppp', self.decoder_name, '\nllll', self.decoder_name == key)
                    # print('OOOOOOOO actual_union_decodername_mapping[key]', actual_union_decodername_mapping[key], 'self.decoder_name', self.decoder_name, self.decoder_name== actual_union_decodername_mapping[key])
                    attribute_names2init_decoder[key] = DecoderMemory.get_decoder(actual_union_decodername_mapping[key])
                    # print('Replace with actual_union_decodername_mapping[key]', actual_union_decodername_mapping[key])
        # 
        if not self.is_section:

            # print('data_dict', data_dict)
            # print('self.decoder_name', self.decoder_name)
            # print('NNNNNN', self.part_desc.attribute_names[0], attribute_names2init_decoder[self.part_desc.attribute_names[0]])
            result_ba_dict = self.get_mapping_content_encoding(attribute_names2init_decoder, data_dict, self.part_desc.attribute_names)
        
            names = self.part_desc.attribute_names
            ba =  mapping_ba_as_ba_sequence(result_ba_dict, names)
            # if 'blocktype' in self.decoder_name.lower():
            #     print('XXX BlockType', end='  ')
            #     print_ba(ba)
            return ba
        else:
            assert isinstance(attribute_names2init_decoder[self.part_desc.attribute_names[0]], FixPart)
            assert attribute_names2init_decoder[self.part_desc.attribute_names[1]] is U32()
            other_names = self.part_desc.attribute_names[2:]
            # print('other_names', other_names)

            data_dict = {name: data_dict[name] for name in other_names}

            content_ba_dict = self.get_mapping_content_encoding(attribute_names2init_decoder, data_dict, other_names)
            content_ba = mapping_ba_as_ba_sequence(content_ba_dict, other_names)
            content_length = len(content_ba)
            final_names =self.part_desc.attribute_names[:2]+ ['content'] 
            final_d = {
                self.part_desc.attribute_names[0]: attribute_names2init_decoder[self.part_desc.attribute_names[0]].encode(),
                self.part_desc.attribute_names[1]: U32().encode(content_length),
                'content': content_ba
            }
            final_ba = mapping_ba_as_ba_sequence(final_d, final_names)
            return final_ba

    def get_mapping_content_encoding(self, attribute_names2init_decoder, data_dict, considered_names):
        result_ba_dict:dict[str, Union[int, bytes, bytearray]] = {}
        for attribute_name in considered_names:
            cur_encoder = attribute_names2init_decoder[attribute_name]
                # print(attribute_name, cur_encoder)
            # print('XZXXXXFDSF attribute_name', attribute_name, data_dict)
            if attribute_name in self.all_fix_part_names:
                cur_encode_result = cur_encoder.encode()
            elif isinstance(data_dict[attribute_name], memoryview):  # for lazy decode
                cur_encode_result = data_dict[attribute_name]
            else:
                # print('XXXXXXX attribute_name', attribute_name, data_dict[attribute_name], attribute_names2init_decoder[attribute_name])
                cur_encode_result = attribute_names2init_decoder[attribute_name].encode(data_dict[attribute_name])
            result_ba_dict[attribute_name] = cur_encode_result
        return result_ba_dict


def gen_common_decoder(part_desc: PartDesc):
    decoder = CommonBehaviorPart(part_desc)
    # assert 0
    DecoderMemory.register_decoder(part_desc.decoder_name, decoder)
    return decoder



def mapping_ba_as_ba_sequence(result_ba_dict, names):
    result_ba = bytearray()
    for attribute_name in names:
        cur_encode_result = result_ba_dict[attribute_name]
        if isinstance(cur_encode_result, int):
            if cur_encode_result > 255:
                raise Exception(f'cur_encode_result: {cur_encode_result}')
            result_ba.append(cur_encode_result)
        else:
            result_ba.extend(cur_encode_result)
    return result_ba