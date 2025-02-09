import re

from extract_block_mutator.encode.byte_define.str2decoder import _get_sub_decoder_repr
# from extract_block_mutator.NG.byte_define
# _get_sub_decoder_repr
class InvalidTypeDescException(Exception): pass


def common_desc_validation(desc_str):
    # if not (desc_str.startswith('<') and desc_str.endswith('>')):
    #     raise InvalidTypeDescException(f'There should be < and > surrounding {desc_str}')
    if ' ' in desc_str:
        raise InvalidTypeDescException(f'There should not be space in {desc_str}')

def type_desc_is_valid(type_desc: str) -> bool:
    if '|' in type_desc:
        raise InvalidTypeDescException(f"Invalid type descruitopm: {type_desc}, consder using Union:... instead. Additionally, the elements of a Union should always be distinct definitions, not Fix parts. It\'s important to carefully consider the elements of a Union. Please consider using the definitions to form a Union and then represent the definitions respectively.")
    
    # if ''
    try:
        if _is_valid_fix_part(type_desc):
            return True
        if _is_valid_vector_type_desc(type_desc):
            return True
        if _is_valid_array_type_desc(type_desc):
            return True
        if _is_valid_optional_type_desc(type_desc):
            return True
        if _is_valid_union_type_desc(type_desc):
            return True
        if _is_single_type_desc(type_desc):
            return True
    except InvalidTypeDescException as e:
        raise InvalidTypeDescException(f'Invalid type desc: {type_desc}. More details: {str(e)}')
    return False
# =====================================
def extract_terms_from_desc(type_desc:str)->list:
    
    if _is_valid_fix_part(type_desc):
        return []
    if _is_single_type_desc(type_desc):
        return [type_desc]
    if type_desc.startswith('<Vec:'):
        sub_descs = _get_sub_decoder_repr(type_desc[5:-1])
        _names = []
        for sub_desc in sub_descs:
            _names.extend(extract_terms_from_desc(sub_desc))
        return _names
    if type_desc.startswith('<Array:'):
        core_part = type_desc[7:-1]
        part_before_num = ':'.join(core_part.split(':')[:-1])
        sub_descs = _get_sub_decoder_repr(part_before_num)
        _names = []
        for sub_desc in sub_descs:
            _names.extend(extract_terms_from_desc(sub_desc))
        return _names
    if type_desc.startswith('<Optional:'):
        sub_descs = _get_sub_decoder_repr(type_desc[10:-1])
        _names = []
        for sub_desc in sub_descs:
            _names.extend(extract_terms_from_desc(sub_desc))
        return _names
    if type_desc.startswith('<Union:'):
        sub_descs = _get_sub_decoder_repr(type_desc[7:-1])
        _names = []
        for sub_desc in sub_descs:
            _names.extend(extract_terms_from_desc(sub_desc))
        return _names
    raise NotImplementedError(f'Not implemented yet: {type_desc}')

# =====================================

def _check_no_nested(desc_str:str)->bool:
    depth = 0
    max_depth = 0
    for ch in desc_str:
        if ch == '<':
            depth += 1
        elif ch == '>':
            depth -= 1
        if depth > max_depth:
            max_depth = depth
        if depth > 1:
            return False
        if depth < 0:
            raise InvalidTypeDescException(f'Invalid desc: {desc_str}')
    return max_depth > 1


hex_p = re.compile(r'(?:0[xX])?[0-9a-fA-F]+')
def is_hex_str(s:str)->bool:
    return bool(hex_p.fullmatch(s))


def _is_valid_fix_part(desc_str: str) -> bool:
    common_desc_validation(desc_str)
    core_str = desc_str[1:-1]
    if not core_str.startswith('Fix'):
        return False
    # check whether the paras are valid
    if not(core_str.count(':') == 2):
        raise InvalidTypeDescException(f'Wrong para count in {desc_str}; Required: 2, but got: {core_str.count(":")}')
    all_parts = core_str.split(':')
    para_parts = all_parts[1:]
    # if not is_hex_str(para_parts[0]):
    #     raise InvalidTypeDescException(f'Invalid para0: {para_parts[0]} in {desc_str}')
    if para_parts[1] not in {'u32', 'hex', 'str', 'byte'}:
        raise InvalidTypeDescException(f'Invalid para0: {para_parts[1]} in {desc_str}')
    return True

def _is_valid_vector_type_desc(desc_str: str) -> bool:
    # print('desc1:', desc_str)
    common_desc_validation(desc_str)
    core_str = desc_str[1:-1]
    if not core_str.startswith('Vec:'):
        return False
    all_parts = core_str.split(':')
    sub_decoder_repr = ':'.join(all_parts[1:-1])
    if not type_desc_is_valid(sub_decoder_repr):
        raise InvalidTypeDescException(f'Invalid sub_decoder_repr: {sub_decoder_repr} in {desc_str}')
    return True

def _is_valid_optional_type_desc(desc_str: str) -> bool:
    common_desc_validation(desc_str)
    core_str = desc_str[1:-1]
    if not core_str.startswith('Optional:'):
        return False
    all_parts = core_str.split(':')
    sub_decoder_repr = ':'.join(all_parts[1:-1])
    if not type_desc_is_valid(sub_decoder_repr):
        raise InvalidTypeDescException(f'Invalid sub_decoder_repr: {sub_decoder_repr} in {desc_str}')
    return True
def _is_valid_array_type_desc(desc_str: str) -> bool:
    common_desc_validation(desc_str)
    core_str = desc_str[1:-1]
    if not core_str.startswith('Array:'):
        return False
    all_parts = core_str.split(':')
    sub_decoder_repr = ':'.join(all_parts[1:-1])
    if not type_desc_is_valid(sub_decoder_repr):
        raise InvalidTypeDescException(f'Invalid sub_decoder_repr: {sub_decoder_repr} in {desc_str}')
    
    if not core_str.split(':')[-1].isdigit():
        raise InvalidTypeDescException(f'Invalid para: {core_str.split(":")[-1]} in {desc_str}')
    return True

def _is_single_type_desc(type_desc: str) -> bool:
    if ':' in type_desc:
        return False
    if type_desc.isdigit():
        raise InvalidTypeDescException(f'Invalid type desc: {type_desc}. It should be a type, rather than a constant number.')
    return True

def _is_valid_union_type_desc(desc_str: str) -> bool:
    # print('XXXX desc2:', desc_str)
    core_str = desc_str[1:-1]
    # print('XXXX core_str:', core_str)
    if not core_str.startswith('Union:'):
        return False
    sub_reprs = _get_sub_decoder_repr(core_str[6:])
    if all([x.strip('<').startswith('Fix') for x in sub_reprs]):
        raise InvalidTypeDescException(f'Invalid type representation: {desc_str}, since the elements of a Union should always be distinct definitions, not fixed parts. It\'s important to carefully consider the elements of a Union. Please consider using the definitions to form a Union and then represent the definitions respectively.')
    if any([x.strip('<').startswith('Fix') for x in sub_reprs]):
        raise InvalidTypeDescException(f'Invalid type representation: {desc_str}, since the elements of a Union should always be distinct definitions, not fixed parts. ')
    if len(sub_reprs) < 2:
        raise InvalidTypeDescException(f'Invalid type representation: {desc_str}. A union should have at least 2 elements.')
    # if 
    # if all(['Fix' in sub_repr for sub_repr in sub_reprs]):
    #     raise InvalidTypeDescException(f'Invalid type representation: {desc_str}, since the elements of a Union should always be distinct definitions, not fixed parts. It\'s important to carefully consider the elements of a Union. Please consider using the definitions to form a Union and then represent the definitions respectively.')
    for sub_repr in sub_reprs:
        if not type_desc_is_valid(sub_repr):
            raise InvalidTypeDescException(f'Invalid sub_repr: {sub_repr} in {desc_str}')
    return True
