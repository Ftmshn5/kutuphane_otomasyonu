"""Veritabanı bağlantısı. DATABASE_URL ortam değişkeniyle değiştirilebilir."""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://kutuphane:kutuphane@localhost:5432/kutuphane_db",
)

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Tüm tablo sınıflarının ortak atası."""


def get_db():
    """Her istek için ayrı bir veritabanı oturumu açar ve sonunda kapatır."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
