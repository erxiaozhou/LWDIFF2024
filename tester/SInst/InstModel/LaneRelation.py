from enum import Enum, auto
from .InstValRelation import InstValRelation
from .InstValRelationHelper import InstValRelationHelper
from util.util import FailedParsingException


class AnyOrAll(Enum):
    ALL = auto()
    ANY = auto()

    def as_short_str(self):
        if self == AnyOrAll.ALL:
            return 'all'
        if self == AnyOrAll.ANY:
            return 'any'
        raise NotImplementedError(f'{self} does not have a short str')

    @classmethod
    def from_str(cls, s: str):
        if s == 'all':
            return cls.ALL
        if s == 'any':
            return cls.ANY
        raise FailedParsingException(
            f'{s} does not have a corresponding AnyOrAll')

    @staticmethod
    def is_valid_str(s: str):
        return s in {'all', 'any'}

    def neg(self):
        if self == AnyOrAll.ALL:
            return AnyOrAll.ANY
        if self == AnyOrAll.ANY:
            return AnyOrAll.ALL
        raise NotImplementedError(f'{self} does not have a neg')


class LaneRelation:
    def __init__(self, any_or_all: AnyOrAll, relation: InstValRelation) -> None:
        self.any_or_all = any_or_all
        self.relation = relation

    @staticmethod
    def is_valid_str(s: str):
        if '_' in s:
            splitted = s.split('_')
            if AnyOrAll.is_valid_str(splitted[0]) and InstValRelationHelper.is_valid_str(splitted[1]):
                return True
        return False

    @classmethod
    def from_str(cls, s: str):
        if not cls.is_valid_str(s):
            raise FailedParsingException(f'{s} is not a valid LaneRelation')
        else:
            splitted = s.split('_')
            any_or_all = AnyOrAll.from_str(splitted[0])
            relation = InstValRelationHelper.from_str(splitted[1])
            return cls(any_or_all, relation)

    def neg(self):
        neg_aa = self.any_or_all.neg()
        neg_rel = self.relation.neg()
        return LaneRelation(neg_aa, neg_rel)
