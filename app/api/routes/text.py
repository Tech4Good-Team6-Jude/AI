from fastapi import APIRouter, Depends

from app.api.dependencies import get_inference_provider
from app.providers.base import InferenceProvider
from app.schemas.text import SimplifyRequest, SimplifyResponse, SimilarRequest, SimilarResponse
from app.services.text_service import TextService

router = APIRouter()


@router.post("/simplify", response_model=SimplifyResponse)
async def simplify(
    request: SimplifyRequest,
    provider: InferenceProvider = Depends(get_inference_provider),
):
    return await TextService(provider).simplify(request)
@router.post("/similar", response_model=SimilarResponse)
async def generate_similar(
    request: SimilarRequest,
    provider: InferenceProvider = Depends(get_inference_provider),
):
    return await TextService(provider).generate_similar(request)