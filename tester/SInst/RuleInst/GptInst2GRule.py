from pathlib import Path
from typing import Callable
from config_inst_info import gpt_data_v2_dir
from config_inst_info import control_inst_names
from config_inst_info import all_inst_names
from ..RuleInst.RuleV2 import RuleV2
from .ValidRulesG import ValidInstGenerator
from .ExtractedInfo import ExtractedInfo
from .CheckAndParseInstInfo import  get_extracted_info_core
from tqdm import tqdm


def _get_support_ops(support_ops):
    if support_ops is None:
        support_ops = (all_inst_names | {
                       'select_1C~t'}) - control_inst_names - {'else', 'end'}
    else:
        support_ops = set(support_ops)
    return support_ops


class GptInstKM:
    _raw_inst_name2op_name: dict[str, str] = {}
    _raw_op_name2rules: dict[str, list[RuleV2]] = {}
    raw_inst_name2valid_context_func: dict[str, Callable] = {}
    raw_inst_name2ValidInstGenerator: dict[str, ValidInstGenerator] = {}
    polished = False
    _has_init_naive_solver_info = False
    _has_init_gpt_specs = False

    def __init__(self,
                 support_ops=None,
                 json_spec_base_dir=gpt_data_v2_dir,
                 just_valid_part: bool = False,
                 ):
        self.support_ops: set[str] = _get_support_ops(support_ops)
        all_extracted_infos = {}
        total_num = len(list(Path(json_spec_base_dir).iterdir()))
        for p in tqdm(Path(json_spec_base_dir).iterdir(), desc='Parsing GPT specs', total=total_num):
            if not (p.name.endswith('.json') or p.name.endswith('_response.txt')):
                continue
            extracted_info: ExtractedInfo = get_extracted_info_core(
                p)
            raw_inst_name = extracted_info.raw_inst_name
            if raw_inst_name in self.support_ops:
                all_extracted_infos[raw_inst_name] = extracted_info

                extracted_info.init_infos_by_gpt_info()
                if not just_valid_part:
                    extracted_info.polish_rules()
        for raw_inst_name, extracted_info in all_extracted_infos.items():
            self._raw_inst_name2op_name[raw_inst_name] = extracted_info.op
            self._raw_op_name2rules[raw_inst_name] = extracted_info.rules
            self.raw_inst_name2valid_context_func[raw_inst_name] = extracted_info.valid_context_func
            self.raw_inst_name2ValidInstGenerator[raw_inst_name] = extracted_info.valid_inst_generator


    def get_rules_by_op(self, op):
        return GptInstKM._raw_op_name2rules[op]

