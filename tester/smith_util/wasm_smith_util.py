from file_util import default_exec_cmd_without_return


# head -c 10000 /dev/urandom | wasm-tools smith --bulk-memory-enabled true --canonicalize-nans true --max-imports 0 --reference-types-enabled true --simd-enabled true -o tt.wasm
default_cmd = 'head -c {} /dev/urandom | wasm-tools smith -o {}'
a_tested_fmt = 'head -c {} /dev/urandom | wasm-tools smith --bulk-memory-enabled true --canonicalize-nans true --max-imports 0 --reference-types-enabled true --simd-enabled true --max-instructions 20000 -o {}'

non_can_fmt = 'head -c {} /dev/urandom | wasm-tools smith --bulk-memory-enabled true --canonicalize-nans false --max-imports 0 --reference-types-enabled true --simd-enabled true --max-instructions 20000 -o {}'

a_tested_fmt = 'head -c {} /dev/urandom | wasm-tools smith --export-everything true  --allow-start-export true --min-funcs 1 --bulk-memory-enabled true --canonicalize-nans false --max-imports 0 --reference-types-enabled true  --simd-enabled true --max-instructions 20000 -o {}'

# --ensure-termination true
# a_tested_ensure_term_fmt = 'head -c {} /dev/urandom | wasm-tools smith --export-everything true  --allow-start-export true --min-funcs 1 --bulk-memory-enabled true --canonicalize-nans false --max-imports 0 --reference-types-enabled true  --simd-enabled true --max-instructions 20000 --ensure-termination -o {}'
simd_ensure_term_fmt = 'head -c {} /dev/urandom | wasm-tools smith --export-everything true  --min-funcs 1 --max-imports 0 --reference-types-enabled true  --simd-enabled true --max-instructions 20000 --ensure-termination -o {}'

a_default_fmt = 'head -c {} /dev/urandom | wasm-tools smith --export-everything true  --min-funcs 1  --max-imports 0 --reference-types-enabled true  --max-instructions 20000  -o {}'

a_default_simplest_fmt = 'head -c {} /dev/urandom | wasm-tools smith --export-everything true  --min-funcs 1  --max-imports 0   --max-instructions 20000  -o {}'

a_default_ensure_term_fmt = 'head -c {} /dev/urandom | wasm-tools smith --export-everything true  --min-funcs 1  --max-imports 0 --reference-types-enabled true  --max-instructions 20000 --ensure-termination -o {}'

a_default_bm_fmt = 'head -c {} /dev/urandom | wasm-tools smith --export-everything true  --min-funcs 1 --bulk-memory-enabled true --max-memories 1 --max-imports 0 --reference-types-enabled true  --max-instructions 20000  -o {}'

a_default_ensure_bm_term_fmt = 'head -c {} /dev/urandom | wasm-tools smith --export-everything true  --min-funcs 1  --bulk-memory-enabled true --max-memories 1 --max-imports 0 --reference-types-enabled true  --max-instructions 20000 --ensure-termination -o {}'
simd_ensure_term_bm_fmt = 'head -c {} /dev/urandom | wasm-tools smith --export-everything true  --min-funcs 1  --bulk-memory-enabled true --max-memories 1 --max-imports 0 --reference-types-enabled true  --simd-enabled true --max-instructions 20000 --ensure-termination -o {}'
a_default_ensure_bm_may_invalid_term_fmt = 'head -c {} /dev/urandom | wasm-tools smith --export-everything true  --maybe-invalid  --min-funcs 1  --bulk-memory-enabled true --max-memories 1 --max-imports 0 --reference-types-enabled true  --max-instructions 20000 --ensure-termination -o {}'

def gen_a_tested_wasm(size, path):
    cmd = a_tested_fmt.format(size, path)
    default_exec_cmd_without_return(cmd)

def gen_a_non_can_wasm(size, path):
    cmd = non_can_fmt.format(size, path)
    default_exec_cmd_without_return(cmd)

def gen_a_non_can_ensure_term_wasm(size, path):
    cmd = simd_ensure_term_fmt.format(size, path)
    # print(cmd, end='  ') 
    # assert 0
    # raise Exception("Here is an exception")
    default_exec_cmd_without_return(cmd)


def gen_a_default_wasm(size, path):
    cmd = a_default_fmt.format(size, path)
    default_exec_cmd_without_return(cmd)
# def exec_a_case

def gen_a_default_ensure_term_wasm(size, path):
    cmd = a_default_ensure_term_fmt.format(size, path)
    default_exec_cmd_without_return(cmd)


def generate_case_with_cmd_template(cmd, size, path):
    cmd = cmd.format(size, path)
    default_exec_cmd_without_return(cmd, timeout=10)
