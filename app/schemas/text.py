from pydantic import BaseModel, Field

from app.schemas.common import InferenceMetadata


class SimplifyRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)
    target_reading_level: int = Field(default=3, ge=1, le=10)
    include_definitions: bool = True


class DifficultWord(BaseModel):
    word: str
    meaning: str


class SimplifyResponse(InferenceMetadata):
    original_text: str
    simplified_text: str
    explanation: str
    difficult_words: list[DifficultWord]
