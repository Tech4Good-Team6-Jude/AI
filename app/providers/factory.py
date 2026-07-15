from app.core.config import settings
from app.providers.base import InferenceProvider
from app.providers.mock import MockInferenceProvider


def create_inference_provider() -> InferenceProvider:
    if settings.provider == "mock":
        return MockInferenceProvider()

    raise RuntimeError(
        f"Unsupported PROVIDER={settings.provider!r}. "
        "providers/factory.py에 실제 Provider를 등록해줘."
    )
