from pydantic import BaseModel
from typing import Sequence, Any


class Message(BaseModel):
    agents: Sequence[Any]
    info: dict


__all__ = ["Message"]
