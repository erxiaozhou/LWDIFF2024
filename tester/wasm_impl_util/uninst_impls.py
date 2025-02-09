from typing import Optional
from util import CLIResult
from .util import combine_path
from extract_dump import dumpData
from util import exec_impl_and_collect_CLI_result
from .wasm_impl_abc import WasmImpl
from extract_dump.dumpDataBase import uninstDumpData
from typing import Optional

fix_name = '/app/to_exec.wasm'


class collectLogExecutor:
    def __init__(self, timeout_th, cmd_fmt, err_channel, set_out2out_err=False, pre_cmd=None, post_cmd=None) -> None:
        self.timeout = timeout_th
        self.cmd_fmt = cmd_fmt
        assert err_channel in ['stdout', 'stderr', 'stdout_stderr']
        if err_channel == 'stdout' and set_out2out_err:
            err_channel = 'stdout_stderr'
        self.err_channel = err_channel
        self.pre_cmd = pre_cmd
        self.post_cmd = post_cmd

    def execute(self, wasm_path, err_channel=None, func_name='to_test'):
        if err_channel is None:
            err_channel = self.err_channel
        return exec_impl_and_collect_CLI_result(
            cmd_fmt=self.cmd_fmt, timeout_th=self.timeout, wasm_path=wasm_path, err_channel=err_channel, pre_cmd=self.pre_cmd, post_cmd=self.post_cmd, func_name=func_name
        )


class logResultGenerator:
    def __init__(self, name):
        self.name = name
        self.cli_result: Optional[CLIResult]=None

    def update_cli_result(self, cli_result: CLIResult):
        self.cli_result = cli_result

    def get_result_obj(self):
        assert self.cli_result is not None
        return uninstDumpData(name=self.name, cli_result=self.cli_result)


class uninstRuntime(WasmImpl):
    def __init__(self, name, executor, result_generator) -> None:
        self.name = name
        self.executor = executor
        self.result_generator: logResultGenerator = result_generator

    def execute_and_collect_txt(self, tc_path, func_name='to_test') -> str:
        return str(self.executor.execute(tc_path, func_name=func_name))

    def execute_and_collect(self, tc_path, func_name='to_test', *args, **kwargs):
        # print(f'func_name: {func_name}')
        # assert 0
        cli_result = self.executor.execute(tc_path, func_name=func_name)
        self.result_generator.update_cli_result(cli_result)
        result = self.result_generator.get_result_obj()
        assert isinstance(result, dumpData)
        return result

    @classmethod
    def from_new_dict(cls, name, dict_, timeout_th=5, set_out2out_err=False):
        cmd_fmt = dict_['std_cmd']
        if 'uninst_pre_cmd' in dict_:
            pre_cmd = dict_['uninst_pre_cmd']
        else:
            pre_cmd = dict_.get('pre_cmd', None)
        if 'uninst_post_cmd' in dict_:
            post_cmd = dict_['uninst_post_cmd']
        else:
            post_cmd = dict_.get('post_cmd', None)
        executor = collectLogExecutor(timeout_th=timeout_th,
                                      cmd_fmt=cmd_fmt,
                                      err_channel=dict_['err_channel'],
                                      set_out2out_err=set_out2out_err,
                                      pre_cmd=pre_cmd,
                                      post_cmd=post_cmd
                                      )
        result_generator = logResultGenerator(name)
        return cls(name, executor, result_generator)

    @classmethod
    def from_cdict(cls, name, dict_, timeout_th=5, set_out2out_err=False):
        cmd_fmt = dict_['std_cmd'].format(dict_['bin_cmd'], '{}')
        #
        inner_cmd = cmd_fmt.format(fix_name)
        cmd = 'docker cp {} {}:{}'.format(
            '{}', dict_['container_name'], fix_name)
        cmd_fmt = ';'.join([cmd, inner_cmd])
        # print(cmd_fmt)
        err_channel = dict_['err_channel']
        executor = collectLogExecutor(timeout_th=timeout_th,
                                      cmd_fmt=cmd_fmt,
                                      err_channel=err_channel,
                                      set_out2out_err=set_out2out_err,
                                      pre_cmd=f'docker exec {dict_["container_name"]} rm {fix_name}',
                                      post_cmd=f'docker exec {dict_["container_name"]} rm {fix_name}'
                                      )
        result_generator = logResultGenerator(name)
        return cls(name, executor, result_generator)

    @classmethod
    def from_old_std_dict(cls, name, dict_, timeout_th=5, set_out2out_err=False):
        return cls._from_dict_core(name, dict_, 'standard_dir', timeout_th, set_out2out_err)

    @classmethod
    def _from_dict_core(cls, name, dict_, dict_type, timeout_th=5, set_out2out_err=False):
        assert dict_type in ['standard_dir', 'lastest_dir']
        cmd_fmt, err_channel = _get_paras_from_dict(dict_)
        executor = collectLogExecutor(
            timeout_th, cmd_fmt, err_channel, set_out2out_err)
        result_generator = logResultGenerator(name)
        return cls(name, executor, result_generator)


def _get_paras_from_dict(dict_):
    bin_path = combine_path(dict_['standard_dir'], dict_['bin_relative_path'])
    cmd_fmt = dict_['std_cmd'].format(bin_path, '{}')
    err_channel = dict_['err_channel']
    assert err_channel in ['stdout', 'stderr', 'stdout_stderr']
    return cmd_fmt, err_channel
