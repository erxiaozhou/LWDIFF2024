import enum
from file_util import read_json


class InsertWrap(enum.Enum):
    NONE = enum.auto()
    BLOCK = enum.auto()
    LOOP = enum.auto()
    IF = enum.auto()
    ELSE = enum.auto()
    PREBLOCK = enum.auto()
    POSTBLOCK = enum.auto()
    PREPTEIF1 = enum.auto()  # TODO ，
    PREPTEIF0 = enum.auto()
    PRIF = enum.auto()
    PREUNREACHABLE = enum.auto()
    POSTUNREACHABLE = enum.auto()
    ANYOP = enum.auto()
    # TODO post if else  pre if else，
    # TODO  unreachble？

    @classmethod
    def from_str(cls, s):
        try:
            return getattr(cls, s)
        except AttributeError:
            raise NotImplementedError(f'{s}')


class InsertWraps:
    def __init__(self, wraps) -> None:
        _inner_wraps_list = []
        _inner_wraps_set = set()
        for candi in wraps:
            assert isinstance(candi, InsertWrap)
            if candi in _inner_wraps_set:
                continue
            _inner_wraps_list.append(candi)
            _inner_wraps_set.add(candi)

        self._inner_wraps_set = _inner_wraps_set
        self._inner_wraps_list = _inner_wraps_list

    def __contains__(self, __key: object) -> bool:
        return __key in self._inner_wraps_set

    def __getitem__(self, __key: int) -> InsertWrap:
        return self._inner_wraps_list[__key]

    def __len__(self) -> int:
        return len(self._inner_wraps_set)

    def as_set(self):
        return self._inner_wraps_set.copy()

    def as_list(self):
        return self._inner_wraps_list.copy()

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._inner_wraps_list})'

    @classmethod
    def from_json(cls, wraps_json):
        support_wraps = read_json(wraps_json)
        support_wraps = [InsertWrap.from_str(s) for s in support_wraps]
        return cls(support_wraps)
