from typing import Union, List
from .PlaceHolder import  is_valid_imm_name, is_valid_op_name
from .PHEnv import PHEnv


class OpImmValSoluiton:
    def __init__(self, val_dict: dict[str, Union[int, float, str]], constrained_symbol_names:List[str]):
        # self._solution_dict_check(val_dict)
        self.val_dict = val_dict
        self.constrained_symbol_names = constrained_symbol_names
        for k in constrained_symbol_names:
            assert k in val_dict

    def get_concrete_val_by_name(self, name):
        return self.val_dict[name]

    @property
    def constrained_op_num(self):
        return len([x for x in self.constrained_symbol_names if is_valid_op_name(x)])

    @property
    def reset_op_idxs(self)->List[int]:
        op_names = [x for x in self.constrained_symbol_names if is_valid_op_name(x)]
        sufffixes = [int(x.split('_')[-1]) for x in op_names]
        return sorted(sufffixes)

    @property
    def reset_op_names(self)->List[str]:
        return [f'op_{x}' for x in self.reset_op_idxs]

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.val_dict})'

    def set_result(self, key, val):
        self.val_dict[key] = val

    def _solution_dict_check(self, val_dict):
        for k in val_dict:
            assert is_valid_op_name(k) or is_valid_imm_name(k)
