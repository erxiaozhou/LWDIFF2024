from functools import lru_cache
from .log_relation0_kwd import content_relation0_list
from enum import Enum, auto

func_sec_size_mismatch = '<function or section size mismatch>'
runtime_self_unsupport = '<runtime self unsupport>'


class ExceptionInfo(Enum):
    ReferenceUnsupport = auto()
    MultiMemUnsupport = auto()
    TooManyLocal = auto()
    InvalidLocalNum = auto()
    StackOperandOverflow = auto()
    SIMDUnsupport = auto()
    UnknownType = auto()
    SectionMismatch = auto()
    UnexpectedEOF = auto()
    FuncSecMismatch = auto()
    FuncMismatch = auto()
    IllegalType = auto()
    IllegalLocalType = auto()
    LargeAlignment = auto()
    IllegalAlignment = auto()
    MemOOB = auto()
    ExportMemOOB = auto()
    ExportTableOOB = auto()
    TableOOB = auto()
    ElemSegOOB = auto()
    Wasm3StackOverflow = auto()
    UnknownFunction = auto()
    FunctionOOB = auto()

    ZeroByteExpected = auto()
    TypeMismatch = auto()
    IllegalIntEncoding = auto()
    Unreachable = auto()
    Segmentationfault = auto()

    FCOpcode = auto()
    FDOpcode = auto()

    ControlStrcDepthRelated = auto()
    IllegalOpcode = auto()
    IntOverflow = auto()
    DevidebyZero = auto()
    InvalidExportKind = auto()
    GlobalOOB = auto()
    InvalidLeadingByte = auto()

    def __str__(self) -> str:
        return self.name

    def is_size_missmatch(self):
        return self in [ExceptionInfo.SectionMismatch,
                        ExceptionInfo.UnexpectedEOF,
                        ExceptionInfo.FuncSecMismatch,
                        ExceptionInfo.FuncMismatch]

categorize_info_coarse = {
    'divide by zero': ExceptionInfo.DevidebyZero,
    'integer overflow': ExceptionInfo.IntOverflow,
    'memory index reserved byte must be zero': ExceptionInfo.ZeroByteExpected,
    'zero byte expected': ExceptionInfo.ZeroByteExpected,
    'operators remaining after end of function': ExceptionInfo.FuncSecMismatch,
    'expected data but found end of stream': ExceptionInfo.FuncSecMismatch,
    'unexpected end of section or function': ExceptionInfo.FuncSecMismatch,
    'Invalid var_i32': ExceptionInfo.IllegalIntEncoding,
    'Invalid var_i64': ExceptionInfo.IllegalIntEncoding,
    'invalid var_u32': ExceptionInfo.IllegalIntEncoding,
    'integer too large': ExceptionInfo.IllegalIntEncoding,
    'integer representation too long': ExceptionInfo.IllegalIntEncoding,
    'Invalid unsigned LEB encoding': ExceptionInfo.IllegalIntEncoding,
    'Invalid signed LEB encoding': ExceptionInfo.IllegalIntEncoding,
    'invalid function code size': ExceptionInfo.FuncMismatch,
    'end of code reached before end of function': ExceptionInfo.FuncMismatch,
    'section size mismatch': ExceptionInfo.SectionMismatch,
    'section contained more data than expected': ExceptionInfo.SectionMismatch,
    'section overrun while parsing Wasm binary': ExceptionInfo.SectionMismatch,
    'control frames remain at end of function': ExceptionInfo.SectionMismatch,
    'section underrun while parsing Wasm binary': ExceptionInfo.SectionMismatch,
    'trailing bytes at end of section': ExceptionInfo.SectionMismatch,
    'table index out of bounds': ExceptionInfo.TableOOB,
    'out of bounds table access': ExceptionInfo.TableOOB,
    'outOfBoundsTableAccess': ExceptionInfo.TableOOB,
    'unsupported opcode fc': ExceptionInfo.FCOpcode,
    'unsupported opcode fd': ExceptionInfo.FDOpcode,
    'Unknown 0xfd subopcode': ExceptionInfo.FDOpcode,
    'SIMD support is not enabled': ExceptionInfo.SIMDUnsupport,
    'v128 value type requires simd feature': ExceptionInfo.SIMDUnsupport,
    'illegal opcode': ExceptionInfo.IllegalOpcode,
    'Unknown opcode': ExceptionInfo.IllegalOpcode,
    'unsupported opcode': ExceptionInfo.IllegalOpcode,
    'no compiler found for opcode': ExceptionInfo.IllegalOpcode,
    'no operation found for opcode': ExceptionInfo.IllegalOpcode,
    'invalid value type': ExceptionInfo.IllegalType,
    'unknown value_type': ExceptionInfo.IllegalType,
    'unknown value type': ExceptionInfo.IllegalType,
    'malformed value type': ExceptionInfo.IllegalType,
    'unexpected global type': ExceptionInfo.IllegalType,
    'invalid local type': ExceptionInfo.IllegalLocalType,
    'multi-memory not enabled': ExceptionInfo.MultiMemUnsupport,
    'bulk memory support is not enabled': ExceptionInfo.MultiMemUnsupport,
    'multi-memory support is not enabled': ExceptionInfo.MultiMemUnsupport,
    'memoryIndex must be less than module.memories.size': ExceptionInfo.MemOOB,
    'exportIt.index must be less than module.memories.size': ExceptionInfo.ExportMemOOB,
    'exportIt.index must be less than module.tables.size': ExceptionInfo.ExportTableOOB,
    'reachedUnreachable': ExceptionInfo.Unreachable,
    'ExceptionInfo.Unreachable executed': ExceptionInfo.Unreachable,
    'Unknown 0xfc subopcode': ExceptionInfo.FCOpcode,
    'out of bounds memory access': ExceptionInfo.MemOOB,
    'outOfBoundsMemoryAccess': ExceptionInfo.MemOOB,
    'type mismatch': ExceptionInfo.TypeMismatch,
    'non-typed select operands must have the same numeric type': ExceptionInfo.TypeMismatch,
    'unexpected end-of-file': ExceptionInfo.UnexpectedEOF,
    'Unexpected EOF': ExceptionInfo.UnexpectedEOF,
    'alignment must not be larger than natural': ExceptionInfo.LargeAlignment,
    'alignment greater than natural alignment': ExceptionInfo.LargeAlignment,
    'alignment too large': ExceptionInfo.LargeAlignment,
    'Mismatched memory alignment': ExceptionInfo.IllegalAlignment,
    'Invalid alignment': ExceptionInfo.IllegalAlignment,
    'reference types support is not enabled': ExceptionInfo.ReferenceUnsupport,
    'unsupported table element type: ExternRef': ExceptionInfo.ReferenceUnsupport,
    'cannot display funcref values': ExceptionInfo.ReferenceUnsupport,
    'cannot display externref': ExceptionInfo.ReferenceUnsupport,
    'locals exceed maximum': ExceptionInfo.TooManyLocal,
    'local count too large': ExceptionInfo.TooManyLocal,
    'too many locals': ExceptionInfo.TooManyLocal,
    'invalid local count': ExceptionInfo.InvalidLocalNum,
    'outOfBoundsElemSegmentAccess': ExceptionInfo.ElemSegOOB,
    'elemSegmentIndex must be less than module.elemSegments.size()': ExceptionInfo.ElemSegOOB,
    'compiling function overran its stack height limit': ExceptionInfo.StackOperandOverflow,
    'wasm operand stack overflow': ExceptionInfo.StackOperandOverflow,
    'fast interpreter offset overflow': ExceptionInfo.StackOperandOverflow,
    'depth must be less than controlStack': ExceptionInfo.ControlStrcDepthRelated,
    'Expected non-empty control stack': ExceptionInfo.ControlStrcDepthRelated,
    'stack was not empty at end of control structure': ExceptionInfo.ControlStrcDepthRelated,
    '[trap] stack overflow': ExceptionInfo.Wasm3StackOverflow,
    'functionIndex must be less than module.functions.size()': ExceptionInfo.FunctionOOB,
    'function index out of bounds': ExceptionInfo.FunctionOOB,
    'unknown value type': ExceptionInfo.UnknownType,
    'Segmentation fault': ExceptionInfo.Segmentationfault,
    
    'malformed export kind': ExceptionInfo.InvalidExportKind,
    'invalid export kind': ExceptionInfo.InvalidExportKind,
    'global index out of bounds': ExceptionInfo.GlobalOOB,
    'invalid leading byte': ExceptionInfo.InvalidLeadingByte,
    'code section have inconsistent lengths': ExceptionInfo.FuncMismatch,
    'unexpected content after last section': ExceptionInfo.FuncMismatch,
}



@lru_cache(maxsize=4096, typed=False)
def extract_keyword_from_content(content):
    for key in content_relation0_list:
        if key.lower() in content.lower():
            content = key
            break
    return content


@lru_cache(maxsize=4096, typed=False)
def get_categorize_info_fine_summary(content):
    content = categorize_info_coarse.get(content, content)
    return content
