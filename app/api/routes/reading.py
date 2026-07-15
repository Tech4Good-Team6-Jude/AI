from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.api.dependencies import get_inference_provider
from app.providers.base import InferenceProvider
from app.schemas.reading import ReadingEvaluationResponse
from app.services.reading_service import ReadingService

router = APIRouter()


@router.post("/evaluate", response_model=ReadingEvaluationResponse)
async def evaluate_reading(
    audio: Annotated[UploadFile, File()],
    expected_text: Annotated[str, Form()],
    language: Annotated[str, Form()] = "ko-KR",
    provider: InferenceProvider = Depends(get_inference_provider),
):
    content = await audio.read()
    return await ReadingService(provider).evaluate(
        audio=content,
        filename=audio.filename or "recording.webm",
        expected_text=expected_text,
        language=language,
    )
