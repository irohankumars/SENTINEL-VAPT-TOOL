from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict

class FindingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    scan_id: int
    title: str
    severity: str
    category: str
    description: str
    url: str
    tool: str
    cwe: str | None
    cvss: float | None
    evidence: str | None
    impact: str | None
    remediation: str | None
    ai_explanation: str | None
    status: str
    created_at: datetime
    updated_at: datetime | None = None
    resolution_note: str | None = None
    fingerprint: str | None = None

class FindingStatusUpdate(BaseModel):
    status: Literal["open", "confirmed", "resolved", "false_positive"]
    resolution_note: str | None = None
