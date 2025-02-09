from typing import Callable, List, Optional
from .Constraint import Constraint


def always_true(*args, **kwds):
    return True

def do_nothing(*args, **kwds):
    pass




def re_dup_funcs(funcs:List[Callable]):
    to_store_funcs = []
    for f in funcs:
        if f in to_store_funcs:
            continue
        if f is do_nothing:
            continue
        if f is always_true:
            continue
        
        # assert not isinstance(f, AndFuncChain)
        to_store_funcs.append(f)
    return to_store_funcs

class FuncChain:
    def __init__(self, funcs:List[Callable]):
        self.funcs = re_dup_funcs(funcs)

    def __len__(self):
        return len(self.funcs)

    def __call__(self, *args, **kwds):
        raise NotImplementedError

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.funcs})'

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return hash(self) == hash(other)

    def __hash__(self) -> int:
        return hash(tuple(self.funcs))

    def append(self, func:Callable):
        if func not in self.funcs:
            self.funcs.append(func)
    def extend(self, funcs:List[Callable]):
        for func in funcs:
            self.append(func)

    def __getitem__(self, idx):
        return self.funcs[idx]

    def __iter__(self):
        return iter(self.funcs)

    @property
    def all_raw_funcs(self):
        funcs = []
        for func in self.funcs:
            if isinstance(func, FuncChain):
                # funcs.extend(func.all_raw_funcs)
                for f in func.all_raw_funcs:
                    if f in funcs:
                        continue
                    funcs.append(f)
            else:
                funcs.append(func)
        return funcs


class BoolFuncChain(FuncChain):pass


class AndFuncChain(BoolFuncChain):
    def __init__(self, funcs: List[Callable]):
        if len(funcs) == 0:
            funcs = [always_true]
        super().__init__(funcs)
        
    def __call__(self, *args, **kwds):
        for _func in self.funcs:
            if not _func(*args, **kwds):
                return False
        return True
    
    @property
    def raw_funcs(self):
        funcs = []
        for func in self.funcs:
            if isinstance(func, AndFuncChain):
                funcs.extend(func.raw_funcs)
            else:
                funcs.append(func)
        return funcs

    def append(self, func:Callable):
        if func not in self.funcs:
            if isinstance(func, AndFuncChain):
                for f in func.raw_funcs:
                    if f not in self.funcs:
                        self.funcs.append(f)
            else:
                self.funcs.append(func)

    # def 

    def __hash__(self) -> int:
        return hash((*self.funcs, 'and'))


class OrFuncChain(BoolFuncChain):
    # def
    def __call__(self, *args, **kwds):
        for _func in self.funcs:
            if _func(*args, **kwds):
                return True
        return False

    def __hash__(self) -> int:
        return hash((*self.funcs, 'or'))

    @property
    def raw_funcs(self):
        funcs = []
        for func in self.funcs:
            if isinstance(func, OrFuncChain):
                funcs.extend(func.raw_funcs)
            else:
                funcs.append(func)
        return funcs

    def append(self, func:Callable):
        if func not in self.funcs:
            if isinstance(func, OrFuncChain):
                for f in func.raw_funcs:
                    if f not in self.funcs:
                        self.funcs.append(f)
            else:
                self.funcs.append(func)


def get_or_func(funcs):
    if any([f is always_true for f in funcs]):
        return always_true
    if len(funcs) == 0:
        return always_true
    return OrFuncChain(funcs)


class PreFuncChain(FuncChain):
    def __call__(self, *args, **kwds):
        # assert len(self.funcs) == 0
        for _func in self.funcs:
            # assert 0
            _func(*args, **kwds)

    @property
    def raw_funcs(self):
        funcs = []
        for func in self.funcs:
            if isinstance(func, PreFuncChain):
                funcs.extend(func.raw_funcs)
            else:
                funcs.append(func)
        return funcs

    def append(self, func:Callable):
        # assert 0
        if func not in self.funcs:
            if isinstance(func, PreFuncChain):
                for f in func.raw_funcs:
                    if f not in self.funcs:
                        self.funcs.append(f)
            else:
                # assert 0
                self.funcs.append(func)

    def __hash__(self) -> int:
        return hash((*self.funcs, 'pre'))
    
class SelectFuncConstraint(Constraint):
    def __init__(self, can_neg_=False, can_apply_func:Optional[FuncChain]=None, pre_func:Optional[FuncChain]=None):
        self.can_neg_ = can_neg_
        if can_apply_func is None:
            can_apply_funcs = AndFuncChain([])
        else:
            assert isinstance(can_apply_func, BoolFuncChain)
            can_apply_funcs = can_apply_func
        if pre_func is None:
            pre_funcs = PreFuncChain([])
        else:
            assert isinstance(pre_func, PreFuncChain)
            pre_funcs = pre_func
            
        self.can_apply_func:BoolFuncChain = can_apply_funcs
        self.pre_func:PreFuncChain = pre_funcs
        # assert len(self.pre_func) == 0
        
    def __eq__(self, other):
        return self.can_apply_func == other.can_apply_func and self.pre_func == other.pre_func

    def __hash__(self):
        return hash((self.can_apply_func, self.pre_func))

    @classmethod
    def from_funcs(cls,  can_apply_funcs:List[Callable], pre_funcs:List[Callable], can_neg_=False):
        target_apply_funcs = []
        target_pre_funcs = []
        for can_apply_func in can_apply_funcs:
            if isinstance(can_apply_func, AndFuncChain):
                target_apply_funcs.extend(can_apply_func.raw_funcs)
            else:
                target_apply_funcs.append(can_apply_func)
        for pre_func in pre_funcs:
            if isinstance(pre_func, PreFuncChain):
                target_pre_funcs.extend(pre_func.raw_funcs)
            else:
                target_pre_funcs.append(pre_func)
        can_apply_func = AndFuncChain(target_apply_funcs)
        pre_func = PreFuncChain(target_pre_funcs)
        return cls(can_neg_, can_apply_func, pre_func)

    @classmethod
    def from_one_func(cls, can_apply_func:Callable, pre_func:Callable, can_neg_=False):
        can_apply_func = AndFuncChain([can_apply_func])
        pre_func = PreFuncChain([pre_func])
        return cls(can_neg_, can_apply_func, pre_func)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.can_apply_func}, {self.pre_func})'

    def can_neg(self) -> bool:
        return False


class SelectFuncConstraintFactoryAnd:
    _hash2func:dict[int, SelectFuncConstraint] = {}
    @staticmethod
    def generate_a_combined_func_from_SelectFuncConstraints(sfuncs:List[SelectFuncConstraint]):
        can_apply_funcs = AndFuncChain([])
        pre_funcs = PreFuncChain([])
        for sfunc in sfuncs:
            can_apply_funcs.extend(sfunc.can_apply_func.funcs)
            pre_funcs.extend(sfunc.pre_func.funcs)
        # print('can_apply_funcs', can_apply_funcs, len(sfuncs[0].can_apply_func.funcs))
        # if len(sfuncs) >0:
        #     print('|||||', sfuncs)
        return SelectFuncConstraint(can_apply_func=can_apply_funcs,pre_func=pre_funcs)

    @staticmethod
    def generate_a_combined_func_from_two_func_list(can_apply_funcs:List[Callable], pre_funcs:List[Callable]):
        return SelectFuncConstraint.from_funcs(can_apply_funcs, pre_funcs)
        
class SelectFuncConstraintFactoryOr:
    _hash2func:dict[int, SelectFuncConstraint] = {}
    @staticmethod
    def generate_a_combined_func_from_SelectFuncConstraints(sfuncs:List[SelectFuncConstraint]):
        # assert len(sfuncs) == 2
        can_apply_funcs = []
        pre_funcs = []
        for sfunc in sfuncs:
            can_apply_funcs.append(sfunc.can_apply_func)
            pre_funcs.append(sfunc.pre_func)
        can_apply_func = OrFuncChain(can_apply_funcs)
        pre_func = PreFuncChain(pre_funcs)
        return SelectFuncConstraint(can_apply_func=can_apply_func, pre_func=pre_func)
