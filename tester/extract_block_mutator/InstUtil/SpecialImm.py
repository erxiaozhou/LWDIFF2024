class SpecialImm:
    pass


class SpecialGlobalIdx(SpecialImm):
    def __init__(self, anno) -> None:
        pass


class UnconstrainedGlobalIdx(SpecialGlobalIdx):
    def __init__(self, type_) -> None:
        # assert 0
        assert isinstance(type_, str)
        self.type_ = type_

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, self.__class__) and self.type_ == __value.type_

    def __hash__(self) -> int:
        return hash(self.type_)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.type_})'


# ======================================================
predefined_funca_names = ['can_f32', 'can_f64', 'can_f32x4', 'can_f64x2']


class predefinedFuncIdx(SpecialImm):
    def __init__(self, func_name) -> None:
        assert func_name in predefined_funca_names
        self.func_name = func_name

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, self.__class__) and self.func_name == __value.func_name

    def __hash__(self) -> int:
        return hash(self.func_name)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.func_name})'
