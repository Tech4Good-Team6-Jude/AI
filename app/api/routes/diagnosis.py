from fastapi import APIRouter, Depends

from app.api.dependencies import get_inference_provider
from app.providers.base import InferenceProvider
from app.schemas.diagnosis import DiagnosisAnalyzeRequest, DiagnosisAnalyzeResponse
from app.services.diagnosis_service import DiagnosisService

router = APIRouter()


@router.post("/analyze", response_model=DiagnosisAnalyzeResponse)
async def analyze(
    request: DiagnosisAnalyzeRequest,
    provider: InferenceProvider = Depends(get_inference_provider),
):
    return await DiagnosisService(provider).analyze(request)
