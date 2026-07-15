from app.core.errors import AppError
from app.providers.base import InferenceProvider
from app.schemas.speech import SttResponse, TtsRequest, TtsResponse


class SpeechService:
    def __init__(self, provider: InferenceProvider):
        self.provider = provider

    async def transcribe(
        self,
        *,
        audio: bytes,
        filename: str,
        language: str,
        expected_text: str | None,
    ) -> SttResponse:
        if not audio:
            raise AppError(code="EMPTY_AUDIO", message="녹음 파일이 비어 있어.")
        return await self.provider.transcribe(
            audio=audio,
            filename=filename,
            language=language,
            expected_text=expected_text,
        )

    async def synthesize(self, request: TtsRequest) -> TtsResponse:
        return await self.provider.synthesize(request)
