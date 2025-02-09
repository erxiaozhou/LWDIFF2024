from typing import List, Optional

from extract_block_mutator.encode.new_defined_data_type import Blocktype
from ..typeReq import typeReq, merge_req
from ..funcType import funcType
from ..funcTypeFactory import funcTypeFactory
from ..InstUtil import Inst, get_insts_ty_req
from ..InstGeneration.InstFactory import InstFactory


start_block_ops = set([
    'block', 'loop', 'if'
])

shold_not_in_dblock = {
    'block', 'loop', 'if', 'else', 'end'
}

class wasmBlock:
    def __init__(self, inner_blocks:Optional[list]=None, block_type: Optional[funcType] = None):
        if inner_blocks is not None: 
            for block in inner_blocks:
                assert block is None or isinstance(block, wasmBlock)
        self.inner_blocks = inner_blocks
        self.block_type = block_type

    def has_no_contained_block(self):
        return self.inner_blocks is None or len(self.inner_blocks) == 0

    def get_type(self, context=None):
        raise NotImplementedError()

    def get_ty_req(self):
        raise NotImplementedError()

    def as_insts(self):
        raise NotImplementedError()

    def copy(self):
        inner_blocks = []
        for block in self.inner_blocks:
            if block is None:
                inner_blocks.append(None)
            else:
                inner_blocks.append(block.copy())
        return self.__class__(inner_blocks, block_type=self.block_type)


class mixWasmBlock(wasmBlock):
    def __init__(self, inner_blocks, block_type: Optional[funcType] = None):
        # assert inner_blocks is not None
        # assert len(inner_blocks) > 1, print([_.__class__.__name__ for _ in inner_blocks])
        super().__init__(inner_blocks=inner_blocks, block_type=block_type)
        assert self.inner_blocks is not None
        assert len(self.inner_blocks) > 1, print([_.__class__.__name__ for _ in self.inner_blocks])

    def get_ty_req(self, context=None):
        # If the block has no contained block, it should be recognized as a direct block
        # and its type is inferred by the function directWasmBlock._infer_self_type
        assert self.inner_blocks is not None and len(self.inner_blocks) > 1
        assert not self.has_no_contained_block()
        base_req = self.inner_blocks[0].get_ty_req(context)
        for block in self.inner_blocks[1:]:
            result = merge_req(base_req, block.get_ty_req(context))
            # print('base_req', base_req, ';;', 'block_req', block.get_ty_req(context))
            # print('result result', result)
            base_req = result
        if base_req is None or base_req.impossible():
            print(f'{self.__class__.__name__};;In get_type ; Fail to infer block type.{[block.get_ty_req(context) for block in self.inner_blocks]}\n{[block.__class__.__name__ for block in self.inner_blocks]}', )
        return base_req

    def get_type(self, context=None):
        if self.block_type is not None:
            result = self.block_type
        else:
            ty_req = self.get_ty_req(context)
            assert not ty_req.impossible(), print(self.__class__.__name__)
            result = ty_req.tys[0]
        return result
    
    def as_insts(self):
        _insts = []
        for block in self.inner_blocks:
            _insts.extend(block.as_insts())
        return _insts

    def inst_num(self):
        return sum([block.inst_num() for block in self.inner_blocks])

class directWasmBlock(wasmBlock):
    def __init__(self, insts: Optional[List[Inst]], block_type: Optional[funcType] = None):
        super().__init__(inner_blocks=None, block_type=block_type)
        self.insts = insts
        if self.insts is not None:
            for inst in self.insts:
                assert inst.opcode_text not in shold_not_in_dblock

    def copy(self):
        if self.insts is None:
            return directWasmBlock(None, block_type=self.block_type)
        else:
            return directWasmBlock(self.insts.copy(), block_type=self.block_type)

    @property
    def uninitialized(self):
        return self.insts is None

    def get_ty_req(self, context=None):
        if self.block_type is not None:
            return typeReq.from_one_ty(self.block_type)

        inst_ty_req =  get_insts_ty_req(self.insts, context)
        assert not inst_ty_req.impossible(), print('Fail to infer the type requirement of directWasmBlock', self.insts)

    def get_type(self, context=None):
        if self.block_type is not None:
            return self.block_type
        ty_req = self.get_ty_req(context)
        assert not ty_req.impossible()
        return ty_req.tys[0]
    def as_insts(self):
        return [i.copy() for i in self.insts]

    def inst_num(self):
        return len(self.insts)


class ifWasmBlock(wasmBlock):
    def __init__(self, inner_blocks=None, block_type: Optional[funcType] = None):
        super().__init__(inner_blocks=inner_blocks, block_type=block_type)
        assert len(self.inner_blocks) == 2

    def get_ty_req(self, context=None):
        # self_type = self.inner_blocks[0].get_type(context)
        # if self.inner_blocks[1] is not None:
        #     assert self.inner_blocks[1].get_type(context) == self_type
        self_type = self.get_type(context)
        if_ty = funcTypeFactory.generate_one_func_type_default(param_type=self_type.param_types + ['i32'], result_type=self_type.result_types)
        return typeReq.from_one_ty(if_ty)

    def get_type(self, context=None):
        if self.block_type is not None:
            return self.block_type
        return self.inner_blocks[0].get_ty_req(context).ty0

    def as_insts(self):
        if self.inner_blocks[1] is None:
            _insts = [
                InstFactory.gen_binary_info_inst_high_single_imm('if', Blocktype(self.get_type()))
                ] + \
                self.inner_blocks[0].as_insts() + [InstFactory.opcode_inst('end')
                                                   ]
        else:
            _insts = [
                InstFactory.gen_binary_info_inst_high_single_imm('if', Blocktype(self.get_type()))
                ] + \
            self.inner_blocks[0].as_insts() + \
                [InstFactory.opcode_inst('else')] + \
                    self.inner_blocks[1].as_insts() + [InstFactory.opcode_inst('end')
            ]
        return _insts

    def inst_num(self):
        if self.inner_blocks[1] is None:
            return 2 + self.inner_blocks[0].inst_num()
        else:
            return 3 + self.inner_blocks[0].inst_num() + self.inner_blocks[1].inst_num()

    @classmethod
    def from_if_block(cls, if_block: wasmBlock, block_type: Optional[funcType] = None):
        inner_blocks = [if_block, None]
        return cls(inner_blocks=inner_blocks, block_type=block_type)

    @classmethod
    def from_if_else_block(cls, if_block: wasmBlock, else_block: wasmBlock, block_type: Optional[funcType] = None):
        inner_blocks = [if_block, else_block]
        return cls(inner_blocks=inner_blocks, block_type=block_type)


class loopWasmBlock(wasmBlock):
    def __init__(self, inner_blocks=None, block_type: Optional[funcType] = None):
        super().__init__(inner_blocks=inner_blocks, block_type=block_type)
        assert len(self.inner_blocks) == 1

    def get_type(self, context=None):
        if self.block_type is not None:
            return self.block_type
        inner_req = self.inner_blocks[0].get_ty_req(context)
        inner_req_ty = inner_req.ty0
        return inner_req_ty

    def get_ty_req(self, context=None):
        return typeReq.from_one_ty(self.get_type(context))

    def as_insts(self):
        loop_inst = InstFactory.gen_binary_info_inst_high_single_imm('loop', Blocktype(self.get_type()))
        return [loop_inst] + self.inner_blocks[0].as_insts() + [InstFactory.opcode_inst('end')]
    def inst_num(self):
        return 2 + self.inner_blocks[0].inst_num()


class blockWasmBlock(wasmBlock):
    def __init__(self, inner_blocks=None, block_type: Optional[funcType] = None):
        super().__init__(inner_blocks=inner_blocks, block_type=block_type)
        assert len(self.inner_blocks) == 1


    def get_type(self, context=None):
        if self.block_type is not None:
            return self.block_type
        return self.inner_blocks[0].get_ty_req(context).ty0

    def get_ty_req(self, context=None):
        return typeReq.from_one_ty(self.get_type(context))

    def as_insts(self):
        block_inst = InstFactory.gen_binary_info_inst_high_single_imm('block', Blocktype(self.get_type()))
        return [block_inst] + self.inner_blocks[0].as_insts() + [InstFactory.opcode_inst('end')]
    def inst_num(self):
        return 2 + self.inner_blocks[0].inst_num()
