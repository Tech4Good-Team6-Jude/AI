.PHONY: install run test lint docker-build docker-run

install:
	python -m pip install -e ".[dev]"

run:
	uvicorn app.main:app --reload --port 8001

test:
	pytest -q

lint:
	ruff check .

docker-build:
	docker build -t ddobak-inference .

docker-run:
	docker run --rm -p 8001:8000 ddobak-inference
