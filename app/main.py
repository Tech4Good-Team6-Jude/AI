from contextlib import asynccontextmanager
from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import settings
from app.core.errors import AppError
from app.providers.factory import create_inference_provider


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 실제 모델이나 외부 SDK 클라이언트는 여기서 한 번만 초기화한다.
    app.state.inference_provider = create_inference_provider()
    yield
    # GPU 메모리, 세션, 네트워크 클라이언트 정리도 여기서 수행한다.


app = FastAPI(
    title="또박또박 Inference Server",
    version="0.1.0",
    docs_url="/docs" if settings.enable_docs else None,
    openapi_url="/openapi.json" if settings.enable_docs else None,
    lifespan=lifespan,
)


@app.middleware("http")
async def add_request_metadata(request: Request, call_next):
    started = perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time-Ms"] = f"{(perf_counter() - started) * 1000:.1f}"
    request_id = request.headers.get("X-Request-Id")
    if request_id:
        response.headers["X-Request-Id"] = request_id
    return response


@app.exception_handler(AppError)
async def handle_app_error(_: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
            "retryable": exc.retryable,
        },
    )


app.include_router(api_router, prefix=settings.api_prefix)
