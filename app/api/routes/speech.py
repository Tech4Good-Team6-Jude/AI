from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.api.dependencies import get_inference_provider
from app.providers.base import InferenceProvider
from app.schemas.speech import SttResponse, TtsRequest, TtsResponse
from app.services.speech_service import SpeechService

router = APIRouter()


@router.post("/transcribe", response_model=SttResponse)
async def transcribe(
    audio: Annotated[UploadFile, File()],
    language: Annotated[str, Form()] = "ko-KR",
    expected_text: Annotated[str | None, Form()] = None,
    provider: InferenceProvider = Depends(get_inference_provider),
):
    content = await audio.read()
    return await SpeechService(provider).transcribe(
        audio=content,
        filename=audio.filename or "recording.webm",
        language=language,
        expected_text=expected_text,
    )


@router.post("/synthesize", response_model=TtsResponse)
async def synthesize(
    request: TtsRequest,
    provider: InferenceProvider = Depends(get_inference_provider),
):
    return await SpeechService(provider).synthesize(request)
