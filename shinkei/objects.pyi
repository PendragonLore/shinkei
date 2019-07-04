from typing import Iterable, Optional, Union


class Version:
    __slots__: Iterable[str]

    api: str
    singyeong: str

    def __init__(self, data: dict) -> None: ...

    def __repr__(self) -> str: ...


class MetadataPayload:
    __slots__: Iterable[str]

    sender: str
    nonce: Optional[str]
    payload: Union[str, int, float, dict]

    def __init__(self, data: dict) -> None: ...

    def __repr__(self) -> str: ...

