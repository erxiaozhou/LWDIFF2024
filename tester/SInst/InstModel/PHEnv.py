from typing import Mapping, Union
from .PlaceHolder import PH, OperandPH, OperandPHFactory, ImmPH, ImmPHFactory

INTERMIEDIA_PH = str


class PHEnv:
    def __init__(self, ph_dict:Mapping[str,Union[OperandPH, ImmPH, INTERMIEDIA_PH]], type_constraints=None):
        self._phs = ph_dict
        op_num, imm_num = self._determine_some_attr(ph_dict)
        self.op_num = op_num
        self.imm_num = imm_num
        # self.determined = not determined
        if type_constraints is None:
            type_constraints = []
        self.type_constraints = type_constraints

    @property
    def determined(self):
        determined = True
        for ph in self._phs.values():
            if isinstance(ph, OperandPH):
                if not ph.ty_determined:
                    determined = False
                    break
        if len(self.type_constraints):
            return False
        return determined

    def __repr__(self):
        return f'PHEnv({self._phs}) <self.determined: {self.determined}> <self._type_constraints: {self.type_constraints}>'

    def get_ph(self, ph_name):
        return self._phs[ph_name]

    def __contains__(self, ph_name):
        return ph_name in self._phs

    def __getitem__(self, ph_name):
        return self._phs[ph_name]

    def _determine_some_attr(self, ph_dict):
        op_num = 0
        imm_num = 0
        for ph in ph_dict.values():
            if isinstance(ph, OperandPH):
                op_num += 1
            if isinstance(ph, ImmPH):
                imm_num += 1
        return op_num, imm_num

    def set_type_constraints(self, type_constraints):
        self.type_constraints = type_constraints

    def get_operand_types(self):
        op_names = [f'op_{i}' for i in range(self.op_num)]
        return [self._phs[op_name].ty for op_name in op_names]
        # return [ph.ty for ph in self._phs.values() if isinstance(ph, OperandPH)]


    def copy(self):
        
        return PHEnv(self._phs.copy(), self.type_constraints.copy())
        
    @classmethod
    def from_raw_type_part_dict(cls, raw_type_part_dict):
        result_d = {}
        for ph_name, ph_thye in raw_type_part_dict.items():
            idx = int(ph_name.split('_')[-1])
            if ph_name.startswith('op'):
                ph = OperandPHFactory.get_operand_ph(ph_thye, idx)
            else:
                ph = ImmPHFactory.get_ph_by_attr(idx, ph_thye)
            result_d[ph_name] = ph
        return cls(result_d)
