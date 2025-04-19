# app/db/connection/base.py
from typing import Any, Protocol

from typing_extensions import runtime_checkable


@runtime_checkable
class IConnectionManager(Protocol):
    async def connect(self) -> Any:
        pass

    async def close(self) -> None:
        pass

    async def ensure_database(self) -> None:
        pass
