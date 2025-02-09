from functools import lru_cache
from typing import Optional
from .possible_ops_detector import get_determined_possible_ops_core_with_prefix
from .possible_ops_detector import non_determined_inst_names

def get_possible_inst_ops_need_prefix(cur_stack: list[str], candidate_ops:Optional[set[str]]=None) -> set[str]:
    determined_possible_inst_ops = get_determined_possible_ops_core_with_prefix(tuple(cur_stack))
    if candidate_ops is not None:
        determined_possible_inst_ops = determined_possible_inst_ops.intersection(candidate_ops)
        non_determined_possible_inst_ops = _get_possible_non_determined_insts_names(frozenset(candidate_ops))
    else:
        non_determined_possible_inst_ops = non_determined_inst_names
    # 
    possible_inst_ops = determined_possible_inst_ops.union(non_determined_possible_inst_ops)
    return possible_inst_ops

@lru_cache(maxsize=1024)
def _get_possible_non_determined_insts_names(candidate_ops:frozenset)->set[str]:
    return non_determined_inst_names.intersection(candidate_ops)
