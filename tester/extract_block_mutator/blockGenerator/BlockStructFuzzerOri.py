# * modified from fuzzingbook
from functools import lru_cache
from typing import Callable, Optional, Set, Union, List
import random
from .DerivationTree import DerivationTree, des2Node
from .util import Expansion

from .BlockStructFuzzer import BlockStructFuzzer

class BlockStructFuzzerOri(BlockStructFuzzer):
    def __init__(self, grammar, min_nonterminals=5, max_nonterminals=10) -> None:
        self.grammar = grammar
        self.min_nonterminals = min_nonterminals
        self.max_nonterminals = max_nonterminals


    def init_block(self):
        return des2Node('<block>')

    def expand_tree(self, tree: DerivationTree) -> None:
        """Expand `tree` in a three-phase strategy until all expansions are complete."""
        self.expand_tree_with_strategy(
            tree, self.expand_node_max_cost, self.min_nonterminals)
        self.expand_tree_with_strategy(
            tree, self.expand_node_randomly, self.max_nonterminals)
        self.expand_tree_with_strategy(
            tree, self.expand_node_min_cost)

        assert tree.possible_expansion_num() == 0

        # return tree


    def is_nonterminal(self, symbol: str) -> bool:
        return symbol in self.grammar

    def expansion_to_children(self, expansion: Expansion) -> List[DerivationTree]:
        if expansion == [""]:  # Special case: epsilon expansion
            return [DerivationTree("<epsilon>", [])]
        return [DerivationTree(s, []) if self.is_nonterminal(s) else DerivationTree(s, None) for s in expansion]

    def choose_node_expansion(self, expansions: list[List[DerivationTree]]) -> int:
        """Return index of expansion in `children_alternatives` to be selected.
           'children_alternatives`: a list of possible children for `node`.
           Defaults to random. To be overloaded in subclasses."""
        # whether contains loop block
        # print(expansions)
        if len(expansions) == 1:
            return 0
        expansion_contain_loop_block = []
        for expansion in expansions:
            for node in expansion:
                if node.name == '<lblock>':
                    expansion_contain_loop_block.append(True)
                    break
            else:
                expansion_contain_loop_block.append(False)

        expansion_contain_loop_block = tuple(expansion_contain_loop_block)
        weights = _contain_loop2prob(expansion_contain_loop_block)
        return random.choices(range(len(expansions)), weights=weights)[0]

    def symbol_cost(self, node_name: str, seen_node_names: Set[str] = None) \
            -> Union[int, float]:
        if node_name not in self.grammar:
            return 0
        if seen_node_names is None:
            seen_node_names = set()
        expansions = self.grammar[node_name]
        return min(self.expansion_cost(e, seen_node_names | {node_name}) for e in expansions)

    def expand_tree_once(self, tree: DerivationTree, expand_func) ->None:
        """Choose an unexpanded symbol in tree; expand it.
           Can be overloaded in subclasses."""
        if tree.need_expansion:
            return expand_func(tree)
        # tree.occur_expansion_before_cal_has_expansion = True
        children = tree.children

        # Find all children with possible expansions
        expandable_child_idxs = []
        # print('In expand_tree_once===============================')
        for i, child in enumerate(children):
            # print(child.children, child.has_possible_expansion(), child._determine_has_possible_expansion(), child.occur_expansion_before_cal_has_expansion)
            if child.has_possible_expansion():
                expandable_child_idxs.append(i)
        child_to_be_expanded = random.choice(expandable_child_idxs)    
       

        # Expand in place
        self.expand_tree_once(children[child_to_be_expanded], expand_func)

        # return tree

    def expansion_cost(self, expansion: Expansion,
                       seen_node_names: Set[str] = None) -> Union[int, float]:
        if seen_node_names is None:
            seen_node_names = set()
        if len(expansion) == 0:
            return 1  # no symbol

        if any(s in seen_node_names for s in expansion):
            return float('inf')

        # the value of a expansion is the sum of all expandable variables
        # inside + 1
        return sum(self.symbol_cost(s, seen_node_names) for s in expansion) + 1

    def expand_node_default(self, node):
        return self.expand_node_randomly(node)

    def expand_node_min_cost(self, node) -> None:
        return self.expand_node_by_cost(node, min)

    def expand_node_max_cost(self, node) -> None:
        return self.expand_node_by_cost(node, max)

    def expand_node_by_cost(self, node: DerivationTree,
                            choose: Callable = min) -> None:
        assert node.need_expansion
        node_name = node.name
        # Fetch the possible expansions from grammar...
        expansions = self.grammar[node_name]
        children_candi_with_cost = [(self.expansion_to_children(expansion),
                                     self.expansion_cost(expansion, {node_name}))
                                    for expansion in expansions]

        costs = [_[1] for _ in children_candi_with_cost]
        chosen_cost = choose(costs)
        children_with_chosen_cost: list[List[DerivationTree]] = [child for (child, child_cost)
                                     in children_candi_with_cost
                                     if child_cost == chosen_cost]

        index = self.choose_node_expansion(children_with_chosen_cost)

        chosen_children = children_with_chosen_cost[index]
        node.set_children(chosen_children)
        # Return with a new list
        # return DerivationTree(node_name, chosen_children)

    def expand_node_randomly(self, node: DerivationTree) -> None:
        """Choose a random expansion for `node` and return it"""
        assert node.need_expansion
        node_name = node.name

        # Fetch the possible expansions from grammar...
        expansions = self.grammar[node_name]
        # expansion_num = len(expansions)
        # if expansion_num == 1:
        #     expansion_idx = 0
        # else:
        #     expansion_idx = random.randrange(0, expansion_num)
        children_alternatives: List[List[DerivationTree]] = [
            self.expansion_to_children(expansion) for expansion in expansions
        ]

        # ... and select a random expansion
        index = self.choose_node_expansion(children_alternatives)
        chosen_children = children_alternatives[index]
        node.set_children(chosen_children)


    def expand_tree_with_strategy(self, tree: DerivationTree,
                                  expand_node_method: Callable,
                                  limit: Optional[int] = None) -> None:
        """Expand tree using `expand_node_method` as node expansion function
        until the number of possible expansions reaches `limit`."""
        # print('In expand_tree_with_strategy===============================')
        while ((limit is None
                or tree.possible_expansion_num() < limit)
               and tree.has_possible_expansion()):
            self.expand_tree_once(tree, expand_func=expand_node_method)
        while True:
            if limit is not None:
                if tree.possible_expansion_num() >= limit:
                    break
            if not tree.has_possible_expansion():
                break
            self.expand_tree_once(tree, expand_func=expand_node_method)

        # return tree

@lru_cache(maxsize=1024)
def _contain_loop2prob(expansion_contain_loop_block:list[bool]):
    exp_num = len(expansion_contain_loop_block)
    contain_loop_block_num = sum(expansion_contain_loop_block)
    if exp_num == contain_loop_block_num or contain_loop_block_num == 0:
        return [1 / exp_num for _ in range(exp_num)]
    sum_loop_block_prob = 0.01
    # sum_loop_block_prob = 0.3
    each_loop_block_prob = sum_loop_block_prob / contain_loop_block_num
    each_other_block_prob = (1 - sum_loop_block_prob) / (exp_num - contain_loop_block_num)
    weights = [each_loop_block_prob if expansion_contain_loop_block[i] else each_other_block_prob for i in range(exp_num)]
    return weights
