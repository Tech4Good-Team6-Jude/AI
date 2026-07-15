from fastapi import APIRouter

router = APIRouter()


@router.get("/health/live")
async def liveness():
    return {"status": "ok"}


@router.get("/health/ready")
async def readiness():
    # 실제 환경에서는 모델 로딩 여부와 외부 AI API 연결 상태를 확인한다.
    return {"status": "ready"}
