from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Müfredat Analiz"
    database_url: str = f"sqlite:///{ROOT / 'data' / 'mufredat.db'}"
    request_delay_seconds: float = 1.5
    max_requests_per_domain_per_minute: int = 20
    user_agent: str = (
        "MufredatAnalizBot/1.0 (ogrenci projesi; kamuya acik mufredat)"
    )
    respect_robots_txt: bool = True
    playwright_enabled: bool = False
    snapshot_dir: Path = ROOT / "data" / "snapshots"


settings = Settings()
settings.snapshot_dir.mkdir(parents=True, exist_ok=True)
(ROOT / "data").mkdir(parents=True, exist_ok=True)
