from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import InferenceMetadata


class ReadingScores(BaseModel):
    accuracy: int = Field(ge=0, le=100)
    fluency: int = Field(ge=0, le=100)
    completeness: int = Field(ge=0, le=100)
    pronunciation: int = Field(ge=0, le=100)
    words_per_minute: float = Field(ge=0)


class WordEvaluation(BaseModel):
    expected: str
    spoken: str
    status: Literal["CORRECT", "MISPRONOUNCED", "OMITTED", "INSERTED"]
    score: int = Field(ge=0, le=100)
    weak_phoneme: str | None = None


class ReadingEvaluationResponse(InferenceMetadata):
    transcript: str
    scores: ReadingScores
    word_results: list[WordEvaluation]
    feedback: str
