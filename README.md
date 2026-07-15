# 또박또박 Inference Server

서비스 서버 내부에서 호출하는 AI 추론 전용 FastAPI 서버 골격이다.
기본 Provider는 Mock이므로 외부 AI 계정 없이 API 계약과 연동을 먼저 개발할 수 있다.

## 실행

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload --port 8001
```

- Swagger: `http://localhost:8001/docs`
- Liveness: `GET http://localhost:8001/internal/v1/health/live`

## 주요 API

- `POST /internal/v1/ocr`
- `POST /internal/v1/speech/transcribe`
- `POST /internal/v1/speech/synthesize`
- `POST /internal/v1/text/simplify`
- `POST /internal/v1/reading/evaluate`
- `POST /internal/v1/diagnosis/analyze`
- `POST /internal/v1/training/generate`

## 구현 순서

1. Mock 응답으로 서비스 서버 연동
2. `providers/aws` 또는 `providers/local` 구현
3. `.env`의 Provider 설정에 따라 실제 Provider 주입
4. 음성 평가 Pipeline 구현
5. 모델 버전, 지연시간, 요청 ID 로그 추가
6. 부하/실패/타임아웃 테스트

## 책임 구분

- `api/routes`: HTTP 입출력
- `schemas`: 요청/응답 계약
- `services`: 검증과 기능 단위 오케스트레이션
- `providers`: AWS/로컬 모델 등 외부 추론 구현
- `pipelines`: STT → 정렬 → 채점처럼 여러 추론 단계를 조합
- `core`: 설정, 공통 오류, 로깅
