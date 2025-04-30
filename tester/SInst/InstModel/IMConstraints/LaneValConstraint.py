import re
from typing import Optional
from ..CombinedConstraint import CombinedAndConstraint, CombinedOrConstraint
from ..ExprConstraintFactory import ExprConstraintFactory

from ..InstValRelation import InstValRelation
from ..InstValRelationHelper import InstValRelationHelper
from ..PHEnv import PHEnv
from ..CPlaceHolder import is_default_imm_ph_name_or_op_ph_name
from ..Expr.LaneDesc import LaneDesc
from ..Expr import Expr
from ..Expr.LaneExpr import LaneExpr
from ..Expr.tool import is_expr_str
from ..Expr.tool import get_expr_from_str

from .ReleaseExistConstraintsUtil import release_exist_cs_from_expr
from ..LaneRelation import AnyOrAll, LaneRelation

from .IMConstraint import IMConstraint
from .IMConstraintResult import IMConstraintResult, get_imconstraint_result_practical


class LaneValConstraint(IMConstraint):
    def __init__(
        self, 
        v1:str,
        v2:str,
        relation: LaneRelation,
        v1_must_contains_lanes:bool=False,  # ,   v1 / v2 。
        v2_must_contains_lanes:bool=False  # ,   v1 / v2 。
    ):
        self.v1 = v1
        self.v2 = v2
        self.v1_must_contains_lanes = v1_must_contains_lanes
        self.v2_must_contains_lanes = v2_must_contains_lanes
        self.relation = relation
        
        assert is_expr_str(v1)
        assert is_expr_str(v2)

    def can_neg(self) -> bool:
        return True


    def as_neg_constraint(self):
        return LaneValConstraint(
            self.v1,
            self.v2, 
            self.relation.neg(),
            self.v1_must_contains_lanes,
            self.v2_must_contains_lanes
            )
    
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.v1}, {self.v2}, {self.relation})'

    @staticmethod
    def is_valid_dict(d: dict) -> bool:
        if len(d) == 3 and set(d.keys()) == {'v1', 'v2', 'relation'}:
            if LaneRelation.is_valid_str(d['relation']):
                if is_expr_str(d['v1']) and \
                    (not _is_possible_val_with_lanes(d['v1'])) and \
                    _is_possible_val_with_lanes(d['v2']):
                    return True
                elif is_expr_str(d['v2']) and \
                    (not _is_possible_val_with_lanes(d['v2'])) and \
                    _is_possible_val_with_lanes(d['v1']):
                    return True
            if InstValRelationHelper.is_valid_str(d['relation']):
                try_extract_v1_result = _extract_attr_from_lane_val_name(d['v1'])
                try_extract_v2_result = _extract_attr_from_lane_val_name(d['v2'])
                if try_extract_v1_result is not None and is_expr_str(d['v2']):
                    assert try_extract_v2_result is None
                    return True
                elif try_extract_v2_result is not None and is_expr_str(d['v1']):
                    assert try_extract_v1_result is None
                    return True
        return False

    
    @classmethod
    def from_dict(cls, d: dict):
        if LaneRelation.is_valid_str(d['relation']):
            lane_relation = LaneRelation.from_str(d['relation'])
            
            if is_expr_str(d['v1']) and \
                (not _is_possible_val_with_lanes(d['v1'])) and \
                _is_possible_val_with_lanes(d['v2']):
                v1 = d['v1']
                v2 = d['v2'].replace('.lanes', '')
                return cls(v1, v2, lane_relation, True, False)
            elif is_expr_str(d['v2']) and \
                (not _is_possible_val_with_lanes(d['v2'])) and \
                _is_possible_val_with_lanes(d['v1']):
                v1 = d['v1'].replace('.lanes', '')
                v2 = d['v2']
                return cls(v1, v2, lane_relation, False, True)
        elif InstValRelationHelper.is_valid_str(d['relation']):
            val_relation = InstValRelationHelper.from_str(d['relation'])
            try_extract_v1_result = _extract_attr_from_lane_val_name(d['v1'])
            try_extract_v2_result = _extract_attr_from_lane_val_name(d['v2'])
            if (try_extract_v1_result is not None) and is_expr_str(d['v2']):
                assert try_extract_v2_result is None
                op_imm_repr, all_or_any = try_extract_v1_result
                v1 = op_imm_repr.replace('.lanes', '')
                v2 = d['v2']
                return cls(v1, v2, LaneRelation(all_or_any, val_relation), True, False)
            elif (try_extract_v2_result is not None) and is_expr_str(d['v1']):
                assert try_extract_v1_result is None
                op_imm_repr, all_or_any = try_extract_v2_result
                v1 = d['v1']
                v2 = op_imm_repr.replace('.lanes', '')
                return cls(v1, v2, LaneRelation(all_or_any, val_relation), False, True)
            raise NotImplementedError()
        raise NotImplementedError()
    
    def release_both_constraints(self, ph_env:PHEnv,*args, **kwds)->list[IMConstraintResult]:
        val_1 = get_expr_from_str(self.v1, ph_env)
        val_2 = get_expr_from_str(self.v2, ph_env)
        ops_in_val1 = val_1.related_ops 
        imms_in_val1 = val_1.related_imms
        ops_in_val2 = val_2.related_ops
        imms_in_val2 = val_2.related_imms
        if self.v1_must_contains_lanes:
            for op in ops_in_val1:
                assert op.ty == 'v128'
            for imm in imms_in_val1:
                assert imm.ty == 'v128'
        if self.v2_must_contains_lanes:
            for op in ops_in_val2:
                assert op.ty == 'v128'
            for imm in imms_in_val2:
                assert imm.ty == 'v128'
        lane_num = ph_env.lane_num
        lane_type = ph_env.lane_type
        assert lane_num is not None
        assert lane_type is not None
            
        exist_val_cs, exist_func_cs = _get_expr_exist_cs(self, ph_env, [val_1, val_2])
        lane_val_cs = []
        for lane_idx in range(lane_num):
            lane_val = LaneExpr(
                LaneDesc(lane_idx, lane_type),
                val_1
                )
            c = ExprConstraintFactory.from_exprs_directly(
                lane_val, 
                val_2, 
                self.relation.relation
                )
            lane_val_cs.append(c)
        if self.relation.any_or_all == AnyOrAll.ALL:
            val_cs = lane_val_cs + exist_val_cs
        else:
            val_cs = [CombinedOrConstraint(lane_val_cs)]  + exist_val_cs
        result = get_imconstraint_result_practical(
            val_constraint=val_cs,
            func_constraint=exist_func_cs
        )
        
        return [result]


def _get_expr_exist_cs(self, ph_env:PHEnv, exprs:list[Expr], *args, **kwds):
    val_cs_ = []
    func_cs_ = []
    for expr in exprs:
        _val_cs, _func_cs = release_exist_cs_from_expr(expr, ph_env)
        val_cs_.extend(_val_cs)
        func_cs_.extend(_func_cs)
    return val_cs_, func_cs_


def _is_possible_val_with_lanes(s:str)->bool:
    if is_default_imm_ph_name_or_op_ph_name(s):
        return True
    if is_default_imm_ph_name_or_op_ph_name(s.replace('.lanes', '')):
        return True
    return False

_p1 = re.compile(r'((?:each)|(?:all)|(?:any)).* (?:(?:element)|(?:lane))s? .*((?:(?:op)|(?:imm))_\d+)')
def _extract_attr_from_lane_val_name(s:str)->Optional[tuple[str, AnyOrAll]]:
    s = s.lower().strip()
    r = _p1.findall(s)
    if r:
        any_all_repr, op_imm_repr = r[0]
        if any_all_repr in {'each', 'all'}:
            relation = AnyOrAll.ALL
        else:
            relation = AnyOrAll.ANY
        return op_imm_repr, relation
    return None