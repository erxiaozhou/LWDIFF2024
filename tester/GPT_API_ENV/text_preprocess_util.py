import re
from typing import Union


def just_strip(text:str)->str:
    return text.strip('\n\t')

def lower_case(text:str)->str:
    return text.lower()

def lower_case_strip(text:str)->str:
    return lower_case(just_strip(text))


_rempove_mbox_p = re.compile(r'\\mbox\{(.*?)\}')
def process_mbox(text:str)->str:
    text = re.sub(_rempove_mbox_p, lambda x : x.group(1), text)
    return text

def process_sup_brackets(text:str)->str:
    text = text.replace('{}', '')
    text = text.replace(r'{:}', ':')
    text = text.replace(r'{u32}', 'u32')
    text = text.replace(r'{u8}', 'u8')
    text = text.replace(r'{u8}', 'u8')
    text = process_mbox(text)
    return text

def process_macro(paragraph:str)->str:
    strs_and_macros = _match_span_coarse(paragraph)
    final_strs = []
    for item in strs_and_macros:
        if isinstance(item, str):
            final_strs.append(item)
        else:
            final_strs.append(item.simplified_text)
    final_s = ''.join(final_strs)
    return final_s


class TempMacro:
    def __init__(self, raw_text:str):
        self.raw_text = raw_text
        # assert 0, 
        self.simplified_text = _process_macro_core(raw_text)
        # print('In __init__', raw_text, '|||', self.simplified_text)


macro_comb_p = re.compile(r'\\def\\\w+\#1\{\{.*?\}\}\\\w+\{.*?\}')
macro_comb_p = re.compile(r'\\def\\mathdef\d*\#1\{.*\}\\mathdef\d+\{.*?\}')
macro_comb_p = re.compile(r'\\def\\mathdef\d*\#1\{(?:[^\\]|\\(?!mathdef))*\}\\mathdef\d+\{.*?\}')
def _match_span_coarse(paragraph)->list[Union[str, TempMacro]]:
    parsed_match_results:list[tuple[int, int, str]] = []
    # match
    new_paragraph = paragraph
    match_result = re.search(macro_comb_p, new_paragraph)
    last_match_end = 0
    
    while match_result is not None:
        coarse_match = match_result.group(0)
        _start, _end = match_result.span()
        new_paragraph = new_paragraph[_end:]
        _start += last_match_end
        _end += last_match_end
        last_match_end = _end
        # print('||| last_match_end', last_match_end, paragraph[_start:_end])
        assert coarse_match == paragraph[_start:_end]
        parsed_match_results.append((_start, _end, coarse_match))
        match_result = re.search(macro_comb_p, new_paragraph)
        # print('len(new_paragraph)', len(new_paragraph))

    
    final_result = []
    start_char_idx = 0
    for _r_stard_idx, _r_end_idx, _r_text in parsed_match_results:
        assert start_char_idx <= _r_stard_idx
        final_result.append(paragraph[start_char_idx:_r_stard_idx])
        final_result.append(TempMacro(_r_text))
        start_char_idx = _r_end_idx
    may_last_str = paragraph[start_char_idx:]
    if may_last_str:
        final_result.append(may_last_str)
    return final_result

# 
macro_def_pattern = re.compile(r'\\def\\(\w+)\#1\{\{(.*?)\}\}')
macro_def_pattern = re.compile(r'^\\def\\(\w+)\#1\{(.*)\}\\mathdef')
# 
_parsing_para_p = re.compile(r'(\d+)#(\d)(.*)')
macro_call_pattern = re.compile(r'\\(\w+)\{(.*)\}$')
def _process_macro_core(text):
    # no re solution
    mathdef_splited_result = text.split('\\mathdef')
    define_part = mathdef_splited_result[1]
    body_raw_part = mathdef_splited_result[2]
    assert len(mathdef_splited_result) == 3
    # define_idx_repr, define_part = define_part.split('#1')
    # 
    define_idx_repr, para_id, define_part = _parsing_para_p.findall(define_part)[0]
    assert para_id == '1'
    # 
    define_part = define_part[1:-1]
    first_lbrcket_idx = body_raw_part.find('{')
    body_idx_repr = body_raw_part[:first_lbrcket_idx]
    body_part = body_raw_part[first_lbrcket_idx+1:-1]
    assert define_idx_repr == body_idx_repr
    if define_part == '{}':
        final_part = body_part
    else:
        final_part = define_part.replace('#1', body_part)
    # print('body_idx_repr', body_idx_repr, ';;', 'define_part', define_part, ";;", 'body_part', body_part)
    return final_part
