import json
from collections import Counter
from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..models import Scan
from ..reports.html_report import render_html
from ..reports.pdf_report import render_pdf

def report_data(db: Session, scan_id: int):
    scan = db.get(Scan, scan_id)
    if not scan: raise HTTPException(404, "Scan not found")
    if scan.status != "completed": raise HTTPException(409, "Reports are only available for completed scans")
    summary = Counter(f.severity for f in scan.findings)
    ordered = {name: summary.get(name, 0) for name in ["Critical","High","Medium","Low","Informational"]}
    return scan, scan.findings, ordered, json.loads(scan.tools_used), scan.project

def create_html(db, scan_id): return render_html(*report_data(db, scan_id))
def create_pdf(db, scan_id): return render_pdf(*report_data(db, scan_id))
