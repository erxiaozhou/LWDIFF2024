from enum import Enum
from typing import Optional

from util.util import FailedParsingException
from SInst.InstModel.InstValRelation import InstValRelation

def to_unsigned(val, bits=32):
            return val & ((1 << bits) - 1)

class InstValRelationHelper:
    @staticmethod
    def compare(relation: InstValRelation, lval, rval) -> bool:
            
        if relation == InstValRelation.EQ:
            return lval == rval
        if relation == InstValRelation.NE:
            return lval != rval
        if relation == InstValRelation.GE:
            return lval >= rval
        if relation == InstValRelation.GT:
            return lval > rval
        if relation == InstValRelation.LE:
            return lval <= rval
        if relation == InstValRelation.LT:
            return lval < rval
        if relation == InstValRelation.UGE:
            return to_unsigned(lval) >= to_unsigned(rval)
        if relation == InstValRelation.UGT:
            return to_unsigned(lval) > to_unsigned(rval)
        if relation == InstValRelation.ULE:
            return to_unsigned(lval) <= to_unsigned(rval)
        if relation == InstValRelation.ULT:
            return to_unsigned(lval) < to_unsigned(rval)
        raise ValueError(f"Unsupported relation: {relation}")

    @staticmethod
    def is_valid_str(s: str) -> bool:
        valid_strs = {
            'eq', 'neq', 'ne', 'ge', 'gt', 'le', 'lt', 'ls', 'is',
            'uge', 'ugt', 'ule', 'ult'  # 
        }
        if s in valid_strs:
            return True
        if InstValRelationHelper.get_relation_str_from_sig_representation(s) is not None:
            return True
        return False


    @classmethod
    def from_str(cls, s: str) -> InstValRelation:
        if s == 'eq' or s == 'is':
            return InstValRelation.EQ
        if s in {'neq', 'ne'}:
            return InstValRelation.NE
        if s == 'ge':
            return InstValRelation.GE
        if s == 'gt':
            return InstValRelation.GT
        if s == 'le':
            return InstValRelation.LE
        if s in {'ls', 'lt'}:
            return InstValRelation.LT
        if s == 'uge':
            return InstValRelation.UGE
        if s == 'ugt':
            return InstValRelation.UGT
        if s == 'ule':
            return InstValRelation.ULE
        if s == 'ult':
            return InstValRelation.ULT
            
        repr_from_sig = cls.get_relation_str_from_sig_representation(s)
        if repr_from_sig is not None:
            return cls.from_str(repr_from_sig)
        raise FailedParsingException(f'{s} does not have a corresponding InstValRelation. Please consider representing the constraint in a different way')

    @staticmethod
    def neg(relation: InstValRelation) -> InstValRelation:
        mapping = {
            InstValRelation.EQ: InstValRelation.NE,
            InstValRelation.NE: InstValRelation.EQ,
            InstValRelation.GE: InstValRelation.LT,
            InstValRelation.LT: InstValRelation.GE,
            InstValRelation.GT: InstValRelation.LE,
            InstValRelation.LE: InstValRelation.GT,
            InstValRelation.UGE: InstValRelation.ULT,
            InstValRelation.ULT: InstValRelation.UGE,
            InstValRelation.UGT: InstValRelation.ULE,
            InstValRelation.ULE: InstValRelation.UGT
        }
        if relation in mapping:
            return mapping[relation]
        raise Exception(f'Not support neg for {relation}')

    @staticmethod
    def get_relation_str_from_sig_representation(s) -> Optional[str]:
        mapping = {
            '==': 'eq',
            '=': 'eq',
            '!=': 'neq',
            '>': 'gt',
            '<': 'lt',
            '>=': 'ge',
            '<=': 'le',
        }
        return mapping.get(s) 