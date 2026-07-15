from app.core.errors import AppError
from app.providers.base import InferenceProvider
from app.schemas.ocr import OcrResponse


class OcrService:
    def __init__(self, provider: InferenceProvider):
        self.provider = provider

    async def extract(
        self,
        *,
        content: bytes,
        filename: str,
        language: str,
        include_bounding_boxes: bool,
    ) -> OcrResponse:
        if not content:
            raise AppError(code="EMPTY_FILE", message="업로드된 파일이 비어 있어.")
        return await self.provider.ocr(
            content=content,
            filename=filename,
            language=language,
            include_bounding_boxes=include_bounding_boxes,
        )
