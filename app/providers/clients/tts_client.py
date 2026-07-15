from dataclasses import dataclass


@dataclass
class TtsResult:
    audio_url: str
    duration_ms: int
    timings: list[dict]


class TtsClient:
    def __init__(self):
        # TTS SDK 초기화
        pass

    async def synthesize(
        self,
        *,
        text: str,
        voice_id: str,
        speed: float,
        include_timings: bool,
    ) -> TtsResult:
        # 실제 TTS 호출
        # 생성된 음성 파일을 스토리지에 저장
        # URL과 단어별 타이밍 반환

        raise NotImplementedError("실제 TTS 구현 필요")