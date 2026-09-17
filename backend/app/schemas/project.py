from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator
from urllib.parse import urlparse
import ipaddress

def validate_http_url(value: str) -> str:
    parsed = urlparse(str(value))
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Only valid HTTP/HTTPS targets are allowed")
    if parsed.username or parsed.password:
        raise ValueError("Target URLs must not contain credentials")
    hostname = (parsed.hostname or "").lower().rstrip(".")
    if hostname == "localhost" or hostname.endswith(".localhost"):
        raise ValueError("Loopback targets are not allowed")
    try:
        if not ipaddress.ip_address(hostname).is_global:
            raise ValueError("Private, loopback, link-local, and reserved targets are blocked")
    except ValueError as exc:
        if "blocked" in str(exc): raise
    return str(value).rstrip("/")

class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    target_url: str
    description: str | None = None
    _url = field_validator("target_url")(validate_http_url)

class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    target_url: str | None = None
    description: str | None = None
    _url = field_validator("target_url")(lambda v: validate_http_url(v) if v else v)

class ProjectRead(ProjectCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime
    scan_count: int = 0
    finding_count: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
