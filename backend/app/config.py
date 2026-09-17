import os
from pathlib import Path
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")

class Settings:
    database_url = os.getenv("DATABASE_URL", "sqlite:///./data/sentinel.db")
    httpx_path = os.getenv("HTTPX_PATH", "httpx")
    nuclei_path = os.getenv("NUCLEI_PATH", "nuclei")
    zap_url = os.getenv("ZAP_URL", "http://localhost:8080")
    ai_api_key = os.getenv("AI_API_KEY", "")
    ai_api_url = os.getenv("AI_API_URL", "https://api.openai.com/v1")
    ai_model = os.getenv("AI_MODEL", "")
    mock_scanners = os.getenv("MOCK_SCANNERS", "true").lower() in {"1", "true", "yes"}
    scanner_timeout = int(os.getenv("SCANNER_TIMEOUT", "120"))
    allow_private_targets = os.getenv("ALLOW_PRIVATE_TARGETS", "false").lower() in {"1", "true", "yes"}
    max_response_bytes = int(os.getenv("MAX_RESPONSE_BYTES", "1048576"))
    cors_origins = [x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if x.strip()]

settings = Settings()
