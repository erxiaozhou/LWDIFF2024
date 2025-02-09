from typing import Callable, Optional
from typing import List

from extract_block_mutator.encode.byte_define.FixPart import FixPart
from .byte_define.NGDecoderP import NGDecoderP
from util.util import return_para

class PartDesc:
    def __init__(self,
                 attribute_names: List[str],
                 attribute_names2init_decoder: dict[str, NGDecoderP],
                 to_wat_component_func:Optional[Callable]=None,
                 to_payload_func:Optional[Callable]=None,
                 
                 decoder_name:str='AnyName',
                 is_section=False,
                 return_is_self_payload=None,
                 lasy_decode=False,
                 support_one_attr_inference=False
                 ) -> None:
        assert len(attribute_names) == len(attribute_names2init_decoder) > 0  # 
        self.attribute_names = attribute_names
        self.attribute_names2init_decoder = attribute_names2init_decoder
        if to_wat_component_func is None:
            to_wat_component_func = return_para
        self.to_wat_component_func = to_wat_component_func
        # if to_payload_func is None:
        #     to_payload_func = return_para
        self.to_payload_func = to_payload_func
        self.decoder_name = decoder_name
        self.decoder_num = len(attribute_names)
        self.is_section = is_section
        if return_is_self_payload is not None:
            self.return_is_self_payload = return_is_self_payload
        else:
            if to_wat_component_func is None:
                self.return_is_self_payload = True
            elif to_wat_component_func is return_para:
                self.return_is_self_payload = True
            else:
                self.return_is_self_payload = False
            if self.to_payload_func:
                self.return_is_self_payload = True
        self.lasy_attribute = lasy_decode
        self.support_one_attr_inference = support_one_attr_inference
        # 
        all_fix_part_names = []
        not_fix_part_names = []
        prefix_num = 0
        self.not_prefix_num = 0
        all_fix_now = True
        for name in self.attribute_names:
            decoder = self.attribute_names2init_decoder[name]
            if isinstance(decoder, FixPart):
                if all_fix_now:
                    prefix_num += 1
                all_fix_part_names.append(name)
                # all_fixed_patrs[name] = decoder
            else:
                self.not_prefix_num += 1
                all_fix_now = False
                not_fix_part_names.append(name)
        self.all_fix_part_names = all_fix_part_names
        self.not_fix_part_names = not_fix_part_names
        # 
        self.prefix_num = prefix_num

    @property
    def not_fix_decoders(self):
        return [self.attribute_names2init_decoder[name] for name in self.not_fix_part_names]

    def get_not_fixed_data(self, data):
        return {name: data[name] for name in self.not_fix_part_names}