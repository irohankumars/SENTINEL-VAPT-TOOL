from pathlib import Path
from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from .config import settings, BACKEND_DIR

if settings.database_url.startswith("sqlite:///./"):
    relative = settings.database_url.removeprefix("sqlite:///./")
    database_url = f"sqlite:///{(BACKEND_DIR / relative).as_posix()}"
else:
    database_url = settings.database_url

if database_url.startswith("sqlite:///"):
    Path(database_url.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(database_url, connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {})
if database_url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _enable_foreign_keys(connection, _):
        cursor = connection.cursor(); cursor.execute("PRAGMA foreign_keys=ON"); cursor.close()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from .models import Project, Scan, Finding  # noqa: F401
    Base.metadata.create_all(bind=engine)
    # Small additive migrations keep existing local databases usable without a migration framework.
    columns = {column["name"] for column in inspect(engine).get_columns("findings")}
    with engine.begin() as connection:
        if "updated_at" not in columns:
            connection.execute(text("ALTER TABLE findings ADD COLUMN updated_at DATETIME"))
        if "resolution_note" not in columns:
            connection.execute(text("ALTER TABLE findings ADD COLUMN resolution_note TEXT"))
        if "fingerprint" not in columns:
            connection.execute(text("ALTER TABLE findings ADD COLUMN fingerprint VARCHAR(64)"))
        connection.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_findings_scan_fingerprint ON findings (scan_id, fingerprint)"))
