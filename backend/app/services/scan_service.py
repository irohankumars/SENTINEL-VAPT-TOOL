import hashlib, json, logging, time
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from ..config import settings
from ..database import SessionLocal
from ..models import Finding, Scan
from ..processors.normalizer import normalize_httpx, normalize_nuclei, normalize_zap
from ..processors.deduplicator import deduplicate
from ..scanners.http_scanner import SafeHttpScanner
from ..scanners.nuclei_scanner import NucleiScanner
from ..scanners.zap_scanner import ZapScanner
from ..scanners.base import ScannerError
from .ai_service import explain_finding

logger = logging.getLogger(__name__)

MOCK_RESULTS = [
 {"title":"Missing Content-Security-Policy","severity":"Medium","category":"Security Misconfiguration","description":"The response does not define a Content-Security-Policy header.","url":"{target}/","tool":"OWASP ZAP","cwe":"CWE-693","cvss":5.3,"evidence":"Content-Security-Policy header absent","impact":"Browsers have fewer restrictions on injected content.","remediation":"Define a restrictive Content-Security-Policy header."},
 {"title":"Exposed Environment File","severity":"High","category":"Information Disclosure","description":"An environment configuration file was accessible over HTTP.","url":"{target}/.env","tool":"Nuclei","cwe":"CWE-200","cvss":7.5,"evidence":"HTTP 200 with environment-style keys","impact":"Secrets and internal configuration may be disclosed.","remediation":"Block access to dotfiles and rotate exposed secrets."},
 {"title":"Missing HSTS Header","severity":"Low","category":"Security Misconfiguration","description":"Strict-Transport-Security is not set.","url":"{target}/","tool":"OWASP ZAP","cwe":"CWE-319","cvss":3.1,"evidence":"Strict-Transport-Security header absent","impact":"Initial connections may be vulnerable to protocol downgrade.","remediation":"Set Strict-Transport-Security after confirming HTTPS coverage."},
]

def _update(db: Session, scan: Scan, progress: int, stage: str):
    scan.progress, scan.current_stage = progress, stage
    db.commit()

def execute_scan(scan_id: int):
    db = SessionLocal()
    scan = db.get(Scan, scan_id)
    if not scan: db.close(); return
    started = time.monotonic()
    try:
        scan.status, scan.started_at, scan.error_message = "running", datetime.now(timezone.utc), None
        _update(db, scan, 5, "Target validation")
        tools = json.loads(scan.tools_used)
        results = []
        if settings.mock_scanners:
            for progress, stage in [(20,"HTTP reconnaissance"),(45,"Nuclei scan"),(70,"ZAP scan")]:
                if scan.cancel_requested: raise InterruptedError
                _update(db, scan, progress, stage); time.sleep(.25)
            results = [{**item, "url":item["url"].format(target=scan.target_url.rstrip('/'))} for item in MOCK_RESULTS]
        else:
            runners = {"httpx":(SafeHttpScanner(),lambda item, target: [item],"HTTP assessment"),"nuclei":(NucleiScanner(),normalize_nuclei,"Nuclei scan"),"zap":(ZapScanner(scan.scan_mode),normalize_zap,"ZAP scan")}
            for index, tool in enumerate(tools):
                if scan.cancel_requested: raise InterruptedError
                scanner, normalizer, stage = runners[tool]
                _update(db, scan, 15 + index * 20, stage)
                for raw in scanner.run(scan.target_url): results.extend(normalizer(raw, scan.target_url))
        _update(db, scan, 80, "Result processing")
        results = deduplicate(results)
        _update(db, scan, 90, "AI analysis")
        for item in results:
            ai = explain_finding(item)
            item["ai_explanation"] = ai if isinstance(ai, str) else None
            item["fingerprint"] = hashlib.sha256(f"{item.get('url','').lower()}|{item.get('title','').lower()}".encode()).hexdigest()
            db.add(Finding(scan_id=scan.id, **item))
        scan.status, scan.progress, scan.current_stage = "completed", 100, "Completed"
        scan.completed_at, scan.duration = datetime.now(timezone.utc), round(time.monotonic()-started, 2)
        db.commit()
    except InterruptedError:
        scan.status, scan.current_stage, scan.completed_at = "cancelled", "Cancelled", datetime.now(timezone.utc)
        scan.duration = round(time.monotonic()-started, 2); db.commit()
    except (ScannerError, Exception) as exc:
        logger.exception("Scan %s failed", scan_id)
        scan.status, scan.current_stage, scan.error_message = "failed", "Failed", str(exc)[:1000]
        scan.completed_at, scan.duration = datetime.now(timezone.utc), round(time.monotonic()-started, 2); db.commit()
    finally: db.close()
