
from collections import Counter
from copy import deepcopy
from functools import lru_cache
from logging import Logger
from random import choice
from typing import List, Optional, Tuple
from SInst.InstModel.Exceptions import UNSolveException
from SInst.RuleInst.determine_insts_for_rulev2 import generate_insts_for_rulev2_byop
from SInst.RuleInst.RuleV2 import RuleV2
from SInst.RuleInst.GptInst2GRule import GptInstKM
from file_util import get_time_string
from ..inst_pose_selector import PosCandi, PosCandis, RandomPosSelector, get_candi_pos
from ..funcType import funcType
from ..InstGeneration.InstFactory import InstFactory
from ..InstUtil.Inst import Inst
from ..Context import Context
from .SpecialInstInputFactoryUtil import InsertMethod, wrap_generated_insts
from .RuleFactoryCounter import RuleFactoryCounter
from .InsertWrap import InsertWrap, InsertWraps
from ..funcTypeFactory import funcTypeFactory
from SInst.InstModel.SelectFuncConstraintTransfer import transfer_func_constraint

 
class RuleV2InputFactory:
    def __init__(self, support_ops=None, support_pos_candis:Optional[PosCandis]=None, support_wraps:Optional[InsertWraps]=None) -> None:
        self.inst_factory = InstFactory()
        self.support_insert_mtds = [InsertMethod.BYOP]
        self.selection_times = 0
        # 
        if support_pos_candis is None:
            support_pos_candis = PosCandis([PosCandi.RANDOM])
        # assert support_pos_candis is not None
        # assert support_wraps is not None
        if support_wraps is None:
            support_wraps = InsertWraps([InsertWrap.NONE])
        # 
        print('support_pos_candis ||', support_pos_candis)
        print('support_wraps ||', support_wraps)
        self.support_pos_candis = support_pos_candis
        self.support_wraps = support_wraps

        gpt_rules = GptInstKM(support_ops)
        # self.rules = deepcopy(gpt_rules.rules)
        # # op
        # for _rule in self.rules:
        #     if _rule.illegal_type:
        #         raise ValueError(f'context_condition_func is None: op:{_rule.op}, rule:{_rule} ;; {len(self.rules)} ;; {_rule.illegal_type}')
        #     if _rule.context_condition_func is None:
        #         raise ValueError(f'context_condition_func is None: op:{_rule.op}, rule:{_rule} ;; {len(self.rules)} ;; {_rule.illegal_type}')
        #     # assert _rule.context_condition_func is not None
        #     # print('RuleV2InputFactory   _rule.context_condition_func', _rule.op, _rule.context_condition_func)
        #     _rule.context_condition_func = transfer_func_constraint(_rule.context_condition_func)

        
        self.pos_selector = RandomPosSelector(support_candis=self.support_pos_candis)
        self.considered_op2rules = {}
        self.considered_rules = []
        self.rule_idx2op_and_group_idx = {}
        self.op_and_group_idx2rule_rule_idx = {}
        
        if support_ops is None:
            support_ops = gpt_rules.support_ops
        self.support_ops = list(support_ops)
        for op in self.support_ops:
            self.considered_op2rules[op] = []
            rules = gpt_rules.get_rules_by_op(op)
            # self.considered_op2rules[_r.raw_op_name] = []
            for _r in rules:
                assert op == _r.raw_op_name
                _r.context_condition_func = transfer_func_constraint(_r.context_condition_func)
                self.considered_op2rules[_r.raw_op_name].append(_r)
        # print('RuleV2InputFactory   self.support_ops', self.support_ops)
        # for _r in self.rules:
        #     self.considered_op2rules[_r.raw_op_name].append(_r)
        self._init_rules_reliated_info()
        # 
        # for _r in self.considered_op2rules['i32.load']:
        #     print(f'VVVZK555 {get_time_string()} {_r.op} rule: {_r} ||| {_r.context_condition_func} ||| {id(_r)}')
        # 
 
        self.support_op_num = len(self.support_ops)
        self.selection_counter = RuleFactoryCounter(self.support_ops, self.support_pos_candis, self.support_wraps, len(self.considered_rules))
        # rule_id2(op, rule_idx in op group)
        self.pos_from_least_to_most = None
        self.rule_idx_from_least_to_most = None

    def _init_rules_reliated_info(self):
        _added_rule_num = 0
        for rules in self.considered_op2rules.values():
            for idx, rule in enumerate(rules):
                self.rule_idx2op_and_group_idx[_added_rule_num] = (rule.raw_op_name, idx)
                self.op_and_group_idx2rule_rule_idx[(rule.raw_op_name, idx)] = _added_rule_num
                _added_rule_num += 1
                self.considered_rules.append(rule)
        # funcid2rule_ids
        can_apply_funcs, func_idx2rule_idxs = get_func_idx2rule_idxs(self.considered_rules)
        self.can_apply_funcs = can_apply_funcs
        self.func_idx2rule_idxs = func_idx2rule_idxs
        self.func_idxs_pass_times = Counter()
        # assert 0, print('len(self.can_apply_funcs)', len(self.can_apply_funcs))
        
    def _get_can_apply_func_idxs(self, context:Context, insts:List[Inst]):
        func_idxs = []
        for _func_idx, _func in enumerate(self.can_apply_funcs):
            # print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^, len(self.can_apply_funcs)', len(self.can_apply_funcs))
            # if _func(context, insts):
                # print('++++++++', '_func_idx, _func', _func_idx, _func)
            if _func(context, insts):
                func_idxs.append(_func_idx)
        #
        # print('ZZZZZZZZZZZZZZZZZZZ',func_idxs)
        self.func_idxs_pass_times.update(func_idxs) 
        return tuple(func_idxs)
    
    def get_can_apply_rule_idxs(self, context:Context, insts:List[Inst]):
        can_apply_func_idxs = self._get_can_apply_func_idxs(context, insts)
        func_idxs_from_least_to_most = [x[0] for x in self.func_idxs_pass_times.most_common()][::-1]
        can_apply_func_idxs = tuple(x for x in func_idxs_from_least_to_most if x in can_apply_func_idxs)
        can_apply_rule_idxs = get_can_apply_rule_idxs(can_apply_func_idxs, self.func_idx2rule_idxs)
        return can_apply_rule_idxs

    def op_count_from_least_to_most(self):
        self.rule_idx_counter_list = [x[0] for x in self.selection_counter.rule_idx_counter.most_common()][::-1]

    def select_rule(self, context:Context, insts:List[Inst],
                          ori_supported_pos_candis:set[PosCandi],
                          can_apply_rule_idxs=None, logger=None)->tuple[RuleV2, int]:
        '''
        ：
        1.  rule_idx 》  rule_idx 》 
        2.  rule_idx 》 
        '''
        if can_apply_rule_idxs is None:
            can_apply_rule_idxs = self.get_can_apply_rule_idxs(context, insts)
        # assert len(can_apply_rule_idxs) > 0
        if len(can_apply_rule_idxs) == 0:
            apply_func_reprs = [str(f)+"\n" for f in self.can_apply_funcs]
            apply_func_repr = ''.join(apply_func_reprs)
            raise ValueError(f'len(can_apply_rule_idxs) == 0: {apply_func_repr}')
        if self.selection_counter.unselected_rule_idxs:
            
            unselected_rule_idxs = set(can_apply_rule_idxs).intersection(self.selection_counter.unselected_rule_idxs)
        else:
            unselected_rule_idxs = set()
        if unselected_rule_idxs:
            candi_rule_idxs = unselected_rule_idxs
        else:
            un_all_covered_rule_idxs = [x for x in can_apply_rule_idxs if x not in self.selection_counter.all_para_covered_rule_idxs]
            if un_all_covered_rule_idxs:
                candi_rule_idxs = []
                for _rule_idx in un_all_covered_rule_idxs:
                    if self.selection_counter.un_all_cover_candis_for_rule_idx(_rule_idx, ori_supported_pos_candis):
                        candi_rule_idxs.append(_rule_idx)
                        break
                if not candi_rule_idxs:
                    candi_rule_idxs = un_all_covered_rule_idxs
            else: # * rule_idx set，
                candi_rule_idxs = can_apply_rule_idxs
        selected_rule_idx = choice(list(candi_rule_idxs))
        return self.considered_rules[selected_rule_idx], selected_rule_idx

    @property
    def least_pos_candi(self):
        return self.selection_counter.least_pos_candi

    def update_rule_idx_from_least_to_most(self):
        if self.rule_idx_from_least_to_most is None:
            self.rule_idx_from_least_to_most = self.selection_counter.rule_idx_from_least_to_most
        if self.selection_times % 2000 == 0:
            self.rule_idx_from_least_to_most = self.selection_counter.rule_idx_from_least_to_most

    def update_pos_from_least_to_most(self):
        if self.pos_from_least_to_most is None:
            self.pos_from_least_to_most = self.selection_counter.pos_from_least_to_most
        if self.selection_times % 2000 == 0:
            self.pos_from_least_to_most = self.selection_counter.pos_from_least_to_most

    def select_pos(self, rule_idx, 
                          insts:List[Inst],
                          length_considering_early_exit:int,
                          ori_supported_pos_candis:set[PosCandi],
                          logger=None)->Tuple[int, PosCandi]:
        
        supported_pos_candis = ori_supported_pos_candis.intersection(self.support_pos_candis.as_set())
        unselected_pos = self.selection_counter.unselected_rule_idx2pos[rule_idx]
        possible_unselected = supported_pos_candis.intersection(unselected_pos)
        if possible_unselected:  #  unselected,  unselected
            pos_candi = choice(list(possible_unselected))
        else:
            # !  uncovered， uncovered
            un_all_covered_pos = self.selection_counter.un_all_cover_candis_for_rule_idx(rule_idx, supported_pos_candis)
            # if logger is not None:
            #     logger.info(f'len(un_all_covered_pos): {len(un_all_covered_pos)}')
            if un_all_covered_pos:
                if not set(un_all_covered_pos).intersection(set(self.pos_from_least_to_most)):
                    raise ValueError(f'un_all_covered_pos:{un_all_covered_pos} ; {self.pos_from_least_to_most}')
                for _pos in self.pos_from_least_to_most:
                    if _pos in un_all_covered_pos:
                        pos_candi = _pos
                        break
            else:
                if len(supported_pos_candis) == 0:
                    raise ValueError(f'No support pos_candis: ori_supported_pos_candis:{ori_supported_pos_candis} ;; self.support_pos_candis.as_set(): {self.support_pos_candis.as_set()}')
                pos_candi = choice(list(supported_pos_candis))
                # ! debug，
                if logger is not None:
                    logger.info(f'Cause reductant: {rule_idx} // {pos_candi} // {list(supported_pos_candis)}')
                    # if not self.selection_counter.rule_idx_all_paras_covered(rule_idx):
                    #     logger.info(f'Cause reductant: {rule_idx} // {pos_candi} // {list(supported_pos_candis)}')
        self.update_pos_from_least_to_most()
        if pos_candi == PosCandi.NewFunc:
            pos = -1   # 
        else:
            pos = get_candi_pos(insts, pos_candi, length_considering_early_exit)
        if logger is not None and ((pos is None) or len(ori_supported_pos_candis) > len(PosCandi) or len(supported_pos_candis) > len(PosCandi)):
            raise ValueError(f'===>pos is None; pos_attr: {pos_candi} ;;\n  {len(ori_supported_pos_candis)}   {len(self.support_pos_candis)}  {len(supported_pos_candis)};;{supported_pos_candis} ;; ;;\n {ori_supported_pos_candis} \n {self.support_pos_candis};; \n\n{length_considering_early_exit} ;;')
        assert pos is not None
        # 
        return pos, pos_candi


    def confirm_selection(self, pos_candi:PosCandi,rule_idx:int, wrap:InsertWrap, logger:Optional[Logger]=None):
        rule = self.considered_rules[rule_idx]
        self.selection_counter.confirm_selection(rule_idx, rule.raw_op_name, pos_candi,wrap= wrap)
        self.selection_times += 1
        if logger is not None and self.selection_times % 500 == 0:
            logger.info(f'===>self.selection_times: {self.selection_times}')
            cov_op_num_and_rate = self.selection_counter.cov_op_num_and_rate
            logger.info(f'===>Op Cov: {cov_op_num_and_rate}')
            if cov_op_num_and_rate[1] > 0.99 and cov_op_num_and_rate[1] < 1:
                logger.info(f'===> Uncovered Op: {self.selection_counter.uncovered_ops}')
            logger.info(f'[{get_time_string()}] ===>Para Cov: {self.selection_counter.para_cov_rate}')
            logger.info(f'===>OpPos Cov: {self.selection_counter.rule_idx_pos_cov_rate}')
            # if self.selection_counter.op_pos_cov_rate[-1] > 0.8:
            #     logger.info(f'Uncovered OpPos: {self.selection_counter.para_cov_rate}')
            if self.selection_counter.rule_idx_pos_cov_rate[-1] > 0.9:
                d = {k:v for k,v in self.selection_counter.unselected_rule_idx2pos.items() if v}
                logger.info(f'===>{d}')
                d = {k:len(v) for k,v in self.selection_counter.unselected_rule_idx_pos2wraps.items() if len(v)}
                logger.info(f'===>{d}')
            logger.info(f'===>CovPara Cov: {self.selection_counter.rule_idx_cov_all_paras_cov_rate}')

    # * look good
    def select_wrap(self, rule_idx, pos, *args, **kwds):  
        unselected_wraps = self.selection_counter.unselected_rule_idx_pos2wraps.get((rule_idx, pos), set())
        if len(unselected_wraps):
            candis = unselected_wraps
        else:
            candis = self.support_wraps.as_set()
        return choice(list(candis))

def generate_insts_for_rule(rule:RuleV2, context:Context, insert_wrap:InsertWrap, insert_m:InsertMethod= InsertMethod.BYOP, max_local=300)->Tuple[List[Inst], funcType]:
    assert insert_m == InsertMethod.BYOP
    # print('nkbngfspbnkgfjbnk concrete_type', concrete_inst_type)
    target_inst, pre_insts, concrete_inst_type, post_insts = generated_insts_for_rule_core(rule, context, max_local)
 
    return wrap_generated_insts(pre_insts, target_inst, concrete_inst_type, insert_wrap, context, post_insts)


def generated_insts_for_rule_core(rule, context, max_local=300):
    try:
        # print(f'Inst under generation: {rule.raw_op_name}  ||, {rule.val_constraints}')
        target_inst,pre_insts, concrete_inst_type, post_insts = generate_insts_for_rulev2_byop(rule, context, max_local=max_local)
        # print('In generated_insts_for_rule_core', target_inst,pre_insts, concrete_inst_type, post_insts,'|>>')
    except UNSolveException as e:
        target_inst = InstFactory.opcode_inst('unreachable')
        pre_insts = []
        concrete_inst_type = funcTypeFactory.generate_one_func_type_default([], [])
        post_insts = []
    return target_inst,pre_insts,concrete_inst_type, post_insts

def get_func_idx2rule_idxs(rules):
    _func_idx2rule_idxs = {}
    can_apply_funcs = []
    func_idx = 0
    func2func_idx = {}
    for idx, rule in enumerate(rules):
        can_apply_func = rule.can_apply_func
        if can_apply_func not in can_apply_funcs:
            _func_idx2rule_idxs[func_idx] = []
            can_apply_funcs.append(can_apply_func)
            func2func_idx[can_apply_func] = func_idx
            func_idx += 1
        if can_apply_func not in func2func_idx:
            similar_func_idx = can_apply_funcs.index(can_apply_func)
            similar_func = can_apply_funcs[similar_func_idx]
            raise ValueError(f'can_apply_func not in func2func_idx: {can_apply_func} ;; {len(func2func_idx)} {len(can_apply_funcs)} {can_apply_func in func2func_idx} {can_apply_func in can_apply_funcs} {hash(can_apply_func)==hash(similar_func)} {can_apply_func==similar_func} ;; \n {can_apply_func} \n {similar_func}')
        _func_idx2rule_idxs[func2func_idx[can_apply_func]].append(idx)
    len_ = len(_func_idx2rule_idxs)
    func_idx2rule_idxs = []
    for i in range(len_):
        func_idx2rule_idxs.append(tuple(_func_idx2rule_idxs[i]))
    func_idx2rule_idxs = tuple(func_idx2rule_idxs)
    return can_apply_funcs, func_idx2rule_idxs


@lru_cache(maxsize=1000)
def get_can_apply_rule_idxs(can_apply_func_idxs, func_idx2rule_idxs):
    can_apply_rule_idxs = []
    for func_idx in can_apply_func_idxs:
        can_apply_rule_idxs.extend(func_idx2rule_idxs[func_idx])
    # print('len(can_apply_rule_idxs)', len(can_apply_rule_idxs), 'len(can_apply_func_idxs)',len(can_apply_func_idxs))
    return can_apply_rule_idxs
