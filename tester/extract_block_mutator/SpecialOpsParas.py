class SpecialOpsParas:
    # func
    def __init__(self, param_tys, val_name_strs, reset_op_idxs) -> None:
        self.param_tys = tuple(param_tys)
        self.val_name_strs = tuple(val_name_strs)
        self.reset_op_idxs = tuple(reset_op_idxs)
        self.changed_op_num = len(self.reset_op_idxs)
        self._func_name = None 
        
    @property
    def func_name(self):
        if self._func_name is None:
            self._func_name = self._get_n_func_name()
        return self._func_name
    @classmethod
    def get_no_param_one(cls):
        return cls([], [], [])

    def __eq__(self, __value) -> bool:
        assert isinstance(__value, SpecialOpsParas)
        return self.param_tys == __value.param_tys and self.val_name_strs == __value.val_name_strs and self.reset_op_idxs == __value.reset_op_idxs

    def __hash__(self) -> int:
        return hash((self.param_tys, self.val_name_strs, self.reset_op_idxs))

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}("{self.param_tys}", "{self.val_name_strs}", {self.reset_op_idxs})'

    def _get_n_func_name(self):
        op_num = len(self.param_tys)
        param_types_str = '-'.join(self.param_tys)
        val_name_strs_str = '-'.join(self.val_name_strs)
        reset_op_idxs_str = '-'.join([str(x) for x in self.reset_op_idxs])
        return f'R{op_num}_{param_types_str}_{val_name_strs_str}_{reset_op_idxs_str}'
