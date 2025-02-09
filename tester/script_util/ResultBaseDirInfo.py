from tqdm import tqdm
from file_util import check_dir, cp_file, read_json, save_json
from pathlib import Path
import re


class ResultBaseDirInfo:
    name_p = re.compile(r'bug_count_result_slot_\d+.json')
    def __init__(self, result_base_dir) -> None:
        self.result_base_dir = Path(result_base_dir)
        self.bug_count_result_dir = self.result_base_dir / 'bug_count_result'
        self.diff_tcs_dir = self.result_base_dir / 'diff_tcs'

    def get_last_bug_count_json(self):
        bug_count_result_dir = self.bug_count_result_dir
        bug_count_jsons = list(bug_count_result_dir.glob('*.json'))
        
        bug_count_jsons = [x for x in bug_count_jsons if ResultBaseDirInfo.name_p.match(x.name)]
        # get the newest one
        bug_count_jsons.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        if len(bug_count_jsons) == 0:
            print(f'No bug_count_result json in {bug_count_result_dir}')
            return 
        return bug_count_jsons[0]

    @property
    def interesting_log_dir(self):
        return Path(self.result_base_dir / 'log_category_base/only_interesting_log_category')
    @property
    def untriggered_interesting_log_dir(self):
        return check_dir(self.result_base_dir / 'log_category_base/only_interesting_log_category_uncatch')

    def get_untriggered_interesting_log(self):
        untriggered_stems = self.get_untriggered_stems()
        paths = list(self.interesting_log_dir.iterdir())
        for p in tqdm(paths, total=len(paths)):
            new_p = self.untriggered_interesting_log_dir / p.name
            if p.name.startswith('0'):
                
                cp_file(p, new_p)
            else:
                data = read_json(p)
                new_data = {}
                for reason, stems in data.items():
                    new_stems = [stem for stem in stems if stem in untriggered_stems]
                    if new_stems:
                        new_data[reason] = new_stems
                if len(new_data):
                    save_json(new_p, new_data)

    @property
    def to_recheck_case_dir(self):
        return check_dir(self.result_base_dir / 'to_recheck_cases')
    @property
    def to_recheck_case_result_dir(self):
        return check_dir(self.result_base_dir / 'to_recheck_cases_result')
        
    def get_diff_tcs_paths(self, stems):
        return [self.diff_tcs_dir / f'{stem}.wasm' for stem in stems]

    def get_no_trigger_diff_tc_paths(self):
        no_trigger_diff_tc_stems = self.get_untriggered_stems()
        ori_tcs_paths = self.get_diff_tcs_paths(no_trigger_diff_tc_stems)
        return ori_tcs_paths

    def get_untriggered_stems(self):
        last_bug_count_json = self.get_last_bug_count_json()
        if last_bug_count_json is None:
            return []
        print(last_bug_count_json)
        bug_count_result = read_json(last_bug_count_json)
        no_trigger_diff_tc_stems = bug_count_result['()']
        return no_trigger_diff_tc_stems

    # def
