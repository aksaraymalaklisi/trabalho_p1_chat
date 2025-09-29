from __future__ import annotations
from pathlib import Path

# This project targets Pydantic v2. BaseSettings lives in `pydantic-settings`.
try:
	from pydantic_settings import BaseSettings  # type: ignore
	from pydantic import Field  # type: ignore
except Exception as exc:  # pragma: no cover - environment dependent
	raise RuntimeError(
		"This project requires pydantic v2 and pydantic-settings. Install them: `pip install pydantic pydantic-settings`."
	) from exc

ROOT = Path(__file__).resolve().parents[1]
class Settings(BaseSettings):
	"""Application settings loaded from environment (or .env file).

	This uses Pydantic BaseSettings so values are validated and documented.
	Both `model_config` (pydantic v2) and `Config` (pydantic v1) are provided
	to increase compatibility across versions.
	"""

	# keep empty by default to avoid raising on import; runtime access should
	# validate presence before connecting to DB
	MONGO_URL: str = Field("", env="MONGO_URL")
	MONGO_DB: str = Field("chatdb", env="MONGO_DB")
	DEFAULT_LIMIT: int = Field(20)
	MAX_LIMIT: int = Field(100)

	# pydantic v2 configuration
	model_config = {"env_file": str(ROOT / ".env"), "env_file_encoding": "utf-8"}

settings = Settings()

# top-level convenience variables (used across the app)
MONGO_URL: str = settings.MONGO_URL
MONGO_DB: str = settings.MONGO_DB
DEFAULT_LIMIT: int = settings.DEFAULT_LIMIT
MAX_LIMIT: int = settings.MAX_LIMIT
