from dataclasses import dataclass


@dataclass
class OcrResult:
    text: str
    blocks: list[dict]


class OcrClient:
    def __init__(self):
        # OCR SDK나 모델 초기화
        # self.client = ...
        pass

    async def extract(
        self,
        *,
        content: bytes,
        filename: str,
        language: str,
        include_bounding_boxes: bool,
    ) -> OcrResult:
        # 여기서 실제 OCR 서비스를 호출
        result = await self._call_ocr_model(content)

        return OcrResult(
            text=result["text"],
            blocks=result["blocks"],
        )

    async def _call_ocr_model(self, content: bytes) -> dict:
        raise NotImplementedError("실제 OCR 구현 필요")