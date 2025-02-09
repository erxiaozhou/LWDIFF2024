_kwd_in_err = [ 'unhandled', 'double free or corruption', 'sanitizer', 'DEADLYSIGNAL', 'panic', 'SIGSEGV']  # 'core dump',
_kwd_in_err_v2 = _kwd_in_err +['segmentation fault']
_kwd_in_err = [k.lower() for k in _kwd_in_err]
_kwd_in_err_v2 = [k.lower() for k in _kwd_in_err_v2]


def _detect_has_crash_in_err(log):
    # print(log)
    if len(log) == 0:
        return False
    lower_log = log.lower()
    for k in _kwd_in_err:
        if k in lower_log:
            return True
    return False

def _detect_has_crash_in_err_v2(log):
    if len(log) == 0:
        return False
    lower_log = log.lower()
    for k in _kwd_in_err_v2:
        if k in lower_log:
            return True
    return False

