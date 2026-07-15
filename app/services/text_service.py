from app.providers.base import InferenceProvider
from app.schemas.text import SimplifyRequest, SimplifyResponse, SimilarRequest, SimilarResponse

class TextService:
    def __init__(self, provider: InferenceProvider):
        self.provider = provider

    async def simplify(self, request: SimplifyRequest) -> SimplifyResponse:
        return await self.provider.simplify(request)

    async def generate_similar(self, request: SimilarRequest) -> SimilarResponse:
        return await self.provider.generate_similar(request)