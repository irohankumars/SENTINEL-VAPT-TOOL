import json, subprocess, threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import httpx
import pytest
from app.config import settings
from app.processors.normalizer import normalize_nuclei, normalize_zap
from app.scanners.base import ScannerError
from app.scanners.http_scanner import SafeHttpScanner
from app.scanners.nuclei_scanner import NucleiScanner
from app.scanners.zap_scanner import ZapScanner
from app.services.target_service import UnsafeTargetError, validate_network_target

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/redirect":
            self.send_response(302); self.send_header("Location", "/redirect"); self.end_headers(); return
        self.send_response(200); self.send_header("Server", "RegressionServer/1.0"); self.send_header("Set-Cookie", "session=test"); self.end_headers()
        self.wfile.write(b"x" * (settings.max_response_bytes + 100))
    def log_message(self, *_): pass

@pytest.fixture
def local_server():
    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    previous = settings.allow_private_targets; settings.allow_private_targets = True
    yield f"http://127.0.0.1:{server.server_port}"
    settings.allow_private_targets = previous; server.shutdown(); thread.join()

def test_safe_http_scanner_headers_cookie_size_and_redirect(local_server):
    findings = SafeHttpScanner().run(local_server)
    titles = {row["title"] for row in findings}
    assert "Missing Content-Security-Policy" in titles
    assert "Server Header Disclosure" in titles
    assert "Cookie Missing Security Attributes" in titles
    with pytest.raises(ScannerError, match="redirect"):
        SafeHttpScanner().run(local_server + "/redirect")

def test_target_dns_rebinding_protection(monkeypatch):
    monkeypatch.setattr(settings, "allow_private_targets", False)
    monkeypatch.setattr("socket.getaddrinfo", lambda *_args, **_kwargs: [(2,1,6,"",("127.0.0.1",80))])
    with pytest.raises(UnsafeTargetError, match="blocked"):
        validate_network_target("https://apparently-public.example")

def test_nuclei_missing_timeout_malformed_and_valid(monkeypatch):
    scanner = NucleiScanner()
    monkeypatch.setattr(subprocess, "run", lambda *_a, **_k: (_ for _ in ()).throw(FileNotFoundError()))
    with pytest.raises(ScannerError, match="not installed"): scanner.run("https://example.com")
    monkeypatch.setattr(subprocess, "run", lambda *_a, **_k: (_ for _ in ()).throw(subprocess.TimeoutExpired("nuclei", 1)))
    with pytest.raises(ScannerError, match="timed out"): scanner.run("https://example.com")
    class Result: returncode=0; stderr=""; stdout='not-json\n'+json.dumps({"template-id":"missing-csp","matched-at":"https://example.com","info":{"name":"Missing CSP","severity":"medium"}})
    monkeypatch.setattr(subprocess, "run", lambda *_a, **_k: Result())
    rows = scanner.run("https://example.com")
    assert len(rows) == 1 and normalize_nuclei(rows[0], "https://example.com")[0]["severity"] == "Medium"

class FakeResponse:
    def __init__(self, payload): self.payload=payload
    def raise_for_status(self): return None
    def json(self): return self.payload
class FakeZapClient:
    def __init__(self,*_a,**_k): pass
    def __enter__(self): return self
    def __exit__(self,*_a): pass
    def get(self,url,params=None):
        if "/action/scan/" in url: return FakeResponse({"scan":"7"})
        if "/view/status/" in url: return FakeResponse({"status":"100"})
        if "/view/alerts/" in url: return FakeResponse({"alerts":[{"alert":"Missing CSP","risk":"Medium","url":"https://example.com","cweid":"693"}]})
        return FakeResponse({"version":"2.16"})

def test_zap_unavailable_polling_success_and_normalization(monkeypatch):
    monkeypatch.setattr(httpx, "Client", lambda *_a, **_k: (_ for _ in ()).throw(httpx.ConnectError("offline")))
    with pytest.raises(ScannerError, match="unavailable"): ZapScanner().run("https://example.com")
    monkeypatch.setattr(httpx, "Client", FakeZapClient)
    rows = ZapScanner("standard").run("https://example.com")
    normalized = normalize_zap(rows[0], "https://example.com")[0]
    assert normalized["title"] == "Missing CSP" and normalized["severity"] == "Medium"
