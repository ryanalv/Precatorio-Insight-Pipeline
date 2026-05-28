from dataclasses import dataclass
from functools import lru_cache
import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _resolve_database_path(value: str | None) -> Path:
    if not value:
        return BASE_DIR / "precatorio_insight.db"

    path = Path(value)
    return path if path.is_absolute() else BASE_DIR / path


@dataclass(frozen=True)
class Settings:
    qwen_api_key: str | None
    qwen_base_url: str | None
    qwen_model: str
    database_path: Path


@lru_cache
def get_settings() -> Settings:
    return Settings(
        qwen_api_key=os.getenv("QWEN_API_KEY") or None,
        qwen_base_url=os.getenv("QWEN_BASE_URL") or None,
        qwen_model=os.getenv("QWEN_MODEL", "qwen-14b"),
        database_path=_resolve_database_path(os.getenv("DATABASE_PATH")),
    )
