from .wasm_impl_abc import WasmImpl
from extract_dump import dumpData
from .common_runtime_util import NomoveBasedExecutor
from .common_runtime_util import dumpedResultGenerator
from util import cmnImplResultPathGroup
from config import EXEC_TIMEOUT


class dumpRuntime(WasmImpl):
    def __init__(self, 
                 name, 
                 executor, 
                 result_generator, 
                 result_path_group:cmnImplResultPathGroup
            ):
        self.name = name
        self.executor = executor
        self.result_generator: dumpedResultGenerator = result_generator
        self.result_path_group = result_path_group

    @classmethod
    def from_new_dict(cls, name, dict_, timeout_th=EXEC_TIMEOUT):
        executor = NomoveBasedExecutor.from_new_dict(dict_, timeout_th)
        result_generator = dumpedResultGenerator(dict_['dump_extractor'], name)
        result_path_group = executor.ori_paths
        return cls(name, executor, result_generator, result_path_group)

    def execute_and_collect(self, tc_path, func_name='to_test'):
        # self.executor
        result_paths = self.result_path_group
        # self.executor.set_result_paths(result_paths)
        self.result_generator.set_result_paths(result_paths)
        cli_result = self.executor.execute(tc_path, func_name=func_name)
        self.result_generator.update_cli_result(cli_result)
        result = self.result_generator.get_result_obj()
        assert isinstance(result, dumpData)
        return result
