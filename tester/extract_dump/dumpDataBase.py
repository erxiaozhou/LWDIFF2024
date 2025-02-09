from pathlib import Path
from abc import abstractmethod

from util import CLIResult
from .dump_data_util import dumpData
from util import cmnImplResultPathGroup


class uninstDumpData(dumpData):
    def __init__(self, name, cli_result: CLIResult):
        super().__init__()
        self.name = name
        self.cli_result = cli_result
        self.exec_status = cli_result.exec_status
        self.log = cli_result.log
        self.failed_exec = not self.exec_status.is_success
        self.common_initialize()

    def common_initialize(self):
        self.can_initialize = True


class halfDumpData(uninstDumpData):
    def __init__(self, paths, name, cli_result: CLIResult):
        self.paths = paths
        assert isinstance(paths, cmnImplResultPathGroup)
        super().__init__(name, cli_result)
        if Path(self.vstack_path).exists():
            self._init_stack(self.vstack_path)

    @abstractmethod
    def _init_stack(self, path): pass

    def common_initialize(self):
        self._init_can_initialize()
        self._init_has_instance()

    def _init_can_initialize(self):
        self.can_initialize = Path(self.vstack_path).exists()

    def _init_has_instance(self):
        self.has_instance = _has_instance(self.has_instance_path)

    @property
    def to_dict(self):
        # ! ，
        new_data = dumpData()
        for k in new_data.__dict__.keys():
            new_data.__dict__[k] = self.__dict__[k]
        return new_data.to_dict

    @property
    def vstack_path(self):
        return self.paths.vstack_path

    @property
    def has_instance_path(self):
        return self.paths.inst_path

    @property
    def store_path(self):
        return self.paths.store_path


class fullDumpResultData(halfDumpData):
    def __init__(self, paths, name, cli_result: CLIResult):
        super().__init__(paths, name, cli_result)
        if Path(self.store_path).exists():
            self._init_store(self.store_path)

    @abstractmethod
    def _init_store(self, store_path): pass

    def _init_can_initialize(self):
        self.can_initialize = Path(self.store_path).exists() and Path(
            self.vstack_path).exists()


def _has_instance(path):
    has_instance_ = False
    path = Path(path)
    if path.exists():
        with open(path, 'rb') as f:
            content = f.read()
        if bytearray(content) == bytearray([0xff, 0xff, 0xff, 0xff]):
            has_instance_ = True
        else:
            has_instance_ = False
    else:
        pass
    return has_instance_
