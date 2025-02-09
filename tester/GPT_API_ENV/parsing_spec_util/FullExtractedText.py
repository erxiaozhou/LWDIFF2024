import pickle
from typing import Optional
from docutils import nodes

from .ref_log_util import oneRefLog
from .extract_info_util import tagRepr
from .extract_info_util import get_doc_parsers
from .extract_info_util import taggedSections
from .customNode import customNode


class FullExtractedText:
    _core_dict:Optional[dict[str, customNode]] = None
    _all_tags:Optional[taggedSections] = None
    _tags2cnodes:Optional[dict[tagRepr, customNode]] = None
    _all_nodes: Optional[list[customNode]] = None
    
    def __init__(self):
        if self._core_dict is None or self._all_tags is None or self._tags2cnodes is None:
            print('Init FullExtractedText')
            print(self._core_dict is None, self._all_tags is None, self._tags2cnodes is None)
            # assert 0
            _all_tags = taggedSections([])
            _core_dict: dict[str, customNode] = {}
            doc_parsers = get_doc_parsers()
            for doc_name, doc_parser in doc_parsers.items():
                tar_sections = doc_parser.tar_sections
                _all_tags = _all_tags + tar_sections
                for _custom_node in doc_parser.custom_nodes:
                    _core_dict[_custom_node.all_title_repr] = _custom_node
            self._core_dict = _core_dict
            self._all_tags = _all_tags
            self._init_tags2cnodes()

    def _init_tags2cnodes(self):
        # node 2 conde
        all_cnodes = self.all_cnodes
        tags2cnodes = {}
        tags2nodes = {}
        for _cnode in all_cnodes:
            logs = _cnode.ref_logs
            related_tags = [_.referred_tag_repr() for _ in logs]
            for _tag in related_tags:
                tags2nodes[_tag] = _cnode.node
        for _tag, _node in tags2nodes.items():
            for cnode in all_cnodes:
                if cnode.node == _node:
                    tags2cnodes[_tag] = cnode
                    break
        self._tags2cnodes = tags2cnodes
        assert len(tags2cnodes) == len(tags2nodes)

    @property
    def all_leaf_cnodes(self)-> list[customNode]:
        return [node for node in self.all_cnodes if node.is_leaf]

    @property
    def all_cnodes(self)-> list[customNode]:
        if self._all_nodes is None:
            keys = list(self.core_dict.keys())
            keys = sorted(keys)
            self._all_nodes = [self.core_dict[key] for key in keys]
        return self._all_nodes

    @property
    def tags2cnodes(self)->dict[tagRepr, customNode]:
        assert self._tags2cnodes is not None
        return self._tags2cnodes

    @property
    def core_dict(self)->dict[str, customNode]:
        assert self._core_dict is not None
        return self._core_dict
    @property
    def all_tags(self)->taggedSections:
        assert self._all_tags is not None
        return self._all_tags

    def dump_data(self, core_dict_p, tags_p, tags2cnodes_p):
        pickle.dump(self._core_dict, open(core_dict_p, 'wb'))
        # print('AAAAAA', len(self.all_tags))
        pickle.dump(self._all_tags, open(tags_p, 'wb'))
        pickle.dump(self._tags2cnodes, open(tags2cnodes_p, 'wb'))

    @classmethod
    def from_dump_data(cls, core_dict_p, tags_p, tags2cnodes_p):
        cls._core_dict = pickle.load(open(core_dict_p, 'rb'))
        cls._all_tags = pickle.load(open(tags_p, 'rb'))
        # print(len(cls._all_tags))
        cls._tags2cnodes = pickle.load(open(tags2cnodes_p, 'rb'))
        return cls()

    def get_all_title_reprs(self):
        return [_.all_title_repr for _ in self.core_dict.values()]

    def get_node_by_tag(self, tag:tagRepr) -> nodes.Node:
        return self.all_tags[tag].tagged_node

    def get_cnode_by_tag(self, tag:tagRepr) -> customNode:
        return self.tags2cnodes[tag]

    def get_cnode_by_ref_log(self, ref_log:oneRefLog) -> customNode:
        return self.tags2cnodes[ref_log.referred_tag_repr()]


# def customNode_filter
