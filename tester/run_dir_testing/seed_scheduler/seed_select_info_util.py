from ..util import caseExecResult
from extract_block_mutator.WasmParser import WasmParser


class SeedSelectInfo:
    def __init__(self, 
                    case_can_be_seed, 
                    can_success_num,  
                    trigger_tester_exception,
                    has_timeout,
                    is_valid,
                    at_least_one_success,
                    all_can_success,
                    unique_visited_guards,
                    selected_num=0,
                    seed_path=None) -> None:
        self.case_can_be_seed = case_can_be_seed
        self.can_success_num = can_success_num
        # TODO attr
        self.trigger_tester_exception = trigger_tester_exception
        self.has_timeout = has_timeout
        self.is_valid = is_valid
        self.at_least_one_success = at_least_one_success
        self.all_can_success = all_can_success
        self.unique_visited_guards = unique_visited_guards
        self.unique_visited_guard_num= len(unique_visited_guards)
        self.selected_num = selected_num
        self.seed_path = seed_path
        self._parser = None
    #     # TODO  total_guard_num ，seed
        # for debug
        self._init_parser_num = 0

    def copy(self):
        # !copy，，
        assert 0
        return SeedSelectInfo(
            case_can_be_seed=self.case_can_be_seed,
            can_success_num=self.can_success_num,
            trigger_tester_exception=self.trigger_tester_exception,
            has_timeout=self.has_timeout,
            is_valid=self.is_valid,
            at_least_one_success=self.at_least_one_success,
            all_can_success=self.all_can_success,
            unique_visited_guards=self.unique_visited_guards,
            selected_num=self.selected_num,
            seed_path=self.seed_path
        )
    @property
    def parser(self):
        # raise NotImplementedError
        if self._parser is None:
            if self.seed_path is not None:
                self._init_parser_num += 1
                self._parser  = WasmParser.from_wasm_path(self.seed_path)
        return self._parser

    @classmethod
    def from_caseExecResult(cls, case_result: caseExecResult, seed_path=None):
        assert case_result.caseCoverage is not None
        return cls(
            case_can_be_seed=case_result.case_can_be_seed,
            can_success_num=case_result.can_success_num,
            trigger_tester_exception=case_result.trigger_tester_exception,
            has_timeout=case_result.has_timeout,
            is_valid=case_result.is_valid,
            selected_num=0,
            all_can_success=case_result.all_can_success,
            at_least_one_success=case_result.at_least_one_success,
            unique_visited_guards=case_result.caseCoverage.unique_visited_guards,
            seed_path=seed_path
        )


class Path2SeedSelectInfoClass:
    def __init__(self):
        self.inner_dict:dict[str, SeedSelectInfo] = {}
        self.states = None

    def get_by_path(self, path):
        path = str(path)
        if path not in self.inner_dict:
            raise Exception(f'Unknow seed_path {path}')
        return self.inner_dict[path]

    def __getitem__(self, path):
        return self.inner_dict[str(path)]

    def __setitem__(self, path, seed_select_info):
        path = str(path)
        self.inner_dict[path] = seed_select_info
        # print('In Path2SeedSelectInfoClass __setitem__', path, 'ath] = seed_select_info')

    def pop(self, path):
        path = str(path)
        return self.inner_dict.pop(path)

    def __contains__(self, path):
        path = str(path)
        return path in self.inner_dict

    def __len__(self):
        return len(self.inner_dict)

    def items(self):
        return self.inner_dict.items()

    def seed_paths(self):
        return list(self.inner_dict.keys())

    def insert_info_from_case_exec_result(self, seed_path, case_exec_result: caseExecResult, states=None):
        assert states is None
        seed_select_info = SeedSelectInfo.from_caseExecResult(case_exec_result, seed_path=seed_path)
        self[str(seed_path)] = seed_select_info

