from enum import Enum, auto
from typing import Any, List, Optional, Set, Tuple, Union

from .SpecialContextConstVal import SpecialContextConstVal, SpecialContextOneDef, SpecialContextOneDefSize, SpecialContextOneSecSize

from ..Exceptions import RequireContextException, InvalidTextPatternException
from WasmInfoCfg import ContextSection2One, ContextValAttr
from WasmInfoCfg import ContextOne2Section
import re
from ..SymbolValue import SymbolValue
from z3 import BitVec, And, Or
from ..PHEnv import PHEnv
from extract_block_mutator.Context import Context
from .util import OneContextValAttr
from .SpecialContextConstVal import SpecialContextScopeVal
from .SpecialContextConstVal import sccv_is_scope

class SpecialContextConstValFactory:
    @staticmethod
    def from_str(s: str) -> SpecialContextConstVal:
        s = s.lower()
        val_attr = _determine_val_attr(s)
        context_val_type = _determine_type(s)
        idx_repr = _determine_idx_repr(s)
        if sccv_is_scope(val_attr, context_val_type):
            return SpecialContextScopeVal(context_val_type, idx_repr, val_attr)
        if context_val_type in ContextOne2Section:
            if val_attr == OneContextValAttr.size or val_attr == OneContextValAttr.max:
                return SpecialContextOneDefSize(context_val_type, idx_repr, val_attr)
            else:
                return SpecialContextOneDef(context_val_type, idx_repr, val_attr)
        elif context_val_type in ContextSection2One and val_attr == OneContextValAttr.size:
            return SpecialContextOneSecSize(context_val_type, idx_repr, val_attr)
        assert 0  # just see ; what the case is  ;; remove this line during testing
        return SpecialContextConstVal(context_val_type, idx_repr, val_attr)

    @staticmethod
    def is_valid_str(s: str) -> bool:
        result = True
        if not isinstance(s, str):
            result = False
        else:
            try:
                SpecialContextConstValFactory.from_str(s)
            except InvalidTextPatternException:
                result = False
        return result

    @staticmethod
    def is_valid_scope_str(s: str) -> bool:
        result = True
        if not isinstance(s, str):
            result = False
        else:
            try:
                val = SpecialContextConstValFactory.from_str(s)
                if not isinstance(val, SpecialContextScopeVal):
                    result = False
            except InvalidTextPatternException:
                result = False
        return result
                

def _determine_val_attr(s: str) -> Optional[OneContextValAttr]:
    suffix_to_attr = {
        '.length': OneContextValAttr.size,
        '.max': OneContextValAttr.max,
        '.maximum': OneContextValAttr.max,
        '.type': OneContextValAttr.val_type,
        '.mut': OneContextValAttr.mutable,
    }
    s = s.lower()
    for suffix, attr in suffix_to_attr.items():
        if s.endswith(suffix):
            return attr
    
    if s.endswith(']'):
        return None
    if s.count('.') == 1:
        return None
    raise InvalidTextPatternException(f'_determine_val_attr not implemented: {s}')




def _determine_type(s: str) -> ContextValAttr:
    prefix_to_type = {
        'context.locals': ContextValAttr.Locals,
        'context.globals': ContextValAttr.Globals,
        'context.mem': ContextValAttr.MemSec,
        'context.mems': ContextValAttr.MemSec,
        'context.data': ContextValAttr.DataSec,
        'context.datas': ContextValAttr.DataSec,
        'context.elem': ContextValAttr.ElemSec,
        'context.elems': ContextValAttr.ElemSec,
        'context.elemsegs': ContextValAttr.ElemSec,
        'context.elements': ContextValAttr.ElemSec,
        'context.funcs': ContextValAttr.Funcs,
        'context.cfuncs': ContextValAttr.Funcs,
        'context.func': ContextValAttr.Funcs,
        'context.tables': ContextValAttr.TableSec,
        'context.table': ContextValAttr.TableSec,
        'context.refs': ContextValAttr.FuncRefs,
        'context.crefs': ContextValAttr.FuncRefs,
    }
    
    s = s.strip().lower()
    to_strip_suffix = set(['.length', '.max', '.type', '.mut'])
    for suffix in to_strip_suffix:
        if s.endswith(suffix):
            s = s[:-len(suffix)]
    if s.startswith('c.'):
        s = s.replace('c.', 'context.')
    if s.count('context.') != 1:
        raise InvalidTextPatternException(f'_determine_type not implemented: {s}')
    for prefix, val_type in prefix_to_type.items():
        if s.startswith(prefix):
            if '[' not in s:
                return val_type
            elif s.endswith(']'):  # this is a constraint for validation the string
                if val_type in ContextSection2One:
                    return ContextSection2One[val_type]
                elif val_type == ContextValAttr.FuncRefs:
                    return ContextValAttr.OneFuncRef
           
    raise InvalidTextPatternException(f'_determine_type not implemented: {s}')



def _determine_idx_repr(s: str) -> Optional[str]:
    match = re.search(r'\[(.*?)\]', s)
    if match:
        return match.group(1)
    return None
