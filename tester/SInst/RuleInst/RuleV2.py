from enum import Enum

from ..InstModel.EmptyValConstraint import EmptyValConstraint

from ..InstModel.NaiveSolvePreInfo import NaiveSolvePreInfo
from ..InstModel.CombinedConstraint import CombinedAndConstraint

from ..InstModel.IMConstraints.util import OPTypeUndeterminedException
from ..InstModel.SelectFuncConstraintFactory import SelectFuncConstraintFactory
from extract_block_mutator.InstUtil.InstReqUtil import get_inst_ty_req

from ..InstModel.ValConstraint import ValConstraint

from ..InstModel.ImSolveInfo import ImSolveInfo
from ..InstModel.SelectFuncConstraint import SelectFuncConstraint, SelectFuncConstraintFactoryAnd
from ..InstModel.PHEnv import PHEnv
from extract_block_mutator.InstGeneration.InstFactory import InstFactory
from extract_block_mutator.Context import Context
from extract_block_mutator.InstUtil.Inst import Inst
from typing import Callable, List, Optional, Tuple
from ..InstModel.ExpExec import ExpExec
from .util import get_ph_constraint_idx
from .util import get_unique_cs_and_process_and
# from .RuleV2Solution import RuleV2Solution
# ===================================


class CSSatisfiable(Enum):
    SATISFIABLE = 1
    UNSATISFIABLE = 2
    UNKNOWN = 3
    UNINITIALIZED = 4


def get_val_constraints(solve_info:ImSolveInfo)->List[ValConstraint]:
    val_constraints = []
    for im_c in solve_info.im_constraints:
        imc_results = im_c.release_both_constraints(solve_info.ph_env)
        val_cs = [imcr.val_constraint for imcr in imc_results]
        func_cs = [imcr.select_func_constraint for imcr in imc_results]
        assert len(func_cs) == len(val_cs) == 1
        assert len(func_cs) == len(val_cs) or ((len(val_cs) == 1) and (len(func_cs) == 0)) , print('val_cs', val_cs, 'func_cs', func_cs)
        val_constraints.extend(val_cs)
        
    return val_constraints


def get_func_constraint(solve_info:ImSolveInfo)->SelectFuncConstraint:
    try:
        select_func_constraints:List[SelectFuncConstraint] = []
        # print('IN get_func_constraint ----------------------------------------------------')
        # for c in solve_info.im_constraints:
        #     print(c)
        # print('----------------------------------------------------')
        for im_c in solve_info.im_constraints:
            imc_results = im_c.release_both_constraints(solve_info.ph_env)
            func_cs = [imcr.select_func_constraint for imcr in imc_results]
            select_func_constraints.extend(func_cs)
        can_apply_funcs = []
        pre_funcs = []
        for sfc in select_func_constraints:
            can_apply_funcs.append(sfc.can_apply_func)
            pre_funcs.append(sfc.pre_func)
            
        context_condition_func = SelectFuncConstraintFactoryAnd.generate_a_combined_func_from_two_func_list(can_apply_funcs, pre_funcs)
        # print('IN get_func_constraint 22222 ----------------------------------------------------')
        # print(can_apply_funcs)
        # print(pre_funcs)
        # print(context_condition_func)
        # print('----------------------------------------------------')
    except OPTypeUndeterminedException as e:
        raise e
        context_condition_func = SelectFuncConstraintFactory.get_default_func_constraint()
    return context_condition_func

class RuleV2:
    def __init__(self, 
                 raw_op_name,  
                 op, 
                 raw_solve_info:ImSolveInfo 
                 ):
        # * raw_op_name  inst rules，inst raw name； rule， attr
        self.raw_op_name = raw_op_name
        self.op = op
        self.raw_solve_info:ImSolveInfo = raw_solve_info
        self.ph_env:PHEnv = raw_solve_info.ph_env
        self.exp_exec = ExpExec.from_trap_bool(raw_solve_info.trap_)
        # 
        self.val_solution = None  # RuleV2Solution
        self.use_naive_solver_info:NaiveSolvePreInfo = NaiveSolvePreInfo.empty_one()
        self.can_use_solution_cache:Optional[bool] = None
        self.target_inst:Optional[Inst] = self._determine_target_inst_if_no_imm(self.ph_env)
        # 
        default_inst_type = None
        # 
        self.illegal_type = not self.ph_env.determined
        self.satisfiable = CSSatisfiable.UNINITIALIZED
        self.context_condition_func = None
        # 
        if self.illegal_type:
            # assert 0
            self.val_constraints = None
            self.imm_idx2constraint_idx = None
            self.op_idx2constraint_idx = None
            
            # raise NotImplementedError('Illegal type')
        else:
            # * 
            context_condition_func: SelectFuncConstraint = get_func_constraint(raw_solve_info)
            # process func constraint
            self.context_condition_func = context_condition_func
            # 
            self.val_constraints: List[ValConstraint] = expand_cs(get_val_constraints(raw_solve_info))
            # print(;)
            self.val_constraints = get_unique_cs_and_process_and(self.val_constraints)
            self.val_constraints = [vc for vc in self.val_constraints if not isinstance(vc, EmptyValConstraint)]
            self.imm_idx2constraint_idx = get_ph_constraint_idx(self.imm_num, self.val_constraints, True)
            self.op_idx2constraint_idx = get_ph_constraint_idx(self.op_num, self.val_constraints, False)
            # 
            
            # print('GREGESGDSGESGERTGERHG self.raw_solve_info.im_constraints')
            # print(self.raw_solve_info.im_constraints)
            # print('================================== self.val_constraints')
            # print(self.val_constraints)
            # print(f'------=====+------------------------------------------ self.raw_op_name: {self.raw_op_name}')
            # print('------------------================-----------------')
            # print('------------------================-----------------')
            
            if self.target_inst is not None:
                default_inst_type_req = get_inst_ty_req(self.target_inst, cur_params=self.operand_types)
                if default_inst_type_req is not None and len(default_inst_type_req.tys) == 1:
                    default_inst_type = default_inst_type_req.ty0
        self.default_inst_type = default_inst_type

    @property
    def can_use_naive_solver(self):
        return self.use_naive_solver_info.can_use_naive_solver

    @property
    def pre_func(self):
        if self.context_condition_func is None:
            return None
        return self.context_condition_func.pre_func

    @property
    def can_apply_func(self):
        if self.context_condition_func is None:
            return None
        return self.context_condition_func.can_apply_func

    @property
    def type_determined(self):
        return self.ph_env.determined

    def _determine_target_inst_if_no_imm(self, ph_env:PHEnv):
        if ph_env.imm_num == 0:
            return InstFactory.opcode_inst(self.op)
        return None

    @property
    def need_solve(self):
        return self.val_solution is None
  
    def need_determine_target_inst(self):
        return self.target_inst is None

    @property
    def imm_num(self):
        return self.ph_env.imm_num

    @property
    def operand_types(self):
        # assert self.type_determined
        if not self.type_determined:
            raise NotImplementedError(f'Not determined: {self}')
        return self.ph_env.get_operand_types()
    @property
    def op_num(self):
        return self.ph_env.op_num

    def apply_pre_func(self, context:Context, insts: List[Inst]):
        assert self.context_condition_func is not None
        if self.pre_func is None:
            return
        self.pre_func(context, insts)
        # print('||| context.local_types', context.local_types)
        


    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.raw_op_name}, {self.op}, {self.ph_env}, {self.context_condition_func}, {self.val_constraints}, {self.exp_exec})'


def expand_cs(ori_cs:List[ValConstraint])->List[ValConstraint]:
    new_cs = ori_cs.copy()
    while any(isinstance(c, CombinedAndConstraint) for c in new_cs):
        cur_new = []
        for i, c in enumerate(new_cs):
            if isinstance(c, CombinedAndConstraint):
                for _c in c.constraints:
                    if _c not in cur_new:
                        cur_new.append(_c)
            else:
                cur_new.append(c)
        new_cs = cur_new
    return new_cs
