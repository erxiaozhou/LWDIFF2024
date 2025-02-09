
from typing import List, Dict
from itertools import chain


Expansion = List[str]
block_grammar: Dict[str, List[List[str]]] = {
    "<program>": [['<block>']],
    "<block>": [['<dblock>'], ['<ifblock>'], ['<lblock>'], ['<bblock>'], ['<block>', '<block>']],
    "<ifblock>": [['<block>'], ['<block>', '<block>']],
    "<lblock>": [['<block>']],
    "<bblock>": [['<block>']],
    "<dblock>": [["<inst*>"]],
}

def get_get_eq_terminal_nodes(grammar: Dict[str, List[List[str]]]):
    non_terminal_nodes = set(grammar.keys())
    eq_terminal_nodes = set(chain(*chain(*grammar.values()))) - non_terminal_nodes
    has_new_elem = False
    first_time = True
    while has_new_elem or first_time:
        first_time = False
        has_new_elem = False
        for k, v in grammar.items():
            if k in eq_terminal_nodes:
                continue
            all_elems = set(chain(*v))
            if all([elem in eq_terminal_nodes for elem in all_elems]):
                eq_terminal_nodes.add(k)
                has_new_elem = True

    return eq_terminal_nodes
