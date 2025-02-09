import pickle
from typing import Optional
from file_util import save_json
from ..parsing_spec_util.FullExtractedText import FullExtractedText
from ..parsing_spec_util.customNode import customNode
from ..parsing_spec_util.ref_log_util import oneRefLog
from ..prepare_data_env.get_background import SpecSearchEngine
from ..prompt_util.util import get_inst_name2exec_inst_name
from .filter import is_contain_op_cnode
from .ref_locator import get_may_op_cnodes
from ..project_cfg import inst_op_info_path
from ..project_cfg import last_inst_op_info_json_path


def get_inst_name2op_desc_practical(enforce_re_generate=False)->dict[str, str]:
    if enforce_re_generate or not inst_op_info_path.exists():
        print('Generate inst_name2op_desc')
        info_ = generate_inst_name2op_desc()
        pickle.dump(info_, open(inst_op_info_path, 'wb'))
        save_json(last_inst_op_info_json_path, info_)
    else:
        print('Load inst_name2op_desc')
        info_ = pickle.load(open(inst_op_info_path, 'rb'))
    return info_


def generate_inst_name2op_desc():
    inst_name2exec_inst_name = get_inst_name2exec_inst_name()
    op_text_search_engine = SpecSearchEngine.get_exec_numeric_default()
    full_search_engine = SpecSearchEngine.get_default()
    full_text = full_search_engine.full_extracted_text
    inst_name2op_desc = {}
    for inst_name, exec_inst_name in inst_name2exec_inst_name.items():
        # if inst_name not in  ['i32.add', 'i32.eqz']:
        #     continue
        exec_fmt_cnode = get_exec_fmt_cnode(full_search_engine, exec_inst_name)
        op_desc = generate_op_desc_for_exec_cnode(
            inst_name,
            exec_fmt_cnode,
            full_text,
            op_text_search_engine
        )
        if op_desc:
            inst_name2op_desc[inst_name] = op_desc
    return inst_name2op_desc


def get_exec_fmt_cnode(search_engine, exec_inst_name):
    exec_info_q = f'execution (exec) of the instruction {exec_inst_name}'
    _, cnodes, _ = search_engine.search_with_cnodes(exec_info_q, k=1)
    target_exec_node: customNode = cnodes[0]
    return target_exec_node


def generate_op_desc_for_exec_cnode(
    inst_name: str,
    cnode: customNode,
    full_text: FullExtractedText,
    op_text_search_engine: SpecSearchEngine
) -> str:
    if not _need_generate_desc_for_cnode(cnode):
        return ''
    else:
        op_cnodes, ref_logs = _locate_op_cnodes_to_desc(
            inst_name,
            cnode,
            full_text,
            op_text_search_engine
        )
        descs = []
        for cnode, ref_log in zip(op_cnodes, ref_logs):
            desc = _generate_desc_for_one_op_cnode(cnode, ref_log)
            descs.append(desc)

        final_desc = _combine_op_cnode_sescs(descs)
        return final_desc


def _need_generate_desc_for_cnode(cnode: customNode) -> bool:
    return is_contain_op_cnode(cnode)


def _locate_op_cnodes_to_desc(
    inst_name: str,
    cnode: customNode,
    full_text: FullExtractedText,
    op_text_search_engine: SpecSearchEngine
) -> tuple[list[customNode], list[Optional[oneRefLog]]]:
    # s1 : ops are mentioned in the cnode
    cnodes_s1, ref_logs_s1 = get_may_op_cnodes(full_text, cnode)
    # s2 : ops are determined by search
    q_fmt = '{}'
    q = q_fmt.format(inst_name)
    _, cnodes, ds = op_text_search_engine.search_with_cnodes(q, k=5)
    titles = [cnode.all_title_repr for cnode in cnodes]
    ds = ds.tolist()
    c0 = cnodes[0]
    result_cnodes = cnodes_s1 + [c0]
    result_ref_logs = ref_logs_s1 + [None]
    return result_cnodes, result_ref_logs
    
    # TODO 
    raise NotImplementedError


def _generate_desc_for_one_op_cnode(cnode: customNode, ref_log: Optional[oneRefLog]) -> str:
    cnode_text = cnode.simplified_text
    if ref_log is not None:
        represented_text = ref_log.wrapped_content
        desc_template = f'The description of the operation {represented_text} is:\n\n{cnode_text}'
        return desc_template
    else:
        # print('No ref log for cnode:', cnode.all_title_repr)
        # print('cnode.title_info.simplified_text', cnode.title_info.simplified_text)
        represented_text =  cnode.title_info.simplified_text
        cnode_text = cnode.simplified_text
        desc_template = f'The description of the operation {represented_text} is:\n\n{cnode_text}'
        return desc_template
        raise NotImplementedError

    raise NotImplementedError


def _combine_op_cnode_sescs(descs: list[str]) -> str:
    s = '\n\n\n'.join(descs)
    return s
