import random
import os
import google.generativeai as genai

class LlmClient:
    def __init__(self):
        # 기존 훈련용 임시 DB 유지
        self.training_db = {
            "ㅊ": {
                "sentences": ["기차가 천천히 출발합니다.", "초록색 치마를 입고 춤을 춰요."],
                "quizzes": [{"text": "다음 중 '차'와 첫소리가 같은 단어를 고르세요.", "choices": ["자전거", "기차", "사과"]}]
            },
            "받침 ㄹ": {
                "sentences": ["하늘에 빨간 풍선이 날아갑니다.", "가을 바람이 솔솔 불어옵니다."],
                "quizzes": [{"text": "다음 중 'ㄹ' 받침이 들어간 단어를 고르세요.", "choices": ["밥", "달", "강"]}]
            }
        }
        self.default_sentences = ["새들이 하늘을 날아다닙니다.", "따뜻한 물을 마셔요."]

        # 🚀 Google Gemini AI 초기화
        api_key = "x"
        if api_key:
            genai.configure(api_key=api_key)
            # 가볍고 빠르면서 똑똑한 flash 모델 사용
            self.model = genai.GenerativeModel("gemini-3.1-flash-lite")
            print("✅ [LLM] Google Gemini AI 연결 완료!")
        else:
            self.model = None
            print("⚠️ [LLM] GEMINI_API_KEY가 없습니다. 임시 모드로 동작합니다.")

    # [1] 기존 훈련 세트 생성 기능
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

    # 🚀 [2] 진짜 인공지능(Gemini)이 만들어주는 유사 문장 생성 기능!
    async def generate_similar(self, text: str, count: int) -> list[str]:
        if not self.model:
            return [f"'{text}'와 비슷한 임시 문장입니다. (API 키 필요)"] * count

        try:
            # AI에게 명령을 내리는 완벽한 프롬프트(Prompt)
            prompt = f"""
            당신은 난독증 청소년을 가르치는 전문 특수교사입니다.
            학생이 다음 문장을 읽는 데 어려움을 겪었습니다: "{text}"

            이 문장의 문법적 구조나 핵심 단어, 발음 패턴을 활용하여,
            학생이 반복해서 읽기 연습을 할 수 있는 아주 자연스러운 유사 문장 딱 {count}개를 만들어주세요.

            조건:
            - 초등학교 고학년~중학생 수준의 쉽고 명확한 단어를 사용하세요.
            - 번호(1., 2. 등), 기호(-, *), 부가적인 설명은 절대 쓰지 마세요.
            - 오직 만들어진 문장만 줄바꿈(엔터)으로 구분해서 출력하세요.
            """
            
            # 구글 서버로 비동기 요청 전송
            response = await self.model.generate_content_async(prompt)
            
            # 응답받은 텍스트를 엔터 단위로 쪼개고 빈 줄은 제거하여 리스트로 만듦
            sentences = [line.strip() for line in response.text.split('\n') if line.strip()]
            
            # 확실하게 요청한 갯수만큼만 잘라서 반환
            return sentences[:count]
            
        except Exception as e:
            print(f"🚨 Gemini API 에러: {e}")
            return [f"'{text}'의 임시 훈련 문장입니다. (에러 복구 모드)"] * count
