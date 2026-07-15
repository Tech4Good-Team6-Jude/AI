from pydantic import BaseModel, Field

from app.schemas.common import InferenceMetadata


class DiagnosisResponseItem(BaseModel):
    item_id: str
    expected_text: str
    transcript: str
    accuracy: int = Field(ge=0, le=100)
    pronunciation: int = Field(ge=0, le=100)


class DiagnosisAnalyzeRequest(BaseModel):
    grade: int = Field(ge=1, le=12)
    responses: list[DiagnosisResponseItem] = Field(min_length=1)


class DiagnosisAnalyzeResponse(InferenceMetadata):
    reading_level: int = Field(ge=1, le=10)
    error_types: list[str]
    weak_phonemes: list[str]
    recommended_training: list[str]
