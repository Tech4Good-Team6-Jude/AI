from app.providers.clients.ocr_client import OcrClient
from app.providers.clients.tts_client import TtsClient

from app.schemas.ocr import BoundingBox, OcrBlock, OcrResponse
from app.schemas.speech import TtsRequest, SttResponse, TtsResponse, WordTiming


class RealInferenceProvider:
    def __init__(self):
        self.ocr_client = OcrClient()
        self.tts_client = TtsClient()

    async def ocr(
        self,
        *,
        content: bytes,
        filename: str,
        language: str,
        include_bounding_boxes: bool,
    ) -> OcrResponse:
        # 가공하지 않고 클라이언트 결과를 그대로 전달합니다!
        return await self.ocr_client.extract(
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

        return TtsResponse(
            audio_url=result.audio_url,
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