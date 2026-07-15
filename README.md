# 또박또박 | 2026 TECH4GOOD HACKERTON — Inference Server

> 2026 TECH4GOOD HACKERTON · 소리로 트고, 훈련으로 굳힌다.

**또박또박 Inference Server**는 서비스 서버 내부에서만 호출되는 AI 추론 전용 FastAPI 서버입니다. OCR, TTS, STT, 문장 단순화 등 실제 AI 연산을 서비스 서버로부터 분리해, 어떤 모델·라이브러리를 쓰는지가 바뀌어도 서비스 서버 코드는 그대로 두고 이 레포만 교체할 수 있도록 설계했습니다.

## 문제와 접근

읽기 어려움을 돕는 기능(쉬운 문장 변환, 소리내어 읽기 채점 등)은 전부 무거운 AI 연산을 필요로 합니다. 이 연산들을 서비스 서버(DB·세션·리포트 관리)와 한 프로세스에 두면 배포·장애·모델 교체가 서로 얽히기 쉽습니다. 그래서 추론 전용 서버로 분리하고, 각 기능을 아래 원칙으로 구현했습니다.

- **무료로 시작**: 전부 무료 티어/오픈소스 라이브러리로 구현해 초기 비용 없이 MVP를 검증합니다.
- **교체 가능한 구조**: `Provider` 계층 뒤에 실제 구현을 숨겨, `PROVIDER=mock`/`real` 전환만으로 서비스 서버 개발과 AI 연동 개발을 분리합니다.
- **의료적 진단 대체 아님**: 이 서버의 어떤 응답도 난독증 진단이나 치료를 대체하지 않습니다.

## 기능별 구현

| 기능 | 엔드포인트 | 실제 구현 |
| --- | --- | --- |
| 이미지 텍스트 추출 | `POST /internal/v1/ocr` | EasyOCR (로컬 모델) |
| 음성 합성 (TTS) | `POST /internal/v1/speech/synthesize` | edge-tts (무료 API) + 단어별 타이밍 |
| 음성 인식 (STT) | `POST /internal/v1/speech/transcribe` | faster-whisper (로컬 모델) |
| 오디오 파일 조회 | `GET /internal/v1/speech/audio/{filename}` | 합성된 오디오 임시 저장·서빙 |
| 문장 단순화 | `POST /internal/v1/text/simplify` | Gemini API |
| 유사 문장 생성 | `POST /internal/v1/text/similar` | Gemini API |
| 소리내어 읽기 채점 | `POST /internal/v1/reading/evaluate` | faster-whisper + 자체 단어 정렬(`difflib`) 로직 |
| 맞춤 학습 문항 생성 | `POST /internal/v1/training/generate` | 룰베이스 (고정 문장 세트, 추후 AI 전환 예정) |

## 실행

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload --port 8001
```

`.env`에서 최소한 아래 두 값은 확인해야 합니다.

```env
PROVIDER=real                # mock이면 가짜 응답만 나옵니다
GEMINI_API_KEY=발급받은_키    # https://aistudio.google.com/app/apikey 에서 무료 발급
```

- Swagger: `http://localhost:8001/docs`
- Liveness: `GET http://localhost:8001/internal/v1/health/live`

`PROVIDER=real`로 처음 켤 때 EasyOCR·faster-whisper 모델을 내려받느라 시간이 걸릴 수 있습니다 (인터넷 필요).

### 테스트 스크립트

```bash
python scripts/tts_direct_test.py "기차가 빠르게 달립니다."       # 서버 없이 TTS 클라이언트만 단독 테스트
python scripts/synthesize_and_save.py "기차가 빠르게 달립니다."   # 서버를 통해 합성 → mp3로 저장
```

## 프로젝트 구조

```text
app/
├── api/
│   ├── routes/           # OCR, speech, text, reading, training 등 HTTP 엔드포인트
│   └── router.py         # 라우터 등록
├── core/
│   ├── config.py         # 환경변수 기반 설정
│   ├── audio_storage.py  # 합성된 오디오 임시 저장/조회
│   └── text_alignment.py # 정답 문장 vs 실제 텍스트 정렬(발음 채점용 공용 로직)
├── schemas/              # 요청/응답 Pydantic 모델
├── services/             # 검증 + provider 오케스트레이션
├── providers/
│   ├── base.py           # Provider Protocol(계약)
│   ├── mock.py           # 고정 응답 (서비스 서버 연동 개발용)
│   ├── real.py           # 실제 Provider 조립
│   └── clients/          # OCR/TTS/STT/LLM 개별 라이브러리 호출부
├── pipelines/            # 여러 추론 단계를 조합 (예: STT → 정렬 → 채점)
└── prompts/              # LLM 프롬프트 파일

scripts/                  # 로컬 개발용 수동 테스트 스크립트
tests/                    # pytest
```

## 책임 구분

- `api/routes`: HTTP 입출력만 담당
- `schemas`: 요청/응답 계약
- `services`: 검증과 기능 단위 오케스트레이션
- `providers`: Mock/Real 전환 지점. `real.py`가 실제 라이브러리(`clients/`)를 조립
- `pipelines`: STT → 정렬 → 채점처럼 여러 추론 단계를 조합하는 로직
- `core`: 설정, 공통 오류, 오디오 저장, 텍스트 정렬 등 공용 유틸리티

## 구현 현황 및 다음 단계

1. ~~Mock 응답으로 서비스 서버 연동~~ ✅
2. ~~실제 Provider(edge-tts, faster-whisper, EasyOCR, Gemini) 구현~~ ✅
3. ~~소리내어 읽기 평가 Pipeline 구현~~ ✅
4. 학습 문항 생성(`training/generate`)을 룰베이스에서 AI 기반으로 전환
5. 오디오 임시 저장소를 서비스 서버의 영구 저장소(S3 등)와 연동
6. 모델 버전, 지연시간, 요청 ID 로그 정비
7. 부하/실패/타임아웃 테스트

## 근거를 반영한 설계

- 기초 읽기 지도는 말소리 단위 인식, 글자-소리 연결, 해독, 연결된 텍스트 읽기를 체계적으로 다루는 방향을 반영합니다.
- TTS와 읽어주기 도구는 읽기 어려움이 있는 학습자의 독해를 보조할 가능성을 보여 준 연구가 있으며, 사용성은 읽기 속도·문서 구조·동적 하이라이트 같은 요소의 영향을 받습니다.
- 이 서버의 응답은 접근성을 위한 지원 도구이며, 난독증을 진단하거나 전문 치료를 대체한다고 주장하지 않습니다.

참고: [IES Foundational Skills Practice Guide](https://ies.ed.gov/ncee/wwc/PracticeGuide/21/Published), [TTS 및 읽어주기 도구 메타분석](https://pmc.ncbi.nlm.nih.gov/articles/PMC5494021/), [난독증 정의와 음운 처리 논의](https://pmc.ncbi.nlm.nih.gov/articles/PMC12198935/)

## 브랜치, 커밋, PR 컨벤션

### 브랜치 전략

```text
main       프로덕션/릴리즈 브랜치
develop    개발 통합 브랜치
작업 브랜치  이슈 단위 작업 브랜치
```

일반 기능, 수정, 문서, 설정 작업은 `develop`을 기준으로 브랜치를 만들고 PR을 보냅니다. `main` 머지는 릴리즈 또는 배포 시점에 진행합니다.

### 브랜치 네이밍

```text
{type}#{issue-number}/{task-name}
```

예시:

```bash
feat#12/tts-word-timing
fix#15/ocr-response-shape
chore#1/github-templates
```

### 커밋 메시지

```text
{type}/#{issue-number}: {작업 요약}
```

예시:

```bash
git commit -m "feat/#12: TTS 단어별 타이밍 추가"
git commit -m "fix/#15: OCR 응답 조립 오류 수정"
git commit -m "docs/#3: README 업데이트"
```

Type은 다음 기준으로 사용합니다.

| Type     | 의미                                                    |
| -------- | ------------------------------------------------------- |
| feat     | 새로운 기능 추가                                        |
| fix      | 버그 수정                                               |
| docs     | 문서 수정                                               |
| style    | 코드 포맷, 세미콜론, 공백 등 동작 변화 없는 스타일 정리 |
| refactor | 기능 변화 없는 코드 구조 개선                           |
| test     | 테스트 추가 또는 수정                                   |
| chore    | 설정, 패키지, 빌드, 레포 관리                           |
| design   | UI 스타일링, 레이아웃, 디자인 수정                      |

### PR 컨벤션

PR 제목은 커밋 메시지와 같은 형식을 사용합니다.

```text
{type}/#{issue-number}: {작업 요약}
```

PR 작성 시에는 PR 템플릿을 따르고 다음 내용을 명확히 남깁니다.

- 간단 설명
- 관련 이슈
- 작업 내용
- 확인 사항
