from enum import Enum, auto
from typing import Optional

from util.util import FailedParsingException


class InstValRelation(Enum):  # TODO 
    EQ = auto()
    NE = auto()
    LE = auto()
    LT = auto()
    GT = auto()
    GE = auto()

    def compare(self, lval, rval):
        if self == InstValRelation.EQ:
            return lval == rval
        if self == InstValRelation.NE:
            return lval != rval
        if self == InstValRelation.GE:
            return lval >= rval
        if self == InstValRelation.GT:
            return lval > rval
        if self == InstValRelation.LE:
            return lval <= rval
        if self == InstValRelation.LT:
            return lval < rval

    @staticmethod
    def is_valid_str(s:str):
        valid_strs = {'eq', 'neq', 'ne', 'ge', 'gt', 'le', 'lt', 'ls'}
        if s in valid_strs:
            return True
        if get_relation_str_from_sig_representation(s) is not None:
            return True
        return False

    def as_short_str(self):
        if self == InstValRelation.EQ:
            return 'eq'
        if self == InstValRelation.NE:
            return 'neq'
        if self == InstValRelation.GE:
            return 'ge'
        if self == InstValRelation.GT:
            return 'gt'
        if self == InstValRelation.LE:
            return 'le'
        if self == InstValRelation.LT:
            return 'lt'
        raise Exception(f'{self} does not have a short str')

    @classmethod
    def from_str(cls, s:str):
        if s == 'eq':
            return cls.EQ
        if s == 'neq':
            return cls.NE
        if s == 'ne':
            return cls.NE
        if s == 'ge':
            return cls.GE
        if s == 'gt':
            return cls.GT
        if s == 'le':
            return cls.LE
        if s == 'ls':
            return cls.LT
        if s == 'lt':
            return cls.LT
        repr_from_sig = get_relation_str_from_sig_representation(s)
        if repr_from_sig is not None:
            return cls.from_str(repr_from_sig)    
        raise FailedParsingException(f'{s} does not have a corresponding InstValRelation. Please consder represent the constraint in a different way')
    
    def neg(self):
        if self == InstValRelation.EQ:
            return InstValRelation.NE
        if self == InstValRelation.NE:
            return InstValRelation.EQ
        if self == InstValRelation.GE:
            return InstValRelation.LT
        if self == InstValRelation.LT:
            return InstValRelation.GE
        if self == InstValRelation.GT:
            return InstValRelation.LE
        if self == InstValRelation.LE:
            return InstValRelation.GT
        raise Exception(f'Not support neg for {self}')

def get_relation_str_from_sig_representation(s)->Optional[str]:
    if s == '==':
        return 'eq'
    if s == '=':
        return 'eq'
    if s == '!=':
        return 'neq'
    if s == '>':
        return 'gt'
    if s == '<':
        return 'lt'
    if s == '>=':
        return 'ge'
    if s == '<=':
        return 'le'
    return None
