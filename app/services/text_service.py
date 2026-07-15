from app.providers.base import InferenceProvider
from app.schemas.text import SimplifyRequest, SimplifyResponse


class TextService:
    def __init__(self, provider: InferenceProvider):
        self.provider = provider

    async def simplify(self, request: SimplifyRequest) -> SimplifyResponse:
        return await self.provider.simplify(request)
