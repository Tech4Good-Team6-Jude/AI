# pipelines

여러 추론 기능을 조합하는 흐름을 둔다.

예시:
- `reading_pipeline.py`: STT → 단어 정렬 → 오류 분류 → 피드백 생성
- `assist_pipeline.py`: OCR → 어려운 문장 탐지 → 문장 단순화
- `diagnosis_pipeline.py`: 문항별 평가 집계 → 오류 유형/레벨 산출

단일 외부 API 호출은 `providers`, 비즈니스 검증은 `services`,
여러 단계를 연결하는 로직만 이 폴더에 둔다.
