from fastapi import APIRouter, Depends

from app.api.dependencies import get_inference_provider
from app.providers.base import InferenceProvider
from app.schemas.text import SimplifyRequest, SimplifyResponse
from app.services.text_service import TextService

router = APIRouter()


@router.post("/simplify", response_model=SimplifyResponse)
async def simplify(
    request: SimplifyRequest,
    provider: InferenceProvider = Depends(get_inference_provider),
):
    return await TextService(provider).simplify(request)
