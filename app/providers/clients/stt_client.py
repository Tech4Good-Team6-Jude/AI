from dataclasses import dataclass


@dataclass
class SttWord:
    text: str
    start_ms: int
    end_ms: int


@dataclass
class SttResult:
    transcript: str
    confidence: float
    words: list[SttWord]


class SttClient:
    async def transcribe(
        self,
        *,
        audio: bytes,
        filename: str,
        language: str,
    ) -> SttResult:
        # 실제 STT 호출
        raise NotImplementedError("실제 STT 구현 필요")