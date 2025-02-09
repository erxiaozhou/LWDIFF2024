import re
from typing import List, Optional


core_line_p1 = re.compile(r'\(elem(?: \(;\d+;\))? (.*)\)$')
core_line_p2 = re.compile(r'\s*(?:\(table (\d+)\))?\s*(?:\(i32.const ([\-\d]+)\))?\s*(.+)$')


def parse_elem_line(elem_lime):
    
    core_line = core_line_p1.findall(elem_lime)
    assert len(core_line)
    core_line = core_line[0].strip()
    
    # 
    core_part_result = core_line_p2.findall(core_line)
    assert len(core_part_result) == 1
    core_part_result = core_part_result[0]
    table_idx = None if not core_part_result[0] else int(core_part_result[0])
    offset = None if not core_part_result[1] else int(core_part_result[1])
    rest_part = core_part_result[2]
    # parsing rest part
    p1_result = _parsing_p1(rest_part)
    p2_result = _parsing_p2(rest_part)
    p3_result = _parsing_p3(rest_part)
    rs = [p1_result, p2_result, p3_result]
    assert len([x for x in rs if x is not None]) == 1, print(rest_part, rs)
    if p1_result is not None:
        has_declare, ref_type, null_and_func_idxs = p1_result
    elif p2_result is not None:
        has_declare, ref_type, null_and_func_idxs = p2_result
    else:
        assert p3_result is not None
        has_declare, ref_type, null_and_func_idxs = p3_result
    
    return (table_idx, offset, has_declare, ref_type, null_and_func_idxs)


_externref_p = re.compile(r'(declare)?\s*externref((?:\s*\(ref\.null\s+extern\))*)$')
def _parsing_p1(line) -> Optional[tuple]:
    p1 = _externref_p
    parsing_result = p1.findall(line)
    if len(parsing_result):
        parsing_result = parsing_result[0]
        has_declare = True if parsing_result[0] == 'declare' else False
        ref_type = 'externref'
        ref_null_count = parsing_result[1].count('(ref.null extern)')
        # print(parsing_result, ref_null_count)
        null_and_func_idx_repr = [None for _ in range(ref_null_count)]
        # TODO
        return (has_declare, ref_type, null_and_func_idx_repr)
    return None

func_ref_p = re.compile(r'(declare)?\s*func((?:\s*\d+)*)$')
def _parsing_p2(line) -> Optional[tuple]:
    p2 = func_ref_p
    parsing_result = p2.findall(line)
    if len(parsing_result):
        parsing_result = parsing_result[0]
        # print('parsing_result[0]', f'<{parsing_result[0]}>')
        has_declare = True if parsing_result[0] == 'declare' else False
        func_idxs = [int(x) for x in parsing_result[1].split() if x]
        ref_type = 'funcref'
        # TODO
        return (has_declare, ref_type,  func_idxs)
    return None


elem_sec_p3 = re.compile(r'(declare)?\s*funcref((?:\s*(?:(?:\(ref\.func\s+\d+\))|(?:\(ref\.null\s+func\))))*)$')
def _parsing_p3(line) -> Optional[tuple]:
    p3 = elem_sec_p3
    parsing_result = p3.findall(line)
    if len(parsing_result):
        parsing_result = parsing_result[0]
        # TODO
        has_declare = True if parsing_result[0] == 'declare' else False
        null_and_func_idxs = _parse_p3_elems(line)
        ref_type = 'funcref'
        return (has_declare, ref_type, null_and_func_idxs)
    return None

inner_brackts_p = re.compile(r'\(([^()]+)\)')
def _parse_p3_elems(line)->List[Optional[int]]:
    inner_contents = inner_brackts_p.findall(line)
    # print(inner_contents)
    null_and_func_idxs = []
    for s in inner_contents:
        if s == 'ref.null func':
            null_and_func_idxs.append(None)
        else:
            assert s.startswith('ref.func ')
            idx = int(s[len('ref.func '):])
            null_and_func_idxs.append(int(idx))
    return null_and_func_idxs

    
