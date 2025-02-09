from typing import Union

from ..funcType import funcType
from ..funcTypeFactory import funcTypeFactory


class Blocktype:
    
    def __init__(self, init_data:Union[int, str, bool, funcType]) -> None:
        # print('LLLLLLLLL init_data', init_data)
        self.init_data = init_data
        self._indicated_type = None
        self._type_id = None
        if isinstance(init_data, bool):
            self._indicated_type = funcTypeFactory.generate_one_func_type_default([], [])
        # self.ty
        elif isinstance(init_data, int):
            self._type_id = init_data
            self._indicated_type = None
            # print('Int init_data', init_data)
        elif isinstance(init_data, funcType):
            self._indicated_type = init_data
            self._type_id = None
        else:
            self._type_id = None
            if isinstance(init_data, str):
                self._indicated_type = funcTypeFactory.generate_one_func_type_default([], [init_data])
            else:
                raise Exception(f'Blocktype init_data is of unexpected type: {init_data} {type(init_data)}')
            # else:
            #     self._indicated_type = init_data
        
    def __repr__(self) -> str:
        return f'Blocktype({self._type_id}, {self._indicated_type}, {self.init_data})'
    def need_type_sec_info(self):
        return self._indicated_type is None
    
    def init_with_type(self):
        return isinstance(self.init_data, funcType)

    # def 

    def init_with_type_sec_info(self, types:list[funcType]):
        assert self._indicated_type is None
        assert self._type_id is not None
        self._indicated_type = types[self._type_id]

    def concrete_type(self, types:list[funcType]):
        if self._indicated_type is not None:
            return self._indicated_type
        else:
            if self._type_id is None:
                raise Exception('Blocktype id should be a number')
            return types[self._type_id]
    
            