from pathlib import Path
import pickle
from docutils import nodes
from typing import List
from sphinx.util.docutils import docutils_namespace
from .ref_log_util import tagRepr
from ..project_cfg import default_env_store_path
from ..project_cfg import doc_core_folder_path
from docutils import nodes
from sphinx.addnodes import document

from .build_text_utilz import parse_rst_folder_with_sphinx
from .build_text_utilz import build_document_structure
from .customNode import customNode


class NoTaggedNodeError(Exception):
    pass
class TaggedNodeTypeError(Exception):
    pass


def traverse_sections(node, custom_nodes, doc_titles, visited_titles=None):
    if visited_titles is None:
        visited_titles = []
    for child in node.children:
        if isinstance(child, nodes.section):
            title_node = child.next_node(nodes.title)
            next_level_titles = visited_titles.copy()
            if title_node:
                title_text = title_node.astext()
                custom_node = customNode(
                    node=child, 
                    innter_titles=visited_titles.copy(), 
                    doc_titles=doc_titles,
                    cur_title_text=title_text
                    )
                custom_nodes.append(custom_node)
                next_level_titles.append(title_text)
            else:
                next_level_titles.append(None)
            traverse_sections(
                node=child, 
                custom_nodes=custom_nodes, 
                doc_titles=doc_titles,
                visited_titles=next_level_titles)


class taggedSection:
    def __init__(self, node:nodes.Node, inner_tag_name:str, doc_name:str):
        # assert isinstance(node, (nodes.section, nodes.paragraph))
        self.tagged_node = node
        self.inner_tag_name = inner_tag_name
        self.doc_name = doc_name

    @property
    def tag_repr(self):
        return tagRepr(self.doc_name, self.inner_tag_name)


class taggedSections:
    def __init__(self, tagged_sections:List[taggedSection]):
        self.tagged_sections = tagged_sections
        # tag_repr2idx
        self.tag_repr2idx:dict[tagRepr, int] = {}
        for idx, _tagged_section in enumerate(tagged_sections):
            self.tag_repr2idx[_tagged_section.tag_repr] = idx

    def __getitem__(self, tag_repr:tagRepr):
        return self.tagged_sections[self.tag_repr2idx[tag_repr]]

    def __len__(self):
        return len(self.tagged_sections)

    def __add__(self, other):
        assert isinstance(other, taggedSections)
        return taggedSections(self.tagged_sections + other.tagged_sections)
    
    def __iter__(self):
        return iter(self.tagged_sections)



class docParser:
    def __init__(self, doc_name:str, one_doc:document):
        self.doc_name = doc_name
        self.one_doc = one_doc
        self._tag_sections = None
        assert isinstance(one_doc, document)
        # assert isinstance(doc_name, nodes.Node)
        for _ in one_doc.traverse():
            assert isinstance(_, nodes.Node)
        # 
        doc_titles = self.doc_name.split('/')
        assert all([_ for _ in doc_titles])

        self.custom_nodes = []
        # inner_file
        traverse_sections(self.one_doc, self.custom_nodes, doc_titles=doc_titles)
        self.parsing_tags()

    @property
    def tar_sections(self)->taggedSections:
        assert self._tag_sections is not None
        return self._tag_sections

    def parsing_tags(self):
        all_nodes = self.one_doc.traverse()
        tag_list = []
        for node_idx, _node in enumerate(all_nodes):
            if isinstance(_node, nodes.target):
                next_node = all_nodes[node_idx + 1]
                refid = _node.attributes.get('refid')
                if refid is None:
                    continue
                if refid[:6] == 'index-' and refid[6:].isdigit():
                    continue
                next_node = self._get_next_not_tag_node(node_idx, all_nodes)
                if not isinstance(next_node, (nodes.section, nodes.paragraph, nodes.enumerated_list, nodes.bullet_list, nodes.math_block, nodes.definition_list)):
                    raise TaggedNodeTypeError(f'The type of the tagged node is not section: {refid} and {next_node} ;; {type(next_node)}')
                cur_tag = taggedSection(node=next_node, inner_tag_name=refid, doc_name=self.doc_name)
                tag_list.append(cur_tag)
        self._tag_sections = taggedSections(tag_list)

    def _get_next_not_tag_node(self, cur_node_idx, all_nodes) -> nodes.Node:
        node_num = len(all_nodes)
        for idx in range(cur_node_idx, node_num):
            _ = all_nodes[idx]
            if not isinstance(_, nodes.target):
                return _
        raise NoTaggedNodeError(f'No tagged node found for the tag {all_nodes[cur_node_idx]}')


def get_doc_parsers_from_env(env):
    doc_parsers:dict[str, docParser] = {}
    print('len(env.found_docs)',len(env.found_docs))
    all_doc_names = env.found_docs
    found_doc_list = [env.get_doctree(docname) for docname in env.found_docs]
    first_node = found_doc_list[0]
    
    for _ in found_doc_list:
        assert isinstance(_, first_node.__class__)
    # print('first_node.__class__', first_node.__class__)
    print('all_doc_names', all_doc_names)
    for docname in env.found_docs:
        doc_ = env.get_doctree(docname)
        doc_parsers[docname] = docParser(doc_name=docname, one_doc=doc_)

    return doc_parsers

def get_doc_parsers():
    env_store_path = Path(default_env_store_path)
    if not env_store_path.exists():
        with docutils_namespace():
            env = parse_rst_folder_with_sphinx(doc_core_folder_path)
            document_structure = build_document_structure(env)
            pickle.dump(env, open(env_store_path, 'wb'))
    print('Loaded env from:', env_store_path)
    env = pickle.load(open(env_store_path, 'rb'))
    doc_parsers = get_doc_parsers_from_env(env)
    return doc_parsers
