
from collections import Counter
from .InsertWrap import InsertWrap, InsertWraps
from ..inst_pose_selector import PosCandi, PosCandis

import pandas as pd
# ======================================== * ==== * ==== * ========================================
# SpecialOpFuncWatFactory


class RuleFactoryCounter:
    def __init__(self, support_ops, support_pose_candis:PosCandis, support_wraps:InsertWraps, rule_num):
        wrap_num = len(support_wraps)
        self.visited_ops = set()
        self.support_ops = support_ops
        support_pose_candis_ = support_pose_candis.as_list()
        self.support_pos_candis = support_pose_candis_
        self.support_op_num = len(support_ops)
        self.support_pos_candi_num = len(support_pose_candis)
        # DataFrame for general stats
        idx = pd.MultiIndex.from_product([range(rule_num), support_pose_candis.as_list()], names=['rule_idx', 'pos_candi'])
        self.op_pos_selection_stats = pd.DataFrame(0, index=idx, columns=['selected_times'])
        
        # self.total_op_pos_candi_key_num = self.support_op_num * self.support_pos_candi_num
        self.total_rule_idx_pos_key_num = rule_num * self.support_pos_candi_num
        self.all_covered_rule_idx_pos = set()
        self.candi_selection_counter = Counter({pos_candi_: 0 for pos_candi_ in support_pose_candis.as_list()})  # 
        self.rule_idx_counter = Counter()
        # self.
        self.all_para_covered_rule_idxs = set()
        # rule_idx related info
        self.rule_num = rule_num
        self.all_para_num = rule_num * wrap_num * len(support_pose_candis)
        self.unselected_rule_idxs = set(range(rule_num))
        self.unselected_rule_idx2pos = {idx: support_pose_candis.as_set() for idx in range(rule_num)}
        # self.unselected_rule_idx_pos = {(idx, pos) for idx in range(rule_num) for pos in support_pose_candis}
        self.unselected_rule_idx_pos2wraps = {(idx, pos): support_wraps.as_set().copy() for idx in range(rule_num) for pos in support_pose_candis.as_set()}
        self.unselected_rule_idx_pos_wrap = {(idx, pos, wrap) for idx in range(rule_num) for pos in support_pose_candis.as_list() for wrap in support_wraps.as_list()}
        
        self.all_rule_selected = False

    @property
    def uncovered_ops(self):
        return set(self.support_ops) - self.visited_ops

    @property
    def rule_idx_from_least_to_most(self):
        return [x[0] for x in self.rule_idx_counter.most_common()][::-1]

    @property
    def least_pos_candi(self):
        return self.candi_selection_counter.most_common()[-1][0]
    @property
    def pos_from_least_to_most(self):
        return [x[0] for x in self.candi_selection_counter.most_common()][::-1]
    @property
    def least_rule_idx(self):
        return self.rule_idx_counter.most_common()[-1][0]

    # def

    def rule_idx_pos_is_all_covered(self, rule_idx, pos_candi):
        if (rule_idx, pos_candi) in self.all_covered_rule_idx_pos:
            return True
        k = (rule_idx, pos_candi)
        unselected_wraps = self.unselected_rule_idx_pos2wraps.get(k)
        covered_ = unselected_wraps is None or len(unselected_wraps) == 0
        if covered_:
            self.all_covered_rule_idx_pos.add((rule_idx, pos_candi))
        return covered_

    def rule_idx_pos_is_selected(self, rule_idx, pos_candi):
        return pos_candi not in self.unselected_rule_idx2pos[rule_idx]

    def un_all_cover_candis_for_rule_idx(self, rule_idx, pos_candis):
        uncovered_candis = []
        for pos_candi in pos_candis:
            if not self.rule_idx_pos_is_all_covered(rule_idx, pos_candi):
                uncovered_candis.append(pos_candi)
        return uncovered_candis
    
    def rule_idx_all_paras_covered(self, rule_idx):
        pos_candis = self.support_pos_candis
        if rule_idx in self.all_para_covered_rule_idxs:
            return True
        all_covered_ = all([self.rule_idx_pos_is_all_covered(rule_idx, pos_candi) for pos_candi in pos_candis])
        if all_covered_:
            self.all_para_covered_rule_idxs.add(rule_idx)
        return all_covered_


    def confirm_selection(self,rule_idx,raw_op_name,  pos_candi, wrap):
        self.visited_ops.add(raw_op_name)
        self.rule_idx_counter.update([rule_idx])
        self.op_pos_selection_stats.at[(rule_idx, pos_candi), 'selected_times'] += 1
        # 
        if rule_idx in self.unselected_rule_idxs:
            self.unselected_rule_idxs.remove(rule_idx)
        if pos_candi in self.unselected_rule_idx2pos[rule_idx]:
            self.unselected_rule_idx2pos[rule_idx].remove(pos_candi)
        key_poss = self.unselected_rule_idx_pos2wraps.get((rule_idx, pos_candi))
        if key_poss is not None and wrap in key_poss:
            key_poss.remove(wrap)
        if (rule_idx, pos_candi, wrap) in self.unselected_rule_idx_pos_wrap:
            self.unselected_rule_idx_pos_wrap.remove((rule_idx, pos_candi, wrap))
            
        self.candi_selection_counter.update([pos_candi])

    @property
    def cov_op_num_and_rate(self):
        visited_count = len(self.visited_ops)
        return visited_count, visited_count / self.support_op_num

    @property
    def rule_idx_pos_cov_rate(self):
        total_rule_idx_pos_combin = self.total_rule_idx_pos_key_num
        cov_op_pos_combin = self.op_pos_selection_stats['selected_times'].gt(0).sum()
        return cov_op_pos_combin, total_rule_idx_pos_combin, cov_op_pos_combin / total_rule_idx_pos_combin if total_rule_idx_pos_combin else 0

    @property
    def para_cov_rate(self):
        total_param_num = self.all_para_num
        unselected_para_num = len(self.unselected_rule_idx_pos_wrap)
        selected_para_num = total_param_num - unselected_para_num
        return selected_para_num, total_param_num, selected_para_num / total_param_num if total_param_num else 0

    @property
    def rule_idx_cov_all_paras_cov_rate(self):
        all_covered_num = 0
        for rule_idx in range(self.rule_num):
            if self.rule_idx_all_paras_covered(rule_idx=rule_idx):
                all_covered_num += 1
        return all_covered_num, self.rule_num, all_covered_num / self.rule_num if self.rule_num else 0
