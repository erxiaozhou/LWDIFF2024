from typing import Any, Optional, Union
from typing import Protocol


class NGDecoderP(Protocol):
    def byte_decode_and_generate(self, ba_view: memoryview) -> tuple[Any, int]:
        ...

    def prefix_info(self) -> memoryview:
        ...
    def encode(self, val:Optional[Any]=None)->Union[int, bytes, bytearray]:
        ...
