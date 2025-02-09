from abc import abstractmethod
from pathlib import Path
from file_util import check_dir, path_write, save_json
from file_util import read_json
from ..message_util import ask_and_get_question
from ..project_cfg import default_op_name2exec_fmt_json_path
from ..project_cfg import cexec_name2fexec_name_json_path
from typing import Optional, Union
from ..api_util import MODEL_VERSION


class QueryFileNames:
    def __init__(self, name_base:str, base_dir:Union[str, Path]) -> None:
        self.base_dir = Path(base_dir)
        self.name_base = name_base
    def __repr__(self):
        return f'{self.__class__.__name__}({self.name_base})'
    @property
    def prompt_txt_path(self)->Path:
        return self.base_dir / f'{self.name_base}_prompt.txt'
    @property
    def prompt_json_path(self)->Path:
        return self.base_dir / f'{self.name_base}_prompt.json'
    @property
    def response_txt_path(self)->Path:
        return self.base_dir / f'{self.name_base}_response.txt'

    @property
    def background_txt_path(self)->Path:
        return self.base_dir / f'{self.name_base}_background.txt'

    def a_query_exist(self)->bool:
        if self.response_txt_path.exists() and (not _file_is_empty(self.response_txt_path)):
            if self.prompt_txt_path.exists():
                assert self.prompt_json_path.exists()
                return True
        return False

def _file_is_empty(file_path:Path)->bool:
    # print(file_path.stat().st_size == 0)
    return file_path.stat().st_size == 0

class OneTaskQueryFileNames:
    def __init__(self, base_dir:Union[str, Path], task_repr:str, max_idx:int):
        self.task_repr = task_repr
        self.max_idx = max_idx
        self.base_dir = base_dir
        check_dir(base_dir)

    def get_query_names(self, idx:int)->QueryFileNames:
        cur_name_base = f'{self.task_repr}_{idx}'
        return QueryFileNames(cur_name_base, self.base_dir)

    @property
    def exist_epoch_num(self):
        idx = 0
        while True:
            query_names = self.get_query_names(idx)
            print('query_names.a_query_exist()',query_names.a_query_exist())
            if not query_names.a_query_exist():
                break
            idx += 1
        return idx

    def get_last_query_names(self)->Optional[QueryFileNames]:
        idx = self.exist_epoch_num
        if idx == 0:
            return None
        return self.get_query_names(idx-1)


    def get_next_query_names(self)->QueryFileNames:
        idx = self.exist_epoch_num
        return self.get_query_names(idx)


def save_message(message, queri_file_names:QueryFileNames):
    path_write(queri_file_names.prompt_txt_path, repr(message))
    save_json(queri_file_names.prompt_json_path, message)

def save_response(response, queri_file_names:QueryFileNames):
    path_write(queri_file_names.response_txt_path, response)

def ask_core_ng(
    queri_file_names:QueryFileNames,
    message:list,
    debug=False,
    skip_exist=False,
    example_text:Optional[str]=None,
    mode_name=MODEL_VERSION
    ):
    if skip_exist:
        if queri_file_names.response_txt_path.exists() and (not _file_is_empty(queri_file_names.response_txt_path)):
            return
    if debug:
        response = ''
    else:
        response = ask_and_get_question(message, mode_name=mode_name)
    if example_text is not None:
        path_write(queri_file_names.background_txt_path, example_text)
    save_response(response, queri_file_names)
    save_message(message, queri_file_names)


def get_inst_name2exec_inst_name() -> dict[str, str]:
    op_name2cexec_name = read_json(default_op_name2exec_fmt_json_path)
    cexec_name2fexec_name = read_json(cexec_name2fexec_name_json_path)
    new_data = {}
    for inst_name, exec_inst_name in op_name2cexec_name.items():
        cname = _process_exec_inst_name(exec_inst_name)
        fname = cexec_name2fexec_name[cname]
        new_data[inst_name] = fname
    return new_data


def get_all_inst_names() -> list[str]:
    inst_name2exec_inst_name = get_inst_name2exec_inst_name()
    return list(inst_name2exec_inst_name.keys())


def _process_exec_inst_name(exec_inst_name) -> str:
    assert exec_inst_name.startswith(':math:`')
    assert exec_inst_name.endswith('`')
    return exec_inst_name[7:-1]
