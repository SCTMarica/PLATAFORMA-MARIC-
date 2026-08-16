.PHONY: help up down build logs \
	e2e e2e-build e2e-up e2e-down e2e-file e2e-test e2e-id \
	e2e-video e2e-video-id e2e-demo \
	e2e-results e2e-open-video e2e-show-trace e2e-clean \
	test

COMPOSE ?= docker compose
E2E_COMPOSE := $(COMPOSE) --profile e2e
# -T: no TTY (required on GitHub Actions; fine for local pytest too)
E2E_RUN := $(E2E_COMPOSE) run --rm -T playwright

# Optional overrides:
#   make e2e-file FILE=tests/e2e/test_01_public_pages.py
#   make e2e-test TEST=tests/e2e/test_01_public_pages.py::test_e2e_01_001_visitor_opens_home
#   make e2e-id ID=e2e_01_001
#   make e2e EVIDENCE=1
FILE ?= tests/e2e/test_01_public_pages.py
TEST ?=
SLOWMO ?= 400
ID ?= e2e_01_001
EVIDENCE ?= 0

# Default run: terminal only. Evidence (video/png/trace) is opt-in.
E2E_QUIET := --video off --screenshot off --tracing off
E2E_EVIDENCE := --video on --screenshot off --tracing on

ifeq ($(EVIDENCE),1)
E2E_OPTS := $(E2E_EVIDENCE)
else
E2E_OPTS := $(E2E_QUIET)
endif

help:
	@echo "Plataforma Maric — comandos úteis"
	@echo ""
	@echo "App local:"
	@echo "  make up              Sobe web + db (desenvolvimento)"
	@echo "  make down            Para a stack de desenvolvimento"
	@echo "  make build           Rebuild da imagem web"
	@echo "  make logs            Logs do web"
	@echo ""
	@echo "E2E — só terminal (sem arquivos em test-results/):"
	@echo "  make e2e             Suite completa"
	@echo "  make e2e-file        Um arquivo (FILE=...)"
	@echo "  make e2e-test        Um teste (TEST=path::nome)"
	@echo "  make e2e-id          Por ID (ID=e2e_01_001)"
	@echo ""
	@echo "E2E — com evidência (vídeo + print + trace):"
	@echo "  make e2e-video       Suite completa com arquivos"
	@echo "  make e2e-video-id    Por ID com arquivos (ID=e2e_01_001)"
	@echo "  make e2e-demo        Evidência + slowmo (destaques no vídeo)"
	@echo "  make e2e EVIDENCE=1  Qualquer alvo acima com evidência"
	@echo "  make e2e-results     Lista evidências geradas"
	@echo "  make e2e-open-video  Abre o último vídeo"
	@echo "  make e2e-show-trace  Abre o último trace no navegador"
	@echo "  make e2e-clean       Limpa test-results/"
	@echo ""
	@echo "Infra E2E:"
	@echo "  make e2e-build       Rebuild Playwright"
	@echo "  make e2e-up          Sobe db-e2e + web-e2e"
	@echo "  make e2e-down        Para profile e2e"
	@echo ""
	@echo "Exemplos:"
	@echo "  make e2e-id ID=e2e_01_002"
	@echo "  make e2e-video-id ID=e2e_01_001"
	@echo "  make e2e-demo ID=e2e_01_001 && make e2e-open-video"

# --- Desenvolvimento ---

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

build:
	$(COMPOSE) build web

logs:
	$(COMPOSE) logs -f web

# --- E2E ---

e2e-build:
	$(E2E_COMPOSE) build playwright web-e2e

e2e-up:
	$(E2E_COMPOSE) up -d db-e2e web-e2e

e2e-down:
	$(E2E_COMPOSE) stop web-e2e db-e2e playwright 2>/dev/null || true
	$(E2E_COMPOSE) rm -f web-e2e db-e2e playwright 2>/dev/null || true

e2e:
	$(E2E_RUN) pytest -v $(E2E_OPTS)

e2e-file:
	$(E2E_RUN) pytest -v $(E2E_OPTS) $(FILE)

e2e-test:
ifndef TEST
	$(error Informe TEST=caminho::nome_do_teste)
endif
	$(E2E_RUN) pytest -v $(E2E_OPTS) $(TEST)

e2e-id:
	$(E2E_RUN) pytest -v $(E2E_OPTS) -k $(ID)

e2e-video:
	$(E2E_RUN) pytest -v $(E2E_EVIDENCE)

e2e-video-id:
	$(E2E_RUN) pytest -v $(E2E_EVIDENCE) -k $(ID)

e2e-demo:
ifdef TEST
	$(E2E_RUN) pytest -v $(E2E_EVIDENCE) $(TEST) --slowmo $(SLOWMO)
else
	$(E2E_RUN) pytest -v $(E2E_EVIDENCE) -k $(ID) --slowmo $(SLOWMO)
endif

e2e-results:
	@echo "=== Evidências em test-results/ ==="
	@echo ""
	@echo "-- Execuções (pastas por horário) --"
	@find test-results -mindepth 1 -maxdepth 1 -type d -name '????-??-??_??-??-??' 2>/dev/null | sort || true
	@echo ""
	@echo "-- Vídeos --"
	@find test-results -type f -name '*.mp4' 2>/dev/null | sort || true
	@find test-results -type f -name '*.webm' 2>/dev/null | sort || true
	@echo ""
	@echo "-- Screenshots --"
	@find test-results -type f -name '*.png' 2>/dev/null | sort || true
	@echo ""
	@echo "-- Traces --"
	@find test-results -type f -name 'trace.zip' 2>/dev/null | sort || true

e2e-open-video:
	@set -e; \
	LATEST_RUN=$$(find test-results -mindepth 1 -maxdepth 1 -type d -name '????-??-??_??-??-??' 2>/dev/null | sort | tail -1); \
	if [ -n "$$LATEST_RUN" ]; then \
		VIDEO=$$(find "$$LATEST_RUN" -type f -name '*.mp4' -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -1 | cut -d' ' -f2-); \
		if [ -z "$$VIDEO" ]; then \
			VIDEO=$$(find "$$LATEST_RUN" -type f -name '*.webm' -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -1 | cut -d' ' -f2-); \
		fi; \
	else \
		VIDEO=$$(find test-results -type f -name '*.mp4' -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -1 | cut -d' ' -f2-); \
		if [ -z "$$VIDEO" ]; then \
			VIDEO=$$(find test-results -type f -name '*.webm' -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -1 | cut -d' ' -f2-); \
		fi; \
	fi; \
	if [ -z "$$VIDEO" ]; then \
		echo "Nenhum vídeo em test-results/. Rode: make e2e-video-id ID=e2e_01_001"; \
		exit 1; \
	fi; \
	echo "Abrindo $$VIDEO"; \
	if command -v xdg-open >/dev/null 2>&1; then xdg-open "$$VIDEO"; \
	elif command -v open >/dev/null 2>&1; then open "$$VIDEO"; \
	else echo "Abra manualmente: $$VIDEO"; fi

e2e-show-trace:
	@set -e; \
	LATEST_RUN=$$(find test-results -mindepth 1 -maxdepth 1 -type d -name '????-??-??_??-??-??' 2>/dev/null | sort | tail -1); \
	if [ -n "$$LATEST_RUN" ]; then \
		TRACE=$$(find "$$LATEST_RUN" -name 'trace.zip' -type f -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -1 | cut -d' ' -f2-); \
	else \
		TRACE=$$(find test-results -name 'trace.zip' -type f -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -1 | cut -d' ' -f2-); \
	fi; \
	if [ -z "$$TRACE" ]; then \
		echo "Nenhum trace.zip em test-results/. Rode: make e2e-video"; \
		exit 1; \
	fi; \
	echo "Abrindo $$TRACE"; \
	if command -v playwright >/dev/null 2>&1; then \
		playwright show-trace "$$TRACE"; \
	else \
		python3 -m playwright show-trace "$$TRACE"; \
	fi

e2e-clean:
	# Artefatos são criados como root pelo container Playwright.
	$(E2E_COMPOSE) run --rm -T --entrypoint sh playwright -c 'rm -rf /app/test-results/*'
	@echo "test-results/ limpo"

test: e2e
