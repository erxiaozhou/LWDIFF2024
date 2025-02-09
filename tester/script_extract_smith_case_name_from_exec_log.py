import sys
from pathlib import Path
import re
from tqdm import tqdm
from file_util import check_dir, save_json


unexec_case_line_p = re.compile(r'line \- ([^ ]+)')
def generate_execed_case_log(result_base_dir):
    raw_log_path = result_base_dir / 'tester_paras/case_name_logger.log'
    tested_stem_path = result_base_dir / 'tested_stems.json'


    stems = set()
    for line in tqdm(raw_log_path.read_text().split('\n')):
        r = unexec_case_line_p.findall(line)
        if r:
            stem = r[0]
            stems.add(stem)
    stems = list(stems)
    save_json(tested_stem_path, stems)
    print('Case Num:', len(stems))
    print('tested_stem_path:', tested_stem_path)
    return stems


if __name__ == '__main__':
    
    result_base_dir = Path(sys.argv[1])

    if len(sys.argv) == 2 or sys.argv[2] == 'generate_log':
        mode = 'generate_log'
        generate_execed_case_log(result_base_dir)
    else:
        assert len(sys.argv) == 5
        mode = sys.argv[2]
        assert mode == 'mv_tested_cases'
        ori_cases_dir = Path(sys.argv[3])
        dir_to_store_execed_cases = check_dir(sys.argv[4])
        execed_cases_stems = generate_execed_case_log(result_base_dir)
        assert len(execed_cases_stems) > 0
        for stem in tqdm(execed_cases_stems):
            ori_case_path = ori_cases_dir / f'{stem}.wasm'
            ori_case_path.replace(dir_to_store_execed_cases / f'{stem}.wasm')
        print(f'Have moved {len(execed_cases_stems)} cases from {ori_cases_dir} to {dir_to_store_execed_cases}')
