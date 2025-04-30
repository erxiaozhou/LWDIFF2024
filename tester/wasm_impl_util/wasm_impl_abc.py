from abc import ABC
from abc import abstractmethod


class WasmImpl(ABC):
    @abstractmethod
    def execute_and_collect(self):
        pass
