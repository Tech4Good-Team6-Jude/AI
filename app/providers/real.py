from app.providers.clients.ocr_client import OcrClient
from app.providers.clients.tts_client import TtsClient
from app.providers.clients.stt_client import SttClient
from app.providers.clients.llm_client import LlmClient
from app.schemas.text import SimplifyRequest, SimplifyResponse, SimilarRequest, SimilarResponse # ◀ 추가
from app.schemas.ocr import BoundingBox, OcrBlock, OcrResponse
from app.schemas.speech import TtsRequest, SttResponse, TtsResponse, WordTiming
from app.schemas.training import TrainingGenerateRequest, TrainingGenerateResponse, TrainingItem

class RealInferenceProvider:
    def __init__(self):
        self.ocr_client = OcrClient()
        self.tts_client = TtsClient()
        self.stt_client = SttClient()
        self.llm_client = LlmClient()

    async def ocr(
        self,
        *,
        content: bytes,
        filename: str,
        language: str,
        include_bounding_boxes: bool,
    ) -> OcrResponse:
        return await self.ocr_client.extract(
            content=content,
            filename=filename,
            language=language,
            include_bounding_boxes=include_bounding_boxes,
        )

    # 🎯 우리가 방금 추가하려 했던 유사 문장 세트 생성 기능!
    async def generate_training(
        self,
        request: TrainingGenerateRequest,
    ) -> TrainingGenerateResponse:
        
        items_data = await self.llm_client.generate_training(
            reading_level=request.reading_level,
            weak_phonemes=request.weak_phonemes,
            error_types=request.error_types,
            duration_minutes=request.duration_minutes,
            exclude_recent_item_ids=request.exclude_recent_item_ids
        )

        items = [
            TrainingItem(
                item_id=item["item_id"],
                type=item["type"],
                text=item["text"],
                choices=item["choices"],
                target_phonemes=item["target_phonemes"]
            )
            for item in items_data
        ]

        return TrainingGenerateResponse(
            items=items,
            model_version="free-rule-based-llm-v1"
        )
    async def generate_similar(self, request: SimilarRequest) -> SimilarResponse:
        sentences = await self.llm_client.generate_similar(
            text=request.text, 
            count=request.count
        )
        return SimilarResponse(
            original_text=request.text,
            similar_sentences=sentences,
            model_version="free-rule-based-similar-v1"
        )