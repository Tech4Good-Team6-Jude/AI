from pydantic import BaseModel, Field

from app.schemas.common import InferenceMetadata


class WordTiming(BaseModel):
    text: str
    start_ms: int = Field(ge=0)
    end_ms: int = Field(ge=0)


class SttResponse(InferenceMetadata):
    transcript: str
    confidence: float = Field(ge=0, le=1)
    words: list[WordTiming]


class TtsRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    voice_id: str = "female-01"
    speed: float = Field(default=0.8, ge=0.5, le=1.5)
    include_timings: bool = True


class TtsResponse(InferenceMetadata):
    audio_url: str
    audio_format: str = "mp3"
    duration_ms: int = Field(ge=0)
    timings: list[WordTiming]