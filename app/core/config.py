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

    # Gemini API (문장 단순화 LLM)
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.1-flash-lite"  # 무료 티어 대상. flash-lite로 바꾸면 할당량 더 넉넉함

    # TTS 오디오 임시 저장 (개발/테스트 편의용. 운영에서는 서비스 서버 저장소로 대체 검토)
    audio_storage_dir: str = "storage/audio"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
