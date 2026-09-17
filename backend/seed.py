import json
from datetime import datetime, timezone, timedelta
from app.database import SessionLocal, init_db
from app.models import Project, Scan, Finding

def seed():
    init_db(); db = SessionLocal()
    if db.query(Project).count(): print("Seed skipped: database already contains projects"); db.close(); return
    velora=Project(name="Velora E-Commerce",target_url="https://velora.local",description="Student e-commerce application")
    campus=Project(name="Campus Connect",target_url="https://campus.sentinel.local",description="Campus collaboration portal")
    db.add_all([velora,campus]); db.flush()
    now=datetime.now(timezone.utc)
    scans=[Scan(project_id=velora.id,target_url=velora.target_url,status="completed",scan_mode="standard",started_at=now-timedelta(days=1,minutes=3),completed_at=now-timedelta(days=1),duration=161,tools_used=json.dumps(["httpx","nuclei","zap"]),progress=100,current_stage="Completed"),Scan(project_id=campus.id,target_url=campus.target_url,status="completed",scan_mode="passive",started_at=now-timedelta(days=3,minutes=2),completed_at=now-timedelta(days=3),duration=112,tools_used=json.dumps(["httpx","zap"]),progress=100,current_stage="Completed"),Scan(project_id=velora.id,target_url=velora.target_url,status="failed",scan_mode="standard",started_at=now-timedelta(days=5),completed_at=now-timedelta(days=5),duration=18,tools_used=json.dumps(["httpx","nuclei"]),progress=20,current_stage="Failed",error_message="Nuclei was unavailable")]
    db.add_all(scans); db.flush()
    samples=[("SQL Injection","Critical","Injection","/api/login","Nuclei","CWE-89",9.8),("Exposed Environment File","High","Information Disclosure","/.env","Nuclei","CWE-200",7.5),("Missing Content-Security-Policy","Medium","Security Misconfiguration","/","OWASP ZAP","CWE-693",5.3),("Missing HSTS Header","Low","Security Misconfiguration","/","OWASP ZAP","CWE-319",3.1),("Technology Disclosure","Informational","Information Disclosure","/","httpx","CWE-200",0.0)]
    for i,(title,severity,category,path,tool,cwe,cvss) in enumerate(samples): db.add(Finding(scan_id=scans[0 if i<4 else 1].id,title=title,severity=severity,category=category,description=f"{title} was detected during the authorized assessment.",url=(velora.target_url if i<4 else campus.target_url)+path,tool=tool,cwe=cwe,cvss=cvss,evidence="Sample scanner evidence",impact="This condition may weaken application security.",remediation="Review the affected behavior and apply the recommended secure configuration."))
    db.commit(); db.close(); print("Seeded 2 projects, 3 scans, and 5 findings")

if __name__ == "__main__": seed()
