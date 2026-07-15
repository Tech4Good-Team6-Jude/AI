"""소리내어 읽기 평가 파이프라인: STT → 단어 정렬 → 채점 → 피드백.

핵심은 _align_words()다. 단순히 같은 위치끼리 비교하면(예전 방식) 아이가
단어 하나를 빼먹거나 더 말하는 순간 그 뒤 단어가 전부 틀린 것처럼
잘못 채점된다. difflib.SequenceMatcher로 정답 문장과 STT 결과를
정렬해서 "빠뜨림(OMITTED)"과 "더 말함(INSERTED)"을 구분한다.
"""

from __future__ import annotations

import difflib
import re

from app.providers.clients.stt_client import SttClient

# 초성/중성/종성 자모 (완성형 한글 유니코드 조합 공식용)
_CHOSEONG = list("ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ")
_JUNGSEONG = list("ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ")
_JONGSEONG = [""] + list("ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ")

_HANGUL_BASE = 0xAC00
_HANGUL_LAST = 0xD7A3

# STT는 문장부호를 받아쓰지 않으므로, 정답 문장에 있는 문장부호는
# 비교 전에 제거해야 "달립니다." vs "달립니다"가 오독으로 잘못 채점되지 않는다.
_PUNCTUATION_PATTERN = re.compile(r"[.,!?;:\"'()\[\]~…·]")


def _strip_punctuation(word: str) -> str:
    return _PUNCTUATION_PATTERN.sub("", word)


def _decompose(char: str) -> tuple[str, str, str] | None:
    """완성형 한글 한 글자를 (초성, 중성, 종성)으로 분해한다. 한글이 아니면 None."""
    if not char or not (_HANGUL_BASE <= ord(char) <= _HANGUL_LAST):
        return None
    offset = ord(char) - _HANGUL_BASE
    cho = offset // (21 * 28)
    jung = (offset % (21 * 28)) // 28
    jong = offset % 28
    return _CHOSEONG[cho], _JUNGSEONG[jung], _JONGSEONG[jong]


def _find_weak_phoneme(expected: str, spoken: str) -> str | None:
    """오독한 단어의 첫 글자를 비교해 어떤 음소를 헷갈렸는지 추정한다."""
    if not expected or not spoken:
        return None

    exp = _decompose(expected[0])
    spk = _decompose(spoken[0])
    if not exp or not spk:
        return None

    exp_cho, _, exp_jong = exp
    spk_cho, _, spk_jong = spk

    if exp_cho != spk_cho:
        return f"{exp_cho}/{spk_cho}"
    if exp_jong != spk_jong and (exp_jong or spk_jong):
        return f"받침 {exp_jong or spk_jong}"
    return None


class ReadingPipeline:
    def __init__(self, stt_client: SttClient):
        self.stt_client = stt_client

    async def evaluate(
        self,
        *,
        audio: bytes,
        filename: str,
        expected_text: str,
        language: str,
    ) -> dict:
        stt_result = await self.stt_client.transcribe(
            audio=audio,
            filename=filename,
            language=language,
        )

        word_results = self._align_words(
            expected_text=expected_text,
            spoken_text=stt_result.transcript,
        )

        accuracy = self._calculate_accuracy(word_results)
        completeness = self._calculate_completeness(word_results)
        pronunciation = self._calculate_pronunciation(word_results, stt_result.confidence)
        words_per_minute = self._calculate_wpm(stt_result.words)
        fluency = self._calculate_fluency(words_per_minute, word_results)
        feedback = self._build_feedback(accuracy, word_results)

        return {
            "transcript": stt_result.transcript,
            "scores": {
                "accuracy": accuracy,
                "fluency": fluency,
                "completeness": completeness,
                "pronunciation": pronunciation,
                "words_per_minute": words_per_minute,
            },
            "word_results": word_results,
            "feedback": feedback,
        }

    def _align_words(self, *, expected_text: str, spoken_text: str) -> list[dict]:
        expected_words = [_strip_punctuation(w) for w in expected_text.split()]
        spoken_words = [_strip_punctuation(w) for w in spoken_text.split()]

        matcher = difflib.SequenceMatcher(None, expected_words, spoken_words)
        results: list[dict] = []

        for tag, e1, e2, s1, s2 in matcher.get_opcodes():
            if tag == "equal":
                for expected, spoken in zip(expected_words[e1:e2], spoken_words[s1:s2]):
                    results.append(
                        {
                            "expected": expected,
                            "spoken": spoken,
                            "status": "CORRECT",
                            "score": 100,
                            "weak_phoneme": None,
                        }
                    )
            elif tag == "replace":
                # 정답 구간과 발화 구간의 길이가 다를 수 있어 짧은 쪽 기준으로 1:1 대응시키고,
                # 남는 쪽은 OMITTED/INSERTED로 처리한다.
                exp_slice = expected_words[e1:e2]
                spk_slice = spoken_words[s1:s2]
                for expected, spoken in zip(exp_slice, spk_slice):
                    results.append(
                        {
                            "expected": expected,
                            "spoken": spoken,
                            "status": "MISPRONOUNCED",
                            "score": 40,
                            "weak_phoneme": _find_weak_phoneme(expected, spoken),
                        }
                    )
                for expected in exp_slice[len(spk_slice):]:
                    results.append(
                        {
                            "expected": expected,
                            "spoken": "",
                            "status": "OMITTED",
                            "score": 0,
                            "weak_phoneme": None,
                        }
                    )
                for spoken in spk_slice[len(exp_slice):]:
                    results.append(
                        {
                            "expected": "",
                            "spoken": spoken,
                            "status": "INSERTED",
                            "score": 0,
                            "weak_phoneme": None,
                        }
                    )
            elif tag == "delete":
                for expected in expected_words[e1:e2]:
                    results.append(
                        {
                            "expected": expected,
                            "spoken": "",
                            "status": "OMITTED",
                            "score": 0,
                            "weak_phoneme": None,
                        }
                    )
            elif tag == "insert":
                for spoken in spoken_words[s1:s2]:
                    results.append(
                        {
                            "expected": "",
                            "spoken": spoken,
                            "status": "INSERTED",
                            "score": 0,
                            "weak_phoneme": None,
                        }
                    )

        return results

    def _calculate_accuracy(self, results: list[dict]) -> int:
        # INSERTED는 정답 문장에 없던 단어라 정답 대비 정확도 계산에서는 제외한다.
        graded = [item for item in results if item["status"] != "INSERTED"]
        if not graded:
            return 0
        correct = sum(item["status"] == "CORRECT" for item in graded)
        return round(correct / len(graded) * 100)

    def _calculate_completeness(self, results: list[dict]) -> int:
        graded = [item for item in results if item["status"] != "INSERTED"]
        if not graded:
            return 0
        attempted = sum(item["status"] != "OMITTED" for item in graded)
        return round(attempted / len(graded) * 100)

    def _calculate_pronunciation(self, results: list[dict], stt_confidence: float) -> int:
        graded = [item for item in results if item["status"] != "INSERTED"]
        if not graded:
            return 0
        avg_word_score = sum(item["score"] for item in graded) / len(graded)
        # 단어별 채점(70%) + STT 인식 신뢰도(30%)를 합쳐 발음 점수로 사용한다.
        return round(avg_word_score * 0.7 + stt_confidence * 100 * 0.3)

    def _calculate_wpm(self, words: list) -> float:
        if len(words) < 2:
            return 0.0
        duration_ms = words[-1].end_ms - words[0].start_ms
        if duration_ms <= 0:
            return 0.0
        return round(len(words) / (duration_ms / 60_000), 1)

    def _calculate_fluency(self, words_per_minute: float, results: list[dict]) -> int:
        if words_per_minute <= 0:
            return 0
        # 우리말 낭독 기준 대략 80~140 wpm을 자연스러운 구간으로 보고,
        # 그 범위를 벗어날수록(너무 느리거나 너무 빠름) 감점한다.
        if 80 <= words_per_minute <= 140:
            pace_score = 100
        elif words_per_minute < 80:
            pace_score = max(0, round(words_per_minute / 80 * 100))
        else:
            pace_score = max(0, round(100 - (words_per_minute - 140) / 2))

        graded = [item for item in results if item["status"] != "INSERTED"]
        smoothness = (
            round(sum(item["status"] == "CORRECT" for item in graded) / len(graded) * 100)
            if graded
            else 0
        )
        return round(pace_score * 0.5 + smoothness * 0.5)

    def _build_feedback(self, accuracy: int, results: list[dict]) -> str:
        mispronounced = [item for item in results if item["status"] == "MISPRONOUNCED"]
        omitted = [item for item in results if item["status"] == "OMITTED"]

        if accuracy >= 90:
            return "정말 또박또박 잘 읽었어!"

        if accuracy >= 70:
            if mispronounced:
                word = mispronounced[0]["expected"]
                return f"잘 읽었어. '{word}' 발음만 조금 더 연습해보자."
            return "잘 읽었어. 조금만 더 연습하면 완벽할 거야."

        if omitted:
            word = omitted[0]["expected"]
            return f"'{word}' 부분을 놓친 것 같아. 천천히 다시 한 번 읽어볼까?"

        return "천천히 다시 한 번 읽어볼까? 급하지 않아도 괜찮아."