
from functools import partial
from .NGDataPayload import generate_payload_with_name
from .PartDesc import PartDesc
from .byte_define.NGDecoderP import NGDecoderP
from typing import List


class DataPayloadPartDesc(PartDesc):
    def __init__(self,
                 attribute_names: List[str],
                 attribute_names2init_decoder: dict[str, NGDecoderP],
                 decoded_attr_kind_name:str='AnyName'
                 ):
        to_wat_component_func = partial(generate_payload_with_name, name=decoded_attr_kind_name)
        super().__init__(
            attribute_names, 
            attribute_names2init_decoder, 
            to_wat_component_func, 
            decoded_attr_kind_name
        )