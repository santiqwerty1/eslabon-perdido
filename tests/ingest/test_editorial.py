#!/usr/bin/env python3
"""Pruebas de scripts/ingest/editorial.py (correcciones editoriales, DEC-062).

Sobre la sección 0 de corredor-mini convertida, como las de la absorción:
todo ocurre en un directorio temporal, y cada prueba parte de un libro mayor
recién convertido.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from entorno import MINI, Entorno, absorber, convertir, corredor, delta_mod  # noqa: E402

import editorial  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "snapshot"))
import snapshot  # noqa: E402


@unittest.skipUnless(importlib.util.find_spec("jsonschema"), "editorial.py exige jsonschema")
class Editorial(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.entorno = Entorno(self.tmp).__enter__()
        self.addCleanup(self._tmp.cleanup)
        self.addCleanup(self.entorno.__exit__, None, None, None)
        self.originales = editorial.EDITORIALES
        editorial.EDITORIALES = self.tmp / "editorials"
        editorial.EDITORIALES.mkdir()
        self.addCleanup(setattr, editorial, "EDITORIALES", self.originales)
        deltas = self.tmp / "deltas"
        with contextlib.redirect_stdout(io.StringIO()):
            assert delta_mod.cmd(deltas / "SEC-000001.json", False, False) == 0
            spec = self.tmp / "corredor-00.json"
            spec.write_text(json.dumps(self.entorno.spec(), ensure_ascii=False), encoding="utf-8")
            assert convertir.convertir(spec, str(MINI), False) == 0
            assert delta_mod.cmd(deltas / "SEC-000001-conversion.json", False, False) == 0
        actuales = absorber.registros_actuales()
        self.alfa = next(r for r, (f, x) in actuales.items() if x.get("preferred_label") == "FIX-Alfa")
        self.beta = next(r for r, (f, x) in actuales.items() if x.get("preferred_label") == "FIX-Beta")
        self.claim = next(r for r, (f, _) in actuales.items() if f == "claims.jsonl")
        self.evid = next(r for r, (f, _) in actuales.items() if f == "evidence.jsonl")

    # --- utilidades -------------------------------------------------------------------------

    def spec(self, **cambios) -> dict:
        s = {
            "decision": "DEC-062",
            "reason": "La conversión no declaró el clado que junta a FIX-Alfa y FIX-Beta.",
            "records": [
                {"key": "@AB", "file": "clades.jsonl", "section": "SEC-000001", "rows": ["C-001"],
                 "reason": "el clado que forman los dos hermanos de C-001",
                 "record": {"preferred_label": "FIX-Alfa+Beta", "description": "Clado de prueba."}},
                {"key": "@CL_A", "file": "claims.jsonl", "section": "SEC-000001", "rows": ["C-001"],
                 "reason": "FIX-Alfa es miembro del clado de C-001",
                 "record": {"claim_type": "relational", "subject_id": self.alfa, "predicate": "member_of",
                            "object": {"entity_id": "@AB"}}},
            ],
            "patches": {
                self.evid: {"reason": "la evidencia de C-001 apoya también la pertenencia",
                            "add": {"supports_claim_ids": ["@CL_A"]}},
                self.beta: {"reason": "la descripción nombra el clado nuevo",
                            "set": {"description": "Clado de prueba, hermano de FIX-Alfa."}},
            },
        }
        s.update(cambios)
        return s

    def escribir(self, spec: dict, nombre: str = "prueba") -> Path:
        ruta = editorial.EDITORIALES / f"{nombre}.json"
        ruta.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
        return ruta

    def construir(self, spec: dict, nombre: str = "prueba") -> dict:
        with contextlib.redirect_stdout(io.StringIO()):
            return editorial.construir(self.escribir(spec, nombre))

    def guardar(self, c: dict) -> Path:
        ruta = self.tmp / "deltas" / c["nombre"]
        ruta.write_text(json.dumps(c["delta"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return ruta

    def aplicar(self, ruta: Path, revertir: bool = False) -> int:
        with contextlib.redirect_stdout(io.StringIO()):
            return delta_mod.cmd(ruta, revertir, False)

    def negativa(self, spec: dict, texto: str, nombre: str = "prueba") -> None:
        with self.assertRaises(SystemExit) as ctx:
            self.construir(spec, nombre)
        self.assertIn(texto, str(ctx.exception))

    # --- casos --------------------------------------------------------------------------------

    def test_alta_con_procedencia_ejes_y_enlaces_de_vuelta(self):
        c = self.construir(self.spec())
        nuevos = {rec["id"]: rec for _, rec in c["altas"]}
        ab, cl = nuevos[c["ids"]["@AB"]], nuevos[c["ids"]["@CL_A"]]
        fila = corredor.correspondencia()["00"]["rows"]["C-001"]
        self.assertEqual(cl["provenance"]["origin"], "editorial")
        self.assertEqual(cl["provenance"]["section_ids"], ["SEC-000001"])
        self.assertEqual(cl["provenance"]["passage_ids"], fila["passage_ids"])
        self.assertEqual(cl["provenance"]["dataset_revision"], c["delta"]["dataset_revision_after"])
        self.assertEqual(cl["epistemic_dimensions"]["evidence_strength"], "medium", "los ejes de C-001")
        self.assertEqual(cl["evidence_ids"], [self.evid], "la evidencia parcheada queda enlazada de vuelta")
        self.assertEqual(ab["claim_ids"], [cl["id"]])
        self.assertEqual(ab["first_introduced_in"], "SEC-000001")
        self.assertTrue(any("DEC-062" in n for n in cl["notes"]))
        cambiados = {rid: despues for rid, (_, _, despues) in c["cambios"].items()}
        self.assertIn(cl["id"], cambiados[self.alfa]["claim_ids"], "el sujeto existente la lista")
        self.assertIn(cl["id"], cambiados[self.evid]["supports_claim_ids"])
        self.assertEqual(cambiados[self.beta]["description"], "Clado de prueba, hermano de FIX-Alfa.")
        bloque = c["delta"]["editorial"]
        self.assertEqual(bloque["rows"], {"SEC-000001": {"C-001": [ab["id"], cl["id"]]}})
        self.assertEqual(bloque["keys"], {"@AB": ab["id"], "@CL_A": cl["id"]})
        self.assertEqual(c["nombre"], "ED-prueba.json")

    def test_aplicar_y_revertir_deja_todo_como_estaba(self):
        antes = {p.name: p.read_bytes() for p in self.entorno.records.glob("*.jsonl")}
        ruta = self.guardar(self.construir(self.spec()))
        self.assertEqual(self.aplicar(ruta), 0)
        self.assertNotEqual(antes, {p.name: p.read_bytes() for p in self.entorno.records.glob("*.jsonl")})
        self.assertEqual(self.aplicar(ruta, revertir=True), 0)
        self.assertEqual(antes, {p.name: p.read_bytes() for p in self.entorno.records.glob("*.jsonl")})

    def test_la_correspondencia_cuenta_los_registros_editoriales(self):
        c = self.construir(self.spec())
        self.assertEqual(self.aplicar(self.guardar(c)), 0)
        s = corredor.correspondencia()["00"]
        cl = c["ids"]["@CL_A"]
        self.assertIn(cl, s["rows"]["C-001"]["record_ids"])
        self.assertEqual(s["editorial_rows"][cl], ["C-001"])
        filas, _ = absorber.filas_de_registros(s)
        self.assertEqual(filas[cl], ["C-001"], "una absorción sabrá de qué fila salió")

    def test_dos_construcciones_dan_el_mismo_delta(self):
        a = self.construir(self.spec())["delta"]
        b = self.construir(self.spec())["delta"]
        self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))

    def test_negativas(self):
        s = self.spec()
        s["records"][1]["rows"] = ["C-099"]
        self.negativa(s, "la fila C-099 no es de SEC-000001")
        s = self.spec()
        s["records"][1]["rows"] = ["C-002"]
        self.negativa(s, "S02, que no tiene ficha")
        s = self.spec()
        s["records"][0]["record"]["provenance"] = {}
        self.negativa(s, "fija provenance")
        s = self.spec(patches={self.claim: {"reason": "x", "add": {"evidence_ids": ["EVID-000009"]}}})
        self.negativa(s, "toca evidence_ids")
        self.negativa(self.spec(patches={"CLAIM-000999": {"reason": "x", "set": {"notes": []}}}), "no existe")
        s = self.spec()
        del s["records"][0]["reason"]
        self.negativa(s, "@AB: sin `reason`")
        s = self.spec(records=[], patches={self.beta: {"reason": "x", "set": {"alias_ids": ["@NADA"]}}})
        self.negativa(s, "claves usadas sin definir: @NADA")
        s = self.spec(records=[], patches={self.beta: {"reason": "x", "set": {"alias_ids": ["CLADE-000999"]}}})
        self.negativa(s, "identificadores que no existen: CLADE-000999")

    def test_se_niega_con_deltas_pendientes_y_fuera_de_su_carpeta(self):
        self.guardar(self.construir(self.spec()))
        self.negativa(self.spec(), "hay deltas sin aplicar", nombre="otra")
        fuera = self.tmp / "suelto.json"
        fuera.write_text(json.dumps(self.spec()), encoding="utf-8")
        with self.assertRaises(SystemExit) as ctx, contextlib.redirect_stdout(io.StringIO()):
            editorial.construir(fuera)
        self.assertIn("tiene que estar en", str(ctx.exception))

    def test_el_snapshot_detecta_un_fichero_editorial_editado(self):
        c = self.construir(self.spec())
        self.assertEqual(self.aplicar(self.guardar(c)), 0)
        raiz = self.tmp / "raiz"
        (raiz / "knowledge").mkdir(parents=True)
        (raiz / "knowledge" / "deltas").symlink_to(self.tmp / "deltas")
        original = snapshot.ROOT
        snapshot.ROOT = raiz
        try:
            self.assertEqual(snapshot.conversiones_alteradas(), [])
            ruta = editorial.EDITORIALES / "prueba.json"
            ruta.write_text(ruta.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            self.assertTrue(any("prueba.json" in p for p in snapshot.conversiones_alteradas()))
        finally:
            snapshot.ROOT = original


if __name__ == "__main__":
    unittest.main()
