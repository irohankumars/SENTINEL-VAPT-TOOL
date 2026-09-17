from datetime import datetime, timezone
from sqlalchemy import DateTime, Float, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base

class Finding(Base):
    __tablename__ = "findings"
    id: Mapped[int] = mapped_column(primary_key=True)
    scan_id: Mapped[int] = mapped_column(ForeignKey("scans.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(250))
    severity: Mapped[str] = mapped_column(String(20))
    category: Mapped[str] = mapped_column(String(120), default="Security Misconfiguration")
    description: Mapped[str] = mapped_column(Text, default="")
    url: Mapped[str] = mapped_column(String(2048))
    tool: Mapped[str] = mapped_column(String(60))
    cwe: Mapped[str | None] = mapped_column(String(30), nullable=True)
    cvss: Mapped[float | None] = mapped_column(Float, nullable=True)
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    impact: Mapped[str | None] = mapped_column(Text, nullable=True)
    remediation: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=True)
    resolution_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    fingerprint: Mapped[str | None] = mapped_column(String(64), nullable=True)
    scan: Mapped["Scan"] = relationship(back_populates="findings")
    __table_args__ = (Index("ix_findings_scan_severity", "scan_id", "severity"), Index("ix_findings_status", "status"))
