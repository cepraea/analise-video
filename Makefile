PYTHON ?= python3
VENV ?= .venv
PIP := $(VENV)/bin/python -m pip
PY := $(VENV)/bin/python
CONTEXT_PACK ?= INC-002
GRAPH_SOURCE ?= workspace
GRAPH_REVISION ?= HEAD
GRAPH_QUERY ?=

.PHONY: bootstrap test build dev-backend dev-frontend clean architecture architecture-check context context-check context-rules-check graph graph-check graph-query graph-views graph-views-check review-staged lore-check hooks-install hooks-uninstall hooks-check test-docs

architecture:
	$(PYTHON) scripts/docs/build_architecture_views.py

architecture-check:
	$(PYTHON) scripts/docs/build_architecture_views.py --check

context:
	$(PYTHON) scripts/docs/build_context_pack.py $(CONTEXT_PACK)

context-check:
	$(PYTHON) scripts/docs/validate_routes.py
	$(PYTHON) scripts/docs/build_context_pack.py --all --check
	$(PYTHON) scripts/docs/build_architecture_views.py --check

context-rules-check:
	$(PYTHON) scripts/docs/check_code_rules.py --source workspace

graph:
	$(PYTHON) scripts/context/build_code_graph.py --source $(GRAPH_SOURCE) --revision $(GRAPH_REVISION)

graph-check:
	$(PYTHON) scripts/context/build_code_graph.py --source $(GRAPH_SOURCE) --revision $(GRAPH_REVISION) --check

graph-query:
	@test -n "$(GRAPH_QUERY)" || (echo "GRAPH_QUERY is required" >&2; exit 2)
	$(PYTHON) scripts/context/query_code_graph.py "$(GRAPH_QUERY)"

graph-views:
	$(PYTHON) scripts/context/build_code_graph_views.py

graph-views-check:
	$(PYTHON) scripts/context/build_code_graph_views.py --check

review-staged:
	$(PYTHON) scripts/git/review_staged.py

lore-check:
	@test -n "$(COMMIT_MESSAGE)" || (echo "COMMIT_MESSAGE is required" >&2; exit 2)
	$(PYTHON) scripts/git/validate_commit_message.py "$(COMMIT_MESSAGE)"

lore-message:
	$(PYTHON) scripts/git/lore_commit.py $(LORE_ARGS)

hooks-install:
	$(PYTHON) scripts/git/install_hooks.py --install

hooks-uninstall:
	$(PYTHON) scripts/git/install_hooks.py --uninstall

hooks-check:
	$(PYTHON) scripts/git/install_hooks.py --check

test-docs:
	$(PYTHON) -m unittest discover -s tests/docs -p 'test_*.py'

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
