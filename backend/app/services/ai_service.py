import logging
import httpx
from ..config import settings

logger = logging.getLogger(__name__)

def explain_finding(finding: dict) -> dict | None:
    if not settings.ai_api_key or not settings.ai_model:
        return None
    prompt = ("Explain this security finding for a beginner. Return JSON with explanation, impact, and remediation only. "
              f"Title: {finding['title']}; severity: {finding['severity']}; URL: {finding['url']}; description: {finding.get('description','')}")
    try:
        response = httpx.post(f"{settings.ai_api_url.rstrip('/')}/chat/completions", headers={"Authorization":f"Bearer {settings.ai_api_key}"}, json={"model":settings.ai_model,"response_format":{"type":"json_object"},"messages":[{"role":"system","content":"You explain defensive security findings. Never provide exploitation steps."},{"role":"user","content":prompt}]}, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as exc:
        logger.warning("AI explanation unavailable: %s", exc)
        return None
