# app/auth/base.py
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class IAuthFlow(Protocol):
    def acquire_token(self) -> dict[str, Any]:
        pass
