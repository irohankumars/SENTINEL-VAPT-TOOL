import json
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from ..database import get_db
from ..models import Project, Scan
from ..schemas.scan import ScanCreate, ScanRead
from ..services.scan_service import execute_scan

router = APIRouter(prefix="/scans", tags=["Scans"])

def serialize(scan):
    data = ScanRead.model_validate(scan).model_dump()
    data["tools"] = json.loads(scan.tools_used)
    data["finding_count"] = len(scan.findings)
    return data

def find_scan(db, scan_id):
    scan = db.scalar(select(Scan).where(Scan.id == scan_id).options(selectinload(Scan.findings)))
    if not scan: raise HTTPException(404, "Scan not found")
    return scan

@router.get("", response_model=list[ScanRead], summary="List scans")
def list_scans(project_id: int | None = None, db: Session = Depends(get_db)):
    query = select(Scan).options(selectinload(Scan.findings)).order_by(Scan.id.desc())
    if project_id: query = query.where(Scan.project_id == project_id)
    return [serialize(x) for x in db.scalars(query).all()]

@router.post("", response_model=ScanRead, status_code=status.HTTP_201_CREATED, summary="Create a pending scan")
def create_scan(payload: ScanCreate, db: Session = Depends(get_db)):
    if payload.project_id and not db.get(Project, payload.project_id): raise HTTPException(404, "Project not found")
    scan = Scan(project_id=payload.project_id,target_url=payload.target_url,status="pending",scan_mode=payload.scan_mode,tools_used=json.dumps(payload.tools))
    db.add(scan); db.commit(); db.refresh(scan); return serialize(scan)

@router.get("/{scan_id}", response_model=ScanRead, summary="Get scan status and progress")
def get_scan(scan_id: int, db: Session = Depends(get_db)): return serialize(find_scan(db, scan_id))

@router.post("/{scan_id}/start", response_model=ScanRead, summary="Start a scan in the background")
def start_scan(scan_id: int, tasks: BackgroundTasks, db: Session = Depends(get_db)):
    scan = find_scan(db, scan_id)
    if scan.status != "pending": raise HTTPException(409, f"Scan cannot start from status '{scan.status}'")
    scan.status, scan.current_stage, scan.progress = "running", "Queued", 1; db.commit()
    tasks.add_task(execute_scan, scan.id)
    return serialize(scan)

@router.post("/{scan_id}/cancel", response_model=ScanRead, summary="Cancel a pending or running scan")
def cancel_scan(scan_id: int, db: Session = Depends(get_db)):
    scan = find_scan(db, scan_id)
    if scan.status not in {"pending","running"}: raise HTTPException(409, f"Scan cannot be cancelled from status '{scan.status}'")
    scan.cancel_requested = True
    if scan.status == "pending": scan.status, scan.current_stage = "cancelled", "Cancelled"
    db.commit(); return serialize(scan)
