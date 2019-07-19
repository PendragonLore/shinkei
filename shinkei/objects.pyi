import re
from typing import Iterable, Optional, Tuple, Union

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


class VersionMetadata:
    __slots__: Iterable[str]

    # noinspection PyUnresolvedReferences
    VALIDATION_REGEX: re.Pattern  # type: ignore

    fmt: str
    _groups: Tuple[str]

    def __init__(self, fmt: str) -> None: ...

    @staticmethod
    def _can_compare(other: VersionMetadata) -> None: ...

    def __str__(self) -> str: ...

    def __repr__(self) -> str: ...

    def __eq__(self, other: VersionMetadata) -> bool: ...  # type: ignore

    def __ne__(self, other: VersionMetadata) -> bool: ...  # type: ignore

    def __le__(self, other: VersionMetadata) -> bool: ...

    def __lt__(self, other: VersionMetadata) -> bool: ...

    def __ge__(self, other: VersionMetadata) -> bool: ...

    def __gt__(self, other: VersionMetadata) -> bool: ...
