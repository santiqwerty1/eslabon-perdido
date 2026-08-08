#!/usr/bin/env python3
"""Pruebas de las familias «Estado» y «Separación de capas» (§19.2).

Cada comprobación se ejercita en las dos direcciones. Un validador probado sólo
contra datos correctos no distingue "correcto" de "no comprobado", que es
justo lo que §19 no quiere; y uno probado sólo contra datos rotos acaba
disparando sobre el dataset real. Por eso hay tres clases de caso:

- `<familia>-ok/`: un conjunto íntegro que no debe producir ni un error ni un
  aviso;
- `<familia>-bad/<caso>/`: una violación por carpeta, con el mensaje que debe
  aparecer. Van en carpetas separadas porque cada caso necesita su propio
  snapshot y su propia cadena de deltas, y algunos se contradicen entre sí;
- los fixtures de referencia de §27.9 y el propio `knowledge/records/`, que se
  recorren enteros exigiendo cero errores.

Uso:
    python3 tests/validation/test_state_separation.py
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures"
CASES = FIXTURES / "validation-families"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # los dataclasses de validate.py lo necesitan
    spec.loader.exec_module(module)
    return module


validate = _load("validate_mod", ROOT / "scripts" / "validate" / "validate.py")
state = _load("family_state", ROOT / "scripts" / "validate" / "families" / "state.py")
separation = _load(
    "family_separation", ROOT / "scripts" / "validate" / "families" / "separation.py"
)


def load_records(directory: Path) -> dict[str, list[dict]]:
    """Lee los .jsonl de una carpeta como los leería el validador."""
    data: dict[str, list[dict]] = {}
    for path in sorted(directory.glob("*.jsonl")):
        data[path.name] = [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    return data


def run_state(case: Path) -> validate.Report:
    state.SNAPSHOTS_DIR = case / "snapshots"
    state.DELTAS_DIR = case / "deltas"
    state.MIGRATIONS_DIR = case / "migrations"
    state.MANIFEST_PATH = case / "manifest.json"
    rep = validate.Report()
    state.check(load_records(case), rep)
    return rep


def run_separation(case: Path) -> validate.Report:
    separation.SCIENCE_DIRS = (case / "views",)
    separation.PROJECTION_DIRS = (case / "projections",)
    separation.GAME_DIRS = ()
    rep = validate.Report()
    separation.check(load_records(case), rep)
    return rep


class Base(unittest.TestCase):
    def assertMessage(self, mensajes: list[str], *fragmentos: str) -> None:
        """Exige un mensaje que contenga todos los fragmentos."""
        for mensaje in mensajes:
            if all(f in mensaje for f in fragmentos):
                return
        self.fail(
            "ningún mensaje contiene "
            + " + ".join(repr(f) for f in fragmentos)
            + "\n  ".join(["\nmensajes:"] + (mensajes or ["(ninguno)"]))
        )

    def assertNoMessage(self, mensajes: list[str], *fragmentos: str) -> None:
        for mensaje in mensajes:
            if all(f in mensaje for f in fragmentos):
                self.fail(f"no debería aparecer: {mensaje}")


# --- familia Estado -----------------------------------------------------------

class TestState(Base):
    def test_conjunto_integro_pasa(self):
        """Idea superada + registro activo + fusión con destino: nada que objetar."""
        rep = run_state(CASES / "state-ok")
        self.assertEqual(rep.errors, [], "el caso íntegro no debe dar errores")
        self.assertEqual(rep.warnings, [], "el caso íntegro no debe dar avisos")
        self.assertTrue(rep.ok)

    def test_record_status_usado_como_sinonimo_de_historical_status(self):
        rep = run_state(CASES / "state-bad" / "record-status-as-synonym")
        self.assertMessage(rep.errors, "CLAIM-000911", "§10.5", "§10.6", "sinónimos")
        self.assertMessage(rep.errors, "CLAIM-000912", "sinónimos")
        # y el patrón global: los dos ejes se mueven juntos en todo el conjunto
        self.assertMessage(rep.warnings, "ideas superadas", "como uno solo")

    def test_deprecacion_sin_reemplazo_ni_razon(self):
        rep = run_state(CASES / "state-bad" / "deprecation-without-reason")
        self.assertMessage(rep.errors, "CLADE-000921", "'deprecated'", "sin reemplazo ni razón")
        self.assertMessage(rep.errors, "CLADE-000922", "'merged'", "sin reemplazo declarado")
        self.assertMessage(rep.errors, "CLADE-000923", "'archived'")
        self.assertEqual(len(rep.errors), 3)

    def test_fuerza_de_evidencia_sin_razon(self):
        rep = run_state(CASES / "state-bad" / "evidence-strength-without-reason")
        self.assertMessage(rep.errors, "CLAIM-000931", "evidence_strength 'high'", "§10.3")
        self.assertMessage(rep.errors, "CLAIM-000932", "evidence_strength 'medium'")
        # 'unknown' es el único valor que no exige razón
        self.assertNoMessage(rep.errors, "CLAIM-000933")
        self.assertEqual(len(rep.errors), 2)

    def test_ejes_colapsados_y_porcentajes_de_confianza(self):
        rep = run_state(CASES / "state-bad" / "collapsed-axes")
        self.assertMessage(rep.errors, "CLAIM-000941", "epistemic_status", "rechazado")
        self.assertMessage(rep.errors, "CLAIM-000942", "confidence", "cifra la certeza")
        self.assertMessage(rep.errors, "CLAIM-000943", "acceptance", "resolution", "independientes")
        self.assertMessage(rep.errors, "CLAIM-000944", "historical_status", "está en la raíz")
        self.assertMessage(rep.errors, "CLAIM-000945", "epistemic_dimensions.record_status")
        self.assertMessage(rep.errors, "CLAIM-000945", "overall_score")

    def test_registro_desaparecido(self):
        rep = run_state(CASES / "state-bad" / "lost-record")
        self.assertMessage(rep.errors, "claims", "SNAP-000900", "no permiten que un registro")
        self.assertMessage(rep.errors, "CLAIM-000952", "ya no está en el dataset")
        self.assertMessage(rep.errors, "records_removed", "§16.4")

    def test_migracion_sin_documentar(self):
        rep = run_state(CASES / "state-bad" / "undocumented-migration")
        self.assertMessage(rep.errors, "1.0.0", "2.0.0", "sin documento")
        self.assertMessage(rep.errors, "REV-000001", "REV-000007", "sin migración documentada")

    def test_migracion_documentada_no_se_denuncia(self):
        """El caso íntegro tiene dos schema_version y un documento que las une."""
        rep = run_state(CASES / "state-ok")
        self.assertNoMessage(rep.errors, "sin documento")
        self.assertNoMessage(rep.errors, "MIGRATE_SCHEMA")


# --- familia Separación de capas ---------------------------------------------

class TestSeparation(Base):
    def test_conjunto_integro_pasa(self):
        rep = run_separation(CASES / "separation-ok")
        self.assertEqual(rep.errors, [], "el caso íntegro no debe dar errores")
        self.assertEqual(rep.warnings, [], "el caso íntegro no debe dar avisos")

    def test_nucleo_con_costos_bonificaciones_y_victoria(self):
        rep = run_separation(CASES / "separation-bad" / "core-with-mechanics")
        self.assertMessage(rep.errors, "CLADE-000811", "energy_cost", "cost")
        self.assertMessage(rep.errors, "CLADE-000811", "victory_condition")
        self.assertMessage(rep.errors, "CLADE-000812", "bonus")
        self.assertMessage(rep.errors, "CLADE-000812", "unlocks")

    def test_direccion_de_las_referencias(self):
        """El núcleo no puede apuntar a la capa 8; la capa 8 sí al núcleo."""
        rep = run_separation(CASES / "separation-bad" / "core-points-to-projection")
        self.assertMessage(rep.errors, "CLAIM-000821", "GAME-000801", "sentido contrario")
        self.assertMessage(rep.errors, "CLAIM-000822", "MECH-000801", "balance")
        self.assertMessage(rep.warnings, "CLAIM-000822", "GAME-000802", "texto libre")
        # y un registro de capa 8 almacenado en el núcleo
        self.assertMessage(rep.errors, "GAME-000821", "capa 8", "junto al núcleo científico")

    def test_la_proyeccion_no_reescribe_la_ciencia(self):
        rep = run_separation(CASES / "separation-bad" / "projection-rewrites-claim")
        self.assertMessage(rep.errors, "GAME-000831", "predicate", "reescribiendo")
        self.assertMessage(rep.errors, "GAME-000831", "claim_text")
        self.assertMessage(rep.errors, "GAME-000831", "CLAIM-000801", "copia")
        self.assertMessage(rep.errors, "CLAIM-000831", "registro científico", "capa de juego")

    def test_las_vistas_identifican_sus_simplificaciones(self):
        rep = run_separation(CASES / "separation-bad" / "view-without-simplifications")
        self.assertMessage(rep.errors, "TAXVIEW-000841", "materializa", "sin declarar una sola simplificación")
        self.assertMessage(rep.errors, "TAXVIEW-000841", "criterios editoriales")
        self.assertMessage(rep.errors, "PHYVIEW-000842", "simplifications[0]", "vacía")
        self.assertMessage(rep.errors, "PHYVIEW-000842", "simplifications[1]", "vacía")

    def test_una_hipotesis_no_se_proyecta_como_hecho(self):
        rep = run_separation(CASES / "separation-bad" / "hypothesis-as-fact")
        self.assertMessage(rep.errors, "GAME-000851", "HYP-000851", "convertir una hipótesis en hecho")
        self.assertMessage(rep.errors, "GAME-000851", "justificación")


# --- lo que ya existe en el repositorio no debe empezar a fallar --------------

class TestSinFalsosPositivos(Base):
    """Un validador que dispara sobre datos correctos no se ejecuta dos veces.

    El control son datos ajenos: los fixtures de referencia de §27.9 y los
    `*-ok` de las demás familias. Ninguno se escribió pensando en «estado» ni en
    «separación de capas», así que si alguna de las dos comprobaciones salta
    ahí, es de estas familias el problema.
    """

    def _fixtures(self):
        for directory in sorted(FIXTURES.iterdir()):
            if directory.is_dir() and directory.name != "validation-families":
                if list(directory.glob("*.jsonl")):
                    yield directory
        for directory in sorted(CASES.iterdir()):
            if directory.is_dir() and directory.name.endswith("-ok"):
                yield directory

    def test_fixtures_de_referencia(self):
        vistos = 0
        for directory in self._fixtures():
            vistos += 1
            with self.subTest(fixture=directory.name):
                self.assertEqual(run_state(directory).errors, [])
                self.assertEqual(run_separation(directory).errors, [])
        self.assertGreater(vistos, 0, "no hay fixtures de referencia que comprobar")

    def test_dataset_real(self):
        """El dataset del repositorio pasa las dos familias tal cual está."""
        rep = validate.run(["state", "separation"])
        self.assertEqual(rep.errors, [])
        self.assertEqual(rep.warnings, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
