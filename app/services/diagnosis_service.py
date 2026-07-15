from app.providers.base import InferenceProvider
from app.schemas.diagnosis import DiagnosisAnalyzeRequest, DiagnosisAnalyzeResponse


class DiagnosisService:
    def __init__(self, provider: InferenceProvider):
        self.provider = provider

    async def analyze(
        self,
        request: DiagnosisAnalyzeRequest,
    ) -> DiagnosisAnalyzeResponse:
        return await self.provider.analyze_diagnosis(request)
