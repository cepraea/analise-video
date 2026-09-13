PYTHON ?= python3
VENV ?= .venv
PIP := $(VENV)/bin/python -m pip
PY := $(VENV)/bin/python

.PHONY: bootstrap test build dev-backend dev-frontend clean

bootstrap:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e "./backend[dev]"
	cd frontend && npm install

test:
	$(PY) -m pytest backend/tests
	cd frontend && npm test

build:
	cd frontend && npm run build

dev-backend:
	$(PY) -m uvicorn cepraea_video.main:app --app-dir backend/src --reload --host 127.0.0.1 --port 8000

dev-frontend:
	cd frontend && npm run dev

clean:
	rm -rf .pytest_cache frontend/dist
