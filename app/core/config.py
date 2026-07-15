from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    api_prefix: str = "/internal/v1"
    provider: str = "mock"
    enable_docs: bool = True
    max_upload_mb: int = 20

    # faster-whisper (STT)
    stt_model_size: str = "small"   # tiny/base/small/medium/large-v3
    stt_device: str = "cpu"         # cpu 또는 cuda
    stt_compute_type: str = "int8"  # cpu면 int8, GPU면 float16 권장

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
