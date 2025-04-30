from pathlib import Path
from util.util import FailedParsingException
from .extract_data_from_GPT_response import GptResponseData
from .ExtractedInfo import ExtractedInfo


def get_extracted_info_core(p: Path):
    assert isinstance(p, Path)
    suffix = p.suffix
    if suffix == '.json':
        inst_info: GptResponseData = GptResponseData.from_json(p)
    elif suffix == '.txt':
        inst_info: GptResponseData = GptResponseData.from_raw_response_file(p)
    extracted_info = ExtractedInfo(inst_info)
    return extracted_info

def extract_and_parse(p):
    assert isinstance(p, Path)
    suffix = p.suffix
    if suffix == '.json':
        inst_info: GptResponseData = GptResponseData.from_json(p)
    elif suffix == '.txt':
        inst_info: GptResponseData = GptResponseData.from_raw_response_file(p)
    exception_information = []
    try:
        extracted_info = get_extracted_info_core(p)
        extracted_info.init_infos_by_gpt_info(exception_on_invalid=True)
    except FailedParsingException as e:
        exception_information.append(f'{e}')
    exception_information.extend(_check_format_part(inst_info))
    exception_information.extend(_check_full_part_type(inst_info))
    if len(exception_information):
        raise FailedParsingException(
            f'Failed to parse the response file {p}. The following exceptions are found:\n{exception_information}')
    return extracted_info


def _check_format_part(inst_info: GptResponseData):
    expected_op_types = {'i32', 'i64', 'f32', 'f64',
                         'v128', 'funcref', 'externref', 'any'}
    expected_imm_types = {'i32', 'i64', 'f32', 'f64', 'funcref', 'externref', 'v128', 'local_idx',
                          'align', 'offset', 'lane_idx', 'table_idx', 'data_idx', 'elem_idx', 'func_idx', 'global_idx'}
    inner_type_part = inst_info.inner_type_part
    exception_info = []
    for k, vs in inner_type_part.items():

        if not isinstance(vs, list):
            vs = [vs]
        if k.startswith('op_'):
            for v in vs:
                if v not in expected_op_types:
                    exception_info.append(
                        f'Unexpected operand type representation: {v}. Pleaze replace {v} with one of {expected_op_types}')
        if k.startswith('imm_'):
            for v in vs:
                if v not in expected_imm_types:
                    exception_info.append(
                        f'Unexpected immediate argument type representation: {v}. Pleaze replace {v} with one of {expected_imm_types}')
    return exception_info


def _check_full_part_type(inst_info: GptResponseData):
    full_type_part = inst_info.full_type_part
    exception_info = []
    assert full_type_part is not None
    for candi_type in full_type_part:
        if not isinstance(candi_type, dict):
            exception_info.append(
                f'The type of the instruction should be a list of mapping with keys `param` and `result`, but got {candi_type}')
            continue
        if set(candi_type.keys()) != {'param', 'result'}:
            exception_info.append(
                f'The keys of the type mapping should be `param` and `result`, but got {set(candi_type.keys())}')
            continue
        params = candi_type['param']
        results = candi_type['result']
        for ty in params:
            info_ = _check_one_val_type_repr(ty)
            if info_ is not None:
                exception_info.extend(info_)
        for ty in results:
            info_ = _check_one_val_type_repr(ty)
            if info_ is not None:
                exception_info.extend(info_)
    return exception_info


def _check_one_val_type_repr(val_repr):
    if val_repr in {'i32', 'i64', 'f32', 'f64', 'v128', 'funcref', 'externref'}:
        return None
    if val_repr == 'any':
        return ['Pleace carefully consider whether `any` is the best choice and try to replace it with a more specific type']
    vals = []
    if not val_repr.endswith('.type'):
        vals.append(
            f'Please consider adding `.type` to the end of the val type representation: {val_repr}')
    if 'imm_' not in val_repr and 'op_' not in val_repr:
        v = f'Please consider use the <imm_xxx> or <op_xxx> to represent a type, rather than {val_repr}'
        vals.append(v)
    return vals


