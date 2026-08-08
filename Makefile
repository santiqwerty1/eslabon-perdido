# Envoltorio del tooling del núcleo científico.
#
# Existe para dar puntos de entrada estables y acotados: un objetivo con nombre
# fijo puede permitirse de forma exacta, mientras que permitir el intérprete
# equivaldría a permitir ejecución arbitraria.
#
# Usa el entorno virtual si existe; si no, el Python del sistema, que funciona
# igualmente aunque la familia `schema` valide menos (ver README).

VENV   := .venv
PYTHON := $(shell [ -x $(VENV)/bin/python ] && echo $(VENV)/bin/python || echo python3)

.PHONY: help setup validate verify snapshot test check clean-generated ingest

help: ## Muestra estos objetivos
	@grep -hE '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@echo
	@echo "  Intérprete en uso: $(PYTHON)"

setup: ## Crea el entorno virtual e instala dependencias
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install --quiet --upgrade pip
	$(VENV)/bin/pip install --quiet -r requirements.txt
	@echo "listo: $(VENV)/bin/python"

validate: ## Ejecuta las once familias de validación (§19.2)
	@$(PYTHON) scripts/validate/validate.py all

verify: ## Comprueba que el estado coincide con el último snapshot (§16.6)
	@$(PYTHON) scripts/snapshot/snapshot.py verify

test: ## Valida todos los fixtures de referencia (§27.9)
	@if [ -f tests/run_tests.py ]; then \
		$(PYTHON) tests/run_tests.py; \
	else \
		echo "tests/run_tests.py todavía no existe (llega con las fases 2-6)"; \
	fi

check: validate verify test ## Todo lo anterior: es lo que ejecuta la CI

ingest: ## Ingiere una sección: make ingest FILE=ruta/al/texto.md
	@test -n "$(FILE)" || { echo "uso: make ingest FILE=ruta/al/texto.md"; exit 1; }
	@$(PYTHON) scripts/ingest/ingest.py "$(FILE)" $(if $(TITLE),--title "$(TITLE)",) $(if $(DRY),--dry-run,)

snapshot: ## Crea un snapshot nuevo del estado actual
	@$(PYTHON) scripts/snapshot/snapshot.py create --label "$(LABEL)"

clean-generated: ## Vacía generated/, que es producto derivado
	@find generated -type f ! -name '.gitkeep' -delete
	@echo "generated/ limpio"
