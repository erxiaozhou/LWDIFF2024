from random import randint
from extract_block_mutator.InstGeneration.InstFactory import InstFactory
from ..InstModel.solver import ValConstraintSolver
from .process_rule_util import one_rule_is_unsatisfiable
from ..InstModel.set_unconstrained_imm_util import set_cs_for_unc_imm_rg
from ..InstModel.Exceptions import ContextIsNoneException
from extract_block_mutator.InstUtil.Inst import Inst
from typing import Optional
from extract_block_mutator.Context import Context
from .RuleV2 import CSSatisfiable, RuleV2
from .ValidationData import ValidationData
from .determine_target_inst_for_rulev2 import just_get_target_inst_for_rulev2


# ，
class ValidInstGenerator:
    def __init__(self, rules:list[RuleV2]):
        self.rules = rules
        self.opcode_text = self._identyfy_op()
        self.has_imm = self._identify_has_imm()
        self.only_one_rule = self._only_one_rule()
        self.rule_num = len(rules)

    @classmethod
    def from_op_name_and_validation_data(cls, raw_inst_name, op, validation_data:ValidationData):
        # ph_envs = validation_data.ph_envs
        im_solve_infos = validation_data.im_solve_infos
        rules = []
        for im_solve_info in im_solve_infos:

            rule = RuleV2(raw_inst_name, op, im_solve_info)
            set_cs_for_unc_imm_rg(rule)
            _satisfiable = one_rule_is_unsatisfiable(rule)
            if _satisfiable == CSSatisfiable.UNSATISFIABLE:
                continue
            rule.satisfiable = _satisfiable
            val_constraints = rule.val_constraints
            assert val_constraints is not None
            rule.can_use_solution_cache = ValConstraintSolver._all_eq_const(val_constraints) and rule.satisfiable == CSSatisfiable.SATISFIABLE
            rule.use_naive_solver_info = ValConstraintSolver.get_naive_solve_pre_info(rule)
            # if not rule.can_use_naive_solver:
            #     print('Not naive solve pattern:', rule)
            rules.append(rule)
        return cls(rules)

    def _identify_has_imm(self)->bool:
        imm_nums = [rule.imm_num for rule in self.rules]
        # check
        # print('ppppppppppppppppppppppp', self.opcode_text, imm_nums)
        assert len(set(imm_nums)) == 1
        return imm_nums[0] > 0

    def _identyfy_op(self)->str:
        ops = [rule.op for rule in self.rules]
        assert len(set(ops)) == 1
        return ops[0]

    def _only_one_rule(self)->bool:
        return len(self.rules) == 1
 

    def generate_random_inst_candi(self, context:Optional[Context], cur_stack_param_types:Optional[list[str]]=None)->Optional[Inst]:
        if not self.has_imm:
            return InstFactory.opcode_inst(self.opcode_text)
        if self.only_one_rule:
            selected_rule_idx = 0
        else:
            selected_rule_idx = randint(0, self.rule_num-1)
        try:
            result =  just_get_target_inst_for_rulev2(self.rules[selected_rule_idx], context)
        except ContextIsNoneException:
            result = None
        return result