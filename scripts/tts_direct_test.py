"""HTTP 서버를 거치지 않고 TtsClient를 직접 호출해서 mp3로 저장하는 스크립트.

base64 인코딩/디코딩이 전혀 없다 - TtsClient가 만든 오디오 bytes를
중간 변환 없이 그대로 파일에 쓴다.

서버를 켤 필요 없음. 프로젝트 루트(pyproject.toml이 있는 곳)에서 실행할 것.

사용법:
    python scripts/tts_direct_test.py "기차가 빠르게 달립니다."
    python scripts/tts_direct_test.py "기차가 빠르게 달립니다." my_output.mp3
"""

from __future__ import annotations

import asyncio
import sys

from app.providers.clients.tts_client import TtsClient


async def main() -> None:
    if len(sys.argv) < 2:
        print('사용법: python scripts/tts_direct_test.py "텍스트" [파일명.mp3]')
        sys.exit(1)

    text = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "output.mp3"

    client = TtsClient()
    result = await client.synthesize(
        text=text,
        voice_id="female-01",
        speed=0.8,
        include_timings=True,
    )

    with open(output_path, "wb") as f:
        f.write(result.audio_bytes)

    print(f"저장 완료: {output_path}")
    print(f"재생 길이: {result.duration_ms}ms")
    print(f"단어 타이밍: {len(result.timings)}개")
    for timing in result.timings:
        print(f"  - {timing['text']}: {timing['start_ms']}ms ~ {timing['end_ms']}ms")


if __name__ == "__main__":
    asyncio.run(main())
