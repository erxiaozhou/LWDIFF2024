from ..parsing_spec_util.FullExtractedText import FullExtractedText
from ..parsing_spec_util.customNode import customNode
from ..parsing_spec_util.ref_log_util import oneRefLog
from ..prepare_data_env.get_background import SpecSearchEngine
from ..prompt_util.util import get_inst_name2exec_inst_name


def get_inst_names_contain_op():
    inst_name2exec_fmt = get_inst_name2exec_inst_name()
    exec_fmt2inst_names = {}
    for inst_name, exec_fmt in inst_name2exec_fmt.items():
        exec_fmt2inst_names.setdefault(exec_fmt, []).append(inst_name)
    exec_fmts = exec_fmt2inst_names.keys()
    op_inst_names = []
    search_engine: SpecSearchEngine = SpecSearchEngine.get_default()
    
    for exec_fmt in exec_fmts:
        exec_cnode = _get_exec_fmt_cnode(search_engine, exec_fmt)
        if is_contain_op_cnode(exec_cnode):
            inst_names = exec_fmt2inst_names[exec_fmt]
            op_inst_names.extend(inst_names)
    return op_inst_names


def _get_exec_fmt_cnode(search_engine: SpecSearchEngine, exec_fmt:str)->customNode:
    exec_info_q = f'execution (exec) of the instruction {exec_fmt}'
    _, cnodes, _ = search_engine.search_with_cnodes(exec_info_q, k=1)
    exec_fmt_cnode = cnodes[0]
    return exec_fmt_cnode


def is_contain_op_cnode(cnode:customNode)->bool:
    unique_ref_logs = cnode.unique_ref_logs
    for ref_log in unique_ref_logs:
        if _ref_log_may_contain_op(ref_log):
            return True
        # whethre contain a reference to specific positions
        # print(f'|| == ref_log: {ref_log}')
    return False
    

def _ref_log_may_contain_op(ref_log:oneRefLog):
    if ref_log.doc_name == 'syntax/instructions':
        if ref_log.ref_name.endswith('op'):
            return True
    if ref_log.doc_name == 'exec/numerics':
        if ref_log.ref_name.startswith('op'):
            return True
    if ref_log.doc_name == 'syntax/instructions':
        if ref_log.ref_name == 'syntax-instr-numeric' or ref_log.ref_name == 'syntax-instr-vec':
            if ref_log.wrapped_content != 'const':
                return True
    return False
