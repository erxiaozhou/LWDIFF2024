import re
from file_util import byte2str
import subprocess
# import re
from enum import Enum
from .detect_crash_util import _detect_has_crash_in_err, _detect_has_crash_in_err_v2

return_para = lambda x: x


# def return_para(*x, **kwds):
#     print('XXX return_para', x, kwds)
#     return x
    # return *args, **kwargs

class execStatus(Enum):
    Timeout = 1
    Crash = 2
    Exception = 3
    Success = 4

    @property
    def is_success(self):
        return self == execStatus.Success

    @property
    def is_timeout(self):
        return self == execStatus.Timeout

    @property
    def is_crash(self):
        return self == execStatus.Crash

    def __eq__(self, __value: object) -> bool:
        return super().__eq__(__value)


def is_failed_content(content):
    assert isinstance(content, str), print(content)
    content = content.lower()
    sig_words = ['error', 'failed', 'exception',
                 'aborted', 'aborting', 'fault']
    return any(wd in content for wd in sig_words)


class CLIResult:
    def __init__(self, has_timeout, has_crash, log: str, returncode=None):
        self.has_timeout = has_timeout
        self.has_crash = has_crash
        assert isinstance(log, str), print(log)
        self.log = log
        self.has_failed_log = is_failed_content(self.log)
        if returncode is not None and returncode != 0:
            if not self.has_failed_log and (not self.has_crash):
                # assert 0
                self.has_crash = True
        self.exec_status = self._get_exec_state()

    @property
    def is_success(self):
        return self.exec_status.is_success

    # @property
    def _get_exec_state(self) -> execStatus:
        if self.has_timeout:
            return execStatus.Timeout
        elif self.has_crash:
            return execStatus.Crash
        elif self.has_failed_log:
            return execStatus.Exception
        else:
            return execStatus.Success

    def __str__(self):
        status_str = str(self.exec_status)
        return f'CLIResult: {status_str}: {self.log}'


def exec_impl_and_collect_CLI_result(cmd_fmt, timeout_th, wasm_path, err_channel, func_name='to_test', pre_cmd=None, post_cmd=None) -> CLIResult:
    assert err_channel in ['stdout', 'stderr', 'stdout_stderr']
    assert '{case_path}' in cmd_fmt
    assert '{func_name}' in cmd_fmt
    if not (func_name.startswith('"') and func_name.endswith('"')):
        func_name = f'"{func_name}"'
    if pre_cmd is not None:
        pre_cmd = _fill_cmd_format_with_wasm_path(pre_cmd, wasm_path)
        subprocess.run(pre_cmd, stderr=subprocess.PIPE,
                       stdout=subprocess.PIPE, shell=True, timeout=timeout_th)
    try:
        # print(f'func_name: {func_name}')
        cmd = cmd_fmt.format(case_path=wasm_path, func_name=func_name)
        # print(cmd)
        p = subprocess.run(cmd, stderr=subprocess.PIPE,
                           stdout=subprocess.PIPE, shell=True, timeout=timeout_th)
        out_content = byte2str(p.stdout).strip(' \t\n')
        err_byte_content = byte2str(p.stderr).strip(' \t\n')
        if err_channel == 'stdout_stderr':
            if len(err_byte_content):
                content = out_content + '\n' + err_byte_content
            else:
                content = out_content
        elif err_channel == 'stdout':
            content = out_content
        elif err_channel == 'stderr':
            content = err_byte_content
        else:
            raise ValueError(f'Unexpected err_channel: {err_channel}')
        if err_channel == 'stdout_stderr' or err_channel == 'stderr':
            has_crash = _detect_has_crash_in_err(err_byte_content)
        else:
            has_crash = _detect_has_crash_in_err_v2(err_byte_content)
        if len(err_byte_content) > 0:
            pre_s = re.sub(r'\d+', '<num_z>', err_byte_content)
            s = f'{pre_s}_{has_crash}'
        has_timeout = False
        returncode = p.returncode
    except subprocess.TimeoutExpired:
        print('Catched! XXXX', wasm_path)
        has_crash = False
        has_timeout = True
        content = ''
        returncode = None
    if post_cmd is not None:
        post_cmd = _fill_cmd_format_with_wasm_path(post_cmd, wasm_path)
        subprocess.run(post_cmd, stderr=subprocess.PIPE,
                       stdout=subprocess.PIPE, shell=True, timeout=timeout_th)
    result = CLIResult(has_timeout=has_timeout,
                       has_crash=has_crash, log=content, returncode=returncode)
    return result


def _fill_cmd_format_with_wasm_path(cmd_fmt, wasm_path):
    return cmd_fmt.format(case_path=wasm_path)
class FailedParsingException(Exception):
    pass

class MayWrongSyntaxWraning(Exception):
    pass
