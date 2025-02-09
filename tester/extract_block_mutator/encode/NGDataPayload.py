from typing import Any, Callable, Protocol
from singleton_decorator import singleton

from extract_block_mutator.encode.util import is_prefix_name


class DataPayload(Protocol):
    def no_data(self)->bool:
        ...
    def need_data(self)->bool:
        ...

class DataPayloadName:
    __slots__ = ['name']
    def __init__(self, name:str):
        self.name = name
    def __repr__(self) -> str:
        return f'DataPayloadName({self.name})'
    def __eq__(self, other):
        if not isinstance(other, DataPayloadName):
            return False
        return self.name == other.name
    def __hash__(self):
        return hash(self.name)
        

class DataPayloadNameFactory:
    _generated_id:dict[str, DataPayloadName] = {}
    max_num = 2000  # soft limit: since there would not so much kind of payload name, if the number is too large (i.e., greater than max_num), it may be a bug
    @staticmethod
    def gen_one(name:str)->DataPayloadName:
        if name in DataPayloadNameFactory._generated_id:
            return DataPayloadNameFactory._generated_id[name]
        if len(DataPayloadNameFactory._generated_id) >= DataPayloadNameFactory.max_num:
            raise Exception(f'The number of generated DataPayloadName is too large; There maybe a bug. Or you can set DataPayloadNameFactory.max_num to a larger number')
        DataPayloadNameFactory._generated_id[name] = DataPayloadName(name)
        return DataPayloadNameFactory._generated_id[name]
    

class CommonDataPayload(DataPayload):
    __slots__ = ['_data']

    def __init__(self, data: dict):
        self._data = data

    @property
    def data(self):
        return self._data
    def __repr__(self) -> str:
        return f'CommonDataPayload({self._data})'
    @data.setter
    def data(self, data: dict):
        raise Exception('It should not be used')

    def copy(self):
        # ! ，  
        return CommonDataPayload(self._data)

    def __setattr__(self, __name: str, __value: Any) -> None:
        # print('XXX __name', __name, '|||', __name == '_data', '|||', hasattr(self, '_data'))
        if __name == '_data' or not hasattr(self, '_data'):
            super().__setattr__(__name, __value)
        elif __name in self._data:
            raise Exception('The DataPayload should not be modified.')
        return super().__setattr__(__name, __value)

    def __getattr__(self, name):
        if name == '_data':
            return object.__getattribute__(self, '_data')
        if name in self._data:
            return self._data[name]
        if len(self._data) == 1:
            # print('XXXXXXXXXXXXXXXXXX len(self._data)', len(self._data))
            return self._data[list(self._data.keys())[0]]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __eq__(self, other):
        if not isinstance(other, CommonDataPayload):
            return False
        print('XXX self._data', self._data, '|||', other._data, self._data == other._data)
        return self._data == other._data

    def __getitem__(self, name):
        # print('XXX self._data', self._data)
        return self._data[name]
    def no_data(self) -> bool:
        if len(self._data) != 0:
            return False
        raise Exception('It should be EmptyDataPayload')

    def need_data(self) -> bool:
        raise Exception('It should be EmptyDataPayload')

class DataPayloadwithName(CommonDataPayload):
    def __init__(self, data:dict, name:str):
        # self.inner_name = name
        self.__dict__['inner_name'] = DataPayloadNameFactory.gen_one(name)
        super().__init__(data)

    def __repr__(self) -> str:
        return f"{self.inner_name}({self._data})"
    def copy(self):
        return  DataPayloadwithName(self._data.copy(), self.inner_name.name)
@singleton
class EmptyDataPayload(DataPayload):
    def __init__(self) -> None: pass

    def no_data(self)->bool:
        return True

    def need_data(self)->bool:
        return False
    def __repr__(self) -> str:
        return 'EmptyDataPayload()'
    

def generate_payload_without_suffix(data:dict):
    new_data = _get_non_prefix_core(data)
    if len(new_data) == 0:
        return EmptyDataPayload()
    return CommonDataPayload(new_data)


def generate_payload_with_name(data:dict, name:str):
    new_data = _get_non_prefix_core(data)
    if len(new_data) == 0:
        return EmptyDataPayload()
    return DataPayloadwithName(new_data, name)

def _get_non_prefix_core(data):
    new_data = {}
    # print('XXX data', data)
    for name, val in data.items():
        if not is_prefix_name(name):
            new_data[name] = val
        else:
            if val is None:
                assert 0
            else:
                new_data[name] = val
    return new_data
