from pathlib import Path
from file_util import read_json
from file_util import save_json


target_path = './inst_ty_info/collected_binary_info.json'
combined_inst_data_dir = './inst_ty_info/combined_inst_data'




if __name__ == '__main__':
    result:dict[str, list] = {}
    for path in Path(combined_inst_data_dir).iterdir():
        stem = path.stem
        result[stem] = read_json(path)['binary_info']
    save_json(target_path, result)
