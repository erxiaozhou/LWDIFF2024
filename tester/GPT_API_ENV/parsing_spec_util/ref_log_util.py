import re
from typing import List, Optional


#  remove font ===================================================================
to_clean_wrappers = [
    ('\\mathsf{', '}'),
    ('\\mathit{', '}'),
    ('\\mathrm{', '}'),
    ('\\mathtt{', '}'),
]
to_clean_head2end = {
    _[0]:_[1] for _ in to_clean_wrappers
}


def clean_font(s:str)->str:
    # 1. locate the wrappers
    located_spans:list[tuple[tuple[int, int], tuple[str, str]]] = []
    matched_stack:list[tuple[str, int]] = []
    i=0
    end_i = len(s)
    heads = [wrapper[0] for wrapper in to_clean_wrappers]
    while i < end_i:
        start_head = _cur_s_starts_with_target_heads(s[i:], heads)
        if start_head is not None:
            matched_stack.append((start_head, i))
            i += len(start_head)
            continue
        if matched_stack:
            last_matched_head = matched_stack[-1][0]
            target_end_head = to_clean_head2end[last_matched_head]
            if s.startswith(target_end_head, i):
                located_spans.append(((matched_stack[-1][1], i), (last_matched_head, target_end_head)))
                matched_stack.pop()
                i += len(target_end_head)
                continue
            else:
                i += 1
        else:
            i += 1
    # 2. determine the spans to remove
    to_remove_spans:list[tuple[int, int]] = []
    for span, (head, end) in located_spans:
        start_span = (span[0], span[0] + len(head))
        end_span = (span[1], span[1] + len(end))
        to_remove_spans.append(start_span)
        to_remove_spans.append(end_span)
    # clean
    to_remove_spans.sort(key=lambda x:x[0], reverse=True)
    chars = list(s)
    for start, end in to_remove_spans:
        chars[start:end] = []
    cleaned_s = ''.join(chars)
    return cleaned_s
#  end remove font ===================================================================


class tagRepr:
    def __init__(self, doc_name:str, inner_tag_name:str):
        self.doc_name = doc_name
        self.inner_tag_name = inner_tag_name
        
    def __hash__(self) -> int:
        return hash((self.doc_name, self.inner_tag_name))
    
    def __eq__(self, o: object) -> bool:
        assert isinstance(o, tagRepr)
        return self.doc_name == o.doc_name and self.inner_tag_name == o.inner_tag_name
    
    def __str__(self) -> str:
        return f'{self.doc_name}::{self.inner_tag_name}'


# parse xref ===================================================================
refhead_pattern = re.compile(r'\\xref\{([^}]+)\}\{([^}]+)\}')


def _cur_s_starts_with_target_heads(s:str, heads:list[str])->Optional[str]:
    for head in heads:
        if s.startswith(head):
            return head
    return None


class oneRefLog:
    # fmt = '\\xref{' + '{}'+ '}' + '{' + '{}'+ '}' + '{' + '{}'+ '}'
    def __init__(self, 
                 doc_name:str, 
                 ref_name:str, 
                 wrapped_content:str
                 ):
        self.doc_name = doc_name
        self.ref_name = ref_name
        self.wrapped_content = wrapped_content

    def referred_tag_repr(self)->tagRepr:
        return tagRepr(self.doc_name, self.ref_name)

    def __eq__(self, o: object) -> bool:
        assert isinstance(o, oneRefLog)
        return self.doc_name == o.doc_name and self.ref_name == o.ref_name and self.wrapped_content == o.wrapped_content
    
    def __hash__(self) -> int:
        return hash((self.doc_name, self.ref_name, self.wrapped_content))

    @property
    def raw_text(self):
        # return f'\\xref{{{self.doc_name}}}{{{self.ref_name}}}{{{self.wrapped_content}}}'
        return ''.join(('\\xref{', self.doc_name, '}{', self.ref_name, '}{', self.wrapped_content, '}'))

    def __repr__(self):
        return f'{self.__class__.__name__}({self.doc_name}, {self.ref_name}, {self.wrapped_content})'

    def simplify_ref_in_str(self, s:str)->str:
        return s.replace(self.raw_text, self.wrapped_content)


def match_xref_core(s)->List[oneRefLog]:
    ref_logs = []
    spans = []
    content = []
    for m in refhead_pattern.finditer(s):
        spans.append(m.span())
        content.append(m.groups())
        # print(m.span(), m.groups())
        # print(s[m.span()[0]:m.span()[1]])
        head_start, head_end = m.span()
        content_start = head_end 
        content_len = _get_matched_rbracket_idx(s[content_start:])
        # print(s[head_end])
        # print(s[content_start], s[content_start + content_len])
        assert s[content_start + content_len] == '}'
        assert s[content_start] == '{'
        assert s[head_start] == '\\', s[head_start]
        doc_name, ref_name = m.groups()
        wrapped_content = s[content_start+1:content_start + content_len]
        cur_log = oneRefLog(doc_name, ref_name, wrapped_content)
        ref_logs.append(cur_log)
    for _log in ref_logs:
        assert _log.raw_text in s
    # assert 0
    return ref_logs
    

def _get_matched_rbracket_idx(s)->int:
    assert s.startswith('{')
    bracket_depth = 0
    for idx, c in enumerate(s):
        if c == '{':
            bracket_depth += 1
        elif c == '}':
            bracket_depth -= 1
            if bracket_depth == 0:
                return idx
    raise ValueError(f'No matching right bracket found: {s}')

# end parse xref ===================================================================
