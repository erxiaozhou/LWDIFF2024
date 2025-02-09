from ..NGDataPayload import DataPayloadwithName
from .DecoderID import DecoderMemory
# DataPayloadwithName

def encode_data_payload_with_name(data_payload: DataPayloadwithName) -> bytearray:
    decoder = DecoderMemory.get_decoder(data_payload.inner_name.name)
    return bytearray(decoder.encode(data_payload))
