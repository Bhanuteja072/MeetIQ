from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    mongodb_url: str = Field("mongodb://localhost:27017", validation_alias="MONGO_URL")
    database_name: str = Field("Meeting_Partner", validation_alias="DATABASE_NAME")
    huggingface_token: str = Field("", validation_alias="HUGGINGFACE_TOKEN")
    assemblyai_api_key: str = Field("", validation_alias="ASSEMBLYAI_API_KEY")
    groq_api_key: str = Field("", validation_alias="GROQ_API_KEY")
    upload_dir: str = Field("/tmp/uploads", validation_alias="UPLOAD_DIR")
    max_file_size_mb: int = Field(200, validation_alias="MAX_FILE_SIZE_MB")
    jwt_secret: str = Field("", validation_alias="JWT_SECRET")
    jwt_algorithm: str = Field("HS256", validation_alias="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(4320, validation_alias="JWT_EXPIRE_MINUTES")  # 3 days
    resend_api_key: str = Field("", validation_alias="RESEND_API_KEY")
    from_email: str = Field("", validation_alias="FROM_EMAIL")
settings = Settings()

# Create upload directory if it doesn't exist
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)