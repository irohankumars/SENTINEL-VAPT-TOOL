import httpx, time
from .base import BaseScanner, ScannerError
from ..config import settings

class ZapScanner(BaseScanner):
    def __init__(self, mode: str = "standard"):
        self.mode = mode

    def run(self, target: str) -> list[dict]:
        try:
            deadline = time.monotonic() + settings.scanner_timeout
            with httpx.Client(timeout=min(settings.scanner_timeout, 30)) as client:
                client.get(f"{settings.zap_url.rstrip('/')}/JSON/core/view/version/").raise_for_status()
                client.get(f"{settings.zap_url.rstrip('/')}/JSON/core/action/accessUrl/", params={"url": target, "followRedirects": "true"}).raise_for_status()
                if self.mode == "standard":
                    scan_id = client.get(f"{settings.zap_url.rstrip('/')}/JSON/spider/action/scan/", params={"url": target, "recurse": "true"}).json().get("scan")
                    self._wait(client, "spider", scan_id, deadline)
                elif self.mode == "active":
                    # Active mode is only reachable through the explicit scan_mode API field.
                    scan_id = client.get(f"{settings.zap_url.rstrip('/')}/JSON/ascan/action/scan/", params={"url": target, "recurse": "true"}).json().get("scan")
                    self._wait(client, "ascan", scan_id, deadline)
                response = client.get(f"{settings.zap_url.rstrip('/')}/JSON/core/view/alerts/", params={"baseurl": target})
                response.raise_for_status()
                return response.json().get("alerts", [])
        except (httpx.HTTPError, ValueError) as exc:
            raise ScannerError(f"OWASP ZAP is unavailable: {exc}") from exc

    def _wait(self, client: httpx.Client, component: str, scan_id: str | None, deadline: float):
        if scan_id is None: raise ScannerError(f"ZAP did not return a {component} scan ID")
        while time.monotonic() < deadline:
            response = client.get(f"{settings.zap_url.rstrip('/')}/JSON/{component}/view/status/", params={"scanId":scan_id})
            response.raise_for_status()
            if int(response.json().get("status", 0)) >= 100: return
            time.sleep(1)
        raise ScannerError(f"OWASP ZAP {component} scan timed out")
