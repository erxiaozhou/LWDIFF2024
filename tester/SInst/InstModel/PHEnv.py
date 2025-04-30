from .PlaceHolder import PH, PHType

class PHEnv:
    def __init__(self, 
                 ph_dict:dict[str,PH], 
                 op:str,
                 type_constraints=None):
        self._phs = ph_dict
        op_num, imm_num = self._determine_some_attr(ph_dict)
        self.op_num = op_num
        self.imm_num = imm_num
        self.op = op
        if type_constraints is None:
            type_constraints = []
        self.type_constraints = type_constraints

    @property
    def lane_type(self):
        if '.' not in self.op:
            return None
        prefix = self.op.split('.')[0]
        if 'x' not in prefix:
            return None
        type_part, _ = self.op.split('x')
        return type_part

    @property
    def lane_num(self):
        lane_type = self.lane_type
        if lane_type is not None:
            return 128 // int(lane_type[1:])
        return None

    def copy(self):
        
        return PHEnv(
            self._phs.copy(), 
            self.op,
            self.type_constraints.copy()
            )
       


    @property
    def determined(self):
        determined = True
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
            if ph.ph_attr == PHType.OPERAND:
                op_num += 1
            if ph.ph_attr == PHType.IMM:
                imm_num += 1
        return op_num, imm_num

    def set_type_constraints(self, type_constraints):
        self.type_constraints = type_constraints

    def get_operand_types(self)->list[str]:
        op_names = [f'op_{i}' for i in range(self.op_num)]
        return [self._phs[op_name].ty for op_name in op_names]
