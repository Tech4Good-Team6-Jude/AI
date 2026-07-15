from typing import Protocol

from app.schemas.diagnosis import DiagnosisAnalyzeRequest, DiagnosisAnalyzeResponse
from app.schemas.ocr import OcrResponse
from app.schemas.reading import ReadingEvaluationResponse
from app.schemas.speech import SttResponse, TtsRequest, TtsResponse
from app.schemas.text import SimplifyRequest, SimplifyResponse
from app.schemas.training import TrainingGenerateRequest, TrainingGenerateResponse


class InferenceProvider(Protocol):
    async def ocr(
        self,
        *,
        content: bytes,
        filename: str,
        language: str,
        include_bounding_boxes: bool,
    ) -> OcrResponse: ...

    async def transcribe(
        self,
        *,
        audio: bytes,
        filename: str,
        language: str,
        expected_text: str | None,
    ) -> SttResponse: ...

    async def synthesize(self, request: TtsRequest) -> TtsResponse: ...

    async def simplify(self, request: SimplifyRequest) -> SimplifyResponse: ...

    async def evaluate_reading(
        self,
        *,
        audio: bytes,
        filename: str,
        expected_text: str,
        language: str,
    ) -> ReadingEvaluationResponse: ...

    async def analyze_diagnosis(
        self,
        request: DiagnosisAnalyzeRequest,
    ) -> DiagnosisAnalyzeResponse: ...

    async def generate_training(
        self,
        request: TrainingGenerateRequest,
    ) -> TrainingGenerateResponse: ...
