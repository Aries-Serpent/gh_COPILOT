from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class GaugeBreakdown(BaseModel):
    name: str
    value: float
    target: float | None = None
    ts: datetime = Field(default_factory=datetime.utcnow)


class ComplianceSummary(BaseModel):
    branch: str
    score: float | None
    model_id: str | None = None
    placeholders_open: int = 0
    gauges: list[GaugeBreakdown] = Field(default_factory=list)
    ts: datetime = Field(default_factory=datetime.utcnow)


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

