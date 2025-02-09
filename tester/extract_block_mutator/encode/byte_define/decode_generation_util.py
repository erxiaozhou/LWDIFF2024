from typing import Optional
from typing import Any
from ..byte_define.NGDecoderP import NGDecoderP


# ! ，
def decode_main(ba_view:memoryview, 
                decoder:NGDecoderP, 
                *, 
                byte_num_limit:Optional[int]=None) -> tuple[Any, int]:
    # * S1 : is a naive defined obj (e.g., self defined enum / int)
    # * S2 : a self-defined struction bject, like func_type 
    # * S3 : is a data structure, like list, containing multiple S1 and S2
    return decoder.byte_decode_and_generate(ba_view)
