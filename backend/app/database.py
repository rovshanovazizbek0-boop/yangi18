from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import DATABASE_URL

FALLBACK_SQLITE_URL = "sqlite:///./ainews.db"


def normalize_database_url(url: str) -> str:
    raw = (url or "").strip() or FALLBACK_SQLITE_URL
    if raw.startswith("postgres://"):
        return "postgresql+psycopg2://" + raw[len("postgres://") :]
    return raw


def resolve_database_url(url: str = DATABASE_URL) -> str:
    normalized = normalize_database_url(url)
    if normalized.startswith("sqlite"):
        return normalized

    probe = create_engine(
        normalized,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 5},
    )
    try:
        with probe.connect() as conn:
            conn.execute(text("SELECT 1"))
        return normalized
    except Exception as error:
        print(
            f"OGOHLANTIRISH: PostgreSQL bazaga ulanib bo'lmadi ({error}); "
            f"vaqtinchalik {FALLBACK_SQLITE_URL} ishlatiladi."
        )
        return FALLBACK_SQLITE_URL
    finally:
        probe.dispose()


ACTIVE_DATABASE_URL = resolve_database_url(DATABASE_URL)
if ACTIVE_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        ACTIVE_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_engine(
        ACTIVE_DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
    )

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
