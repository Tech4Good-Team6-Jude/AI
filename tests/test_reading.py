from fastapi.testclient import TestClient

from app.main import app


def test_reading_evaluate_with_mock_provider():
    with TestClient(app) as client:
        response = client.post(
            "/internal/v1/reading/evaluate",
            data={"expected_text": "기차가 빠르게 달립니다.", "language": "ko-KR"},
            files={"audio": ("reading.webm", b"fake-audio", "audio/webm")},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["scores"]["accuracy"] == 91
    assert body["model_version"] == "mock-reading-1"
