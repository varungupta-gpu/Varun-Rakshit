import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    App-level settings — env-overridable with sensible defaults.
    Constants (WORLD_CONFIG, thresholds) and path defaults live here
    so every entry point (main.py, run_job.py) shares a single source of truth.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # ── Environment ──────────────────────────────────────────────────
    IS_DOCKER: bool = os.path.exists("/app")
    DATA_DIR: str = os.getenv("DATA_DIR", "/app/data" if os.path.exists("/app") else "./data")
    LOG_LEVEL: str = "DEBUG"
    CLEANUP_AFTER_REQUEST: bool = False

    # ── GCP / Cloud ──────────────────────────────────────────────────
    GCP_PROJECT_ID: str = "video-backend-dev"
    GCS_BUCKET_NAME: str = "video-platform-storage-dev"
    REGION: str = "asia-south1"
    GOOGLE_API_KEY: str = "AIzaSyC7bALRM3hKEVKbffCmgirAgOYgJ1alGlw"

    # ── Langfuse ─────────────────────────────────────────────────────
    LANGFUSE_SECRET_KEY: str = "sk-lf-e1e3d9f5-da14-4c3b-8ce6-a39bb18c9a96"
    LANGFUSE_PUBLIC_KEY: str = "pk-lf-91e86b78-1ab4-4390-8a4b-013d53bfc14f"
    LANGFUSE_BASE_URL: str = "https://cloud.langfuse.com"

settings = Settings()
