"""TTS 결과 오디오를 로컬 디스크에 저장하고 다시 꺼내오는 유틸리티.

주의: 이건 개발/테스트 편의를 위한 임시 저장소다. 서버가 재시작되거나
컨테이너가 재배포되면 파일이 사라질 수 있고, 여러 인스턴스로 스케일링하면
인스턴스마다 저장 위치가 달라져 문제가 생긴다. 실제 서비스 운영 단계에서는
서비스 서버의 영구 저장소(S3 등)로 옮기는 걸 검토해야 한다.
"""

from __future__ import annotations

import uuid
from pathlib import Path

from app.core.config import settings
from app.core.errors import AppError


def _storage_dir() -> Path:
    path = Path(settings.audio_storage_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_audio(audio_bytes: bytes, *, extension: str = "mp3") -> str:
    """오디오 bytes를 저장하고 파일명(=조회용 식별자)을 반환한다."""
    filename = f"{uuid.uuid4().hex}.{extension}"
    file_path = _storage_dir() / filename
    file_path.write_bytes(audio_bytes)
    return filename


def build_audio_url(filename: str) -> str:
    """저장된 파일을 GET /internal/v1/speech/audio/{filename}으로 조회할 수 있는
    경로를 반환한다. (호스트 부분은 서비스 서버가 이미 알고 있는 base URL을
    그대로 붙여 쓰면 된다.)
    """
    return f"{settings.api_prefix}/speech/audio/{filename}"


def resolve_audio_path(filename: str) -> Path:
    """조회 요청으로 들어온 filename을 안전하게 실제 파일 경로로 변환한다.

    경로 조작(../ 등)을 통한 임의 파일 접근을 막기 위해, 최종 경로가
    저장 디렉터리 밖으로 벗어나지 않는지 검증한다.
    """
    storage_dir = _storage_dir().resolve()
    candidate = (storage_dir / filename).resolve()

    if storage_dir not in candidate.parents and candidate != storage_dir:
        raise AppError(
            code="INVALID_AUDIO_FILENAME",
            message="올바르지 않은 파일 이름이야.",
            status_code=400,
        )

    if not candidate.is_file():
        raise AppError(
            code="AUDIO_NOT_FOUND",
            message="해당 오디오 파일을 찾을 수 없어.",
            status_code=404,
        )

    return candidate
