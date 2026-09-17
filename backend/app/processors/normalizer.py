from ..services.severity_service import normalize_severity, cvss_for_severity

def normalize_httpx(item: dict, target: str) -> list[dict]:
    findings = []
    technologies = item.get("tech", []) or item.get("technologies", [])
    if technologies or item.get("webserver"):
        details = ", ".join(technologies + ([item["webserver"]] if item.get("webserver") else []))
        findings.append({"title":"Technology Disclosure","severity":"Informational","category":"Information Disclosure","description":"The target exposes technology information in its responses.","url":item.get("url", target),"tool":"httpx","cwe":"CWE-200","cvss":0.0,"evidence":details,"impact":"Technology details may help an attacker select targeted tests.","remediation":"Remove unnecessary version and server headers."})
    return findings

def normalize_nuclei(item: dict, target: str) -> list[dict]:
    info = item.get("info", {})
    severity = normalize_severity(info.get("severity"))
    classification = info.get("classification", {}) or {}
    cwe = classification.get("cwe-id") or classification.get("cwe_id")
    if isinstance(cwe, list): cwe = cwe[0] if cwe else None
    return [{"title":info.get("name") or item.get("template-id", "Nuclei finding"),"severity":severity,"category":(info.get("tags") or ["Vulnerability"])[0] if isinstance(info.get("tags"), list) else "Vulnerability","description":info.get("description", "Detected by a Nuclei template."),"url":item.get("matched-at", target),"tool":"Nuclei","cwe":cwe,"cvss":classification.get("cvss-score") or cvss_for_severity(severity),"evidence":item.get("matcher-name") or item.get("template-id"),"impact":"The detected condition may weaken application security.","remediation":"Review the linked template guidance and correct the affected component."}]

def normalize_zap(item: dict, target: str) -> list[dict]:
    risk = item.get("risk", item.get("riskdesc", "Informational")).split()[0]
    severity = normalize_severity(risk)
    return [{"title":item.get("alert", "OWASP ZAP finding"),"severity":severity,"category":item.get("alertRef", "Web Application Security"),"description":item.get("description", "Detected by OWASP ZAP."),"url":item.get("url", target),"tool":"OWASP ZAP","cwe":f"CWE-{item['cweid']}" if item.get("cweid") and str(item.get("cweid")) != "0" else None,"cvss":cvss_for_severity(severity),"evidence":item.get("evidence") or item.get("param"),"impact":item.get("other", "This condition may weaken application security."),"remediation":item.get("solution", "Review and correct the affected application behavior.")}]
