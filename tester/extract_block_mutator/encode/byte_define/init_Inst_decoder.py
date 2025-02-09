from functools import partial
from config_inst_info import raw_binary_info
from config_inst_info import inst_bynary_type_desc_path
from extract_block_mutator.InstUtil.Inst import NoImmInst
from ...InstGeneration.InstFactory import InstFactory
from .NGDecoderP import NGDecoderP
from file_util import read_json, save_json
from ..util import is_hex_str, is_imm_u32
from ..util import get_default_prefix_name
from ..byte_define.PreDatafroDecoder import gen_decoder_by_type_desc_reprs

u32_imm_types = {
    'funcidx',
    'tableidx',
    'localidx',
    'typeidx',
    'elemidx',
    'offset',
    'dataidx',
    'globalidx',
    'labelidx',
    'laneidx',
    'align',
}
# init_u32_imm_types
for imm_repr in u32_imm_types:
    gen_decoder_by_type_desc_reprs(
        type_desc_reprs=[(imm_repr, '<u32>')],
        decoder_name=imm_repr
    )



def to_payload_func_for_inst(x):
    if isinstance(x, NoImmInst):
        return None
    # print('HHHHHHHHHHHHHHHHHH x', x)
    return x.imm_part

def get_inst_decoder() -> dict[str, NGDecoderP]:
    inst_name2type_desc_repr = _get_inst_name2type_desc_repr()
    inst_name2decoders: dict[str, NGDecoderP] = {}
    for inst_name, type_desc_reprs in inst_name2type_desc_repr.items():
        # print('===== Cur processing inst name:', inst_name)
        # print('||||||||| type_desc_reprs:', type_desc_reprs)
        inst_name2decoders[inst_name] = gen_decoder_by_type_desc_reprs(
            type_desc_reprs=type_desc_reprs,
            # to_wat_component_func=lambda x : InstFactory.generate_binary_info_inst(inst_name, x),
            to_wat_component_func=partial(
                InstFactory.generate_binary_info_inst,
                inst_name
            ),
            to_payload_func=to_payload_func_for_inst,
            decoder_name=inst_name,
            return_is_self_payload=True,
            # lasy_decode=True,
            support_one_attr_inference=True
            # use_l
        )
    return inst_name2decoders


def get_all_ng_names():
    names = set()
    for name in _get_inst_name2type_desc_repr().keys():
        names.add(name)
    return names


def _get_inst_name2type_desc_repr():
    '''
    * for structured insts, which contains insts, we just process the parts before insts
    * for common insts, we follow the same way
    * for end, er add it manually
    '''
    if not inst_bynary_type_desc_path.exists():
        inst_name2processed_text_repr = {}
        for inst_name, descs in raw_binary_info.items():
            name_and_tys = []
            # pre-process the original text
            for desc in descs:
                name, ty = _parse_one_token_desc(desc)
                # print('ASDASD ty', ty)
                if ty.startswith('inst'):  # if it is a structured inst
                    # re-check whether it is a structured inst
                    last_repr, last_ty = _parse_one_token_desc(descs[-1])
                    assert last_repr == '0B' and last_ty == 'hex', descs
                    # assert 0
                    break
                
                name_and_tys.append((name, ty))
            inst_name2processed_text_repr[inst_name] = name_and_tys
        #
        inst_name2type_desc_repr = {}
        for inst_name, name_and_tys in inst_name2processed_text_repr.items():
            # print(inst_name, name_and_tys)
            # # new_repr
            # assert len(name_and_tys) == 2
            # raw_repr, raw_ty_desc = name_and_tys[0]
            new_descs:list[tuple[str, str]] = []
            for idx, (raw_repr, raw_ty_desc) in enumerate(name_and_tys):
                new_repr, new_ty_desc = _process_one_part(raw_repr, raw_ty_desc, idx)
                new_descs.append((new_repr, new_ty_desc))
            inst_name2type_desc_repr[inst_name] = new_descs
        inst_name2type_desc_repr['end'] = [(get_default_prefix_name(0), '<Fix:0B:hex>')]
        inst_name2type_desc_repr['else'] = [(get_default_prefix_name(0), '<Fix:05:hex>')]
        save_json(inst_bynary_type_desc_path, inst_name2type_desc_repr)
    inst_name2type_desc_repr = read_json(inst_bynary_type_desc_path)
    # print('len(inst_name2type_desc_repr)', len(inst_name2type_desc_repr))
    return inst_name2type_desc_repr


def _parse_one_token_desc(token_desc:str):
    assert token_desc.startswith('<') and token_desc.endswith('>'), token_desc
    token_desc = token_desc[1:-1]
    # assert token_desc.count(':') == 1, token_desc
    eachparts = token_desc.split(':')
    name = eachparts[0].strip()
    ty = ':'.join([t.strip() for t in eachparts[1:]])
    return name, ty


def _process_one_part(repr_:str, type_:str, idx:int)->tuple[str,str]:
    assert ' ' not in repr_, repr_
    if is_hex_str(repr_) and type_ in {'u32', 'hex'}:
        type_repr = f'<Fix:{repr_}:{type_}>'
        name = get_default_prefix_name(idx)
        return name, type_repr
    else:
        name = repr_
        try:
            type_repr = _get_type_repr_by_raw_repr(type_)
        except NotImplementedError:
            print(f'Not implemented for repr:{repr_};; type:{type_}')
            type_repr = 'xxxx'
        return name, type_repr
    raise NotImplementedError(f'Not implemented for repr:{repr_};; type:{type_}')


def _get_type_repr_by_raw_repr(raw_type_repr:str)->str:
    # if 'vec'
    # raw_type_repr = raw_type_repr.strip(' *')
    if is_imm_u32(raw_type_repr):
        return raw_type_repr
        return '<u32>'
    if raw_type_repr in {'f32', 'f64', 'i32', 'i64', 'byte'}:
        return f'<{raw_type_repr}>'
    if raw_type_repr == 'valtype':
        return '<valtype>'
    if raw_type_repr == 'reftype':
        return '<valtype>'
    if raw_type_repr == 'blocktype':
        return '<blocktype>'
    if ':' in raw_type_repr:
        # * array pattern
        sub_paras = raw_type_repr.split(':')
        sub_repr = _get_type_repr_by_raw_repr(sub_paras[0])
        repeat_time = sub_paras[1]
        return f'<Array:{sub_repr}:{repeat_time}>'
    if raw_type_repr.endswith('*'):  # * there is a possible empry ph 
        empty_repr = '<empty>'  # empty 's repr
        main_raw_repr = raw_type_repr.strip(' *')
        main_repr = _get_type_repr_by_raw_repr(main_raw_repr)
        return f'<Union:{main_repr}:{empty_repr}>'
    if raw_type_repr.startswith('vec(') and raw_type_repr.endswith(')'):
        sub_ty = raw_type_repr[4:-1]
        sub_repr = _get_type_repr_by_raw_repr(sub_ty)
        return f'<Vec:{sub_repr}>'
    raise NotImplementedError(f'Not implemented for {raw_type_repr}')


