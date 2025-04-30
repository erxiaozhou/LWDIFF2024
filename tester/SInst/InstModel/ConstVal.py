import re
from .CVasSymVal import CVasSymVal

class ConstVal(CVasSymVal):
    def __init__(self, n) -> None:
        self.n = n

    def concrete_val(self, *arg, **kwds):
        return self.n
  
    def can_skip(self):
        return False
    def __repr__(self) -> str:
        return f'ConstVal({self.n})'
    def __hash__(self) -> int:
        return hash(('ConstVal', self.n))

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, ConstVal) and self.n == __value.n
    
    @staticmethod
    def is_valid_str(s):
        if s is None:
            return False
        if not isinstance(s, str):
            s = str(s)

        if s.isdigit():
            return True
        if _is_float(s):
            return True
        if s.startswith('-') and s[1:].isdigit():
            return True
        if s.lower() in set(['inf', 'nan', 'infinity']):
            return True
        can_be = True
        try:
            eval(s)
        except:
            can_be = False
        return can_be
    @classmethod
    def from_str(cls, s:str):
        if s.isdigit():
            return cls(int(s))
        if s.startswith('-') and s[1:].isdigit():
            return cls(-int(s[1:]))
        if s.lower() in set(['inf', 'infinity']):
            return cls(float('inf'))
        if s.lower() in set(['nan']):
            return cls(float('nan'))
        return cls(eval(s))
        raise ValueError(f"Invalid const val str {s}")
    

def _is_float(s: str) -> bool:
    float_regex = re.compile(r'^-?\d+(\.\d+)?([eE][-+]?\d+)?$')
    return bool(float_regex.match(s))
