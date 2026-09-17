from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from ..models import Finding, Scan

def query_findings(db: Session, severity=None, tool=None, status=None, search=None, project_id=None, scan_id=None):
    query = select(Finding).join(Scan)
    if severity: query = query.where(Finding.severity.ilike(severity))
    if tool: query = query.where(Finding.tool.ilike(tool))
    if status: query = query.where(Finding.status.ilike(status))
    if scan_id: query = query.where(Finding.scan_id == scan_id)
    if project_id: query = query.where(Scan.project_id == project_id)
    if search:
        pattern = f"%{search}%"
        query = query.where(or_(Finding.title.ilike(pattern), Finding.url.ilike(pattern), Finding.description.ilike(pattern)))
    return list(db.scalars(query.order_by(Finding.created_at.desc())))
