import json, subprocess
from .base import BaseScanner, ScannerError
from ..config import settings

class HttpxScanner(BaseScanner):
    def run(self, target: str) -> list[dict]:
        try:
            result = subprocess.run(
                [settings.httpx_path, "-u", target, "-json", "-silent", "-tech-detect", "-title", "-server"],
                capture_output=True, text=True, timeout=settings.scanner_timeout, shell=False,
            )
        except FileNotFoundError as exc:
            raise ScannerError("httpx is not installed or HTTPX_PATH is incorrect") from exc
        except subprocess.TimeoutExpired as exc:
            raise ScannerError("httpx scan timed out") from exc
        if result.returncode != 0:
            raise ScannerError(result.stderr.strip() or "httpx scan failed")
        output = []
        for line in result.stdout.splitlines():
            try: output.append(json.loads(line))
            except json.JSONDecodeError: continue
        return output
