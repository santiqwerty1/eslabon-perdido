#!/usr/bin/env python3
"""Pruebas de las familias «geografía», «hipótesis» y «evidencia» de §19.2.

Cada familia se ejecuta contra dos fixtures de tests/fixtures/validation-families/:

    <familia>-ok    registros correctos; la familia no debe decir nada
    <familia>-bad   un registro por comprobación, cada uno mal a propósito

La segunda mitad es la que importa: una familia que nunca dispara no distingue
«correcto» de «no comprobado», que es justo lo que la guía prohíbe. Por eso las
expectativas son positivas —«esta comprobación tiene que sonar»— y no un simple
recuento.

Los fixtures no son corpus (§4.7): entidades, regiones y linajes llevan nombres
de prueba deliberadamente neutros. Ninguna afirmación de estos ficheros describe
nada del mundo real.

Uso:
    python3 tests/validation/test_geography_hypotheses_evidence.py
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FAMILIES = ROOT / "scripts" / "validate" / "families"
FIXTURES = ROOT / "tests" / "fixtures" / "validation-families"

# Fragmento distintivo de cada mensaje esperado, con la comprobación que lo
# produce. El texto completo puede reformularse; lo que la prueba fija es que la
# comprobación exista y dispare sobre el registro correcto.
EXPECTED: dict[str, dict[str, list[tuple[str, str]]]] = {
    "geography-bad": {
        "errors": [
            ("§12.1 yacimiento en el fichero de regiones", "SITE-000002 está en regions.jsonl"),
            ("§12.1 prefijo de región con tipo de yacimiento", "REGION-000040 lleva prefijo REGION-"),
            ("§12.1 región de alcance que es un yacimiento", "CLAIM-000001.scope.region_ids incluye SITE-000001"),
            ("§12.1 referencia geográfica anidada inexistente", "REGION-000099, que no existe"),
            ("§12.1 site_ids con una región", "EVID-000001.site_ids incluye REGION-000010"),
            ("§12.1 region_ids con un yacimiento", "EVID-000001.region_ids incluye SITE-000001"),
            ("§12.1 región dentro de un yacimiento", "CLAIM-000002 coloca la región"),
            ("§12.1 yacimiento que contiene una región", "CLAIM-000003 hace que el yacimiento"),
            ("§9.4 derivación sin marcar en la procedencia", "CLAIM-000004 lleva regla de derivación"),
            ("§9.4 procedencia derivada sin regla", "CLAIM-000005 declara origin='derived' sin regla"),
            ("§19.2 coexistencia inferida sólo por tiempo", "CLAIM-000007 infiere coexistencia"),
        ],
        "warnings": [
            ("§14.1 'contains' no derivada", "CLAIM-000003 afirma 'contains'"),
            ("§12.2 ubicación sin observación ni inferencia", "CLAIM-000006 ubica LINEAGE-000004"),
            ("§9.4 derivada sin dependencias", "CLAIM-000008 deriva coexistencia sin declarar"),
            ("§14.4 coexistencia explícita contra la geografía", "CLAIM-000009 afirma coexistencia"),
        ],
    },
    "hypotheses-bad": {
        "errors": [
            ("§15.2 requisito no incluido", "CLAIM-000208 como requisito pero no lo incluye"),
            ("§9.2 incluida y excluida a la vez", "incluye y excluye CLAIM-000204"),
            ("§15.2 incompatibles en la misma hipótesis", "la hipótesis HYP-000201 selecciona CLAIM-000203 y CLAIM-000204"),
            ("§15.2 incompatibles en la misma vista", "la vista PHYVIEW-000201 selecciona CLAIM-000203 y CLAIM-000204"),
            ("§11.3 ciclo de ascendencia", "contiene un ciclo de ascendencia"),
            ("§15.3 reticulación aplanada a árbol", "aplana reticulación a un formato de árbol"),
            ("§17 paso 9 vista con dos alternativas", "que se declaran alternativas"),
            ("§15.2 vista con dos hipótesis del mismo grupo de conflicto", "del mismo grupo de conflicto"),
            ("§15.2 vista que selecciona lo excluido", "selecciona CLAIM-000204, que HYP-000202 excluye"),
            ("§15.2 vista sin el requisito de su hipótesis", "sin seleccionar su requisito CLAIM-000201"),
            ("§15.1 hipótesis sin apoyo enlazado", "no enlaza evidencia ni fuente favorable"),
            ("§6.4 evidencia favorable que cuestiona", "como evidencia favorable, pero EVID-000202 cuestiona"),
            ("§6.4 contraevidencia que respalda", "como evidencia contraria, pero EVID-000201 respalda"),
        ],
        "warnings": [
            ("§19.2 requisito en registro superado", "cuyo registro está en 'superseded'"),
            ("§10.6 selección de un registro superado", "incluye CLAIM-000207, en estado 'superseded'"),
            ("§9.3 alcance que la hipótesis desconoce", "CLAIM-000206 limita su alcance a HYP-000201"),
            ("§9.3 vista que selecciona fuera de su alcance", "cuyo alcance se limita a ['HYP-000201']"),
            ("§15.1 hipótesis sin oposición registrada", "no registra contraevidencia ni fuentes opuestas"),
            ("§14.5 alternativa no simétrica", "que no le devuelve el enlace"),
        ],
    },
    "evidence-bad": {
        "errors": [
            ("§4.1 valor cuantitativo sin fuente", "guarda el valor 0.85 sin fuente"),
            ("§10.7 valor cuantitativo sin método", "guarda el valor 0.85 sin método"),
            ("§4.1 porcentaje de confianza inventado", "prohíbe los porcentajes arbitrarios de confianza"),
            ("§4.1 afirmación cuantitativa sin soporte", "CLAIM-000402 afirma el valor 1.8 sin soporte"),
            ("§6.4 soporte estadístico sin fuente", "RESULT-000401 guarda soporte"),
            ("§4.1 resultado sin fuente", "RESULT-000401 guarda el valor 0.99"),
            ("§13.1 proporción sin respaldo", "EVENT-000401 cuantifica la participación"),
            ("E.7 evidencia que respalda y cuestiona a la vez", "EVID-000405 respalda y cuestiona"),
            ("§19.2 respaldo con el sentido invertido", "CLAIM-000403 se apoya en EVID-000402, que la cuestiona"),
            ("§19.2 evidencia que no respalda lo que dice", "que no respalda esa afirmación"),
            ("§6.4 contraevidencia con el sentido invertido", "como contraevidencia, pero EVID-000404 la respalda"),
            ("E.7 evidencia sin fuente ni cuestión pendiente", "EVID-000406 no tiene fuente ni cuestión"),
            ("§10.3 fuerza de evidencia sin razón", "CLAIM-000406 declara evidence_strength='high' sin razón"),
        ],
        "warnings": [
            ("§10.7 medida sin escala, nodo ni condiciones", "no registra escala, nodo o relación"),
            ("§10.7 valor sin unidad ni escala", "guarda un valor sin unidad ni escala"),
            ("§10.7 soporte sin escala", "guarda soporte 'posterior_probability' sin escala"),
            ("§6.4 evidencia que no se vincula a nada", "no respalda ni cuestiona ninguna afirmación"),
            ("§6.4 enlace unidireccional", "que no la enlaza"),
            ("§19.2 fuente sin localizador específico", "sin localizador específico"),
            ("§6.4 evidencia estadística sin resultado", "es estadística y no enlaza resultado"),
            ("§4.1 fuerza alta sin evidencia", "declara fuerza de evidencia alta"),
        ],
    },
}


class Report:
    """Mismo contrato que scripts/validate/validate.py, sin depender de él."""

    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.infos: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def info(self, msg: str) -> None:
        self.infos.append(msg)


def load_family(name: str):
    spec = importlib.util.spec_from_file_location(f"family_{name}", FAMILIES / f"{name}.py")
    if spec is None or spec.loader is None:
        raise RuntimeError(f"no se pudo cargar la familia {name}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_fixture(name: str) -> dict[str, list[dict]]:
    directory = FIXTURES / name
    if not directory.is_dir():
        raise RuntimeError(f"falta el fixture {directory}")
    return {
        f.name: [json.loads(line) for line in f.read_text(encoding="utf-8").splitlines() if line.strip()]
        for f in sorted(directory.glob("*.jsonl"))
    }


def run_family(name: str, fixture: str) -> Report:
    rep = Report()
    load_family(name).check(load_fixture(fixture), rep)
    return rep


def main() -> int:
    failures: list[str] = []

    for family in ("geography", "hypotheses", "evidence"):
        mod = load_family(family)
        if getattr(mod, "NAME", None) != family:
            failures.append(f"{family}: NAME no coincide con el nombre del módulo")
        if getattr(mod, "PHASE", "ausente") is not None:
            failures.append(f"{family}: PHASE debería ser None (la familia ya es ejecutable)")

        fixture_ok = f"{family}-ok"
        rep = run_family(family, fixture_ok)
        for msg in rep.errors:
            failures.append(f"{fixture_ok}: ERROR inesperado — {msg}")
        for msg in rep.warnings:
            failures.append(f"{fixture_ok}: WARNING inesperado — {msg}")
        print(f"{fixture_ok}: {len(rep.errors)} errores, {len(rep.warnings)} advertencias, "
              f"{len(rep.infos)} informativos")

        fixture_bad = f"{family}-bad"
        rep = run_family(family, fixture_bad)
        expected = EXPECTED[fixture_bad]
        found = 0
        for severity, bucket in (("errors", rep.errors), ("warnings", rep.warnings)):
            for label, needle in expected[severity]:
                if any(needle in msg for msg in bucket):
                    found += 1
                else:
                    failures.append(f"{fixture_bad}: no se detectó {label} (esperaba {needle!r})")
        total = len(expected["errors"]) + len(expected["warnings"])
        print(f"{fixture_bad}: {found}/{total} comprobaciones dispararon "
              f"({len(rep.errors)} errores, {len(rep.warnings)} advertencias emitidos)")

    if failures:
        print()
        for msg in failures:
            print(f"FALLO   {msg}")
        print(f"\n{len(failures)} fallos")
        return 1

    print("\nPRUEBAS CORRECTAS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
