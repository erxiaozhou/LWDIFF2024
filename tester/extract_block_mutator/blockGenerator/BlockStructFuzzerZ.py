# * modified from fuzzingbook
from functools import lru_cache
from typing import Callable, Optional, Set, Union, List
import random
from .DerivationTree import DerivationTree, des2Node, print_tree
from .util import Expansion, get_get_eq_terminal_nodes
from .BlockStructFuzzer import BlockStructFuzzer


class BlockStructFuzzerZ(BlockStructFuzzer):
    def __init__(self, grammar, min_depth=5, max_depth=20) -> None:
        self.grammar = grammar
        self.min_depth = min_depth
        self.max_depth = max_depth
        assert self.min_depth <= self.max_depth
        self._nonterminals = set(self.grammar.keys())
        self._eq_nonterminals = self._nonterminals - get_get_eq_terminal_nodes(self.grammar)


    def init_block(self):
        return des2Node('<block>')

    def expand_tree(self, tree: DerivationTree) -> None:
        self.expand_with_depth(tree, 'grow_depth', 0)
        assert not tree.has_possible_expansion(), print_tree(tree)


    def expand_with_depth(self, tree: DerivationTree, phase:str, cur_depth: int):
        assert phase in ['soon_over', 'random', 'grow_depth']
        if tree.is_leaf():
            return None
        if phase == 'soon_over':
            self.expand_tree_over_soon(tree)
            for child in tree.children:
                self.expand_with_depth(child, 'soon_over', cur_depth+1)
        elif phase == 'random':
            self.expand_node_randomly(tree)
            if cur_depth <= self.max_depth:
                for child in tree.children:
                    self.expand_with_depth(child, 'random', cur_depth+1)
            else:
                for child in tree.children:
                    self.expand_with_depth(child, 'soon_over', cur_depth+1)
        else:
            self.expand_tree_grow_depth(tree)
            if cur_depth <= self.min_depth:
                if len(tree.children) == 1:
                    self.expand_with_depth(tree.children[0], 'grow_depth', cur_depth+1)
                else:
                    selected_idx_for_depth = random.choice(range(len(tree.children)))
                    for idx, child in enumerate(tree.children):
                        if idx == selected_idx_for_depth:
                            self.expand_with_depth(child, 'grow_depth', cur_depth+1)
                        else:
                            
                            self.expand_with_depth(child, 'random', cur_depth+1)
            else:
                for child in tree.children:
                    self.expand_with_depth(child, 'random', cur_depth)
            
        



    def is_nonterminal(self, symbol: str) -> bool:
        return symbol in self._nonterminals

    def is_eq_nonterminal(self, symbol: str) -> bool:
        return symbol in self._eq_nonterminals

    def expansion_to_children(self, expansion: Expansion) -> List[DerivationTree]:
        if expansion == [""]:  # Special case: epsilon expansion
            return [DerivationTree("<epsilon>", [])]
        return [DerivationTree(s, []) if self.is_nonterminal(s) else DerivationTree(s, None) for s in expansion]

    def expansion_has_nonterminal(self, expansion: Expansion) -> bool:
        return any(self.is_eq_nonterminal(s) for s in expansion) 




    def expand_tree_grow_depth(self, node: DerivationTree) -> None:
        assert node.need_expansion
        node_name = node.name

        expansions = self.grammar[node_name]
        children_alternatives: List[List[DerivationTree]] = [
            self.expansion_to_children(expansion) for expansion in expansions if self.expansion_has_nonterminal(expansion)
        ]

        index = choose_node_expansion(children_alternatives)
        chosen_children = children_alternatives[index]
        node.set_children(chosen_children)


    def expand_node_randomly(self, node: DerivationTree) -> None:
        assert node.need_expansion
        node_name = node.name

        expansions = self.grammar[node_name]
        children_alternatives: List[List[DerivationTree]] = [
            self.expansion_to_children(expansion) for expansion in expansions
        ]

        index = choose_node_expansion(children_alternatives)
        chosen_children = children_alternatives[index]
        node.set_children(chosen_children)

    def expand_tree_over_soon(self, node: DerivationTree) -> None:
        assert node.need_expansion
        node_name = node.name

        expansions = self.grammar[node_name]
       
        can_terminal_expansions = [expansion for expansion in expansions if not self.expansion_has_nonterminal(expansion)]
        if len(can_terminal_expansions):
            children_alternatives: List[List[DerivationTree]] = [
                self.expansion_to_children(expansion) for expansion in can_terminal_expansions
            ]
            index = choose_node_expansion(children_alternatives)
            chosen_children = children_alternatives[index]
            node.set_children(chosen_children)
        else:
            children_alternatives: List[List[DerivationTree]] = [
                self.expansion_to_children(expansion) for expansion in expansions
            ]
            
            index = choose_node_expansion(children_alternatives)
            chosen_children = children_alternatives[index]
            node.set_children(chosen_children)




def choose_node_expansion(expansions: list[List[DerivationTree]]) -> int:
    if len(expansions) == 1:
        return 0
    return random.choice(range(len(expansions)))
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

@lru_cache(maxsize=1024)
def _contain_loop2prob(expansion_contain_loop_block:list[bool]):
    exp_num = len(expansion_contain_loop_block)
    contain_loop_block_num = sum(expansion_contain_loop_block)
    if exp_num == contain_loop_block_num or contain_loop_block_num == 0:
        return [1 / exp_num for _ in range(exp_num)]
    sum_loop_block_prob = 0.01
    each_loop_block_prob = sum_loop_block_prob / contain_loop_block_num
    each_other_block_prob = (1 - sum_loop_block_prob) / (exp_num - contain_loop_block_num)
    weights = [each_loop_block_prob if expansion_contain_loop_block[i] else each_other_block_prob for i in range(exp_num)]
    return weights

