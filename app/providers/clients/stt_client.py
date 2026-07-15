"""faster-whisper 기반 STT 클라이언트.

faster-whisper는 로컬(이 서버 안)에서 도는 실제 추론이다. edge-tts와
달리 외부 API 호출이 아니라 CPU/GPU 자원을 이 프로세스가 직접 쓴다.
그래서 두 가지를 신경써야 한다:

1. 모델 로딩이 수 초~수십 초 걸리므로 요청마다 새로 만들면 안 되고
   프로세스당 한 번만 로드해서 재사용한다.
2. transcribe() 자체가 동기 blocking 호출이라 그대로 async def 안에서
   돌리면 이벤트 루프가 멈춘다. asyncio.to_thread로 스레드풀에 위임한다.

최초 실행 시 HuggingFace Hub에서 모델 가중치를 내려받으므로 네트워크와
디스크 공간이 필요하다 (small 기준 약 500MB).
"""

from __future__ import annotations

import asyncio
import io
from dataclasses import dataclass
from functools import lru_cache

from faster_whisper import WhisperModel

from app.core.config import settings
from app.core.errors import AppError


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


@lru_cache(maxsize=1)
def _load_model() -> WhisperModel:
    """프로세스당 한 번만 로드된다 (lru_cache로 싱글턴화)."""
    return WhisperModel(
        settings.stt_model_size,
        device=settings.stt_device,
        compute_type=settings.stt_compute_type,
    )


def _to_whisper_language_code(language: str) -> str:
    # "ko-KR" -> "ko" 처럼 whisper가 기대하는 2글자 코드로 변환
    return language.split("-")[0].lower()


class SttClient:
    async def transcribe(
        self,
        *,
        audio: bytes,
        filename: str,
        language: str,
    ) -> SttResult:
        try:
            return await asyncio.to_thread(self._transcribe_sync, audio, language)
        except AppError:
            raise
        except Exception as exc:  # noqa: BLE001 - 모델/디코딩 오류 전체를 흡수
            import traceback
            traceback.print_exc()  # 임시: 실제 원인을 터미널에 출력
            raise AppError(
                code="STT_UPSTREAM_ERROR",
                message="음성 인식 중 오류가 발생했어.",
                status_code=502,
                retryable=True,
            ) from exc

    def _transcribe_sync(self, audio: bytes, language: str) -> SttResult:
        model = _load_model()
        segments, _info = model.transcribe(
            io.BytesIO(audio),
            language=_to_whisper_language_code(language),
            word_timestamps=True,
            vad_filter=True,  # 녹음 앞뒤 무음 구간 제거 (아이들 녹음엔 침묵이 김)
        )

        words: list[SttWord] = []
        text_parts: list[str] = []
        probabilities: list[float] = []

        for segment in segments:
            stripped = segment.text.strip()
            if stripped:
                text_parts.append(stripped)
            for word in segment.words or []:
                words.append(
                    SttWord(
                        text=word.word.strip(),
                        start_ms=round(word.start * 1000),
                        end_ms=round(word.end * 1000),
                    )
                )
                probabilities.append(word.probability)

        transcript = " ".join(text_parts)

        if not transcript:
            raise AppError(
                code="STT_NO_SPEECH",
                message="녹음에서 음성을 인식하지 못했어. 다시 녹음해줘.",
                status_code=422,
                retryable=False,
            )

        confidence = sum(probabilities) / len(probabilities) if probabilities else 0.0

        return SttResult(
            transcript=transcript,
            confidence=round(confidence, 4),
            words=words,
        )