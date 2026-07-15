from app.providers.base import InferenceProvider
from app.schemas.ocr import OcrResponse

class OcrService:
    def __init__(self, provider: InferenceProvider):
        # 팩토리에 의해 결정된 InferenceProvider(여기서는 RealInferenceProvider)를 주입받습니다.
        self.provider = provider

    async def extract(
        self,
        *,
        content: bytes,
        filename: str,
        language: str = "ko",
        include_bounding_boxes: bool = False,
    ) -> OcrResponse:
        # 실제 AI Provider의 ocr 함수를 호출하여 결과를 반환합니다.
        return await self.provider.ocr(
            content=content,
            filename=filename,
            language=language,
            include_bounding_boxes=include_bounding_boxes,
        )