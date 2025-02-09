from typing import List, Optional

from .OneInstReqUtil import InstTypeReqF
from ..Context import Context
from ..typeReq import merge_req, typeReq
from .Inst import Inst
import re
from ..funcTypeFactory import funcTypeFactory


select_p = re.compile(r'\(result\s*(\w+)\)')
def get_insts_ty_req(insts, context):
    # print('=========================================================')
    base_ty_req = typeReq.from_one_ty(
        funcTypeFactory.generate_one_func_type_default(param_type=[], result_type=[]))
    for inst in insts:
        cur_inst_req = get_inst_ty_req(inst, context)
        # print('inst, base_ty_req, cur_inst_req', inst, base_ty_req, cur_inst_req)
        base_ty_req = merge_req(base_ty_req, cur_inst_req)
    return base_ty_req

def get_inst_ty_req(inst: Inst, context_info: Optional[Context] = None, cur_params:Optional[List[str]]=None) -> Optional[typeReq]:
    InstTypeReqF()
    return InstTypeReqF.just_get_type_req(inst, context_info, cur_params)
