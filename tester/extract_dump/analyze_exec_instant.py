from .dump_data_util import dumpData


def at_least_one_can_execute(dumped_results):
    return _get_can_execute_num(dumped_results) > 0


def at_least_one_can_instantiate(dumped_results):
    return _get_can_instantiate(dumped_results) > 0


def _get_can_execute_num(dumped_results):
    can_exec_num = 0
    for result in dumped_results:
        assert isinstance(result, dumpData)
        if not result.failed_exec:
            can_exec_num += 1
    return can_exec_num


def _get_can_instantiate(dumped_results):
    can_inst_num = 0
    for result in dumped_results:
        assert isinstance(result, dumpData)
        if result.has_instance:
            can_inst_num += 1
    return can_inst_num
