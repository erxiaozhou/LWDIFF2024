from pathlib import Path
from file_util import read_json, save_json
from time import time

from .tester import Tester
from .tester_util import testerExecInfo
from .tester_util import testerExecPaths
from .no_mutation_tester import noMutationTester
from .tester_factory import TesterFactory


class testingInfoSaver:
    def __init__(self, paras):
        assert isinstance(paras, mutationParas)
        self.paras = paras
        self.start_time = None
        self.end_time = None

    def save_config(self, exec_info, config_path=None):
        assert isinstance(exec_info, testerExecInfo)
        if config_path is None:
            config_path = self.paras.tester_exec_paths.config_log_path
        d = {}
        d['config'] = self.paras.to_dict_for_save
        d['exec_info'] = repr(exec_info.to_dict)
        d['time'] = self.exec_time
        print(config_path)
        save_json(config_path, d)

    def init_start_time(self):
        self.start_time = time()

    def init_end_time(self):
        self.end_time = time()

    @property
    def exec_time(self):
        assert self.start_time is not None
        assert self.end_time is not None
        return self.end_time - self.start_time


class mutationParas:
    def __init__(self, tester, tester_exec_paths, tested_dir, impls, running_paras) -> None:
        self.tester = tester
        assert isinstance(tester_exec_paths, testerExecPaths)
        self.tester_exec_paths: testerExecPaths = tester_exec_paths
        self.tested_dir = tested_dir
        self.impls = impls
        self.running_paras = running_paras

    @classmethod
    def get_no_mutation_paras(cls, result_base_dir, tested_dir, impls, tester_exec_paths=None, check_not_exist=True, testing_time=None):
        tester_exec_paths = get_tester_exec_paths(
            result_base_dir, tester_exec_paths, check_not_exist)
        return cls(
            tested_dir=tested_dir,
            tester=noMutationTester(),
            impls=impls,
            tester_exec_paths=tester_exec_paths,
            running_paras={
                'exec_paths': tester_exec_paths,
                'impls': impls,
                'testing_time': testing_time,
                'tc_paths_iterator':  _get_tcs_name_and_path(tested_dir)
            }
        )

    @classmethod
    def get_testing_paras(cls, tested_dir, 
                            result_base_dir, 
                            impls, 
                            runtime_names, 
                            config_file_path, 
                            seed_scheduler_name, 
                            mutation_selector_name, 
                            tester_name_prefix,
                            structure_name,
                            testing_time
                            ):
        tester_exec_paths = get_tester_exec_paths(
            result_base_dir, None)
        return cls(
            tested_dir=tested_dir,
            tester=TesterFactory.generate_a_tester_from_config(
                runtime_names=runtime_names,
                config_file_path=config_file_path,
                tester_exec_paths=tester_exec_paths,
                tested_dir=tested_dir, seed_scheduler_name=seed_scheduler_name,
                mutation_selector_name=mutation_selector_name,
                structure_name=structure_name,
                tester_name_prefix=tester_name_prefix
            ),
            impls=impls,
            tester_exec_paths=tester_exec_paths,
            running_paras={
                'impls': impls,
                'testing_time': testing_time
            }
        )

    @classmethod
    def get_testing_SOSP_paras(cls, tested_dir, 
                            result_base_dir, 
                            impls, 
                            runtime_names, 
                            config_file_path, 
                            seed_scheduler_name, 
                            tester_name_prefix,
                            phase_scheduler_name,
                            testing_time,
                            pos_candis_json,
                            wraps_json,
                            seed_updater_json,
                            add_random_phase
                            ):
        tester_exec_paths = get_tester_exec_paths(
            result_base_dir, None)
        actions = read_json(config_file_path)['actions']
        return cls(
            tested_dir=tested_dir,
            tester=TesterFactory.generate_a_SOPS_tester(
                runtime_names=runtime_names,
                actions=actions,
                tester_exec_paths=tester_exec_paths,
                tested_dir=tested_dir, seed_scheduler_name=seed_scheduler_name,
                phase_scheduler_name=phase_scheduler_name,
                tester_name_prefix=tester_name_prefix,
                pos_candis_json=pos_candis_json,
                wraps_json=wraps_json,
                seed_updater_json=seed_updater_json,
                add_random_phase=add_random_phase
            ),
            impls=impls,
            tester_exec_paths=tester_exec_paths,
            running_paras={
                'impls': impls,
                'testing_time': testing_time
            }
        )

    @property
    def to_dict_for_save(self):
        d = {}
        for name, attr in self.__dict__.items():
            if isinstance(attr, Path):
                d[name] = str(attr)
            elif isinstance(attr, testerExecPaths):
                d[name] = attr.to_str_dict
            # ! 
            elif name == 'impls':
                impls = attr
                d['runtimes'] = [impl.name for impl in impls]
            elif isinstance(attr, Tester):
                d[name] = repr(attr)
            else:
                d[name] = attr
        return d


def _get_tcs_name_and_path(dir_):
    dir_ = Path(dir_)
    for p in dir_.iterdir():
        if p.suffix == '.wasm':
            path = str(p)
            tc_name = p.stem
            yield (tc_name, path)

            
def get_tester_exec_paths(result_base_dir, tester_exec_paths=None, check_not_exist=True) -> testerExecPaths:
    if tester_exec_paths is None:
        tester_exec_paths = testerExecPaths.from_result_base_dir(
            result_base_dir, check_not_exist)
    else:
        assert isinstance(tester_exec_paths, testerExecPaths)
    return tester_exec_paths
