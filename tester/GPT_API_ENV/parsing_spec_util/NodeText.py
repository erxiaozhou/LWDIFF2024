from ..text_preprocess_util import just_strip, process_macro, process_sup_brackets
from ..message_util import MAX_EBD_TOKEN_NUM, text_oversize
from .ref_log_util import clean_font
from .ref_log_util import match_xref_core
from docutils import nodes


class NodeText:
    def __init__(self, node:nodes.Node, remove_title=True):
        
        self.node = node
        self.remove_title = remove_title
        # 
        raw_text = node.astext()
        if remove_title and isinstance(node, nodes.section) and node.next_node(nodes.title):
            title_text = node.next_node(nodes.title).astext()
            assert raw_text.startswith(title_text)
            raw_text = raw_text[len(title_text):]
            
        self.raw_text = raw_text
        self.ref_logs = self._init_ref_logs()
        self.unique_ref_logs = list(set(self.ref_logs))
        # 
        self._simplified_text = None
        self._no_math_raw_text = None
        self._no_math_simple_text = None

    @property
    def no_math_text(self):
        if self._no_math_raw_text is None:
            text = ''
            for _n in self.node.children:
                if self.remove_title and isinstance(_n, nodes.title):
                    continue
                if isinstance(_n, nodes.math_block):
                    continue
                _cur_text = _n.astext()
                if _cur_text:
                    text = text + '\n' + _cur_text
            self._no_math_raw_text = text
        return self._no_math_raw_text

    @property
    def no_math_simplified_text(self)->str:
        if self._no_math_simple_text is None:
            _no_math_simple_text = self._simply_text_core(self.no_math_text)
            _no_math_simple_text = just_strip(_no_math_simple_text)
            self._no_math_simple_text = _no_math_simple_text
        return self._no_math_simple_text

    @property
    def simplified_text(self)->str:
        if self._simplified_text is None:
            _simplified_text = self._simply_text_core(self.raw_text)
            _simplified_text = just_strip(_simplified_text)
            # assert 0
            # print('Before', _simplified_text)
            # print('*******************************************')
            _simplified_text = process_macro(_simplified_text)
            _simplified_text = process_sup_brackets(_simplified_text)
            self._simplified_text = _simplified_text
        return self._simplified_text

    @property
    def no_math_simplified_text_oversize(self)->bool:
        return text_oversize(self.no_math_simplified_text)

    @property
    def simplified_text_oversize(self)->bool:
        return text_oversize(self.simplified_text)

    def _simply_text_core(self, s):
        no_font_text = clean_font(s)
        simplified_text = self.simplify_ref_in_str(no_font_text)
        return simplified_text

    def _init_ref_logs(self):
        no_font_text: str = clean_font(self.raw_text)
        ref_logs = match_xref_core(no_font_text)
        return ref_logs

    def simplify_ref_in_str(self, s:str)->str:
        for ref_log in self.ref_logs:
            s = ref_log.simplify_ref_in_str(s)
        return s

