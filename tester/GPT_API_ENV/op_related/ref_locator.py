from ..parsing_spec_util.FullExtractedText import FullExtractedText
from ..parsing_spec_util.customNode import customNode
from ..parsing_spec_util.ref_log_util import oneRefLog


def refs_in_cnode(cnode:customNode)->list[oneRefLog]:
    unique_ref_logs = cnode.unique_ref_logs
    contain_op_ref_logs = []
    for ref_log in unique_ref_logs:
        if _ref_log_refers_to_op(ref_log):
            contain_op_ref_logs.append(ref_log)
    return contain_op_ref_logs


def get_may_op_cnodes(full_text:FullExtractedText, cnode: customNode)-> tuple[list[customNode], list[oneRefLog]]:
    contain_op_ref_logs = refs_in_cnode(cnode)
    may_op_cnodes = []
    for ref_log in contain_op_ref_logs:
        cnode = full_text.get_cnode_by_ref_log(ref_log)
        may_op_cnodes.append(cnode)
    return may_op_cnodes, contain_op_ref_logs
    

def _ref_log_refers_to_op(ref_log:oneRefLog):
    if ref_log.doc_name == 'exec/numerics':
        if ref_log.ref_name.startswith('op'):
            return True
    return False
