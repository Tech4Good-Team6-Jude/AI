from app.core.audio_storage import build_audio_url, save_audio
from app.pipelines.reading_pipeline import ReadingPipeline
from app.providers.clients.llm_client import LlmClient
from app.providers.clients.ocr_client import OcrClient
from app.providers.clients.stt_client import SttClient
from app.providers.clients.tts_client import TtsClient

from app.schemas.ocr import OcrResponse
from app.schemas.reading import ReadingEvaluationResponse, ReadingScores, WordEvaluation
from app.schemas.speech import TtsRequest, SttResponse, TtsResponse, WordTiming
from app.schemas.text import DifficultWord, SimilarRequest, SimilarResponse, SimplifyRequest, SimplifyResponse
from app.schemas.training import TrainingGenerateRequest, TrainingGenerateResponse, TrainingItem


class RealInferenceProvider:
    def __init__(self):
        self.ocr_client = OcrClient()
        self.tts_client = TtsClient()
        self.stt_client = SttClient()
        self.llm_client = LlmClient()
        self.reading_pipeline = ReadingPipeline(self.stt_client)

    async def ocr(
        self,
        *,
        content: bytes,
        filename: str,
        language: str,
        include_bounding_boxes: bool,
    ) -> OcrResponse:
        # ocr_client가 이미 완성된 OcrResponse(OcrBlock 객체 리스트 포함)를
        # 반환하므로 그대로 돌려준다. 여기서 딕셔너리로 취급해 재조립하면 안 된다.
        return await self.ocr_client.extract(
            content=content,
            filename=filename,
            language=language,
            include_bounding_boxes=include_bounding_boxes,
        )

    async def synthesize(self, request: TtsRequest) -> TtsResponse:
        result = await self.tts_client.synthesize(
            text=request.text,
            voice_id=request.voice_id,
            speed=request.speed,
            include_timings=request.include_timings,
        )

        filename = save_audio(result.audio_bytes)

        return TtsResponse(
            audio_url=build_audio_url(filename),
            duration_ms=result.duration_ms,
            timings=[
                WordTiming(
                    text=item["text"],
                    start_ms=item["start_ms"],
                    end_ms=item["end_ms"],
                )
                for item in result.timings
            ],
            model_version="real-tts-v1",
        )

    async def transcribe(
        self,
        *,
        audio: bytes,
        filename: str,
        language: str,
        expected_text: str | None,
    ) -> SttResponse:
        result = await self.stt_client.transcribe(
            audio=audio,
            filename=filename,
            language=language,
        )

        return SttResponse(
            transcript=result.transcript,
            confidence=result.confidence,
            words=[
                WordTiming(
                    text=word.text,
                    start_ms=word.start_ms,
                    end_ms=word.end_ms,
                )
                for word in result.words
            ],
            model_version="real-stt-v1",
        )

    async def simplify(self, request: SimplifyRequest) -> SimplifyResponse:
        result = await self.llm_client.simplify(
            text=request.text,
            target_reading_level=request.target_reading_level,
            include_definitions=request.include_definitions,
        )

        return SimplifyResponse(
            original_text=request.text,
            simplified_text=result.simplified_text,
            explanation=result.explanation,
            difficult_words=[
                DifficultWord(word=item.word, meaning=item.meaning)
                for item in result.difficult_words
            ],
            model_version="real-llm-v1",
        )

    async def evaluate_reading(
        self,
        *,
        audio: bytes,
        filename: str,
        expected_text: str,
        language: str,
    ) -> ReadingEvaluationResponse:
        result = await self.reading_pipeline.evaluate(
            audio=audio,
            filename=filename,
            expected_text=expected_text,
            language=language,
        )

        return ReadingEvaluationResponse(
            transcript=result["transcript"],
            scores=ReadingScores(**result["scores"]),
            word_results=[WordEvaluation(**item) for item in result["word_results"]],
            feedback=result["feedback"],
            model_version="real-reading-v1",
        )

    async def generate_training(
        self,
        request: TrainingGenerateRequest,
    ) -> TrainingGenerateResponse:
        items_data = await self.llm_client.generate_training(
            reading_level=request.reading_level,
            weak_phonemes=request.weak_phonemes,
            error_types=request.error_types,
            duration_minutes=request.duration_minutes,
            exclude_recent_item_ids=request.exclude_recent_item_ids,
        )

        items = [
            TrainingItem(
                item_id=item["item_id"],
                type=item["type"],
                text=item["text"],
                choices=item["choices"],
                target_phonemes=item["target_phonemes"],
            )
            for item in items_data
        ]

        return TrainingGenerateResponse(
            items=items,
            model_version="free-rule-based-llm-v1",
        )

    async def generate_similar(self, request: SimilarRequest) -> SimilarResponse:
        sentences = await self.llm_client.generate_similar(
            text=request.text,
            count=request.count,
        )
        return SimilarResponse(
            original_text=request.text,
            similar_sentences=sentences,
            model_version="gemini-similar-v1",
        )