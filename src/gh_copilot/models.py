from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class PlaceholderKind(str, Enum):
    TODO = "TODO"
    FIXME = "FIXME"
    TBD = "TBD"


class PlaceholderTask(BaseModel):
    file: str
    line: int
    kind: PlaceholderKind
    sha: str | None = None
    ts: datetime = Field(default_factory=datetime.utcnow)


class ScoreModel(BaseModel):
    model_id: str
    lint: float = 0.30
    tests: float = 0.40
    placeholders: float = 0.20
    sessions: float = 0.10
    min_score: float = 0.85
    effective_from: datetime


class ScoreInputs(BaseModel):
    run_id: str
    lint: float
    tests: float
    placeholders: float
    sessions: float
    model_id: str
    ts: datetime = Field(default_factory=datetime.utcnow)


class ScoreSnapshot(BaseModel):
    branch: str
    score: float
    model_id: str
    inputs: ScoreInputs
    ts: datetime = Field(default_factory=datetime.utcnow)
