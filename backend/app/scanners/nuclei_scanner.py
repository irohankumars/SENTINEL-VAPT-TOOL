import json, subprocess
from .base import BaseScanner, ScannerError
from ..config import settings

class NucleiScanner(BaseScanner):
    def run(self, target: str) -> list[dict]:
        try:
            result = subprocess.run(
                [settings.nuclei_path, "-u", target, "-jsonl", "-silent", "-no-interactsh"],
                capture_output=True, text=True, timeout=settings.scanner_timeout, shell=False,
            )
        except FileNotFoundError as exc:
            raise ScannerError("Nuclei is not installed or NUCLEI_PATH is incorrect") from exc
        except subprocess.TimeoutExpired as exc:
            raise ScannerError("Nuclei scan timed out") from exc
        if result.returncode != 0:
            raise ScannerError(result.stderr.strip() or "Nuclei scan failed")
        output = []
        for line in result.stdout.splitlines():
            try: output.append(json.loads(line))
            except json.JSONDecodeError: continue
        return output
