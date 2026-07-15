"""로컬 추론 서버의 /speech/synthesize를 호출해서 결과를 mp3 파일로 저장하는
테스트용 스크립트.

서버가 이미 떠 있어야 한다 (uvicorn app.main:app --reload --port 8001).

동작 방식: /speech/synthesize는 audio_url(추론 서버가 저장해둔 파일의
조회 경로)만 반환한다. 이 스크립트는 그 URL을 다시 GET으로 요청해서
실제 mp3 바이트를 받아 로컬에 저장한다.

사용법:
    python scripts/synthesize_and_save.py "기차가 빠르게 달립니다."
    python scripts/synthesize_and_save.py "기차가 빠르게 달립니다." my_output.mp3
"""

from __future__ import annotations

import sys

import httpx

BASE_URL = "http://127.0.0.1:8001"
SYNTHESIZE_URL = f"{BASE_URL}/internal/v1/speech/synthesize"


def main() -> None:
    if len(sys.argv) < 2:
        print('사용법: python scripts/synthesize_and_save.py "텍스트" [저장할파일명.mp3]')
        sys.exit(1)

    text = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "output.mp3"

    print(f"1) 합성 요청 중... (text={text!r})")
    response = httpx.post(SYNTHESIZE_URL, json={"text": text}, timeout=30)
    response.raise_for_status()
    data = response.json()

    audio_url = data["audio_url"]
    full_url = f"{BASE_URL}{audio_url}" if audio_url.startswith("/") else audio_url

    print(f"2) 저장된 오디오 조회 중... ({full_url})")
    audio_response = httpx.get(full_url, timeout=30)
    audio_response.raise_for_status()

    with open(output_path, "wb") as f:
        f.write(audio_response.content)

    print(f"저장 완료: {output_path}")
    print(f"서버 내 조회 경로: {audio_url}")
    print(f"재생 길이: {data['duration_ms']}ms")
    print(f"단어 타이밍: {len(data['timings'])}개")
    for timing in data["timings"]:
        print(f"  - {timing['text']}: {timing['start_ms']}ms ~ {timing['end_ms']}ms")


if __name__ == "__main__":
    main()
