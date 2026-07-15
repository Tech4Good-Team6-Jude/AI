from app.schemas.diagnosis import DiagnosisAnalyzeRequest, DiagnosisAnalyzeResponse
from app.schemas.ocr import BoundingBox, OcrBlock, OcrResponse
from app.schemas.reading import (
    ReadingEvaluationResponse,
    ReadingScores,
    WordEvaluation,
)
from app.schemas.speech import SttResponse, TtsRequest, TtsResponse, WordTiming
from app.schemas.text import DifficultWord, SimplifyRequest, SimplifyResponse
from app.schemas.training import (
    TrainingGenerateRequest,
    TrainingGenerateResponse,
    TrainingItem,
)


class MockInferenceProvider:
    async def ocr(
        self,
        *,
        content: bytes,
        filename: str,
        language: str,
        include_bounding_boxes: bool,
    ) -> OcrResponse:
        return OcrResponse(
            text="봄바람이 살랑살랑 불어옵니다.",
            blocks=[
                OcrBlock(
                    text="봄바람이",
                    confidence=0.98,
                    bounding_box=BoundingBox(x=0.1, y=0.2, width=0.2, height=0.05)
                    if include_bounding_boxes
                    else None,
                )
            ],
            model_version="mock-ocr-1",
        )

    async def transcribe(
        self,
        *,
        audio: bytes,
        filename: str,
        language: str,
        expected_text: str | None,
    ) -> SttResponse:
        transcript = expected_text or "기차가 빠르게 달립니다."
        return SttResponse(
            transcript=transcript,
            confidence=0.92,
            words=[WordTiming(text=word, start_ms=i * 500, end_ms=(i + 1) * 500)
                   for i, word in enumerate(transcript.split())],
            model_version="mock-stt-1",
        )

    async def synthesize(self, request: TtsRequest) -> TtsResponse:
        words = request.text.split()
        return TtsResponse(
            audio_url="https://example.invalid/mock-audio.mp3",
            duration_ms=max(len(words), 1) * 600,
            timings=[
                WordTiming(text=word, start_ms=i * 600, end_ms=(i + 1) * 600)
                for i, word in enumerate(words)
            ],
            model_version="mock-tts-1",
        )

    async def simplify(self, request: SimplifyRequest) -> SimplifyResponse:
        return SimplifyResponse(
            original_text=request.text,
            simplified_text="문제를 해결할 방법을 찾아보았어.",
            explanation="어려운 말을 읽기 쉬운 표현으로 바꿨어.",
            difficult_words=[
                DifficultWord(word="타개하다", meaning="어려운 문제를 해결하다")
            ],
            model_version="mock-llm-1",
        )

    async def evaluate_reading(
        self,
        *,
        audio: bytes,
        filename: str,
        expected_text: str,
        language: str,
    ) -> ReadingEvaluationResponse:
        words = expected_text.split()
        return ReadingEvaluationResponse(
            transcript=expected_text,
            scores=ReadingScores(
                accuracy=91,
                fluency=82,
                completeness=100,
                pronunciation=86,
                words_per_minute=63,
            ),
            word_results=[
                WordEvaluation(
                    expected=word,
                    spoken=word,
                    status="CORRECT",
                    score=90,
                    weak_phoneme=None,
                )
                for word in words
            ],
            feedback="전체적으로 잘 읽었어. 문장 끝을 조금 더 또박또박 읽어보자.",
            model_version="mock-reading-1",
        )

    async def analyze_diagnosis(
        self,
        request: DiagnosisAnalyzeRequest,
    ) -> DiagnosisAnalyzeResponse:
        return DiagnosisAnalyzeResponse(
            reading_level=3,
            error_types=["PHONEME_SUBSTITUTION"],
            weak_phonemes=["ㅈ/ㅊ", "받침 ㄹ"],
            recommended_training=["유사 음소 구분", "문장 소리 내어 읽기"],
            model_version="mock-diagnosis-1",
        )

    async def generate_training(
        self,
        request: TrainingGenerateRequest,
    ) -> TrainingGenerateResponse:
        return TrainingGenerateResponse(
            items=[
                TrainingItem(
                    item_id="mock-item-1",
                    type="READ_ALOUD",
                    text="기차가 천천히 출발합니다.",
                    choices=None,
                    target_phonemes=request.weak_phonemes[:1],
                ),
                TrainingItem(
                    item_id="mock-item-2",
                    type="PHONEME_MATCH",
                    text="다음 중 '차'와 같은 첫소리를 고르세요.",
                    choices=["자", "차", "사"],
                    target_phonemes=["ㅊ"],
                ),
            ],
            model_version="mock-training-1",
        )
