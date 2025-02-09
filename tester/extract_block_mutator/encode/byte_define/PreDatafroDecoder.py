from typing import Any, Callable, Optional

from extract_block_mutator.encode.byte_define.DecoderID import PartDescMemory
from ..NGDataPayload import generate_payload_with_name

from .str2decoder import FixPartDecoderFactory, type_desc_parser
from .NGDecoderP import NGDecoderP
from .CommonBehaviorPart import gen_common_decoder
from ..PartDesc import PartDesc
from util.util import return_para


def the_one_non_prefix_name_optional(attribute_name2type_descs):
    fix_num = 0
    possible_name = None
    for name, desc  in attribute_name2type_descs.items():
        if not FixPartDecoderFactory.support(desc):
            fix_num += 1
            possible_name= name
    if fix_num == 1:
        return possible_name
    return None


def is_only_union_and_get_name(attribute_name2type_descs:dict[str, str])->Optional[str]:
    union_name = None
    if len(attribute_name2type_descs) == 1:
        for name, desc in attribute_name2type_descs.items():
            # if UnionDecoderFactory.support(desc):
            union_name = name
            break
    return union_name
    # for name, desc in attribute_name2type_descs.items():
    #     if name

def _process_name(name:str):
    return name.replace('?','').replace('*','')

def gen_part_desc_by_dicts(
    dicts:list[dict],
    to_wat_component_func:Optional[Callable]=None,
    decoder_name:str='AnyName',
    to_payload_func=None,
    is_section=False,
    return_is_self_payload=None,
    lasy_decode=False,
    support_one_attr_inference=False
    )->PartDesc:
    pass

    datapayload_name= decoder_name
    attribute_names:list[str] = []
    attribute_name2type_descs:dict[str, str] = {}
    attribute_name2decoders:dict[str, NGDecoderP] = {}
    # init
    # for name, type_desc in type_desc_reprs:
    for component_dict in dicts:
        name = component_dict['name']
        name = _process_name(name)
        type_desc = component_dict['type']
        assert name not in attribute_names
        assert name not in attribute_name2type_descs
        if type_desc.lower() == '<vec:byte>':
            type_desc = '<ByteVec>'
        attribute_names.append(name)
        attribute_name2type_descs[name] = type_desc
        
        attribute_name2decoders[name] = type_desc_parser(type_desc)
    
    the_one_union_name = is_only_union_and_get_name(attribute_name2type_descs)
    new_to_wat_component_func, new_return_is_self_payload = get_p_to_wat_component_func(to_wat_component_func, datapayload_name, the_one_union_name)
    if return_is_self_payload is None:
        return_is_self_payload = new_return_is_self_payload
    part_desc = PartDesc(
        attribute_names=attribute_names, 
        attribute_names2init_decoder=attribute_name2decoders, 
        to_wat_component_func=new_to_wat_component_func,
        decoder_name=decoder_name,
        to_payload_func=to_payload_func,
        is_section=is_section,
        return_is_self_payload=return_is_self_payload,
        lasy_decode=lasy_decode,
        support_one_attr_inference=support_one_attr_inference
        )
    return part_desc

def gen_decoder_by_type_desc_reprs_in_dicts(
    dicts:list[dict],
    to_wat_component_func:Optional[Callable]=None,
    decoder_name:str='AnyName',
    to_payload_func=None,
    is_section=False,
    return_is_self_payload=None,
    lasy_decode=False,
    support_one_attr_inference=False
    )->NGDecoderP:
    part_desc = gen_part_desc_by_dicts(
    dicts,
    to_wat_component_func,
    decoder_name,
    to_payload_func,
    is_section,
    return_is_self_payload,
    lasy_decode,
    support_one_attr_inference
    )
    PartDescMemory.register_desc(decoder_name, part_desc)
    return gen_common_decoder(part_desc)


def gen_decoder_by_type_desc_reprs(
    type_desc_reprs:list[tuple[str, str]],
    to_wat_component_func:Optional[Callable]=None,
    decoder_name:str='AnyName',
    to_payload_func=None,
    is_section=False,
    return_is_self_payload=None,
    lasy_decode=False,
    support_one_attr_inference=False
    )->NGDecoderP:
    datapayload_name= decoder_name
    attribute_names:list[str] = []
    attribute_name2type_descs:dict[str, str] = {}
    attribute_name2decoders:dict[str, NGDecoderP] = {}
    # init
    for name, type_desc in type_desc_reprs:
        assert name not in attribute_names
        assert name not in attribute_name2type_descs
        name = _process_name(name)
        if type_desc.lower() == '<vec:byte>':
            type_desc = '<ByteVec>'
        attribute_names.append(name)
        attribute_name2type_descs[name] = type_desc
        
        attribute_name2decoders[name] = type_desc_parser(type_desc)
    # the_one_non_prefix_name = the_one_non_prefix_name_optional(attribute_name2type_descs)
    
    the_one_union_name = is_only_union_and_get_name(attribute_name2type_descs)
    #
    # if return_is_self_payload is None:
    new_to_wat_component_func, new_return_is_self_payload = get_p_to_wat_component_func(to_wat_component_func, datapayload_name, the_one_union_name)
    if return_is_self_payload is None:
        return_is_self_payload = new_return_is_self_payload
    part_desc = PartDesc(
        attribute_names=attribute_names, 
        attribute_names2init_decoder=attribute_name2decoders, 
        to_wat_component_func=new_to_wat_component_func,
        decoder_name=decoder_name,
        to_payload_func=to_payload_func,
        is_section=is_section,
        return_is_self_payload=return_is_self_payload,
        lasy_decode=lasy_decode,
        support_one_attr_inference=support_one_attr_inference
        )
    PartDescMemory.register_desc(decoder_name, part_desc)
    return gen_common_decoder(part_desc)



def get_p_to_wat_component_func(to_wat_component_func:Optional[Callable], datapayload_name:str, the_one_non_prefix_name:Optional[str])->tuple[Callable, bool]:
    if to_wat_component_func is None:
        actual_toactual_actual_mponent_func = return_para
    else:
        # assert 0
        actual_toactual_actual_mponent_func = to_wat_component_func
    is_default_func = actual_toactual_actual_mponent_func is return_para
    # 
    if is_default_func:
        if the_one_non_prefix_name is None:
            func =  lambda data: generate_payload_with_name(PartDescMemory.get_desc(datapayload_name).get_not_fixed_data(data), datapayload_name)
            return_is_self_payload = True
        else:
            func = lambda data: data[the_one_non_prefix_name]
            return_is_self_payload = False
    else:
        # data = PartDescMemory.get_desc(datapayload_name).get_not_fixed_data(data)
        
        func =  lambda data: actual_toactual_actual_mponent_func(generate_payload_with_name(PartDescMemory.get_desc(datapayload_name).get_not_fixed_data(data), datapayload_name))
        return_is_self_payload = False
    return func, return_is_self_payload
