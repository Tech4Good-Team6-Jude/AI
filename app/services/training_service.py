from app.providers.base import InferenceProvider
from app.schemas.training import TrainingGenerateRequest, TrainingGenerateResponse


class TrainingService:
    def __init__(self, provider: InferenceProvider):
        self.provider = provider

    async def generate(
        self,
        request: TrainingGenerateRequest,
    ) -> TrainingGenerateResponse:
        return await self.provider.generate_training(request)
