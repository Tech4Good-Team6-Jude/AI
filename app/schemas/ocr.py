from pydantic import BaseModel, Field

from app.schemas.common import InferenceMetadata


class BoundingBox(BaseModel):
    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)
    width: float = Field(ge=0, le=1)
    height: float = Field(ge=0, le=1)


class OcrBlock(BaseModel):
    text: str
    confidence: float = Field(ge=0, le=1)
    bounding_box: BoundingBox | None = None


class OcrResponse(InferenceMetadata):
    text: str
    blocks: list[OcrBlock]
