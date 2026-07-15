from app.core.errors import AppError
from app.providers.base import InferenceProvider
from app.schemas.reading import ReadingEvaluationResponse


class ReadingService:
    def __init__(self, provider: InferenceProvider):
        self.provider = provider

    async def evaluate(
        self,
        *,
        audio: bytes,
        filename: str,
        expected_text: str,
        language: str,
    ) -> ReadingEvaluationResponse:
        if not audio:
            raise AppError(code="EMPTY_AUDIO", message="녹음 파일이 비어 있어.")
        if not expected_text.strip():
            raise AppError(code="EMPTY_EXPECTED_TEXT", message="정답 문장이 필요해.")
        return await self.provider.evaluate_reading(
            audio=audio,
            filename=filename,
            expected_text=expected_text,
            language=language,
        )
