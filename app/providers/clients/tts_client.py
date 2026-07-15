"""Microsoft Edge 온라인 TTS(edge-tts)를 감싸는 클라이언트.

edge-tts는 별도 계정/API 키 없이 쓸 수 있는 무료 TTS지만, 공식 SLA가
없는 비공식 서비스다. MS 쪽 API가 바뀌면 라이브러리 업데이트가 필요할
수 있고, 트래픽이 커지면 유료 Provider로 교체할 수도 있다 — 그래서
이 클라이언트를 provider(real.py) 뒤에 숨겨서 교체 가능하게 둔다.

이 클라이언트는 오디오를 파일로 저장하지 않는다. bytes만 반환하고,
저장/URL 발급은 서비스 서버(파일 저장소를 가진 쪽)의 책임이다.
"""

from __future__ import annotations

from dataclasses import dataclass

import edge_tts
from edge_tts.exceptions import NoAudioReceived

from app.core.errors import AppError

DEFAULT_VOICE = "ko-KR-SunHiNeural"
VOICE_ALIASES: dict[str, str] = {
    "female-01": "ko-KR-SunHiNeural",
    "male-01": "ko-KR-InJoonNeural",
}


@dataclass
class TtsResult:
    audio_bytes: bytes
    duration_ms: int
    timings: list[dict]


def _speed_to_rate(speed: float) -> str:
    """TtsRequest.speed(0.5~1.5, 1.0=기본)를 edge-tts의 rate 문자열로 변환."""
    percent = round((speed - 1.0) * 100)
    sign = "+" if percent >= 0 else ""
    return f"{sign}{percent}%"


def _resolve_voice(voice_id: str) -> str:
    return VOICE_ALIASES.get(voice_id, voice_id or DEFAULT_VOICE)


class TtsClient:
    def __init__(self):
        # edge-tts는 매번 새 Communicate 인스턴스를 만들어 쓰는 구조라
        # 여기서 초기화할 SDK 클라이언트가 따로 없다.
        pass

    async def synthesize(
        self,
        *,
        text: str,
        voice_id: str,
        speed: float,
        include_timings: bool,
    ) -> TtsResult:
        voice = _resolve_voice(voice_id)
        rate = _speed_to_rate(speed)

        communicate = edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary")

        audio_chunks: list[bytes] = []
        timings: list[dict] = []

        try:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_chunks.append(chunk["data"])
                elif include_timings and chunk["type"] == "WordBoundary":
                    # offset/duration은 100-nanosecond 단위로 온다.
                    start_ms = chunk["offset"] // 10_000
                    duration_ms = chunk["duration"] // 10_000
                    timings.append(
                        {
                            "text": chunk["text"],
                            "start_ms": start_ms,
                            "end_ms": start_ms + duration_ms,
                        }
                    )
        except NoAudioReceived as exc:
            raise AppError(
                code="TTS_NO_AUDIO",
                message="TTS 서비스에서 오디오를 받지 못했어.",
                status_code=502,
                retryable=True,
            ) from exc
        except Exception as exc:  # noqa: BLE001 - 업스트림 네트워크/프로토콜 오류 흡수
            raise AppError(
                code="TTS_UPSTREAM_ERROR",
                message="TTS 서비스 호출 중 오류가 발생했어.",
                status_code=502,
                retryable=True,
            ) from exc

        if not audio_chunks:
            raise AppError(
                code="TTS_NO_AUDIO",
                message="TTS 서비스에서 오디오를 받지 못했어.",
                status_code=502,
                retryable=True,
            )

        audio_bytes = b"".join(audio_chunks)
        duration_ms = timings[-1]["end_ms"] if timings else 0

        return TtsResult(
            audio_bytes=audio_bytes,
            duration_ms=duration_ms,
            timings=timings,
        )