from fastapi import Request

from app.providers.base import InferenceProvider


def get_inference_provider(request: Request) -> InferenceProvider:
    return request.app.state.inference_provider
