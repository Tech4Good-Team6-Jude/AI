from fastapi import APIRouter, Depends

from app.api.dependencies import get_inference_provider
from app.providers.base import InferenceProvider
from app.schemas.training import TrainingGenerateRequest, TrainingGenerateResponse
from app.services.training_service import TrainingService

router = APIRouter()


@router.post("/generate", response_model=TrainingGenerateResponse)
async def generate(
    request: TrainingGenerateRequest,
    provider: InferenceProvider = Depends(get_inference_provider),
):
    return await TrainingService(provider).generate(request)
