from app.core.audio_storage import build_audio_url, save_audio
from app.pipelines.reading_pipeline import ReadingPipeline
from app.providers.clients.llm_client import LlmClient
from app.providers.clients.ocr_client import OcrClient
from app.providers.clients.stt_client import SttClient
from app.providers.clients.tts_client import TtsClient

from app.schemas.ocr import BoundingBox, OcrBlock, OcrResponse
from app.schemas.reading import ReadingEvaluationResponse, ReadingScores, WordEvaluation
from app.schemas.speech import TtsRequest, SttResponse, TtsResponse, WordTiming
from app.schemas.text import DifficultWord, SimplifyRequest, SimplifyResponse


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
        result = await self.ocr_client.extract(
            content=content,
            filename=filename,
            language=language,
            include_bounding_boxes=include_bounding_boxes,
        )

        return OcrResponse(
            text=result.text,
            blocks=[
                OcrBlock(
                    text=block["text"],
                    confidence=block["confidence"],
                    bounding_box=BoundingBox(**block["bounding_box"])
                    if block.get("bounding_box")
                    else None,
                )
                for block in result.blocks
            ],
            model_version="real-ocr-v1",
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