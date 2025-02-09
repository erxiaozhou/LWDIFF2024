from enum import Enum
from typing import Callable
from file_util import read_json
from .customNode import customNode


class cNodeFilterStrategy(Enum):
    NOT_APPENDIX_IS_LEAF = 0
    ALL = 1
    NOT_TOO_LONG = 2
    NOT_TOO_LONG_NOT_APPENDIX = 3
    NOT_APPENDIX_IS_LEAF_NOT_ABBR = 4


def get_customNode_filter(cfg_name:cNodeFilterStrategy)-> 'customNode_filter':
    cfg_name2func = {
        cNodeFilterStrategy.NOT_APPENDIX_IS_LEAF: customNode_filter.cfg_not_appendix_is_leaf,
        cNodeFilterStrategy.NOT_APPENDIX_IS_LEAF_NOT_ABBR: customNode_filter.clf_is_not_abbr_leaf_not_appendix,
        cNodeFilterStrategy.ALL: customNode_filter.cfg_all,
        cNodeFilterStrategy.NOT_TOO_LONG: customNode_filter.cfg_not_too_long,
        cNodeFilterStrategy.NOT_TOO_LONG_NOT_APPENDIX: customNode_filter.cfg_not_too_long_not_appendix
    }
    return cfg_name2func[cfg_name]()


class customNode_filter:
    def __init__(self, func_chain:list[Callable[[customNode], bool]]):
        self.func_chain = func_chain

    # @classmethod
    # def from_keywords(cls, keywords: list[str]):
    #     _d = {
    #         'is_leaf': _is_leaf_node,
    #         'not_appendix': _is_not_appendix
    #     }
    @classmethod
    def cfg_not_appendix_is_leaf(cls):
        return cls([_is_leaf_node, _is_not_appendix])

    @classmethod
    def clf_is_not_abbr_leaf_not_appendix(cls):
        return cls([_is_leaf_but_not_abbr, _is_not_appendix])

    @classmethod
    def cfg_all(cls):
        return cls([_always_true])

    @classmethod
    def cfg_not_too_long(cls):
        return cls([_is_not_too_long_no_math_simplified_text])

    @classmethod
    def cfg_not_too_long_not_appendix(cls):
        return cls([_is_not_too_long_no_math_simplified_text, _is_not_appendix])


    def get_expected_nodes(self, nodes: list[customNode])->list[customNode]:
        return [node for node in nodes if self.is_expected_node(node)]

    def is_expected_node(self, node: customNode)->bool:
        for func in self.func_chain:
            if not func(node):
                return False
        return True
    


# single detect funcs
def _is_leaf_node(node: customNode)->bool:
    return node.is_leaf

def _is_leaf_but_not_abbr(node: customNode)->bool:
    return node.is_leaf_but_not_abbr

def _is_not_appendix(node: customNode)->bool:
    return not node.all_title_repr.lower().startswith('appendix')


def _always_true(node: customNode)->bool:
    return True

def _is_not_too_long_no_math_simplified_text(node: customNode)->bool:
    return not node.node_text.no_math_simplified_text_oversize

