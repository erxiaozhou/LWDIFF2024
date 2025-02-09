import random
from typing import Dict, List, Optional, Tuple, Union
from enum import Enum
from ..funcType import funcType
from ..funcTypeFactory import funcTypeFactory

from ..InstUtil import Inst 
from ..funcType import funcType
from ..Context import Context
from ..blockParser.block import directWasmBlock, mixWasmBlock, wasmBlock

class ActionType(Enum):
    INSERT = 0
    REPLACE = 1
    DELETE = 2


class Action:
    def __init__(self, action_type, action_location: Union[int, List[int]], exp_type: Optional[funcType] = None):
        self.action_type = action_type
        self.action_location = action_location
        self.exp_type = exp_type

        if action_type == ActionType.INSERT:
            assert isinstance(action_location, int)
        else:
            assert isinstance(action_location, list)
            assert len(action_location) == 2

        if action_type == ActionType.INSERT:
            assert isinstance(action_location, int)
        elif action_type == ActionType.REPLACE:
            assert isinstance(action_location, list)
            assert len(action_location) == 2
        elif action_type == ActionType.DELETE:
            assert isinstance(action_location, list)
            assert len(action_location) == 2
        # 
        if self.action_type == ActionType.INSERT:
            self.to_replace_indexs = [self.action_location, self.action_location]
        else:
            self.to_replace_indexs = self.action_location
        assert isinstance(self.to_replace_indexs, list) and len(self.to_replace_indexs) == 2

    def __repr__(self) -> str:
        return f'Action({self.action_type}, {self.action_location}, {self.exp_type})'

    @property
    def to_replace_length(self):
        return self.to_replace_indexs[1] - self.to_replace_indexs[0]


def get_defalut_action(insts: List[Inst]):
    insts_num = len(insts)
    insert_position = random.randint(0, insts_num)
    insert_position = 0
    return Action(ActionType.INSERT, insert_position, funcTypeFactory.generate_one_func_type_default([], []))


def weighted_random_choice(lst):
    weights = [2 ** i for i in range(len(lst))][::-1]
    total_weight = sum(weights)
    probabilities = [weight / total_weight for weight in weights]
    lst_len = len(lst)
    probabilities = [(p + 1/lst_len)/2 for p in probabilities]
    # probabilities = 
    result = random.choices(lst, probabilities)[0]
    return result





def find_a_case_by_location(block_tree, location: tuple[int]):
    if len(location) == 0:
        return block_tree
    else:
        return find_a_case_by_location(block_tree.inner_blocks[location[0]], location[1:])
