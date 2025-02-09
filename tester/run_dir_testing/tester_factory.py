from typing import List
from time import time
from run_dir_testing.MABCore.MABUCBT import MABUCBTSelector
from run_dir_testing.MABSolutionSelector import MABSolutionSelector
from run_dir_testing.RandomSolutionSelector import RandomSolutionSelector
from .StructureTesterBaseV2 import StructureTesterBaseV2
from .StructureTesteV2SOPS import StructureTesteV2SOPS
from .StructureTesterBase import StructureTesterBase
from .seed_scheduler.V3SeedScheduler import V3SeedScheduler
from .StructureTesterBase import StructureTesterBase
from .seed_scheduler.seed_select_info_util import Path2SeedSelectInfoClass
from .tester_util import testerExecInfo, testerExecPaths
from .tester import Tester
from file_util import check_dir, cp_file, path_write, read_json
from file_util import get_logger
from .components.Random_mutation_selector import RandomMutationSelector

from .MABCore.EpsGreedy import EpsGreedySelector
from .MABCore.SWEGreedy import SWEGreedySelector


seed_scheduler_names = ['Random', 'V1', 'V2', 'V3', 'BR', 'BLRU', 'BLRS']
mutation_scheduler_names = ['Random', 'MBA', 'MBAWL', 'MBAUCBTWL', 'MBASM', 'MABWGSW']
state_based_mutation_scheduler_names = ['Qlearning', 'Qlearning_self']
std_state_mutation_scheduler_name = ['StateSMSW']
it_mutation_scheduler_names = ['CIMABUCBT']
all_mutation_selector_names = mutation_scheduler_names + state_based_mutation_scheduler_names + std_state_mutation_scheduler_name + it_mutation_scheduler_names

name2seed_scheduler = {
    'V3': V3SeedScheduler,
}


name2strcuture = {
    'V1S': StructureTesterBase,
    'V2S': StructureTesterBaseV2,
    'V2SOPS': StructureTesteV2SOPS
}


class TesterFactory:
    @staticmethod
    def geenrate_a_tester(runtime_names: List[str],
                          actions,
                          tester_name_prefix,
                          tester_exec_paths: testerExecPaths,
                          tested_dir,
                          seed_scheduler_name,
                          structure_name,
                          mutation_selector_name) -> Tester:
        seed_scheduler_class = name2seed_scheduler[seed_scheduler_name]
        seed_scheduler_logger = get_logger('seed_scheduler', f'{tester_exec_paths.tester_para_dir}/seed_scheduler.log')
        mutation_selector_logger = get_logger('mutation_selector', f'{tester_exec_paths.tester_para_dir}/mutation_selector.log')

        if mutation_selector_name in mutation_scheduler_names:
            seedPath2SeedSelectInfo = Path2SeedSelectInfoClass()
            # seed_scheduler
            seed_scheduler = seed_scheduler_class.from_seed_dir(
            tested_dir, seedPath2SeedSelectInfo, seed_scheduler_logger)
            # mutation select0r
            mutation_selector = RandomMutationSelector(actions=actions)
            # 
            structure_class = name2strcuture[structure_name]
            return structure_class(runtime_names=runtime_names,
                                       actions=actions,
                                       tester_name_prefix=tester_name_prefix,
                                       tester_exec_paths=tester_exec_paths,
                                       mutation_selector=mutation_selector,
                                       seed_scheduler=seed_scheduler,
                                       seedPath2SeedSelectInfo=seedPath2SeedSelectInfo)
    @staticmethod
    def generate_a_tester_from_config(runtime_names, config_file_path, tester_exec_paths, tested_dir, seed_scheduler_name, mutation_selector_name, tester_name_prefix, structure_name):
        config_paras = read_json(config_file_path)
        return TesterFactory.geenrate_a_tester(runtime_names, config_paras['actions'], tester_name_prefix, tester_exec_paths, tested_dir, seed_scheduler_name, structure_name, mutation_selector_name)
    @staticmethod
    def generate_a_SOPS_tester(runtime_names: List[str],
                          actions,
                          tester_name_prefix,
                          tester_exec_paths: testerExecPaths,
                          tested_dir,
                          seed_scheduler_name,
                          phase_scheduler_name,
                          pos_candis_json,
                          wraps_json,
                          seed_updater_json,
                          add_random_phase
                          ) -> StructureTesteV2SOPS:
        seed_scheduler_class = name2seed_scheduler[seed_scheduler_name]
        seed_scheduler_logger = get_logger('seed_scheduler', f'{tester_exec_paths.tester_para_dir}/seed_scheduler.log')
        
        seedPath2SeedSelectInfo = Path2SeedSelectInfoClass()
        # seed_scheduler
        seed_scheduler = seed_scheduler_class.from_seed_dir(
        tested_dir, seedPath2SeedSelectInfo, seed_updater_json, seed_scheduler_logger)
        # 
        if add_random_phase:
            phase_names = ['random'] + actions
        else:
            phase_names = actions
        # mutation selector
        assert phase_scheduler_name in {'Random', 'MABUCB', 'MABEPS'}
        if phase_scheduler_name == 'Random':
            phase_mutation_scheduler = RandomSolutionSelector(phase_names=phase_names)
        elif phase_scheduler_name == 'MABUCB':
            mutation_selector = MABUCBTSelector(actions=phase_names)
            phase_mutation_scheduler = MABSolutionSelector(phase_names, mutation_selector)
        elif phase_scheduler_name == 'MABEPS':
            mutation_selector = EpsGreedySelector(actions=phase_names)
            phase_mutation_scheduler = MABSolutionSelector(phase_names, mutation_selector)
        else:
            raise ValueError(f'phase_scheduler_name: {phase_scheduler_name}')

        # add_random_phase
        return StructureTesteV2SOPS(runtime_names=runtime_names,
                                    actions=actions,
                                    tester_name_prefix=tester_name_prefix,
                                    tester_exec_paths=tester_exec_paths,
                                    seed_scheduler=seed_scheduler,
                                    seedPath2SeedSelectInfo=seedPath2SeedSelectInfo,
                                    mutation_scheduler=phase_mutation_scheduler,
                                    pos_candi_json_path=pos_candis_json,
                                    insert_wrap_json_path=wraps_json)