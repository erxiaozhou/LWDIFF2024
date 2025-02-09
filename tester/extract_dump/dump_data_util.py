from file_util import pickle_dump, pickle_load
from typing import List, Optional
from util import CLIResult


class dumpData:
    def __init__(self):
        self.failed_exec = None
        self.name = None
        self.can_initialize = None
        self.cli_result: Optional[CLIResult] = None
        # 
        self.log = None
        # 
        self.has_instance = None
        self.global_bytes = []
        self.global_types = []
        self.global_infered_vals = []
        self.global_muts = []
        self.global_num = -1
        self.table_num = -1
        self.default_table_len = -1
        self.mem_num = -1
        self.default_mem_length = -1
        self.default_mem_page_num = -1
        self.default_mem_data = None
        # stack
        self.stack_num = -1
        self.stack_types = []
        self.stack_infered_vals = []
        self.stack_bytes = []
        self.stack_bytes_process_nan = []

    @property
    def to_dict(self):
        data = self.__dict__.copy()
        return data
    
    def dump(self, path):
        pickle_dump(path, self.to_dict)
    
    def __repr__(self) -> str:
        return str(self.__dict__)


def get_extractor_from_pkl(path):
    obj = pickle_load(path)
    result_obj = dumpData()
    assert isinstance(obj, dict)
    if isinstance(obj, dict):
        result_obj.__dict__.update(obj)
    else:
        result_obj.__dict__.update(obj.__dict__)
    return result_obj


no_exec_state_attrs = [
    'global_bytes',
    'global_types',
    'global_num',
    # 'global_infered_vals',
    # 'global_muts',
    'default_table_len',
    'table_num',
    'mem_num',
    'default_mem_length',
    'default_mem_page_num',
    'default_mem_data',
    'stack_num',
    'stack_types',
    'stack_bytes_process_nan',

    # 'stack_bytes',
    # 'stack_infered_vals',
]
_to_compare_attrs = no_exec_state_attrs + ['cli_result']

def get_diff_attr_names(data1, data2, to_compare_attrs):
    assert isinstance(data1, dumpData)
    assert isinstance(data2, dumpData)
    # if to_compare_attrs is None:
    #     to_compare_attrs = _to_compare_attrs
    different_attr_names = []
    for attr_name in to_compare_attrs:
        attr1 = getattr(data1, attr_name)
        attr2 = getattr(data2, attr_name)
        if attr1 != attr2:
            different_attr_names.append(attr_name)
    return different_attr_names
