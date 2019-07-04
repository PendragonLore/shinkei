from typing import Tuple, List


class HandlerMeta(type):
    __shinkei_handlers__: List[Tuple[str, str]]
    __shinkei_handler_name__: str


def listens_to(name: str): ...


class Handler(metaclass=HandlerMeta):
    __shinkei_handlers__: List[Tuple[str, str]]
    __shinkei_handler_name__: str

    @property
    def qualified_name(self) -> str: ...
