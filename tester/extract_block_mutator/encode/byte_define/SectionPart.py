from file_util import read_json
from .PreDatafroDecoder import gen_decoder_by_type_desc_reprs
from .PreDatafroDecoder import gen_decoder_by_type_desc_reprs_in_dicts
from ..util import FailedDecodeException, get_default_prefix_name
from ..NGDataPayload import DataPayloadwithName

from .init_Inst_decoder import get_all_ng_names, get_inst_decoder
from ..new_defined_data_type import Blocktype
from ...funcTypeFactory import funcTypeFactory
from ..PartDesc import PartDesc
from .CommonBehaviorPart import gen_common_decoder
from .structure_decoder import UnionPart
from .DecoderID import DecoderMemory, PartDescMemory
from ...InstUtil.Inst import Inst
from .NGDecoderP import NGDecoderP
from ...watFunc import watFunc
from typing import List
from util.encoding_util import read_next_leb_num
from singleton_decorator import singleton
import leb128
from WasmInfoCfg import globalValMut
from config_inst_info import desc_path

raw_desc_dict = read_json(desc_path)

def gen_from_desc_dict(desc_dict:dict, decoder_name:str, **kwds):
    dicts:list = desc_dict[decoder_name]
    # 
    if kwds.get('is_section'):
        if dicts[1]['type'] != 'u32' or len(dicts) < 3:
            dicts.insert(
                1, {
                    "name": "section_length",
                    "type": "u32"
                    
                }
            )
    # 
    paras = {
        'dicts': dicts,
        'decoder_name':decoder_name
    }
    paras.update(kwds)
    decoder = gen_decoder_by_type_desc_reprs_in_dicts(**paras)
    return decoder

def gen_fix_content_encoder(encoder_name, encoding, encoded):
    def new_to_payload_func(to_encoded_val):
        if to_encoded_val != encoded:
            raise FailedDecodeException
        return DataPayloadwithName(
            data ={'type_repr': encoded},
            name=encoder_name
        )
    return gen_decoder_by_type_desc_reprs(
        type_desc_reprs = [
            ('type_repr', f'<Fix:{hex(encoding)}:hex>')
        ],
        decoder_name=encoder_name,
        to_wat_component_func=lambda x : encoded,
        to_payload_func= new_to_payload_func
    )

gen_fix_content_encoder('i32_tyrepr', 0x7F, 'i32')
gen_fix_content_encoder('i64_tyrepr', 0x7E, 'i64')
gen_fix_content_encoder('f32_tyrepr', 0x7D, 'f32')
gen_fix_content_encoder('f64_tyrepr', 0x7C, 'f64')
gen_fix_content_encoder('v128_tyrepr', 0x7B, 'v128')
gen_fix_content_encoder('funcref_tyrepr', 0x70, 'funcref')
gen_fix_content_encoder('externref_tyrepr', 0x6F, 'externref')
gen_fix_content_encoder('mut_mut', 0x01, globalValMut.Mut)
gen_fix_content_encoder('mut_const', 0x00, globalValMut.Const)


gen_from_desc_dict(raw_desc_dict, 'reftype')
gen_from_desc_dict(raw_desc_dict, 'numtype')
gen_from_desc_dict(raw_desc_dict, 'vectype')
gen_from_desc_dict(raw_desc_dict, decoder_name='valtype')




gen_from_desc_dict(raw_desc_dict, 'functype',
    to_wat_component_func =lambda x:  funcTypeFactory.generate_one_func_type_default(
        param_type=x.data['param'], result_type=x.data['result']),
    to_payload_func= lambda x: DataPayloadwithName(
       data={ 'param': x.param_types,
        'result':x.result_types},
       name='functype'
    )
)


gen_from_desc_dict(raw_desc_dict, 'limits_without_max')
gen_from_desc_dict(raw_desc_dict, 'limits_with_max')
gen_from_desc_dict(raw_desc_dict, 'limits')

gen_from_desc_dict(raw_desc_dict, 'tabletype')
gen_from_desc_dict(raw_desc_dict, 'globaltype')



EmptyBlockTypePart = gen_decoder_by_type_desc_reprs(
    type_desc_reprs=[
        ('blocktype', '<Fix:40:hex>')
    ],
    decoder_name='EmptyBlockTypePart',
    to_wat_component_func = lambda x:True,
)

IntReprBlockTypePart = gen_decoder_by_type_desc_reprs(
    type_desc_reprs=[
        ('blocktype', '<i33>')
    ],
    decoder_name='IntReprBlockTypePart',

)

ValTypeReprBlockTypePart = gen_decoder_by_type_desc_reprs(
    type_desc_reprs=[
        ('blocktype', '<valtype>')
    ],
    decoder_name='ValTypeReprBlockTypePart',
 
)

funcTypeReprBlocktypePart = gen_decoder_by_type_desc_reprs(
    type_desc_reprs=[
        ('blocktype', '<functype>')
        
    ],
    decoder_name='funcTypeReprBlocktypePart',

)

def blocktype2payload_func(bty:Blocktype)->DataPayloadwithName:
    # print('===========================bty.init_data', bty.init_data)
    init_data = bty.init_data
    if isinstance(init_data, int) and (not isinstance(init_data, bool)):
        return DataPayloadwithName(
            data={'blocktype': init_data},
            name='IntReprBlockTypePart'
        )
    elif isinstance(init_data, str):
        return DataPayloadwithName(
            data={'blocktype': init_data},
            name='ValTypeReprBlockTypePart'
        )
    # elif isinstance(init_data, funcType):
    #     return DataPayloadwithName(
    #         data={'blocktype': init_data},
    #         name='funcTypeReprBlocktypePart'
    #     )
    elif isinstance(init_data, bool):
        return DataPayloadwithName(
            data={'blocktype': init_data},
            name='EmptyBlockTypePart'
        )
    else:
        raise Exception(f'Unknown type of blocktype: {init_data}, type: {type(init_data)}')

BlockTypePart = gen_decoder_by_type_desc_reprs(
    type_desc_reprs=[
        ('blocktype', '<Union:<EmptyBlockTypePart>:<ValTypeReprBlockTypePart>:<IntReprBlockTypePart>')
    ],
    decoder_name='blocktype',
    to_wat_component_func = lambda x:Blocktype(x['blocktype']),
    to_payload_func=blocktype2payload_func
)


InstD = gen_common_decoder(
    part_desc=PartDesc(
        attribute_names=['inst'],
        attribute_names2init_decoder= {
            'inst': UnionPart(
           sub_decoders= list(get_inst_decoder().values())
        )
        },
        to_wat_component_func=lambda data: data['inst'],
        to_payload_func= lambda x: DataPayloadwithName(
            data={'inst': x},
            name=x.opcode_text
        ),
        decoder_name='Inst'
        
    )
)

op_has_no_imm_by_opcode2 = set()
for name in get_all_ng_names():
    desc = PartDescMemory.get_desc(name)
    if desc.not_prefix_num == 0:
        op_has_no_imm_by_opcode2.add(name)


Expr = gen_decoder_by_type_desc_reprs(
    type_desc_reprs=[
        ('expr', '<Inst>'),
        (get_default_prefix_name(0),  '<Fix:0B:hex>')
    ],
    decoder_name='Expr',
)



gen_from_desc_dict(raw_desc_dict, 'global')

gen_from_desc_dict(raw_desc_dict, 'memtype')

gen_from_desc_dict(raw_desc_dict, 'memory')


gen_from_desc_dict(raw_desc_dict, 'passive_def')



gen_from_desc_dict(raw_desc_dict, 'active_memory_zero')



# memidx

gen_from_desc_dict(raw_desc_dict, 'memidx')
gen_from_desc_dict(raw_desc_dict, 'funcidx')
gen_from_desc_dict(raw_desc_dict, 'globalidx')
gen_from_desc_dict(raw_desc_dict, 'tableidx')

gen_from_desc_dict(raw_desc_dict, 'active_memory_index')



gen_from_desc_dict(raw_desc_dict, 'data')
gen_from_desc_dict(raw_desc_dict, 'func_importdesc')

gen_from_desc_dict(raw_desc_dict, 'table_importdesc')

gen_from_desc_dict(raw_desc_dict, 'mem_importdesc')

gen_from_desc_dict(raw_desc_dict, 'global_importdesc')

gen_from_desc_dict(raw_desc_dict, 'import')


gen_from_desc_dict(raw_desc_dict, 'func_exportdesc')
gen_from_desc_dict(raw_desc_dict, 'table_exportdesc')
gen_from_desc_dict(raw_desc_dict, 'mem_exportdesc')
gen_from_desc_dict(raw_desc_dict, 'global_exportdesc')

gen_from_desc_dict(raw_desc_dict, 'export')



gen_from_desc_dict(raw_desc_dict, 'elemkind',
    to_wat_component_func = lambda x: 'funcref',
    to_payload_func= lambda x: DataPayloadwithName(
        data={'val': 'funcref'},
        name='elemkind'
    ))

gen_from_desc_dict(raw_desc_dict, 'active_elem_seg0')
gen_from_desc_dict(raw_desc_dict, 'passive_elem_seg0')
gen_from_desc_dict(raw_desc_dict, 'active_elem_seg1')
gen_from_desc_dict(raw_desc_dict, 'declarative_elem_seg0')
gen_from_desc_dict(raw_desc_dict, 'active_elem_seg2')
gen_from_desc_dict(raw_desc_dict, 'passive_elem_seg1')
gen_from_desc_dict(raw_desc_dict, 'active_elem_seg3')
gen_from_desc_dict(raw_desc_dict, 'declarative_elem_seg1')
gen_from_desc_dict(raw_desc_dict, 'element_segment')


gen_from_desc_dict(raw_desc_dict, 'locals')



LocalsPart = gen_decoder_by_type_desc_reprs(
    type_desc_reprs=[
        ('locals', '<Vec:<locals>>')
    ],
    decoder_name='LocalsPart',
)



type_sec_decoder = gen_from_desc_dict(raw_desc_dict, 'typesec',
    to_wat_component_func= lambda data: data['ft'],
    is_section=True
)
#

function_sec_decoder = gen_from_desc_dict(raw_desc_dict, 'function_section',
    to_wat_component_func= lambda data: data['section_content'],
    is_section=True
)



memory_sec_decoder=gen_from_desc_dict(raw_desc_dict, 'memory_section', 
    to_wat_component_func= lambda data: data['memories'],is_section=True)

gen_from_desc_dict(raw_desc_dict, 'table')


table_sec_decoder=gen_from_desc_dict(raw_desc_dict, 'tablesec', 
    to_wat_component_func= lambda data: data['tables'],is_section=True)



global_sec_decoder=gen_from_desc_dict(raw_desc_dict, 'global_section',
    to_wat_component_func= lambda data: data['globals'],
    is_section=True
)


start_sec_decoder = gen_from_desc_dict(raw_desc_dict, 'start')
start_sec_decoder = gen_from_desc_dict(
    raw_desc_dict, 'start_section',
    is_section=True,
    to_wat_component_func= lambda data: data['start_function']
)


export_sec_decoder = gen_from_desc_dict(
    raw_desc_dict, 'export_section',
    to_wat_component_func= lambda data: data['exports'],
    is_section=True,
)



import_sec_decoer=gen_from_desc_dict(raw_desc_dict, 'import_section', 
    to_wat_component_func= lambda data: data['imports'],is_section=True)


data_count_sec_decoder = gen_from_desc_dict(
    raw_desc_dict, 'data_count_section',
    is_section=True,
    to_wat_component_func= lambda data: data['n']
)


elem_sec_decoder = gen_from_desc_dict(
    raw_desc_dict, 'element_section',
    is_section=True,
    to_wat_component_func= lambda data: data['element_segments']
)


data_sec_decoder = gen_from_desc_dict(
    raw_desc_dict, 'data_section',
    is_section=True,
    to_wat_component_func= lambda data: data['data_segments']
)

@singleton
class FuncDecoder(NGDecoderP):

    def byte_decode_and_generate(self, ba_view:memoryview):
        size, offset = read_next_leb_num(ba_view, 0)
        max_offset = size+ offset
        cur_offset = offset
        
        raw_locals, local_offset = LocalsPart.byte_decode_and_generate(ba_view[cur_offset:])
        # 
        locals = []
        for local_def in raw_locals:
            for i in range(local_def['count']):
                locals.append(local_def['value_type'])
        # 
        insts:List[Inst] = []
        cur_offset += local_offset
        actual_length = size +  offset
        
        no_end_insts_max_size = max_offset - 1
        while cur_offset < no_end_insts_max_size:  # * -1 for the inst `end`
            
            inst, offset = InstD.byte_decode_and_generate(ba_view[cur_offset:])
            cur_offset += offset
            insts.append(inst)
        
        return watFunc(
            insts=insts,
            defined_local_types=locals,
            func_ty=None
        ), actual_length


    def encode(self, val: watFunc):
        corecore_core_lt = bytearray()
        local_ba = LocalsPart.encode(val.locals_with_def_repr)
        corecore_core_lt.extend(local_ba) # type: ignore
        for inst in val.insts:
            corecore_core_lt += InstD.encode(inst)
        corecore_core_lt.append(0x0b)
        core_len = len(corecore_core_lt)
        size_ba = leb128.u.encode(core_len)
        return size_ba + corecore_core_lt
            

    def prefix_info(self) -> memoryview:
        return memoryview(bytes())

FuncPart = FuncDecoder()
DecoderMemory.register_decoder('Func', FuncPart)

# 
code_sec_decoder = gen_from_desc_dict(
    raw_desc_dict, 'code_section',
    is_section=True,
    to_wat_component_func= lambda data: data['code_entries']
)



custom_sec_decoder = gen_decoder_by_type_desc_reprs(
    type_desc_reprs=[
        ('name', '<utf8str>'),
        ('payload', '<AllSizeG:byte>')
    ],
        decoder_name='custom',
)
custom_sec_decoder = gen_from_desc_dict(
    raw_desc_dict, 
    decoder_name='custom_section',
    is_section=True
)

section_decoder = gen_decoder_by_type_desc_reprs(
    type_desc_reprs=[
        ('section', '<Union:custom_section:typesec:function_section:import_section:tablesec:memory_section:global_section:export_section:start_section:element_section:code_section:data_count_section:data_section>')
    ],
        decoder_name='Section',
        
)

module_decoder = gen_decoder_by_type_desc_reprs(
    type_desc_reprs=[
        (get_default_prefix_name(0), '<Fix:0_61_73_6d_1_0_0_0:bytes>'),
        ('sections', '<AllSizeG:Section>')
    ],
        decoder_name='Module',
        to_wat_component_func= lambda data: data['sections'],
)
