import re
from urllib.parse import urlsplit, urlunsplit

ALIASES = {"contentsecuritypolicy header missing":"missing content security policy", "content security policy header missing":"missing content security policy", "missing csp":"missing content security policy"}

def _key(item: dict) -> tuple[str, str]:
    parts = urlsplit(item.get("url", ""))
    url = urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/") or "/", "", ""))
    title = re.sub(r"[^a-z0-9 ]", "", item.get("title", "").lower()).strip()
    title = ALIASES.get(title, title)
    return url, title

def deduplicate(findings: list[dict]) -> list[dict]:
    unique = {}
    for finding in findings:
        key = _key(finding)
        if key not in unique:
            unique[key] = finding
    return list(unique.values())
