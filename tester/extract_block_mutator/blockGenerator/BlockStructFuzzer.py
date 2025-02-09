from typing import Protocol

class BlockStructFuzzer(Protocol):
    def init_block(self):
        ...
    def expand_tree(self) -> None:
        ...