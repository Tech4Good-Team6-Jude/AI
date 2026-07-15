from pydantic import BaseModel, Field

from app.schemas.common import InferenceMetadata


class TrainingGenerateRequest(BaseModel):
    reading_level: int = Field(ge=1, le=10)
    weak_phonemes: list[str] = Field(default_factory=list)
    error_types: list[str] = Field(default_factory=list)
    duration_minutes: int = Field(default=10, ge=1, le=30)
    exclude_recent_item_ids: list[str] = Field(default_factory=list)


class TrainingItem(BaseModel):
    item_id: str
    type: str
    text: str
    choices: list[str] | None = None
    target_phonemes: list[str] = Field(default_factory=list)


class TrainingGenerateResponse(InferenceMetadata):
    items: list[TrainingItem]
