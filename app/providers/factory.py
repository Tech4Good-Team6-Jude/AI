from app.core.config import settings
from app.providers.base import InferenceProvider
from app.providers.mock import MockInferenceProvider
from app.providers.real import RealInferenceProvider


def create_inference_provider() -> InferenceProvider:
    if settings.provider == "mock":
        return MockInferenceProvider()

    if settings.provider == "real":
        return RealInferenceProvider()

    raise RuntimeError(
        f"Unsupported PROVIDER={settings.provider!r}"
    )