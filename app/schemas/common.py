from pydantic import BaseModel, Field


class InferenceMetadata(BaseModel):
    model_version: str
    latency_ms: float | None = Field(default=None, ge=0)
