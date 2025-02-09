from ..parsing_spec_util import FullExtractedText
from file_util import save_json, read_json
from ..project_cfg import default_core_dict_p
from ..project_cfg import default_tags_p
from ..project_cfg import default_tags2cnodes_p
from ..project_cfg import default_tar_names_p
from ..project_cfg import default_titles_p
from ..project_cfg import default_op_name2exec_fmt_json_path
from ..project_cfg import raw_cp910_jsons_dir
from pathlib import Path


def get_full_extracted_text(enforce_rerun:bool=False)->FullExtractedText:
    # need_init
    if enforce_rerun:
        need_init = True
    else:
        need_init = (not Path(default_core_dict_p).exists()) or (not Path(default_tags_p).exists())
    if need_init:
        extracted_result = _init_text_and_dump()
    else:
        try:
            # assert 0
            extracted_result = FullExtractedText.from_dump_data(default_core_dict_p, default_tags_p, tags2cnodes_p=default_tags2cnodes_p)
        except Exception as e:
            # raise e
            print('Error in loading from dump data, re-init')
            extracted_result = _init_text_and_dump()
    return extracted_result

def _init_text_and_dump():
    extracted_result = FullExtractedText()
    extracted_result.dump_data(core_dict_p=default_core_dict_p, tags_p=default_tags_p, tags2cnodes_p=default_tags2cnodes_p)
    
    tar_names = []
    titles = []
    for _ in extracted_result.all_tags:
        tar_names.append(str(_.tag_repr))
    for _ in extracted_result.core_dict.values():
        titles.append(_.all_title_repr)
    save_json(default_tar_names_p, tar_names)
    save_json(default_titles_p, titles)
    return extracted_result


def get_op_name2exec_fmt(enforce_rerun:bool=False)->dict[str, str]:
    if enforce_rerun:
        need_init = True
    else:
        need_init = not (Path(default_op_name2exec_fmt_json_path).exists())
    if need_init:
        data = {}
        ori_dir = Path(raw_cp910_jsons_dir)
        for p in ori_dir.iterdir():
            if p.is_file():
                raw_data = read_json(p)
                inst_name = p.stem
                exec_inst_name = raw_data['exec_data']['raw_title']
                data[inst_name] = exec_inst_name
        save_json(default_op_name2exec_fmt_json_path, data)
    else:
        data = read_json(default_op_name2exec_fmt_json_path)
    return data

