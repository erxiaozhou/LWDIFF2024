'''
 decoder ID ，decoder。decoder。
decoder ==> decoded data ，decoder ID。
'''
from extract_block_mutator.encode.PartDesc import PartDesc
from .NGDecoderP import NGDecoderP


class DecoderID:
    __slots__ = ['name']
    def __init__(self, name) -> None:
        self.name = name

    def __eq__(self, other):
        if not isinstance(other, DecoderID):
            return False
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)
    def __repr__(self) -> str:
        return f'DecoderID({self.name})'

class DecoderIDFactory:
    _generated_id:dict[str, DecoderID] = {}

    @staticmethod
    def register_decoder_id(name:str)->None:
        if name in DecoderIDFactory._generated_id:
            if _process_decoder_id_name(name) == '<anyname>':
                return
            # raise Exception(f'The name {name} is already registered')
        DecoderIDFactory._generated_id[name] = DecoderIDFactory.tmp_gen(name)

    @staticmethod
    def register_and_gen(name:str)->DecoderID:
        DecoderIDFactory.register_decoder_id(name)
        return DecoderIDFactory._generated_id[name]

    @staticmethod
    def tmp_gen(name:str)->DecoderID:
        name = _process_decoder_id_name(name)
        return DecoderID(name)

def _process_decoder_id_name(name:str)->str:
    name = name.lower()
    name = name.strip('<>')
    return f'<{name}>'


class DecoderMemory:
    _decoder2decoder:dict[DecoderID, NGDecoderP] = {}
    
    @staticmethod
    def existed(decoder_name:str)->bool:
        decoder_id = DecoderIDFactory.tmp_gen(decoder_name)
        return decoder_id in DecoderMemory._decoder2decoder
    
    @staticmethod
    def get_decoder(decoder_name:str)->NGDecoderP:
        if _process_decoder_id_name(decoder_name) == '<anyname>':
            raise Exception('The name <AnyName> is not allowed')
        
        if not DecoderMemory.existed(decoder_name):
            raise Exception(f'The decoder {decoder_name} is not registered')
        
        return DecoderMemory._decoder2decoder[DecoderIDFactory.tmp_gen(decoder_name)]
    
    @staticmethod
    def _register_decoder(decoder_id:DecoderID, decoder:NGDecoderP)->None:
        DecoderMemory._decoder2decoder[decoder_id] = decoder

    @staticmethod
    def register_decoder(name:str, decoder:NGDecoderP)->None:
        decoder_id = DecoderIDFactory.register_and_gen(name)
        DecoderMemory._register_decoder(decoder_id, decoder)
        # assert 0
        # print(f'Registered decoder: {decoder_id.name}')
    @staticmethod
    def support_decoder_ids()->set[DecoderID]:
        return set(DecoderMemory._decoder2decoder.keys())


class PartDescMemory:
    _decoder2decoder:dict[DecoderID, PartDesc] = {}
    
    @staticmethod
    def existed(decoder_name:str)->bool:
        decoder_id = DecoderIDFactory.tmp_gen(decoder_name)
        return decoder_id in PartDescMemory._decoder2decoder

    @staticmethod
    def get_desc(name:str)->PartDesc:
        if _process_decoder_id_name(name) == '<anyname>':
            raise Exception('The name <AnyName> is not allowed')
        
        if not PartDescMemory.existed(name):
            raise Exception(f'The part_desc {name} is not registered')
        
        return PartDescMemory._decoder2decoder[DecoderIDFactory.tmp_gen(name)]
  
    @staticmethod
    def _register_decoder(decoder_id:DecoderID, decoder:PartDesc)->None:
        PartDescMemory._decoder2decoder[decoder_id] = decoder

    @staticmethod
    def register_desc(name:str, decoder:PartDesc)->None:
        decoder_id = DecoderIDFactory.register_and_gen(name)
        PartDescMemory._register_decoder(decoder_id, decoder)

    @staticmethod
    def support_decoder_ids()->set[DecoderID]:
        return set(PartDescMemory._decoder2decoder.keys())
