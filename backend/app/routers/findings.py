from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Finding
from ..schemas.finding import FindingRead, FindingStatusUpdate
from ..services.finding_service import query_findings

router = APIRouter(prefix="/findings", tags=["Findings"])

@router.get("", response_model=list[FindingRead], summary="List and filter findings")
def list_findings(severity: str|None=None,tool: str|None=None,status: str|None=None,search: str|None=None,project_id: int|None=None,scan_id: int|None=None,db: Session=Depends(get_db)):
    return query_findings(db,severity,tool,status,search,project_id,scan_id)

@router.get("/{finding_id}", response_model=FindingRead, summary="Get finding details")
def get_finding(finding_id: int, db: Session = Depends(get_db)):
    finding = db.get(Finding, finding_id)
    if not finding: raise HTTPException(404, "Finding not found")
    return finding

@router.patch("/{finding_id}/status", response_model=FindingRead, summary="Update finding disposition")
def update_status(finding_id: int, payload: FindingStatusUpdate, db: Session = Depends(get_db)):
    finding = db.get(Finding, finding_id)
    if not finding: raise HTTPException(404, "Finding not found")
    finding.status = payload.status
    finding.resolution_note = payload.resolution_note
    db.commit(); db.refresh(finding); return finding
