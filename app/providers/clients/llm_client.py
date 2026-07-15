import random

class LlmClient:
    def __init__(self):
        # 난독증 음운 훈련용 DB (취약 음소별 맞춤 문장 및 퀴즈 세트)
        self.training_db = {
            "ㅊ": {
                "sentences": [
                    "기차가 천천히 출발합니다.",
                    "초록색 치마를 입고 춤을 춰요.",
                    "차가운 바람이 창문으로 들어옵니다."
                ],
                "quizzes": [
                    {"text": "다음 중 '차'와 첫소리가 같은 단어를 고르세요.", "choices": ["자전거", "기차", "사과"]}
                ]
            },
            "받침 ㄹ": {
                "sentences": [
                    "하늘에 빨간 풍선이 날아갑니다.",
                    "교실 물통에 물을 가득 담았어요.",
                    "가을 바람이 솔솔 불어옵니다."
                ],
                "quizzes": [
                    {"text": "다음 중 'ㄹ' 받침이 들어간 단어를 고르세요.", "choices": ["밥", "달", "강"]}
                ]
            }
        }

        # 기본 디폴트 데이터
        self.default_sentences = [
            "새들이 하늘을 자유롭게 날아다닙니다.",
            "아침에 일어나서 따뜻한 물을 마셔요."
        ]

    # 1. 훈련 세트 생성 함수 (온전히 끝까지 작성됨)
    async def generate_training(
        self,
        *,
        reading_level: int,
        weak_phonemes: list[str],
        error_types: list[str],
        duration_minutes: int,
        exclude_recent_item_ids: list[str]
    ) -> list[dict]:
        
        generated_items = []
        item_counter = 1

        target_phonemes = weak_phonemes if weak_phonemes else ["ㅊ", "받침 ㄹ"]

        for phoneme in target_phonemes:
            data = self.training_db.get(phoneme, {
                "sentences": self.default_sentences,
                "quizzes": [{"text": "올바르게 읽은 단어를 고르세요.", "choices": ["나무", "나부", "다무"]}]
            })

            for sentence in random.sample(data["sentences"], min(2, len(data["sentences"]))):
                generated_items.append({
                    "item_id": f"train-{phoneme}-{item_counter}",
                    "type": "READ_ALOUD",
                    "text": sentence,
                    "choices": None,
                    "target_phonemes": [phoneme]
                })
                item_counter += 1

            for quiz in random.sample(data["quizzes"], min(1, len(data["quizzes"]))):
                generated_items.append({
                    "item_id": f"train-{phoneme}-{item_counter}",
                    "type": "PHONEME_MATCH",
                    "text": quiz["text"],
                    "choices": quiz["choices"],
                    "target_phonemes": [phoneme]
                })
                item_counter += 1

        return generated_items

    # 2. 방금 추가하신 유사 문장 생성 함수 (위 함수가 끝난 뒤 안전하게 분리됨!)
    async def generate_similar(self, text: str, count: int) -> list[str]:
        """
        학생이 막힌 문장(text)의 패턴을 분석해 유사한 문장을 생성합니다.
        """
        if "겨울" in text:
            return [
                "추운 겨울에는 눈이 펑펑 내립니다.",
                "겨울방학에 친구들과 썰매장에 갔어요.",
                "따뜻한 겨울 코트와 장갑을 준비했습니다."
            ][:count]
        elif "가나다라" in text:
            return [
                "가나다라 노래를 신나게 부릅니다.",
                "아자차카 타파하를 재미있게 배웁니다.",
                "한글 공부는 언제나 즐겁습니다."
            ][:count]
        else:
            return [
                f"'{text}'와 비슷한 구조로 만든 첫 번째 연습 문장입니다.",
                f"'{text}'의 핵심 패턴을 살린 두 번째 연습 문장입니다.",
                f"'{text}'에서 어휘만 살짝 바꾼 세 번째 연습 문장입니다."
            ][:count]