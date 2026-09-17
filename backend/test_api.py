import os
from pathlib import Path
TEST_DATABASE = Path(__file__).parent / "data" / "test_sentinel.db"
if TEST_DATABASE.exists(): TEST_DATABASE.unlink()
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DATABASE.as_posix()}"
from fastapi.testclient import TestClient
from app.main import app
from app.processors.deduplicator import deduplicate
from app.services import scan_service

def test_complete_mock_workflow():
    with TestClient(app) as client:
        assert client.get("/docs").status_code == 200
        project = client.post("/api/projects", json={"name":"Verification Target","target_url":"https://verify.local","description":"Automated test"})
        assert project.status_code == 201
        project_id = project.json()["id"]
        scan = client.post("/api/scans", json={"project_id":project_id,"target_url":"https://verify.local","scan_mode":"standard","tools":["httpx","nuclei","zap"]})
        assert scan.status_code == 201 and scan.json()["status"] == "pending"
        scan_id = scan.json()["id"]
        started = client.post(f"/api/scans/{scan_id}/start")
        assert started.status_code == 200
        finished = client.get(f"/api/scans/{scan_id}").json()
        assert finished["status"] == "completed" and finished["progress"] == 100
        findings = client.get("/api/findings", params={"scan_id":scan_id}).json()
        assert len(findings) >= 3
        updated = client.patch(f"/api/findings/{findings[0]['id']}/status", json={"status":"resolved"})
        assert updated.status_code == 200 and updated.json()["status"] == "resolved"
        html = client.get(f"/api/reports/{scan_id}/html")
        pdf = client.get(f"/api/reports/{scan_id}/pdf")
        assert html.status_code == 200 and "SentinelVAPT" in html.text and "Verification Target" in html.text
        assert pdf.status_code == 200 and pdf.content.startswith(b"%PDF")

def test_rejects_unsafe_target_scheme():
    with TestClient(app) as client:
        response = client.post("/api/scans", json={"target_url":"file:///etc/passwd","scan_mode":"standard","tools":[]})
        assert response.status_code == 422
        for target in ["", "http://localhost", "http://127.0.0.1", "http://10.0.0.1", "http://169.254.1.1", "http://192.0.2.1", "ftp://example.com", "http://user:pass@example.com"]:
            assert client.post("/api/scans", json={"target_url":target,"scan_mode":"standard","tools":[]}).status_code == 422

def test_project_crud_and_missing_resource():
    with TestClient(app) as client:
        created = client.post("/api/projects", json={"name":"CRUD Target","target_url":"https://crud.example","description":"before"})
        assert created.status_code == 201
        project_id = created.json()["id"]
        assert client.get(f"/api/projects/{project_id}").json()["name"] == "CRUD Target"
        updated = client.put(f"/api/projects/{project_id}", json={"name":"Updated Target","description":"after"})
        assert updated.status_code == 200 and updated.json()["description"] == "after"
        assert client.delete(f"/api/projects/{project_id}").status_code == 204
        assert client.get(f"/api/projects/{project_id}").status_code == 404

def test_scan_validates_project_and_state_transition():
    with TestClient(app) as client:
        missing = client.post("/api/scans", json={"project_id":999999,"target_url":"https://example.com","scan_mode":"standard","tools":[]})
        assert missing.status_code == 404
        scan = client.post("/api/scans", json={"target_url":"https://example.com","scan_mode":"passive","tools":[]}).json()
        assert client.post(f"/api/scans/{scan['id']}/cancel").json()["status"] == "cancelled"
        assert client.post(f"/api/scans/{scan['id']}/start").status_code == 409
        assert client.get(f"/api/reports/{scan['id']}/pdf").status_code == 409
        assert client.get("/api/reports/999999/pdf").status_code == 404

def test_finding_filters_and_confirmed_status():
    with TestClient(app) as client:
        findings = client.get("/api/findings", params={"severity":"High","tool":"Nuclei"})
        assert findings.status_code == 200
        if findings.json():
            finding_id = findings.json()[0]["id"]
            updated = client.patch(f"/api/findings/{finding_id}/status", json={"status":"confirmed","resolution_note":"Manually reproduced"})
            assert updated.status_code == 200
            assert updated.json()["status"] == "confirmed"
            assert updated.json()["resolution_note"] == "Manually reproduced"
        assert client.patch("/api/findings/999999/status", json={"status":"invented"}).status_code == 422

def test_deduplication_normalizes_known_aliases():
    rows = [
        {"url":"https://example.com/","title":"Missing CSP","tool":"ZAP"},
        {"url":"https://example.com","title":"Content-Security-Policy Header Missing","tool":"Nuclei"},
    ]
    assert len(deduplicate(rows)) == 1

def test_scanner_failure_is_persisted(monkeypatch):
    monkeypatch.setattr(scan_service.settings, "mock_scanners", False)
    monkeypatch.setattr(scan_service.SafeHttpScanner, "run", lambda *_: (_ for _ in ()).throw(RuntimeError("controlled scanner failure")))
    with TestClient(app) as client:
        scan = client.post("/api/scans", json={"target_url":"https://example.com","scan_mode":"passive","tools":["httpx"]}).json()
        client.post(f"/api/scans/{scan['id']}/start")
        result = client.get(f"/api/scans/{scan['id']}").json()
        assert result["status"] == "failed"
        assert "controlled scanner failure" in result["error_message"]
    monkeypatch.setattr(scan_service.settings, "mock_scanners", True)

def test_dashboard_and_security_headers():
    with TestClient(app) as client:
        response = client.get("/api/dashboard")
        assert response.status_code == 200
        assert {"metrics","severity","recent_scans","recent_findings"} <= response.json().keys()
        assert response.headers["x-content-type-options"] == "nosniff"
