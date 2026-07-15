from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.api.dependencies import get_inference_provider
from app.providers.base import InferenceProvider
from app.schemas.ocr import OcrResponse
from app.services.ocr_service import OcrService

router = APIRouter()


@router.post("", response_model=OcrResponse)
async def extract_text(
    file: Annotated[UploadFile, File()],
    language: Annotated[str, Form()] = "ko",
    include_bounding_boxes: Annotated[bool, Form()] = True,
    provider: InferenceProvider = Depends(get_inference_provider),
):
    content = await file.read()
    return await OcrService(provider).extract(
        content=content,
        filename=file.filename or "upload",
        language=language,
        include_bounding_boxes=include_bounding_boxes,
    )
