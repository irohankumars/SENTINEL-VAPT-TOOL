import httpx
from .base import BaseScanner, ScannerError
from ..config import settings
from ..services.target_service import validate_network_target, UnsafeTargetError

SECURITY_HEADERS = {
    "content-security-policy": ("Missing Content-Security-Policy", "Medium", "CWE-693", 5.3, "Define a restrictive Content-Security-Policy header."),
    "strict-transport-security": ("Missing HSTS Header", "Low", "CWE-319", 3.1, "Enable HSTS after confirming HTTPS coverage."),
    "x-content-type-options": ("Missing X-Content-Type-Options", "Low", "CWE-693", 3.1, "Set X-Content-Type-Options to nosniff."),
    "x-frame-options": ("Missing Clickjacking Protection", "Medium", "CWE-1021", 4.3, "Set frame-ancestors in CSP or X-Frame-Options."),
    "referrer-policy": ("Missing Referrer-Policy", "Low", "CWE-200", 3.1, "Set an appropriate Referrer-Policy."),
}

class SafeHttpScanner(BaseScanner):
    def run(self, target: str) -> list[dict]:
        try:
            validate_network_target(target)
            limits = httpx.Limits(max_connections=3, max_keepalive_connections=1)
            with httpx.Client(timeout=httpx.Timeout(10, connect=5), follow_redirects=True, max_redirects=5, limits=limits, headers={"User-Agent":"SentinelVAPT/0.1 defensive-assessment"}) as client:
                with client.stream("GET", target) as response:
                    size = 0
                    for chunk in response.iter_bytes():
                        size += len(chunk)
                        if size > settings.max_response_bytes: break
                    final_url, headers, status = str(response.url), response.headers, response.status_code
            findings = []
            for header, (title,severity,cwe,cvss,remediation) in SECURITY_HEADERS.items():
                if header not in headers and not (header == "strict-transport-security" and not final_url.startswith("https://")):
                    findings.append({"title":title,"severity":severity,"category":"Security Misconfiguration","description":f"The response does not include the {header} security header.","url":final_url,"tool":"HTTP Scanner","cwe":cwe,"cvss":cvss,"evidence":f"{header} header absent (HTTP {status})","impact":"Browser-side security protections may be reduced.","remediation":remediation})
            if headers.get("server"):
                findings.append({"title":"Server Header Disclosure","severity":"Informational","category":"Information Disclosure","description":"The response identifies its web server.","url":final_url,"tool":"HTTP Scanner","cwe":"CWE-200","cvss":0.0,"evidence":f"Server: {headers['server']}","impact":"Technology details can assist targeted reconnaissance.","remediation":"Suppress unnecessary server product and version details."})
            for cookie in headers.get_list("set-cookie"):
                missing = [flag for flag in ("Secure","HttpOnly","SameSite") if flag.lower() not in cookie.lower()]
                if missing:
                    findings.append({"title":"Cookie Missing Security Attributes","severity":"Medium","category":"Session Management","description":"A response cookie lacks recommended security attributes.","url":final_url,"tool":"HTTP Scanner","cwe":"CWE-614","cvss":5.3,"evidence":f"Missing: {', '.join(missing)}","impact":"Session cookies may be exposed to theft or cross-site requests.","remediation":"Apply Secure, HttpOnly, and an appropriate SameSite policy."})
            return findings
        except UnsafeTargetError as exc: raise ScannerError(str(exc)) from exc
        except httpx.HTTPError as exc: raise ScannerError(f"HTTP assessment failed: {exc}") from exc
