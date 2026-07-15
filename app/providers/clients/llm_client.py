"""Google Gemini API 기반 문장 단순화 LLM 클라이언트.

무료 티어(Google AI Studio에서 발급한 API 키)를 사용한다. 시작하기 전에
알아둘 것:

1. 결제를 등록하지 않은 무료 티어는 구글 약관상 입력/출력이 구글 제품
   개선에 활용될 수 있다. 아동의 학습 텍스트를 다루는 서비스이므로,
   이 데이터 처리 정책이 팀 정책과 맞는지 별도로 검토가 필요하다.
2. 무료 티어 할당량(RPM/RPD)은 최근 계속 축소되어 왔다. 코드에 고정된
   숫자를 믿지 말고 Google AI Studio의 Rate Limits 화면에서 실제 한도를
   확인해야 한다.
3. 프롬프트는 이 파일이 아니라 app/prompts/simplify_system.txt에 있다.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from google import genai
from google.genai import types

from app.core.config import settings
from app.core.errors import AppError

_SYSTEM_INSTRUCTION_PATH = Path(__file__).resolve().parents[2] / "prompts" / "simplify_system.txt"


@dataclass
class LlmDifficultWord:
    word: str
    meaning: str


@dataclass
class LlmSimplifyResult:
    simplified_text: str
    explanation: str
    difficult_words: list[LlmDifficultWord]


def _load_system_instruction() -> str:
    return _SYSTEM_INSTRUCTION_PATH.read_text(encoding="utf-8")


class LlmClient:
    def __init__(self):
        if not settings.gemini_api_key:
            raise RuntimeError(
                "GEMINI_API_KEY가 설정되지 않았어. .env에 값을 넣어줘 "
                "(https://aistudio.google.com/app/apikey 에서 무료 발급 가능)."
            )
        self._client = genai.Client(api_key=settings.gemini_api_key)
        self._system_instruction = _load_system_instruction()

    async def simplify(
        self,
        *,
        text: str,
        target_reading_level: int,
        include_definitions: bool,
    ) -> LlmSimplifyResult:
        prompt = (
            f"[목표 읽기 수준] {target_reading_level} (1~10, 낮을수록 쉬움)\n"
            f"[어려운 단어 뜻풀이 포함 여부] {'포함' if include_definitions else '미포함'}\n"
            f"[원문]\n{text}"
        )

        try:
            response = await self._client.aio.models.generate_content(
                model=settings.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self._system_instruction,
                    response_mime_type="application/json",
                    temperature=0.3,
                ),
            )
        except Exception as exc:  # noqa: BLE001 - 네트워크/할당량/모델 오류 전체 흡수
            import traceback

            raise AppError(
                code="LLM_UPSTREAM_ERROR",
                message="문장 단순화 중 오류가 발생했어.",
                status_code=502,
                retryable=True,
            ) from exc

        try:
            data = json.loads(response.text)
            return LlmSimplifyResult(
                simplified_text=data["simplified_text"],
                explanation=data["explanation"],
                difficult_words=[
                    LlmDifficultWord(word=item["word"], meaning=item["meaning"])
                    for item in data.get("difficult_words", [])
                ],
            )
        except (KeyError, TypeError, json.JSONDecodeError) as exc:
            raise AppError(
                code="LLM_INVALID_RESPONSE",
                message="LLM 응답 형식이 올바르지 않아.",
                status_code=502,
                retryable=True,
            ) from exc