"""LLM 클라이언트: 문장 단순화(Gemini) + 학습 문항 생성(룰베이스) + 유사 문장 생성(Gemini).

두 사람이 각자 만든 기능을 하나의 클라이언트로 합쳤다:
- simplify(): Gemini API 실제 호출
- generate_training(): 아직 룰베이스 임시 구현 (고정 문장 목록 + random.sample).
  나중에 Gemini 호출로 교체 예정.
- generate_similar(): Gemini API 실제 호출. 원래 구버전 SDK(google.generativeai)로
  따로 만들어졌던 걸, simplify와 같은 SDK(google-genai)/같은 클라이언트 인스턴스를
  쓰도록 통일했다. (API 키를 하드코딩하지 않고 settings에서 읽도록도 고쳤다.)

무료 티어 유의사항:
1. 결제를 등록하지 않은 무료 티어는 구글 약관상 입력/출력이 구글 제품
   개선에 활용될 수 있다. 아동의 학습 텍스트를 다루는 서비스이므로,
   이 데이터 처리 정책이 팀 정책과 맞는지 별도로 검토가 필요하다.
2. 무료 티어 할당량(RPM/RPD)은 최근 계속 축소되어 왔다. 코드에 고정된
   숫자를 믿지 말고 Google AI Studio의 Rate Limits 화면에서 실제 한도를
   확인해야 한다.
3. simplify()의 프롬프트는 이 파일이 아니라 app/prompts/simplify_system.txt에 있다.
"""

from __future__ import annotations

import json
import random
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
        # ------------------------------------------------------------
        # 학습 문항/유사 문장용 임시 데이터 (generate_training은 아직 이것만 사용)
        # ------------------------------------------------------------
        self.training_db = {
            "ㅊ": {
                "sentences": ["기차가 천천히 출발합니다.", "초록색 치마를 입고 춤을 춰요."],
                "quizzes": [
                    {"text": "다음 중 '차'와 첫소리가 같은 단어를 고르세요.", "choices": ["자전거", "기차", "사과"]}
                ],
            },
            "받침 ㄹ": {
                "sentences": ["하늘에 빨간 풍선이 날아갑니다.", "가을 바람이 솔솔 불어옵니다."],
                "quizzes": [
                    {"text": "다음 중 'ㄹ' 받침이 들어간 단어를 고르세요.", "choices": ["밥", "달", "강"]}
                ],
            },
        }
        self.default_sentences = ["새들이 하늘을 날아다닙니다.", "따뜻한 물을 마셔요."]

        # ------------------------------------------------------------
        # Gemini 클라이언트 (simplify, generate_similar가 이 인스턴스 하나를 공유)
        # ------------------------------------------------------------
        if not settings.gemini_api_key:
            raise RuntimeError(
                "GEMINI_API_KEY가 설정되지 않았어. .env에 값을 넣어줘 "
                "(https://aistudio.google.com/app/apikey 에서 무료 발급 가능)."
            )
        self._client = genai.Client(api_key=settings.gemini_api_key)
        self._system_instruction = _load_system_instruction()

    # ==================================================================
    # 문장 단순화 (Gemini)
    # ==================================================================
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
            traceback.print_exc()
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

    # ==================================================================
    # 학습 문항 생성 (룰베이스 임시 구현 - 아직 Gemini 미사용)
    # ==================================================================
    async def generate_training(
        self,
        *,
        reading_level: int,
        weak_phonemes: list[str],
        error_types: list[str],
        duration_minutes: int,
        exclude_recent_item_ids: list[str],
    ) -> list[dict]:
        generated_items = []
        item_counter = 1
        target_phonemes = weak_phonemes if weak_phonemes else ["ㅊ", "받침 ㄹ"]

        for phoneme in target_phonemes:
            data = self.training_db.get(
                phoneme,
                {
                    "sentences": self.default_sentences,
                    "quizzes": [{"text": "올바르게 읽은 단어를 고르세요.", "choices": ["나무", "나부", "다무"]}],
                },
            )

            for sentence in random.sample(data["sentences"], min(2, len(data["sentences"]))):
                generated_items.append(
                    {
                        "item_id": f"train-{phoneme}-{item_counter}",
                        "type": "READ_ALOUD",
                        "text": sentence,
                        "choices": None,
                        "target_phonemes": [phoneme],
                    }
                )
                item_counter += 1
            for quiz in random.sample(data["quizzes"], min(1, len(data["quizzes"]))):
                generated_items.append(
                    {
                        "item_id": f"train-{phoneme}-{item_counter}",
                        "type": "PHONEME_MATCH",
                        "text": quiz["text"],
                        "choices": quiz["choices"],
                        "target_phonemes": [phoneme],
                    }
                )
                item_counter += 1
        return generated_items

    # ==================================================================
    # 유사 문장 생성 (Gemini) - simplify와 클라이언트/SDK를 공유하도록 통일
    # ==================================================================
    async def generate_similar(self, text: str, count: int) -> list[str]:
        prompt = (
            "당신은 난독증 청소년을 가르치는 전문 특수교사입니다.\n"
            f'학생이 다음 문장을 읽는 데 어려움을 겪었습니다: "{text}"\n\n'
            "이 문장의 문법적 구조나 핵심 단어, 발음 패턴을 활용하여, "
            f"학생이 반복해서 읽기 연습을 할 수 있는 아주 자연스러운 유사 문장 딱 {count}개를 만들어주세요.\n\n"
            "조건:\n"
            "- 초등학교 고학년~중학생 수준의 쉽고 명확한 단어를 사용하세요.\n"
            "- 번호(1., 2. 등), 기호(-, *), 부가적인 설명은 절대 쓰지 마세요.\n"
            "- 오직 만들어진 문장만 줄바꿈(엔터)으로 구분해서 출력하세요."
        )

        try:
            response = await self._client.aio.models.generate_content(
                model=settings.gemini_model,
                contents=prompt,
            )
        except Exception as exc:  # noqa: BLE001 - 네트워크/할당량/모델 오류 전체 흡수
            raise AppError(
                code="LLM_UPSTREAM_ERROR",
                message="유사 문장 생성 중 오류가 발생했어.",
                status_code=502,
                retryable=True,
            ) from exc

        sentences = [line.strip() for line in response.text.split("\n") if line.strip()]
        return sentences[:count]
