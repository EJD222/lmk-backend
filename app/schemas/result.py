from datetime import datetime

from pydantic import BaseModel
from typing import Any

from app.constants import ResultType


class ResultOut(BaseModel):
    id: str
    type: ResultType
    value: Any


class SessionMeta(BaseModel):
    topic: str
    participant_count: int
    created_at: datetime
    top_pick: ResultOut | None

class ResultsResponse(BaseModel):
    results: list[ResultOut]
    meta: SessionMeta