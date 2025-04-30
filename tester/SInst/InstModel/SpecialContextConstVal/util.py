from enum import Enum, auto
from typing import Optional

from WasmInfoCfg import ContextValAttr
from extract_block_mutator.SpecialConst import SpecialModuleConst, SpecialModuleConstGetter, SpecialContextOneDefConst

from extract_block_mutator.Context import Context

class OneContextValAttr(Enum):
    size = auto()
    max = auto()
    val_type = auto()
    data_seg_attr = auto()
    elem_seg_attr = auto()
    mutable = auto()

    def can_get_scope(self):
        return self in {
            OneContextValAttr.val_type,
            OneContextValAttr.data_seg_attr,
            OneContextValAttr.elem_seg_attr,
            OneContextValAttr.mutable
        }

one_def_attr2size_val = {
        (ContextValAttr.OneMem, OneContextValAttr.size): SpecialContextOneDefConst.OneMemCurSize,
        (ContextValAttr.OneMem, OneContextValAttr.max): SpecialContextOneDefConst.OneMemMax,
        (ContextValAttr.OneTable, OneContextValAttr.size): SpecialContextOneDefConst.OneTableLen,
        (ContextValAttr.OneElemSeg, OneContextValAttr.size): SpecialContextOneDefConst.OneElemSegLen,
        (ContextValAttr.OneDataSeg, OneContextValAttr.size): SpecialContextOneDefConst.OneDataSegLen,
    }


def get_concrete_val_for_one_def_attr(
    context_val_type:ContextValAttr,
    val_attr:OneContextValAttr,
    idx_repr:Optional[str],
    context:Context
    ):
    assert idx_repr is not None
    assert (context_val_type, val_attr) in one_def_attr2size_val
    idx = int(idx_repr)
    return one_def_attr2size_val[(context_val_type, val_attr)].get_concrete_value(context=context, idx=idx)


sec_attr2size_val = {
        ContextValAttr.Locals: SpecialModuleConst.LocalNum,
        ContextValAttr.Globals: SpecialModuleConst.CurGlobalNum,
        ContextValAttr.MemSec: SpecialModuleConst.CurMemNum,
        ContextValAttr.Funcs: SpecialModuleConst.CurFuncNum,
        ContextValAttr.TableSec: SpecialModuleConst.CurTableNum,
        ContextValAttr.DataSec: SpecialModuleConst.CurDataSegNum,
        ContextValAttr.ElemSec: SpecialModuleConst.CurElemSegNum,
    }


def get_sec_size_concrete_val(
    context_val_type: ContextValAttr,
    context: Context
):
    assert context_val_type in sec_attr2size_val
    module_const = sec_attr2size_val[context_val_type]
    return SpecialModuleConstGetter(module_const).get_concrete_value(loader=context)
