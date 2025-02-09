from .DerivationTree import DerivationTree
import re
import string
from typing import Any, Callable
from graphviz import Digraph

def default_graph_attr(dot):
    dot.attr('node', shape='plain')


def default_edge_attr(dot, start_node, stop_node):
    dot.edge(repr(start_node), repr(stop_node))


def extract_node(node: DerivationTree, id):
    node_name = node.name
    children = node.children if node.children is not None else []
    annotation = node.annotation if node.annotation is not None else ''

    return node_name, children, repr(annotation)


def default_node_attr(dot, nid, symbol, ann):
    dot.node(repr(nid), dot_escape(symbol))


def dot_escape(s: str, show_ascii=None) -> str:
    """Return s in a form suitable for dot.
    If `show_ascii` is True or length of `s` is 1, also append ascii value."""
    escaped_s = ''
    if show_ascii is None:
        show_ascii = (len(s) == 1)  # Default: Single chars only

    if show_ascii and s == '\n':
        return '\\\\n (10)'

    s = s.replace('\n', '\\n')
    for c in s:
        if re.match('[,<>\\\\"]', c):
            escaped_s += '\\' + c
        elif c in string.printable and 31 < ord(c) < 127:
            escaped_s += c
        else:
            escaped_s += '\\\\x' + format(ord(c), '02x')

        if show_ascii:
            escaped_s += f' ({ord(c)})'

    return escaped_s


def display_tree(derivation_tree: DerivationTree,
                 log: bool = False,
                 extract_node: Callable = extract_node,
                 node_attr: Callable = default_node_attr,
                 edge_attr: Callable = default_edge_attr,
                 graph_attr: Callable = default_graph_attr) -> Digraph:

    # If we import display_tree, we also have to import its functions
    

    counter = 0

    def traverse_tree(dot, tree, id=0):
        (symbol, children, annotation) = extract_node(tree, id)
        node_attr(dot, id, symbol, annotation)

        if children:
            for child in children:
                nonlocal counter
                counter += 1
                child_id = counter
                edge_attr(dot, id, child_id)
                traverse_tree(dot, child, child_id)

    dot = Digraph(comment="Derivation Tree")
    graph_attr(dot)
    traverse_tree(dot, derivation_tree)
    if log:
        print(dot)
    return dot

def save_tree(derivation_tree: DerivationTree,
              path: str):
    dot = display_tree(derivation_tree)
    # dot.render(path, view=False)
    dot.render(path, view=False,format='pdf')
