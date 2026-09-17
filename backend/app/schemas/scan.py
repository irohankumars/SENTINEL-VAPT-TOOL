from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator
from .project import validate_http_url

class ScanCreate(BaseModel):
    project_id: int | None = None
    target_url: str
    scan_mode: Literal["passive", "standard", "active"] = "standard"
    tools: list[Literal["httpx", "nuclei", "zap"]] = Field(default_factory=lambda: ["httpx", "nuclei", "zap"])
    _url = field_validator("target_url")(validate_http_url)

class ScanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    project_id: int | None
    target_url: str
    status: str
    scan_mode: str
    started_at: datetime | None
    completed_at: datetime | None
    duration: float | None
    tools: list[str] = Field(default_factory=list)
    progress: int
    current_stage: str
    error_message: str | None
    finding_count: int = 0
