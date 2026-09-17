import json
from collections import Counter
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Finding, Project, Scan

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("", summary="Get dashboard metrics and recent activity")
def dashboard(db: Session = Depends(get_db)):
    severity = Counter(dict(db.execute(select(Finding.severity, func.count(Finding.id)).group_by(Finding.severity)).all()))
    statuses = Counter(dict(db.execute(select(Scan.status, func.count(Scan.id)).group_by(Scan.status)).all()))
    recent_scans = list(db.scalars(select(Scan).order_by(Scan.id.desc()).limit(5)))
    recent_findings = list(db.scalars(select(Finding).order_by(Finding.created_at.desc()).limit(5)))
    return {
        "metrics": {"projects":db.scalar(select(func.count(Project.id))) or 0,"scans":sum(statuses.values()),"active_scans":statuses.get("running",0)+statuses.get("pending",0),"completed_scans":statuses.get("completed",0),"open_findings":db.scalar(select(func.count(Finding.id)).where(Finding.status.in_(["open","confirmed"]))) or 0},
        "severity": {name:severity.get(name,0) for name in ["Critical","High","Medium","Low","Informational"]},
        "recent_scans": [{"id":s.id,"project_id":s.project_id,"target_url":s.target_url,"status":s.status,"scan_mode":s.scan_mode,"started_at":s.started_at,"completed_at":s.completed_at,"duration":s.duration,"tools":json.loads(s.tools_used),"progress":s.progress,"current_stage":s.current_stage,"error_message":s.error_message,"finding_count":len(s.findings)} for s in recent_scans],
        "recent_findings": recent_findings,
    }
