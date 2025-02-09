from WasmInfoCfg import SectionType
from ..parser_to_file_util import parser2wasm
from ..WasmParser import  WasmParser
from file_util import cp_file
from typing import Iterable, Optional, Set, Union, List
from pathlib import Path
from .Fuzzer import Fuzzer
from random import choice, shuffle
from ..ModuleFuzzerUtil.mutations import insert_data_count_mutation, insert_custom_section_mutaiton, rewrite_custom_section_mutation, delete_custom_section_mutation, insert_memory_mutation, reset_random_memory_mutation, insert_passive_data_mutation, insert_active_data_mutation, delete_data_mutation, reset_random_data_mutation, insert_global_mutation, insert_table_mutation, delete_table_mutation, reset_table_mutation, reset_elem_seg_mutation, delete_elem_seg_mutation, insert_passive_elem_mutation, insert_active_elem_mutation, insert_declarative_elem_mutation, insert_type_mutation, insert_func_mutation, insert_local_mutation, extend_return_type_mutation, insert_start_mutation, replace_start_mutation, insert_export_mutaiton, rename_export_mutation
from ..ModuleFuzzerUtil.DefMutation import Mutation


class _MutationsForOneSection:
    def __init__(self, mutations:Iterable[Mutation]) -> None:
        self._mutations = mutations

    def __iter__(self):
        new_list = list(self._mutations)
        shuffle(new_list)
        return iter(new_list)

class MutationsSolution:
    def __init__(self, mutations_for_each_section:List[Set[Mutation]]) -> None:
        self.mutations_for_each_section = [_MutationsForOneSection(_) for _ in mutations_for_each_section]

def _group_mutations_by_section_type(mutations:List[Mutation])->dict[SectionType, Set[Mutation]]:
    result = {}
    for mutation in mutations:
        result.setdefault(mutation.section_type, set()).add(mutation)
    return result


class ValidModuleMutationManager:
    support_mutations = [
        insert_data_count_mutation, 
        insert_custom_section_mutaiton,
        rewrite_custom_section_mutation,
        delete_custom_section_mutation,
        insert_memory_mutation,

        reset_random_memory_mutation,
        insert_passive_data_mutation,
        insert_active_data_mutation,
        reset_random_data_mutation,
        insert_global_mutation,

        insert_table_mutation,
        # reset_table_mutation,
        # reset_elem_seg_mutation,
        insert_passive_elem_mutation,
        insert_active_elem_mutation,
        insert_declarative_elem_mutation,
        insert_type_mutation,

        insert_func_mutation,
        insert_local_mutation,
        extend_return_type_mutation,
        insert_start_mutation,
        replace_start_mutation,

        insert_export_mutaiton,
        rename_export_mutation
    ]
    section_type2mutations: dict[SectionType, Set[Mutation]] = _group_mutations_by_section_type(support_mutations)

    def __init__(self, enabled_def_types:Optional[Set[SectionType]]=None) -> None:
        # main logic
        if enabled_def_types is None:
            enabled_def_types = set(ValidModuleMutationManager.section_type2mutations.keys())
        self.enabled_def_types = enabled_def_types
        self.support_def_num = len(self.enabled_def_types)
    def get_mutation_sequences(self)->MutationsSolution:
        results = [self.section_type2mutations[_] for _ in self.enabled_def_types]
        shuffle(results)
        solution = MutationsSolution(results)
        return solution
        
class ValidModuleFuzzer(Fuzzer):
    def __init__(self) -> None:
        self.mutation_manager = ValidModuleMutationManager()
        self.test_num = max(1, int(self.mutation_manager.support_def_num * 0.75))
        self.test_num = 1
        super().__init__()
        

    def fuzz_one(self, ori_wasm: Union[Path, str], tgt_wasm_path, parser:Optional[WasmParser]=None, remove_loop_=False):
        ori_parser = self.get_parser_of_ori_wasm(ori_wasm, parser, remove_loop_)
        assert self.logger is not None
        mutation_sequence = self.mutation_manager.get_mutation_sequences()
        selected_mutations = []
        i=0
        for mutations in mutation_sequence.mutations_for_each_section:
            if i >= self.test_num:
                break
            for mutation in mutations:
                # 
                apply_result = mutation.can_apply(ori_parser)

                # 
                if apply_result:
                    # print('ZZZ mutation.name', mutation.name)
                    selected_mutations.append(mutation)
                    mutation.apply(ori_parser)
                    i += 1
                    break
        selected_mutation_names = [_.name for _ in selected_mutations]
        self.logger.info(msg=f'Ori Case Name: {Path(ori_wasm).stem}, New Case Name: {Path(tgt_wasm_path).stem}  ; selected_mutation_names: {selected_mutation_names}')
        print(selected_mutation_names)
        # for mutation in wat_mutation_names_to_apply:
        #     mutation.apply(ori_parser)
        parser2wasm(ori_parser, tgt_wasm_path)
        if not Path(tgt_wasm_path).exists():
            cp_file(ori_wasm, tgt_wasm_path)

