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

.PHONY: help setup validate verify snapshot test check clean-generated ingest corpus-freeze corpus-verify corpus-diff convert

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

ingest: ## Ingiere una sección: make ingest CORPUS=../corredor SECCION=03 [DRY=1], o FILE=texto.md
	@if [ -n "$(CORPUS)" ]; then \
		test -n "$(SECCION)" || { echo "uso: make ingest CORPUS=ruta[@ref] SECCION=NN [DRY=1]"; exit 1; }; \
		$(PYTHON) scripts/ingest/ingest.py "$(CORPUS)" --seccion "$(SECCION)" $(if $(DRY),--dry-run,); \
	else \
		test -n "$(FILE)" || { echo "uso: make ingest CORPUS=ruta[@ref] SECCION=NN, o make ingest FILE=ruta/al/texto.md"; exit 1; }; \
		$(PYTHON) scripts/ingest/ingest.py "$(FILE)" $(if $(TITLE),--title "$(TITLE)",) $(if $(DRY),--dry-run,); \
	fi

convert: ## Convierte en registros una sección ya ingerida: make convert CORPUS=../corredor SECCION=06 [DRY=1]
	@test -n "$(CORPUS)" -a -n "$(SECCION)" || { echo "uso: make convert CORPUS=ruta[@ref] SECCION=NN [DRY=1]"; exit 1; }
	@$(PYTHON) scripts/ingest/convertir.py "knowledge/corpus/conversions/corredor-$(SECCION).json" --corpus "$(CORPUS)" $(if $(DRY),--dry-run,)

corpus-freeze: ## Congela una versión del corpus: make corpus-freeze CORPUS=../corredor@ref DEC=DEC-…
	@test -n "$(CORPUS)" || { echo "uso: make corpus-freeze CORPUS=ruta[@ref] [DEC=DEC-…] [SUSTITUYE=manifiesto]"; exit 1; }
	@$(PYTHON) scripts/ingest/freeze.py create "$(CORPUS)" $(if $(DEC),--decision "$(DEC)",) $(if $(SUSTITUYE),--sustituye "$(SUSTITUYE)",)

corpus-verify: ## Comprueba que una copia es la versión congelada: make corpus-verify CORPUS=… FREEZE=…
	@test -n "$(CORPUS)" -a -n "$(FREEZE)" || { echo "uso: make corpus-verify CORPUS=ruta[@ref] FREEZE=manifiesto"; exit 1; }
	@$(PYTHON) scripts/ingest/freeze.py verify "$(CORPUS)" "$(FREEZE)"

corpus-diff: ## Qué cambió entre dos versiones: make corpus-diff ANTES=../corredor@af7e799 DESPUES=../corredor
	@test -n "$(ANTES)" -a -n "$(DESPUES)" || { echo "uso: make corpus-diff ANTES=ruta[@ref] DESPUES=ruta[@ref] [DETALLE=1]"; exit 1; }
	@$(PYTHON) scripts/ingest/freeze.py diff "$(ANTES)" "$(DESPUES)" $(if $(DETALLE),--detalle,)

snapshot: ## Crea un snapshot nuevo del estado actual
	@$(PYTHON) scripts/snapshot/snapshot.py create --label "$(LABEL)"

clean-generated: ## Vacía generated/, que es producto derivado
	@find generated -type f ! -name '.gitkeep' -delete
	@echo "generated/ limpio"
