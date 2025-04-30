from functools import lru_cache
from .one_runtime_log_util import oneRuntimeLog


def log_dict2key(log_dict: dict[str, oneRuntimeLog])->str:
    sorted_keys = get_sorted_keys(tuple(log_dict.keys()))
    sorted_list = []
    for k in sorted_keys:
        one_log = log_dict[k]
        if str(one_log):
            impl_repr = f'<{k}::{one_log}>'
            sorted_list.append(impl_repr)
    key = '||'.join(sorted_list)
    return key


@lru_cache(maxsize=1024, typed=False)
def get_sorted_keys(keys):
    return sorted(keys, key=lambda x: x)