from typing import List, Sequence, Union

from .PlaceHolder import is_op_ty_desc_str
from .Constraint import Constraint
from WasmInfoCfg import val_type_strs


class indicatedType:pass

class OpTypeSolution:
    def __init__(self, phs:dict[int, set[Union[str, indicatedType]]]):
        self.op_idx2tycandis = phs
        self.func_requirement = None
        self.op_poss = set(phs.keys())

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.op_idx2tycandis})"

    @classmethod
    def from_phs(cls):
        raise NotImplementedError("from_phs not implemented")

class naiveOpTypeSolution(OpTypeSolution):
    def __init__(self, phs:dict[int, set[str]]):
        super().__init__(phs) # type: ignore

class emptyOpTySolution(naiveOpTypeSolution):
    def __init__(self):
        super().__init__(dict())

class NoConstraintOpTypeSolution(OpTypeSolution):
    def __init__(self):
        pass
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

def _get_expand_op_type_solution(op_poss:set[int], ty_solution:naiveOpTypeSolution)->naiveOpTypeSolution:
    op_idx2tycandis = ty_solution.op_idx2tycandis.copy()
    full_op_idx2tycandis = {}
    for op_pos in op_poss:
        if op_pos in op_idx2tycandis:
            full_op_idx2tycandis[op_pos] = op_idx2tycandis[op_pos].copy()
        else:
            full_op_idx2tycandis[op_pos] = val_type_strs.copy()
    return naiveOpTypeSolution(full_op_idx2tycandis)


def combine_type_solution(soluitons:Sequence[OpTypeSolution])->OpTypeSolution:
    # print('FDBFGHBGTDHNTDNTYJH len(soluitons)', len(soluitons))
    if len(soluitons) == 0:
        return emptyOpTySolution()
    soluitons = [s for s in soluitons if not isinstance(s, NoConstraintOpTypeSolution)]
    if all(isinstance(s, naiveOpTypeSolution) for s in soluitons):
        op_poss = set()
        for s in soluitons:
            op_poss.update(s.op_poss)
        # print('#@($JVDFO)AAAAAPPPP   op_poss', op_poss)
        # 
        new_d = {}
        for pos in op_poss:
            new_d[pos] = val_type_strs.copy()
        for solution in soluitons:
            assert isinstance(solution, naiveOpTypeSolution)
            full_solution = _get_expand_op_type_solution(op_poss, solution)
            for pos in op_poss:
                new_d[pos] = new_d[pos].intersection(full_solution.op_idx2tycandis[pos])
        return naiveOpTypeSolution(new_d)
        raise NotImplementedError("combine_type_solution not implemented")
    raise NotImplementedError("combine_type_solution not implemented")
    # if isinstance(s1, naiveOpTypeSolution) and isinstance(s2, naiveOpTypeSolution):
    
    #     keys = set(s1.phs.keys()) | set(s2.phs.keys())
    #     new_d = {}
    #     for k in keys:
    #         new_d[k] = s1.phs.get(k, set()).intersection(s2.phs.get(k, set()))
    #     return naiveOpTypeSolution(new_d)
    # raise NotImplementedError("combine_type_solution not implemented")


class TypeConstraint(Constraint):
    def __init__(self) -> None:
        raise NotImplementedError("TypeConstraint not implemented")

    def __repr__(self) -> str:
        raise NotImplementedError("TypeConstraint not implemented")

    def get_valid_candis(self)->List[OpTypeSolution]:
        raise NotImplementedError("get_valid_candis not implemented")

    def get_invalid_candis(self)->List[OpTypeSolution]:
        raise NotImplementedError("get_invalid_candis not implemented")

    def copy(self):
        raise NotImplementedError("copy not implemented")

    def can_neg(self) -> bool:
        raise NotImplementedError("can_neg not implemented")
    
    def as_neg_constraint(self):
        raise NotImplementedError("as_new_eq not implemented")


class TypeEqConstConstraint(TypeConstraint):
    def __init__(self, op_pos:int, ty, is_eq) -> None:
        self.op_pos = op_pos
        self.op_poss = {op_pos}
        self.ty = ty
        self.is_eq = is_eq
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.op_pos}, {self.ty}, {self.is_eq})"

    def __hash__(self) -> int:
        return hash((self.op_pos, self.ty, self.is_eq))
    def __eq__(self, o: object) -> bool:
        if not isinstance(o, TypeEqConstConstraint):
            return False
        return self.op_pos == o.op_pos and self.ty == o.ty and self.is_eq == o.is_eq

    @staticmethod
    def is_valid_dict(d:dict)->bool:
        if len(d) == 3:
            if 'v1' in d and is_op_ty_desc_str(d['v1']):
                if ('v2' in d) and isinstance(d['v2'], str) and (d['v2'] in val_type_strs):
                    if 'relation' in d and d['relation'] == 'eq':
                        return True
        return False

    def get_valid_candis(self) -> List[naiveOpTypeSolution]:
        d = {self.op_pos: {self.ty}}
        return [naiveOpTypeSolution(d)]

    @classmethod
    def from_d(cls, d:dict):
        assert cls.is_valid_dict(d)
        op_pos = _get_op_pos_from_op_ty_desc_str(d['v1'])
        return cls(op_pos, d['v2'], True)
    
    def copy(self):
        return TypeEqConstConstraint(self.op_pos, self.ty, self.is_eq)

    def can_neg(self):
        return True
    
    def as_neg_constraint(self):
        type_set = val_type_strs - {self.ty}
        return TypeScopeConstraint(self.op_pos, type_set)


def _is_imm_ty_desc_str(s:str)->bool:
    if s.startswith('imm_') and s.endswith('.type'):
        return True
    return False


def _get_op_pos_from_op_ty_desc_str(s:str)->int:
    return int(s[3:-5])


class OpTypeEqOpTypeConstraint(TypeConstraint):
    def __init__(self, op_pos1, op_pos2, is_eq) -> None:
        self.op_pos1 = op_pos1
        self.op_pos2 = op_pos2
        self.op_poss = {op_pos1, op_pos2}
        self.is_eq = is_eq
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.op_pos1}, {self.op_pos2}, {self.is_eq})"
    def get_valid_candis(self) -> List[naiveOpTypeSolution]:
        if self.is_eq:
            solutions = []
            for ty in val_type_strs:
                d = {self.op_pos1: {ty}, self.op_pos2: {ty}}
                solutions.append(naiveOpTypeSolution(d))
            return solutions
        raise NotImplementedError("get_valid_candis not implemented")
    def can_neg(self):
        return True
    def as_neg_constraint(self):
        return OpTypeEqOpTypeConstraint(self.op_pos1, self.op_pos2, not self.is_eq)

    @staticmethod
    def is_valid_dict(d:dict)->bool:
        if len(d) == 3:
            if 'v1' in d and isinstance(d['v1'], str) and is_op_ty_desc_str(d['v1']):
                if 'v2' in d and isinstance(d['v2'], str) and is_op_ty_desc_str(d['v2']):
                    if 'relation' in d and d['relation'] == 'eq':
                        return True
        return False

    @classmethod
    def from_d(cls, d:dict):
        assert cls.is_valid_dict(d)
        op_pos1 = _get_op_pos_from_op_ty_desc_str(d['v1'])
        op_pos2 = _get_op_pos_from_op_ty_desc_str(d['v2'])
        return cls(op_pos1, op_pos2, True)


class TypeScopeConstraint(TypeConstraint):
    def __init__(self, op_pos, type_set:set) -> None:
        self.op_pos = op_pos
        self.op_poss = {op_pos}
        self.type_set = type_set.copy()

    def all_candis(self):
        raise NotImplementedError("all_candis not implemented")
        # return [TypeConstraint(self.op_pos, ty, True) for ty in self.type_set]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.op_pos}, {self.type_set})"
    
    @staticmethod
    def is_valid_dict(d:dict)->bool:
        # eq any pattern
        if _d_match_eq_any_pattern(d):
            return True
        if _d_match_eq_ty_candis(d):
            return True
        return False
    
    def get_valid_candis(self) -> List[naiveOpTypeSolution]:
        solutions = []
        for ty in self.type_set:
            d = {self.op_pos: {ty}}
            solutions.append(naiveOpTypeSolution(d))
        return solutions
    
    @classmethod
    def from_d(cls, d:dict):
        assert cls.is_valid_dict(d)
        if _d_match_eq_any_pattern(d):
            op_pos = _get_op_pos_from_op_ty_desc_str(d['v1'])
            return cls(op_pos, val_type_strs.copy())
        if _d_match_eq_ty_candis(d):
            op_pos = _get_op_pos_from_op_ty_desc_str(d['v1'])
            return cls(op_pos, set(d['v2']))
        raise NotImplementedError("from_d not implemented")

    def can_neg(self):
        if self.type_set == val_type_strs:
            return False
        return True
    def as_neg_constraint(self):
        return val_type_strs - self.type_set


def _d_match_eq_any_pattern(d):
    if len(d) == 3:
        if 'v1' in d and is_op_ty_desc_str(d['v1']):
            if 'v2' in d and  d['v2'] == 'any':
                if 'relation' in d and d['relation'] == 'eq':
                    return True
    return False


def _d_match_eq_ty_candis(d:dict)->bool:
    if len(d) == 3:
        if 'v1' in d and is_op_ty_desc_str(d['v1']):
            if ('v2' in d) and isinstance(d['v2'], list):
                if set(d['v2']).issubset(val_type_strs):
                    if 'relation' in d and d['relation'] == 'in':
                        return True
    return False

class immTypeEqConstraint(TypeConstraint):
    def __init__(self):
        # TODO do nothing now
        pass
        self.op_poss = set()
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
    def get_valid_candis(self) -> List[naiveOpTypeSolution]:
        return [NoConstraintOpTypeSolution()]
    def can_neg(self):
        return False

    @staticmethod
    def is_valid_dict(d:dict)->bool:
        if len(d) == 3:
            if 'v1' in d and _is_imm_ty_desc_str(d['v1']):
                if 'v2' in d and  d['v2'] in (val_type_strs | {'table_idx', 'global_idx'}):
                    if 'relation' in d and d['relation'] == 'eq':
                        return True
        return False

    @classmethod
    def from_d(cls, d:dict):
        assert cls.is_valid_dict(d)
        return cls()
