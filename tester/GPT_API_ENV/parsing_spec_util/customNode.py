from docutils import nodes
from typing import List


from .NodeText import NodeText
from .ref_log_util import clean_font, match_xref_core



class _TitleInfo:
    def __init__(self, 
                 innter_titles:list[str], 
                 doc_titles:list[str], 
                 cur_title_text:str):
        self.doc_titles = doc_titles
        self.inner_titles = innter_titles
        self.cur_title_text = cur_title_text
        # analyze cur title
        simplified_text = clean_font(cur_title_text)
        self.refs = match_xref_core(simplified_text)
        # simplify the title
        for _ref in self.refs:
            simplified_text = simplified_text.replace(_ref.raw_text, _ref.wrapped_content)
        self.simplified_text = simplified_text
        self.depth = len(doc_titles) + len(innter_titles)

    @property
    def all_title_repr(self):
        s = ' '.join([*self.doc_titles, *self.inner_titles, self.simplified_text])
        return s 
        
    @property
    def raw_all_titles(self):
        return self.doc_titles + self.inner_titles + [self.cur_title_text]

    
def get_a_node_title(node:nodes.Node)->str:
    assert isinstance(node, nodes.Node)
    title_node = node.next_node(nodes.title)
    if title_node:
        return title_node.astext()
    return ''


class customNode:
    def __init__(self, node:nodes.Node, innter_titles, doc_titles, cur_title_text):
        self.node = node
        self.title_info = _TitleInfo(
            innter_titles=innter_titles,
            doc_titles=doc_titles,
            cur_title_text=cur_title_text
        )
        self.node_text = NodeText(node, True)
        
    @property
    def ref_logs(self):
        return self.node_text.ref_logs

    @property
    def unique_ref_logs(self):
        return self.node_text.unique_ref_logs

    @property
    def no_math_simplified_text_oversize(self):
        return self.node_text.no_math_simplified_text_oversize

    @property
    def simplified_text_oversize(self):
        return self.node_text.simplified_text_oversize

    @property
    def no_math_simplified_text(self):
        return self.node_text.no_math_simplified_text

    @property
    def simplified_text(self):
        return self.node_text.simplified_text

    @property
    def is_leaf(self):
        is_leaf = not any(isinstance(_, nodes.section) for _ in self.node.children)
        return is_leaf

    @property
    def is_leaf_but_not_abbr(self):
        section_nodes = [n for n in self.node.children if isinstance(n, nodes.section)]
        not_abbr_section_nodes = [n for n in section_nodes if get_a_node_title(n) != 'Abbreviations']
        return len(not_abbr_section_nodes) == 0

    @property
    def is_abbreviations(self):
        return self.cur_title_text == 'Abbreviations'

    @property
    def all_title_repr(self):
        return self.title_info.all_title_repr
    @property
    def cur_title_text(self):
        return self.title_info.cur_title_text

    @property
    def depth(self):
        return self.title_info.depth

    @property
    def raw_all_titles(self):
        return self.title_info.raw_all_titles

    @property
    def is_exec_numeric(self):
        # assert not ['exec', 'numerics'] == self.title_info.doc_titles
        return ['exec', 'numerics'] == self.title_info.doc_titles

    @property
    def is_binary(self):
        return 'binary' == self.title_info.doc_titles[0]

    @property
    def is_valid(self):
        return 'valid' == self.title_info.doc_titles[0]

    @property
    def inner_nodes(self)->List[nodes.Node]:
        return self.node.traverse()
