import random
from typing import Dict, List, Optional, Tuple, Union
from enum import Enum
from file_util import read_json
from .InstUtil.Inst import Inst
from .InstUtil.Inst import is_if_inst
# Inst.is_if_inst
class PosOffset(Enum):
    BEFORE = 0
    AFTER = 1
    def get_offset(self):
        if self == PosOffset.BEFORE:
            return 0
        elif self == PosOffset.AFTER:
            return 1
        raise NotImplementedError

class PosAnchor(Enum):
    BLOCK = 0
    LOOP = 1
    IF = 2
    ELSE = 3
    BR = 4
    BR_IF = 5
    BR_TABLE = 6
    RETURN = 7
    END = 8


def get_poss_from_insts(insts: List[Inst], pos:PosAnchor, preturn_idx=None)->List[int]:
    if pos == PosAnchor.RETURN:
        return [idx for idx, inst in enumerate(insts) if inst.opcode_text == 'return']
    if preturn_idx is not None:
        insts = insts[:preturn_idx]
    if pos == PosAnchor.BLOCK:
        return [idx for idx, inst in enumerate(insts) if inst.opcode_text == 'block']
    elif pos == PosAnchor.LOOP:
        return [idx for idx, inst in enumerate(insts) if inst.opcode_text == 'loop']
    elif pos == PosAnchor.IF:
        return [idx for idx, inst in enumerate(insts) if is_if_inst(inst)]
    elif pos == PosAnchor.ELSE:
        return [idx for idx, inst in enumerate(insts) if inst.opcode_text == 'else']
    elif pos == PosAnchor.BR:
        return [idx for idx, inst in enumerate(insts) if inst.opcode_text == 'br']
    elif pos == PosAnchor.BR_IF:
        return [idx for idx, inst in enumerate(insts) if inst.opcode_text == 'br_if']
    elif pos == PosAnchor.BR_TABLE:
        return [idx for idx, inst in enumerate(insts) if inst.opcode_text == 'br_table']
    elif pos == PosAnchor.END:
        return [idx for idx, inst in enumerate(insts) if inst.opcode_text == 'end']
    else:
        raise NotImplementedError


class PosCandi(Enum):
    FIRST = 0
    LAST = 1
    RANDOM = 2 
    DEEP = 3
    PR_RANDOM = 4
    PR_FINAL = 5
    AFTER_PRFIRST = 6
    NewFunc = 7
    ForceReturn = 8
    BBLOCK = (PosAnchor.BLOCK, PosOffset.BEFORE)
    ABLOCK = (PosAnchor.BLOCK, PosOffset.AFTER)
    BLOOP = (PosAnchor.LOOP, PosOffset.BEFORE)
    ALOOP = (PosAnchor.LOOP, PosOffset.AFTER)
    BIF = (PosAnchor.IF, PosOffset.BEFORE)
    AIF = (PosAnchor.IF, PosOffset.AFTER)
    BELSE = (PosAnchor.ELSE, PosOffset.BEFORE)
    AELSE = (PosAnchor.ELSE, PosOffset.AFTER)
    BBR = (PosAnchor.BR, PosOffset.BEFORE)
    ABR = (PosAnchor.BR, PosOffset.AFTER)
    BBR_IF = (PosAnchor.BR_IF, PosOffset.BEFORE)
    ABR_IF = (PosAnchor.BR_IF, PosOffset.AFTER)
    BBR_TABLE = (PosAnchor.BR_TABLE, PosOffset.BEFORE)
    ABR_TABLE = (PosAnchor.BR_TABLE, PosOffset.AFTER)
    BRETURN = (PosAnchor.RETURN, PosOffset.BEFORE)
    ARETURN = (PosAnchor.RETURN, PosOffset.AFTER)

    @classmethod
    def from_str(cls, s):
        try:
            return getattr(cls, s)
        except AttributeError:
            raise NotImplementedError(f'{s}')
    
    def is_insts_pos(self):
        return isinstance(self.value, int)
    def is_block_pos(self):
        return isinstance(self.value, tuple)


class PosCandis:
    def __init__(self, candis) -> None:
        _inner_poss_list = []
        _inner_poss_set = set()
        for candi in candis:
            assert isinstance(candi, PosCandi)
            if candi in _inner_poss_set:
                continue
            _inner_poss_list.append(candi)
            _inner_poss_set.add(candi)

        self._inner_poss_set = _inner_poss_set
        self._inner_poss_list = _inner_poss_list
        
    def __contains__(self, __key: object) -> bool:
        return __key in self._inner_poss_set
    
    def __getitem__(self, __key: int) -> PosCandi:
        return self._inner_poss_list[__key]

    def as_list(self):
        return self._inner_poss_list.copy()
    
    def __len__(self) -> int:
        return len(self._inner_poss_set)
    
    def as_set(self):
        return self._inner_poss_set.copy()
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self._inner_poss_list})'

    @classmethod
    def from_json(cls, json_path):
        return cls([PosCandi.from_str(s) for s in read_json(json_path)])


def get_support_pos_candis_from_insts(insts: List[Inst], preturn_idx:Optional[int]=None)->set[PosCandi]:
    support_candis = set([PosCandi.FIRST, PosCandi.LAST, PosCandi.RANDOM, PosCandi.NewFunc, PosCandi.ForceReturn])
    # support_candis = [PosCandi.FIRST, PosCandi.LAST, PosCandi.RANDOM]
    if preturn_idx == len(insts):
        preturn_idx = None
    if preturn_idx is not None:
        support_candis.update( [PosCandi.PR_RANDOM, PosCandi.PR_FINAL, PosCandi.AFTER_PRFIRST])
    # candi_insts = insts
    for inst_idx, inst in enumerate(insts):
        
        if inst.opcode_text == 'return':
            support_candis.update(  [PosCandi.BRETURN, PosCandi.ARETURN])
        if preturn_idx is not None and inst_idx >= preturn_idx:
            continue
        if inst.opcode_text == 'block':
            support_candis.update(  [PosCandi.BBLOCK, PosCandi.ABLOCK])
        elif inst.opcode_text == 'loop':
            support_candis.update(  [PosCandi.BLOOP, PosCandi.ALOOP])
        elif is_if_inst(inst):
            support_candis.update(  [PosCandi.BIF, PosCandi.AIF])
        elif inst.opcode_text == 'else':
            support_candis.update(  [PosCandi.BELSE, PosCandi.AELSE])
        elif inst.opcode_text == 'br':
            support_candis.update(  [PosCandi.BBR, PosCandi.ABR])
        elif inst.opcode_text == 'br_if':
            support_candis.update(  [PosCandi.BBR_IF, PosCandi.ABR_IF])
        elif inst.opcode_text == 'br_table':
            support_candis.update(  [PosCandi.BBR_TABLE, PosCandi.ABR_TABLE])
            if PosCandi.ForceReturn in support_candis:
                support_candis.remove(PosCandi.ForceReturn)
        elif inst.opcode_text == 'end':
            support_candis.update(  [PosCandi.DEEP])
    return support_candis

def _get_first_if_idx(insts: List[Inst])->int:
    for idx, inst in enumerate(insts):
        if is_if_inst(inst):
            return idx
    return len(insts)

def get_candi_pos(insts: List[Inst], pos_candi:PosCandi, preturn_idx:int)->Optional[int]:
    if pos_candi == PosCandi.FIRST:
        return 0
    elif pos_candi == PosCandi.LAST:
        # if insts[0].opcode_text in []
        return len(insts)
    elif pos_candi == PosCandi.RANDOM:
        return random.choice(range(len(insts)+1))
    elif pos_candi == PosCandi.DEEP:  # !  preturn
        depths = inst_depth_for_insert(insts)
        max_ = max(depths)
        if max_ == 0:
            return None
        idxs = [idx for idx, depth in enumerate(depths) if depth == max_]
        return random.choice(idxs)
    elif pos_candi == PosCandi.ForceReturn:
        return random.choice(range(min(preturn_idx, _get_first_if_idx(insts))+1))
    elif pos_candi == PosCandi.PR_RANDOM:
        if preturn_idx == len(insts):
            return None
        return random.choice(range(preturn_idx+1))
    elif pos_candi == PosCandi.PR_FINAL:
        if preturn_idx == len(insts):
            return None
        return preturn_idx
    elif pos_candi == PosCandi.AFTER_PRFIRST:
        if preturn_idx == len(insts):
            return None
        assert insts[preturn_idx].opcode_text in ['return', 'br', 'unreachable'], f'{insts[preturn_idx].opcode_text}'
        return preturn_idx+1
    if pos_candi.is_block_pos():
        ori_anchor_pos = get_poss_from_insts(insts, pos_candi.value[0], preturn_idx)
        offset = pos_candi.value[1].get_offset()
        anchor_poss = [pos+offset for pos in ori_anchor_pos]
        if len(anchor_poss) == 0:
            return None
        return random.choice(anchor_poss)


class RandomPosSelector:
    def __init__(self, support_candis=None) -> None:
        if support_candis is None:
            support_candis = list(PosCandi)
        self.support_candis = support_candis
        self.selection_counter = {}
        for pos_candi in PosCandi:
            self.selection_counter[pos_candi] = 0

    def random_select_pos(self, insts: List[Inst], preturn_idx, cur_candis=None) -> Tuple[int, PosCandi]:
        candis = list(self.support_candis)
        if cur_candis is not None:
            candis = [candi for candi in candis if candi in cur_candis]
        # from rare to frequent
        candis = sorted(candis, key=lambda x: self.selection_counter[x])
        assert self.selection_counter[candis[0]] <= self.selection_counter[candis[-1]]
        while True:
            # ! ，
            for pos_candi in candis:
            # pos_candi = random.choice(candis)
                pos = get_candi_pos(insts, pos_candi, preturn_idx)
                if pos is not None:
                    self.selection_counter[pos_candi] += 1
                    return pos, pos_candi
                else:
                    candis.remove(pos_candi)


def inst_depth_for_insert(insts: List[Inst]):
    
    inst_depth_log = []
    cur_depth = 0
    for inst in insts:
        if (inst.opcode_text in ('loop', 'block')) or is_if_inst(inst):
            inst_depth_log.append(cur_depth)
            cur_depth += 1
        elif inst.opcode_text == 'else':
            inst_depth_log.append(cur_depth)
        elif inst.opcode_text == 'end':
            inst_depth_log.append(cur_depth)
            cur_depth -= 1
        else:
            inst_depth_log.append(cur_depth)
        assert cur_depth >= 0
    assert cur_depth == 0

    inst_depth_log.append(0)
    return inst_depth_log

