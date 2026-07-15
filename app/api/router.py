from fastapi import APIRouter

from app.api.routes import diagnosis, health, ocr, reading, speech, text, training

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(ocr.router, prefix="/ocr", tags=["ocr"])
api_router.include_router(speech.router, prefix="/speech", tags=["speech"])
api_router.include_router(text.router, prefix="/text", tags=["text"])
api_router.include_router(reading.router, prefix="/reading", tags=["reading"])
api_router.include_router(diagnosis.router, prefix="/diagnosis", tags=["diagnosis"])
api_router.include_router(training.router, prefix="/training", tags=["training"])
