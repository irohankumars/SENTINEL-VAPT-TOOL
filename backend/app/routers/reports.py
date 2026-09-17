from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.report_service import create_html, create_pdf

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/{scan_id}/pdf", summary="Download a PDF assessment report")
def pdf_report(scan_id: int, db: Session = Depends(get_db)):
    return Response(create_pdf(db, scan_id), media_type="application/pdf", headers={"Content-Disposition":f'attachment; filename="sentinel-scan-{scan_id}.pdf"'})

@router.get("/{scan_id}/html", summary="Download an HTML assessment report")
def html_report(scan_id: int, db: Session = Depends(get_db)):
    return Response(create_html(db, scan_id), media_type="text/html", headers={"Content-Disposition":f'attachment; filename="sentinel-scan-{scan_id}.html"'})
