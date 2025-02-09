from ast import Tuple
from pathlib import Path
from typing import Callable, List, Optional
from ..project_cfg import op_name2exec_fmt_json_path
from file_util import save_json
from ..parsing_spec_util.FullExtractedText import FullExtractedText
from ..parsing_spec_util.customNode_filter import cNodeFilterStrategy, get_customNode_filter
from ..parsing_spec_util.customNode import customNode
from .prepare_data_env import get_full_extracted_text
from .prepare_data_env import get_op_name2exec_fmt
from ..project_cfg import text2embedding_data_text_dir
from ..project_cfg import text2embedding_data_embedding_dir
from ..project_cfg import text2embedding_dim
from ..message_util import get_emb_array_from_text
from faiss import IndexFlatIP
import numpy as np
import hashlib
from enum import Enum


class searchTextStrategy(Enum):
    ByTitle = 0
    ByContent = 1


class TextReprStrategy(Enum):
    SimpliedTextWithTitle = 0
    NoMathSimplifiedTextWithTitle = 1
    SimpliedTextWithoutTitle = 2
    NoMathSimplifiedTextWithoutTitle = 3
    

def get_repr_for_cnode(cnode:customNode, title:str, text_repr_strategy:TextReprStrategy)->str:
    if text_repr_strategy == TextReprStrategy.SimpliedTextWithTitle:
        return f'{title}\n{cnode.simplified_text}'
    if text_repr_strategy == TextReprStrategy.NoMathSimplifiedTextWithTitle:
        return f'{title}\n{cnode.no_math_simplified_text}'
    if text_repr_strategy == TextReprStrategy.SimpliedTextWithoutTitle:
        return cnode.simplified_text
    if text_repr_strategy == TextReprStrategy.NoMathSimplifiedTextWithoutTitle:
        return cnode.no_math_simplified_text
    raise NotImplementedError


class FullTextSearchStrategy:
    def __init__(self,
                    cnode_filter_strategy:cNodeFilterStrategy,
                    search_strategy:searchTextStrategy,
                    contain_ref:bool,
                    text_repr_strategy:TextReprStrategy
                 ):
        self.cnode_filter_strategy = cnode_filter_strategy
        self.search_strategy = search_strategy
        self.contain_ref = contain_ref
        self.text_repr_strategy = text_repr_strategy

    def __repr__(self):
        return f'FullTextSearchStrategy({self.cnode_filter_strategy}, {self.search_strategy}, {self.contain_ref}, {self.text_repr_strategy})'

    @classmethod
    def get_default(cls):
        return cls(
            cnode_filter_strategy=cNodeFilterStrategy.NOT_APPENDIX_IS_LEAF_NOT_ABBR,
            search_strategy=searchTextStrategy.ByTitle,
            contain_ref=False,
            text_repr_strategy=TextReprStrategy.SimpliedTextWithTitle
        )
    @classmethod
    def get_default_debug(cls):
        return cls(
            cnode_filter_strategy=cNodeFilterStrategy.NOT_TOO_LONG_NOT_APPENDIX,
            search_strategy=searchTextStrategy.ByTitle,
            contain_ref=False,
            text_repr_strategy=TextReprStrategy.SimpliedTextWithTitle,
            # text_repr_strategy=TextReprStrategy.NoMathSimplifiedTextWithoutTitle,
        )


# one paragraph level =========================================
def get_embedding_pratical(text)->np.ndarray:
    text_path = _get_text_path(text)
    embedding_path = _get_embedding_path(text)
    if (not embedding_path.exists()) or (not text_path.exists()):
        embedding = get_emb_array_from_text(text)
        embedding = embedding.reshape(1, -1)
        np.save(embedding_path, embedding)
        text_path.write_text(text)
    else:
        # embedding = np.fromfile(embedding_path, dtype=np.float32)
        embedding = np.load(embedding_path)
    embedding = embedding.reshape(1, -1)
    # print('In get_embedding_pratical:', type(embedding), embedding.shape)
    return embedding


def _get_text_path(text:str)->Path:
    text_hash = _get_text_hash(text)
    return text2embedding_data_text_dir / f'{text_hash}.txt'


def _get_embedding_path(text:str)->Path:
    text_hash = _get_text_hash(text)
    return text2embedding_data_embedding_dir / f'{text_hash}.npy'


def _get_text_hash(text:str):
    # text = text.strip('\n \t')
    # text
    return hashlib.sha256(text.encode()).hexdigest()
    # return hex(hash(text).)[2:]

def clean_generated_files():
    for p in text2embedding_data_text_dir.iterdir():
        p.unlink()
    for p in text2embedding_data_embedding_dir.iterdir():
        p.unlink()

# one paragraph level end =========================================
# full search engine =========================================

class _TextSearchEngine:
    '''
    only conduct **search** for a list of texts
    does not conduct **map** or other operations
    '''
    def __init__(self, texts:list[str]):
        embeddings = [get_embedding_pratical(text) for text in texts]
        self.texts = texts
        self.embeddings = embeddings
        self.embedding_index = IndexFlatIP(text2embedding_dim)
        for embedding in embeddings:
            # print(type(embedding), embedding.shape)
            self.embedding_index.add(embedding)

    def seatch_by_text(self, q_test:str, k:int=1, debug=False):
        return self.search_by_text_with_idx(q_test, k=k, debug=debug)[0]

    def search_by_text_with_idx(self, q_test:str, k:int=1, debug=False):
        distances, indices = self._search_by_text_core(q_test, k=k, debug=debug)
        # print('=== indices', indices)
        texts = [self.texts[i] for i in indices]
        return texts, indices, distances

    def _search_by_text_core(self, q_test:str, k:int=1, debug=False):
        q_embedding = get_embedding_pratical(q_test)
        distances, indices = self.embedding_index.search(q_embedding, k=k)
        # print('distances', distances)
        distances = distances[0]
        indices = indices[0]
        if debug:
            print('len(indices)', len(indices))
            print('len(distances)', len(distances), distances)
            print_search_result(self.texts, distances, indices)
        return distances, indices


def print_search_result(ori_texts, distances, indices):
    def _repr_one_text(text:str):
        if len(text) < 60:
            return text
        return text[:60] + '...'
    for i, (d, text_idx) in enumerate(zip(distances, indices)):
        # print(idx)
        print(f'{i}: {d}     {text_idx}     {_repr_one_text(ori_texts[text_idx])}')

class TextScopeStrategy(Enum):
    Full = 0
    ExecNumeric = 1
    AllBinary = 2
    AllValid = 3

class SpecSearchEngine:
    def __init__(self, search_strategy:Optional[FullTextSearchStrategy]=None, text_strategy=TextScopeStrategy.Full):
        if search_strategy is None:
            search_strategy = FullTextSearchStrategy.get_default()
        self.search_strategy = search_strategy
        # 
        full_extracted_text: FullExtractedText = get_full_extracted_text()
        self.full_extracted_text = full_extracted_text
        # 
        op_name2exec_fmt = get_op_name2exec_fmt()
        self.op_name2exec_fmt = op_name2exec_fmt
        save_json(op_name2exec_fmt_json_path, op_name2exec_fmt)
        # 
        self._title_text_base:Optional[_TextSearchEngine] = None
        # keys : the keys for search
        # key2result_func : a function, get the text from the key
        if text_strategy == TextScopeStrategy.Full:
            considered_nodes = self._get_full_considered_cnodes(self.search_strategy.cnode_filter_strategy)
        elif text_strategy == TextScopeStrategy.ExecNumeric:
            considered_nodes = self._get_exec_numeric_cnodes(self.search_strategy.cnode_filter_strategy)
        elif text_strategy == TextScopeStrategy.AllBinary:
            considered_nodes = self.get_all_binary_cnodes(self.search_strategy.cnode_filter_strategy)
        elif text_strategy == TextScopeStrategy.AllValid:
            considered_nodes = self.get_all_valid_cnodes(self.search_strategy.cnode_filter_strategy)
        else:
            raise ValueError(f'Unknown text_strategy: {text_strategy}')
        self.considered_nodes = considered_nodes

        if self.search_strategy.search_strategy == searchTextStrategy.ByTitle:
            keys, key2result_func = self._get_keys_and_key2result_func_for_by_title(considered_nodes)
        elif self.search_strategy.search_strategy == searchTextStrategy.ByContent:
            keys, key2result_func = self._get_keys_and_key2result_func_for_by_content(considered_nodes)
        else:
            raise NotImplementedError
        self.keys = keys
        self.key2result_func = key2result_func
        self._text_search_engine = _TextSearchEngine(keys)

    def _get_full_considered_cnodes(self, strategy:cNodeFilterStrategy)->list[customNode]:
        cnode_filter = get_customNode_filter(strategy)
        cnodes = self.full_extracted_text.all_cnodes
        cnodes = cnode_filter.get_expected_nodes(cnodes)
        return cnodes

    def _get_exec_numeric_cnodes(self, strategy:cNodeFilterStrategy)->list[customNode]:
        all_cnodes = self._get_full_considered_cnodes(strategy)
        exec_numeric_cnodes = []
        for cnode in all_cnodes:
            if cnode.is_exec_numeric:
                exec_numeric_cnodes.append(cnode)
        return exec_numeric_cnodes

    def get_all_binary_cnodes(self, strategy:cNodeFilterStrategy)->list[customNode]:
        all_cnodes = self._get_full_considered_cnodes(strategy)
        exec_numeric_cnodes = []
        for cnode in all_cnodes:
            if cnode.is_binary:
                exec_numeric_cnodes.append(cnode)
        return exec_numeric_cnodes

    def get_all_valid_cnodes(self, strategy:cNodeFilterStrategy)->list[customNode]:
        all_cnodes = self._get_full_considered_cnodes(strategy)
        exec_numeric_cnodes = []
        for cnode in all_cnodes:
            if cnode.is_valid:
                exec_numeric_cnodes.append(cnode)
        return exec_numeric_cnodes

    @classmethod
    def get_default(cls):
        return cls(FullTextSearchStrategy.get_default())

    @classmethod
    def get_exec_numeric_default(cls):
        return cls(FullTextSearchStrategy.get_default(), text_strategy=TextScopeStrategy.ExecNumeric)

    @classmethod
    def get_all_binary_default(cls):
        return cls(FullTextSearchStrategy.get_default(), text_strategy=TextScopeStrategy.AllBinary)

    @classmethod
    def get_all_valid_default(cls):
        return cls(FullTextSearchStrategy.get_default(), text_strategy=TextScopeStrategy.AllValid)

    def search(self, q:str, k:int=1):
        searched_keys = self._text_search_engine.seatch_by_text(q, k=k)
        searched_keys, _, distances = self._text_search_engine.search_by_text_with_idx(q, k=k)
        results = [self.key2result_func(key) for key in searched_keys]
        return results

    def search_with_cnodes(self, q:str, k:int=1):
        # searched_keys = self._text_search_engine.seatch_by_text(q, k=k)
        searched_keys, key_idxs, distances = self._text_search_engine.search_by_text_with_idx(q, k=k)
        results = [self.key2result_func(key) for key in searched_keys]
        related_nodes = [self.considered_nodes[idx] for idx in key_idxs]
        return results, related_nodes, distances

    def _get_keys_and_key2result_func_for_by_title(self, considered_nodes: list[customNode])->tuple[list, Callable[[str], str]]:
        key2texts = {}
        keys = []
        for n in considered_nodes:
            k = n.all_title_repr
            keys.append(k)
            key2texts[k] = get_repr_for_cnode(n, n.all_title_repr, self.search_strategy.text_repr_strategy)
        def key2result_func(key:str):
            return key2texts[key]
        return keys, key2result_func

    def _get_keys_and_key2result_func_for_by_content(self, considered_nodes: list[customNode])->tuple[list, Callable[[str], str]]:
        keys = [get_repr_for_cnode(n, n.all_title_repr, self.search_strategy.text_repr_strategy) for n in considered_nodes]
        func_ = lambda key: key
        return keys, func_

    def _get_q_embedding(self, q_test:str):
        return get_embedding_pratical(q_test)
