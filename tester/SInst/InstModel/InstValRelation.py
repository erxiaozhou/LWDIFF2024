from enum import Enum, auto


class InstValRelation(Enum):  
    EQ = auto()
    NE = auto()
    LE = auto()
    LT = auto()
    GT = auto()
    GE = auto()
    
    ULE = auto()
    ULT = auto()
    UGT = auto()
    UGE = auto()

    
    def neg(self):
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
        if self in mapping:
            return mapping[self]
        raise Exception(f'Not support neg for {self}')

    def is_greater(self)->bool:
        if self in {
            InstValRelation.GT,
            InstValRelation.UGT,
        }:
            return True
        return False
    
    def is_less(self)->bool:
        if self in {
            InstValRelation.LT,
            InstValRelation.ULT,
        }:
            return True
        return False
    
    def reverse(self)->'InstValRelation':
        if self == InstValRelation.EQ:
            return InstValRelation.EQ
        elif self == InstValRelation.NE:
            return InstValRelation.NE
        elif self == InstValRelation.GE:
            return InstValRelation.LE
        elif self == InstValRelation.GT:
            return InstValRelation.LT
        elif self == InstValRelation.LE:
            return InstValRelation.GE
        elif self == InstValRelation.LT:
            return InstValRelation.GT
        elif self == InstValRelation.UGE:
            return InstValRelation.ULT
        elif self == InstValRelation.ULE:
            return InstValRelation.UGT
        elif self == InstValRelation.UGT:
            return InstValRelation.ULE
        elif self == InstValRelation.UGE:
            return InstValRelation.ULT
        else:
            raise Exception(f'Not support reverse for {self}')
