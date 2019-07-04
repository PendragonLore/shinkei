from typing import Optional, Callable, Union


class ExponentialBackoff:
    _base: int
    _exp: int
    _max: int
    _reset_time: int
    _last_invocation: float
    _randfunc: Callable[..., Union[int, float]]

    def __init__(self, base: Optional[int] = ..., *, integral: Optional[bool] = ...) -> None: ...

    def delay(self) -> Union[int, float]: ...
