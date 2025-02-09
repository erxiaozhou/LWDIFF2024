from file_util import path_read, check_dir, read_json, save_json
from pathlib import Path
from typing import Dict, List, Optional, Union
import json
from WasmInfoCfg import val_type_strs
from util.util import FailedParsingException


def repr_val(val):
    if isinstance(val, (dict, list)):
        return val
    return str(val)

class GptResponseData:
    def __init__(self,
                 inst_name: str,
                 inner_type_part: dict,
                 validate_part: dict,
                 execution_part: List,
                 full_type_part: Optional[list] = None
                 ):
        
        self.raw_inst_name = inst_name
        op, inst_name = _get_op_from_raw_name(inst_name)
        self.op = op
        self.full_type_part = full_type_part
        # checkinner_type_part
        for k, type_repr in inner_type_part.items():
            if not k.startswith('op_') and not k.startswith('imm_'):
                raise FailedParsingException(f'The representation for immediate arguments or operands should start with "op_" or "imm_",and ened with a number representing the operand /immediate argument index, ranther than {k}')
            # if 
        self.inner_type_part = inner_type_part
        if not isinstance(validate_part, dict):
            raise FailedParsingException('validation rules should be organized as a map')
        # if not 
        if not {'InputConstraint', 'ContextConstraint'}.issubset(set(validate_part.keys())):
            raise FailedParsingException(f'validation rules should be organized as a map, and should have keys: InputConstraint, ContextConstraint, the actual keys in the response are {set(validate_part.keys())}')
        self.validate_part: dict = validate_part  # type: ignore
        if not isinstance(execution_part, list):
            raise FailedParsingException('execution_part should be a list')
        # new_execution_part = []
        # for d in execution_part:
        #     if not isinstance(d, dict):
        #         raise FailedParsingException('execution_part should be a list of dict')
        #     new_d = {}
        #     for k, v in d.items():
        #         new_d[k] = repr_val(v)
        #     new_execution_part.append(new_d)
        #     print('FDGSSFGSG new_d', new_d)
        self.execution_part = execution_part

    @property
    def raw_validate_context_constraints(self):
        return self.validate_part['ContextConstraint']

    @property
    def raw_validate_input_constraints(self):
        return self.validate_part['InputConstraint']
    @property
    def always_valid(self):
        context_cs = self.raw_validate_context_constraints
        non_trival_input_cs = []
        for constraint_dict in self.raw_validate_input_constraints:
            if not self._is_trival_type_eq_valid_cs(constraint_dict):
                non_trival_input_cs.append(constraint_dict)
        if len(context_cs) == 0 and len(non_trival_input_cs) == 0:
            return True
        return False

    def _is_trival_type_eq_valid_cs(self, d):
        if d['v1'].endswith('.type') and d['v2'] in val_type_strs and d['relation'] == 'eq':
            return True

    def write_to_json(self, json_file_path: Union[str, Path]):
        d = {
            'inst_name': self.raw_inst_name,
            'type_part': self.inner_type_part,
            'validate_part': self.validate_part,
            'execution_part': self.execution_part,
            'full_type_part': self.full_type_part,
        }
        save_json(json_file_path, d)

    @classmethod
    def from_json(cls, json_str: Union[str, Path]):
        # print('||| == >> json_str', json_str)
        d = read_json(json_str)
        inst_name = Path(json_str).name[:-5]
        return cls(inst_name, d['type_part'], d['validate_part'], d['execution_part'], d.get('full_type_part'))

    @classmethod
    def from_raw_response_file(cls, raw_file_path: Union[str, Path]):
        content = path_read(raw_file_path)
        inst_name = _get_inst_name_from_raw_file_path(raw_file_path)
        data_part_texts = _get_data_part_texts(content)
        print(raw_file_path)

        if len(data_part_texts) != 4:
            if len(data_part_texts) < 4:
                raise FailedParsingException('There may be some missing parts')
            else:
                raise FailedParsingException('There may be some unexpected parts. If your answer for a question is in multiple JSON parts, please put them in a single JSON part.')
        inner_type_part = decode_json_part(data_part_texts[0])
        check_op_imm_type_response(inner_type_part)
        validate_part = decode_json_part(data_part_texts[1])
        try:
            full_type_part = json.loads(data_part_texts[2])
        except json.JSONDecodeError:
            print(f'failed to parsing the full_type_part in {raw_file_path}')
            # Summarize the type of the instruction
            raise FailedParsingException(f"The JSON desribing the instruction's type is ill-formatted. Please chekc the JSON in the response.")
        execution_part = decode_json_part(data_part_texts[3])

        if isinstance(validate_part, list):
            input_cs = []
            context_cs = []
            for _cs_part in validate_part:
                input_cs.extend(_cs_part['InputConstraint'])
                context_cs.extend(_cs_part['ContextConstraint'])
                # assert _cs_part['Valid']
            validate_part = {
                'InputConstraint': input_cs,
                'ContextConstraint': context_cs,
            }  # type: ignore

        return cls(
            inst_name=inst_name,
            inner_type_part=inner_type_part,
            validate_part=validate_part,
            execution_part=execution_part,
            full_type_part=full_type_part
        )

def check_op_imm_type_response(data:dict):
    if isinstance(data, list):
        raise FailedParsingException('The response describing the type of immediate arguments and operands should be  a dict, not a list')
    for k in data.keys():
        if not (k.startswith('op_') or k.startswith('imm_')) :
            raise FailedParsingException(f'The response describing the type of immediate arguments and operands is ill-formatted. The key {k} is not expected. The key should start with "op_" or "imm_".')

def decode_json_part(text):
    if '...' in text:
        raise FailedParsingException('The response should be a valid json. Do not use "..." in the response, though you do not know some components.')
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise FailedParsingException(f'The response should be a valid json. The current JSON \n\n{text}\n\n in the response is ill-formatted: {e}')


def _get_data_part_texts(content):
    a_data_part_in_process = False
    cur_lines = []
    data_part_texts = []
    for line in content.split('\n'):
        if line.strip() == '```json':
            a_data_part_in_process = True
        elif line.strip() == '```':
            a_data_part_in_process = False
            if cur_lines:
                data_part_texts.append('\n'.join(cur_lines))
                cur_lines = []
        elif a_data_part_in_process:
            cur_lines.append(line)
    # print(data_part_texts)
    data_part_texts = [
        x for x in data_part_texts if 'validation_description' not in x]
    return data_part_texts


def _get_inst_name_from_raw_file_path(raw_file_path):
    if Path(raw_file_path).stem.endswith('_response'):
        inst_name = Path(raw_file_path).stem[:-len('_response')]
    elif Path(raw_file_path).stem.endswith('_1_result'):
        inst_name = Path(raw_file_path).stem[:-len('_1_result')]
    elif Path(raw_file_path).stem.endswith('_result'):
        inst_name = Path(raw_file_path).stem[:-len('_result')]
    else:
        raise FailedParsingException('Unexpected file name')
    return inst_name


def process_all_insts(raw_response_dir, json_output_dir):
    for raw_file_path in raw_response_dir.glob('*_response.txt'):
        inst_name = _get_inst_name_from_raw_file_path(raw_file_path)
        GptResponseData.from_raw_response_file( 
            raw_file_path).write_to_json(
            json_output_dir / f'{inst_name}.json')


def extract_a_text_to_json(raw_text_path, json_output_path):
    GptResponseData.from_raw_response_file(raw_text_path).write_to_json(json_output_path)


def _get_op_from_raw_name(raw_name):
    if '~' not in raw_name:
        text_name = raw_name
    else:
        text_name = raw_name.split('_')[0]
        raw_name = raw_name.split('~')[0]
        
    return text_name, raw_name
