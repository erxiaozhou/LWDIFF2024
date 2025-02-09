import subprocess
from pathlib import Path
from file_util import byte2str, check_dir, cp_file, path_read
from util import is_failed_content
from get_impls_util import get_lastest_uninst_impls
from get_impls_util import get_ori_cp910_impls
from wasm_impl_util import uninstRuntime
import tempfile
import re
from tqdm import tqdm


latest_impls = get_lastest_uninst_impls()
latest_impls_dict = {impl.name: impl for impl in latest_impls}

cp910_contianer_impls = get_ori_cp910_impls()
cp910_contianer_impls_dict = {
    impl.name: impl for impl in cp910_contianer_impls}


_case_p = re.compile(r'^.*?\.wasm:.*?:')
def get_wasm_validate_err(p):
    p = subprocess.run(['wasm-validate', str(p)], capture_output=True)
    err_text = p.stderr.decode()
    err_text = re.sub(_case_p, '', err_text)
    return err_text

# ========================= validate wasm ==============================


def validate_wasm(wasm_path, print_detail_reason=False,timeout=10):
    cmd = 'wasm-validate {}'.format(wasm_path)
    p = subprocess.run(cmd, stderr=subprocess.PIPE,
                       stdout=subprocess.PIPE, timeout=timeout, shell=True)
    if print_detail_reason:
        reason = byte2str(p.stderr).strip(' \t\n')
        if reason:
            print(reason)
    if bool(p.returncode) != bool(p.stderr):
        print('2893239fdbbninnio', 'bool(p.returncode) != bool(p.stderr)',
              bool(p.returncode), bool(p.stderr))
    # assert bool(p.returncode) == bool(p.stderr), print(p.stderr, p.returncode, cmd)
    return not bool(p.returncode)

def get_validation_info(wasm_path):
    cmd = 'wasm-validate {}'.format(wasm_path)
    p = subprocess.run(cmd, stderr=subprocess.PIPE,
                       stdout=subprocess.PIPE, timeout=10, shell=True)
    reason = byte2str(p.stderr).strip(' \t\n')
    if len(reason) == 0:
        return None
    else:
        return reason

# ======================================================================


def wasm2wat(wasm_path, wat_path):
    cmd = 'wasm2wat --no-check {} -o {}'.format(wasm_path, wat_path)
    subprocess.run(cmd, timeout=5, shell=True)


def wat_content2wasm(wat_content, wasm_path):
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(wat_content.encode())
        # f.flush()
    cmd = 'wat2wasm  --no-check {}  -o {}'.format(f.name, wasm_path)
    subprocess.run(cmd, timeout=5, shell=True)
    Path(f.name).unlink()


def wat2wasm(wat_path, wasm_path):
    content = path_read(wat_path)
    wat_content2wasm(content, wasm_path)


def get_wat_from_wasm(wasm_path):
    wasm_path = str(wasm_path)
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file_path = temp_file.name
    cmd = f'wasm2wat --no-check {wasm_path} -o {temp_file_path}'
    # Path(temp_file_path).unlink()
    p = subprocess.run(cmd, stderr=subprocess.PIPE,
                       stdout=subprocess.PIPE, shell=True, timeout=5)
    err_log = byte2str(p.stderr).strip(' \t\n')
    if err_log:
        return None
    else:
        content = path_read(temp_file_path)
        Path(temp_file_path).unlink()
        return content


def wasms_dir2wats(base_dir, result_dir):
    base_dir = Path(base_dir)
    result_dir = check_dir(result_dir)
    for wasm_path in tqdm(base_dir.iterdir()):
        if wasm_path.name[-5:] != '.wasm':
            continue
        # print(wasm_path)
        stem = wasm_path.name[:-5]
        wat_path = result_dir / (stem+'.wat')
        wasm2wat(wasm_path, wat_path)


# container ===========================================================


def get_log_by_container_impl(impl, wasm_wat_path):
    if isinstance(impl, str):
        impl_name = impl
        impl = cp910_contianer_impls_dict[impl_name]
    assert isinstance(impl, uninstRuntime)
    log = impl.execute_and_collect_txt(wasm_wat_path)
    return log


# lastest ===========================================================


def get_log_by_lastest_impl(impl, wasm_wat_path):
    if isinstance(impl, str):
        impl_name = impl
        impl = latest_impls_dict[impl_name]
    assert isinstance(impl, uninstRuntime)
    log = impl.execute_and_collect_txt(wasm_wat_path)
    return log


def is_executable_by_latest_impl(impl, wasm_wat_path):
    log = get_log_by_lastest_impl(impl, wasm_wat_path)
    return not is_failed_content(log)


# common ===========================================================


def get_log_by_impl(impl, wasm_wat_path):
    assert isinstance(impl, uninstRuntime)
    log = impl.execute_and_collect_txt(wasm_wat_path)
    return log


def is_executable_by_impl(impl, wasm_wat_path):
    log = get_log_by_impl(impl, wasm_wat_path)
    if is_failed_content(log):
        return False
    else:
        return True
