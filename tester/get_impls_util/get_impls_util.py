from .container_impl_paras.cimpl_ori_cp910_paras import cimpl_ori_cp910_paras
from wasm_impl_util import dumpRuntime
from wasm_impl_util import uninstRuntime
from .impl_paras_lastest import impl_paras_lastest
from .impl_paras_always_new import impl_paras_always_new


def get_ori_cp910_impls():
    impls = []
    for name, para_dict_ in cimpl_ori_cp910_paras.items():
        impl = uninstRuntime.from_cdict(name, para_dict_)
        impls.append(impl)
    return impls


def get_always_new_uninst_impls():
    impls = []
    for name in impl_paras_always_new.keys():
        impl = uninstRuntime.from_new_dict(name, impl_paras_always_new[name])
        impls.append(impl)
    return impls


def get_lastest_uninst_impls():
    impls = []
    for name in impl_paras_lastest.keys():
        impl = uninstRuntime.from_new_dict(name, impl_paras_lastest[name])
        impls.append(impl)
    return impls


def get_lastest_halfdump_impls():
    impls = []
    for name in impl_paras_lastest.keys():
        impl = dumpRuntime.from_new_dict(name, impl_paras_lastest[name])
        impls.append(impl)
    return impls
