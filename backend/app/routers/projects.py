from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from ..database import get_db
from ..models import Project, Scan
from ..schemas.project import ProjectCreate, ProjectRead, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["Projects"])

def serialize(project):
    data = ProjectRead.model_validate(project).model_dump()
    data["scan_count"] = len(project.scans)
    findings = [finding for scan in project.scans for finding in scan.findings]
    data["finding_count"] = len(findings)
    data["critical_count"] = sum(f.severity == "Critical" for f in findings)
    data["high_count"] = sum(f.severity == "High" for f in findings)
    data["medium_count"] = sum(f.severity == "Medium" for f in findings)
    return data

@router.get("", response_model=list[ProjectRead], summary="List projects")
def list_projects(db: Session = Depends(get_db)):
    items = db.scalars(select(Project).options(selectinload(Project.scans).selectinload(Scan.findings)).order_by(Project.updated_at.desc())).all()
    return [serialize(item) for item in items]

@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED, summary="Create a project")
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(**payload.model_dump()); db.add(project); db.commit(); db.refresh(project)
    return serialize(project)

@router.get("/{project_id}", response_model=ProjectRead, summary="Get a project")
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.scalar(select(Project).where(Project.id == project_id).options(selectinload(Project.scans).selectinload(Scan.findings)))
    if not project: raise HTTPException(404, "Project not found")
    return serialize(project)

@router.put("/{project_id}", response_model=ProjectRead, summary="Update a project")
def update_project(project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project: raise HTTPException(404, "Project not found")
    for key, value in payload.model_dump(exclude_unset=True).items(): setattr(project, key, value)
    db.commit(); db.refresh(project); return serialize(project)

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a project")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project: raise HTTPException(404, "Project not found")
    db.delete(project); db.commit(); return Response(status_code=204)
