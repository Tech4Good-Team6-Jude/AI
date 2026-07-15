from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# (선택) 실제 API 라우터들이 만들어지면 주석을 해제하고 연결합니다.
# from app.api.v1 import stt, assistant

# ==========================================
# 1. Lifespan 설정 (서버 시작/종료 시 실행될 로직)
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # [StartUp] 서버가 켜질 때 실행할 코드
    # 여기에 대용량 AI 모델(Whisper 등)을 메모리/GPU에 로드하는 로직을 넣습니다.
    print("==========================================")
    print("🚀 [또박또박 AI] AI 추론 서버를 시작합니다.")
    print("📦 로컬 AI 모델(Whisper)을 GPU 메모리에 로딩하는 중...")
    print("==========================================")
    
    # 예시로 app.state에 모델을 담아두면, 다른 API 파일(라우터)에서도 이 모델을 공유해서 쓸 수 있습니다.
    # app.state.whisper_model = WhisperModel("base", device="cuda")
    
    yield  # ◀ 이 시점에 서버가 클라이언트 요청을 받기 시작합니다.

    # [ShutDown] 서버가 꺼질 때 실행할 코드
    # GPU 메모리를 안전하게 비우거나 세션을 닫는 작업을 수행합니다.
    print("==========================================")
    print("🛑 [또박또박 AI] AI 추론 서버를 안전하게 종료합니다.")
    print("==========================================")


# ==========================================
# 2. FastAPI 앱 초기화 (Lifespan 주입)
# ==========================================
app = FastAPI(
    title="또박또박 AI 추론 API 서버",
    description="난독증 해결 학습 도우미 '또박또박'의 AI(STT, LLM) 처리를 담당하는 전용 서버입니다.",
    version="1.0.0",
    lifespan=lifespan
)


# ==========================================
# 3. CORS(보안 설정) 미들웨어 추가
# ==========================================
# 개발 단계에서는 모든 외부 접속(*)을 허용하여 백엔드/프론트엔드와 편하게 연결합니다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# 4. API 라우터 등록
# ==========================================
# 추후 작성할 API 기능들을 메인 앱에 붙여주는 단계입니다.
# (지금은 파일이 없으므로 주석 처리해 두고, 나중에 파일 생성 후 주석을 해제합니다.)
# app.include_router(stt.router, prefix="/api/v1/stt", tags=["Speech-To-Text"])
# app.include_router(assistant.router, prefix="/api/v1/assistant", tags=["Dyslexia Assistant"])


# ==========================================
# 5. 헬스 체크용 기본 엔드포인트 (통신 테스트용)
# ==========================================
@app.get("/", tags=["Health Check"])
def read_root():
    """
    AI 서버가 정상적으로 켜져 있는지 확인하는 테스트용 API입니다.
    """
    return {
        "status": "online",
        "service": "또박또박 AI Inference Server",
        "message": "서버가 정상적으로 작동 중이며, 통신 가능한 상태입니다."
    }

# 이 임시 엔드포인트는 백엔드 개발자와의 통신 규격을 맞추기 위해 임시로 열어둡니다.
@app.post("/api/v1/test-stt", tags=["Health Check"])
def test_stt():
    """
    백엔드 서버와 POST 통신이 잘 연결되는지 확인하는 임시 API입니다.
    """
    return {
        "status": "success",
        "recognized_text": "가나다라 마바사 (테스트용 AI 결과)"
    }