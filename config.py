from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    mongodb_url: str ="mongodb://localhost:27017",
    database_name: str = "Meeting_Partner",
    upload_dir: str = "uploads",
    max_file_size_mb: int = 100

    class config:
        env_file = ".env"
settings = Settings()

# Create upload directory if it doesn't exist
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)