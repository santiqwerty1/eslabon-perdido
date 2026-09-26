#!/usr/bin/env python3
"""Pruebas de scripts/ingest/convertir.py sobre tests/fixtures/corredor-mini.

Todo ocurre en un directorio temporal: el dataset, las congelaciones, los deltas
y los registros se reapuntan a él, así que el libro mayor real no se toca.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "ingest"))
sys.path.insert(0, str(ROOT / "scripts" / "validate"))

import convertir  # noqa: E402
import corredor  # noqa: E402
import delta as delta_mod  # noqa: E402
import freeze  # noqa: E402
import ingest  # noqa: E402

MINI = ROOT / "tests" / "fixtures" / "corredor-mini"


class Entorno:
    """Un libro mayor vacío, con la sección 00 del fixture ya ingerida."""

    def __init__(self, tmp: Path):
        self.tmp = tmp
        self.records = tmp / "records"
        shutil.copytree(ROOT / "knowledge" / "records", self.records)
        for f in self.records.glob("*.jsonl"):
            f.write_text("", encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            freeze.cmd_create(argparse.Namespace(fuente=str(MINI), salida=str(tmp / "mini.json"), repositorio="x",
                                                 decision=None, sustituye=None, fecha="2026-09-25"))
        registro = json.loads((tmp / "mini.json").read_text(encoding="utf-8"))
        self.huella = registro["fingerprint"]
        (tmp / "dataset.json").write_text(json.dumps({
            "dataset_revision": "REV-000000",
            "corpus_freeze": {"path": str(tmp / "mini.json"), "fingerprint": self.huella}}), encoding="utf-8")
        self.parches = {
            (ingest, "MANIFEST"): tmp / "dataset.json",
            (ingest, "DELTAS"): tmp / "deltas",
            (ingest, "SECTIONS"): tmp / "sections",
            (ingest, "PASSAGES"): tmp / "passages",
            (ingest, "REPORTS"): tmp / "reports",
            (ingest, "RECORDS"): self.records,
            (delta_mod, "RECORDS"): self.records,
        }

    def __enter__(self):
        self.originales = {k: getattr(*k) for k in self.parches}
        for (mod, nombre), valor in self.parches.items():
            setattr(mod, nombre, valor)
        with contextlib.redirect_stdout(io.StringIO()):
            corredor.ingerir(str(MINI), "00", None, False)
        self.delta_sec = json.loads((self.tmp / "deltas" / "SEC-000001.json").read_text(encoding="utf-8"))
        self.etiquetas = sorted({op["after"]["original_text"] for op in self.delta_sec["operations"]
                                 if op["file"] == "mentions.jsonl"})
        return self

    def __exit__(self, *exc):
        for (mod, nombre), valor in self.originales.items():
            setattr(mod, nombre, valor)

    def spec(self, **cambios) -> dict:
        s = {
            "freeze": {"version": "x", "fingerprint": self.huella},
            "section": "00",
            "decision": "DEC-057",
            "records": [
                {"key": "@Alfa", "file": "clades.jsonl", "rows": ["C-001"],
                 "record": {"preferred_label": "FIX-Alfa", "description": "Clado de prueba."}},
                {"key": "@Beta", "file": "clades.jsonl", "rows": ["C-001"],
                 "record": {"preferred_label": "FIX-Beta", "description": "Clado de prueba."}},
                {"key": "@CL1", "file": "claims.jsonl", "rows": ["C-001"],
                 "record": {"claim_type": "relational", "subject_id": "@Alfa", "predicate": "sister_group_of",
                            "object": {"entity_id": "@Beta"}}},
                {"key": "@EV1", "file": "evidence.jsonl", "rows": ["C-001"],
                 "record": {"evidence_type": "molecular", "description": "Lo dice el resumen.",
                            "source_id": "@S01", "locator": "resumen",
                            "supports_claim_ids": ["@CL1"], "challenges_claim_ids": []}},
            ],
            "rows": {"C-001": {"destination": "B", "keys": ["@CL1", "@EV1", "@Alfa", "@Beta"]},
                     **{f"C-00{n}": {"destination": "H", "keys": [], "note": "fuera de la prueba"} for n in range(2, 6)}},
            "mentions": {e: {"mention_type": "unresolved", "disposition": "discarded_with_reason", "targets": [],
                             "reason": "fuera de la prueba"} for e in self.etiquetas},
        }
        s["mentions"]["FIX-Alfa"] = {"mention_type": "clade", "disposition": "new_entity",
                                     "targets": ["@Alfa"], "reason": "clado de la prueba"}
        s.update(cambios)
        return s

    def construir(self, spec: dict) -> dict:
        ruta = self.tmp / "spec.json"
        ruta.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            return convertir.construir(ruta, str(MINI))


class Convertir(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.entorno = Entorno(Path(self._tmp.name)).__enter__()

    def tearDown(self):
        self.entorno.__exit__(None, None, None)
        self._tmp.cleanup()

    def registros(self, r: dict) -> dict[str, dict]:
        return {rec["id"]: rec for _, rec in r["salida"]}

    def test_la_fila_se_convierte_con_su_procedencia_y_sus_ejes(self):
        r = self.entorno.construir(self.entorno.spec())
        recs = self.registros(r)
        [claim] = [c for c in recs.values() if c["id"].startswith("CLAIM-")]
        self.assertEqual(claim["provenance"]["passage_ids"],
                         self.entorno.delta_sec["corpus_origin"]["rows"]["C-001"]["passage_ids"])
        self.assertEqual(claim["provenance"]["section_ids"], ["SEC-000001"])
        self.assertEqual(claim["epistemic_dimensions"]["evidence_strength"], "medium")
        self.assertEqual(claim["epistemic_dimensions"]["evidence_strength_reason"], "Lo dice el resumen.")
        [ev] = [e for e in recs.values() if e["id"].startswith("EVID-")]
        self.assertEqual(claim["evidence_ids"], [ev["id"]])
        [fuente] = [s for s in recs.values() if s["id"].startswith("SRC-")]
        self.assertEqual((fuente["citation_key"], fuente["doi"]), ("S01", "https://doi.org/10.0000/fixture.1"))
        alfa = next(e for e in recs.values() if e.get("preferred_label") == "FIX-Alfa")
        self.assertEqual((alfa["entity_type"], alfa["claim_ids"]), ("clade", [claim["id"]]))

    def test_toda_mencion_recibe_su_destino(self):
        r = self.entorno.construir(self.entorno.spec())
        self.assertEqual(len(r["actualizadas"]), len(self.entorno.etiquetas))
        despues = {d["original_text"]: d for _, d in r["actualizadas"]}
        alfa = next(e["id"] for e in self.registros(r).values() if e.get("preferred_label") == "FIX-Alfa")
        self.assertEqual(despues["FIX-Alfa"]["disposition"], "new_entity")
        self.assertEqual(despues["FIX-Alfa"]["resolution"]["target_ids"], [alfa])

    def test_los_registros_validan_contra_los_esquemas(self):
        try:
            import jsonschema  # noqa: F401
        except ImportError:
            self.skipTest("jsonschema no instalado")
        import validate
        r = self.entorno.construir(self.entorno.spec())
        delta_mod.apply_ops(self.entorno.delta_sec["operations"])
        delta_mod.apply_ops(r["delta"]["operations"])
        rep = validate.run(["schema", "references", "coverage", "provenance"], self.entorno.records)
        self.assertEqual(rep.errors, [])

    def test_una_fila_sin_destino_se_rechaza(self):
        spec = self.entorno.spec()
        del spec["rows"]["C-005"]
        with self.assertRaises(SystemExit) as e:
            self.entorno.construir(spec)
        self.assertIn("filas sin destino: C-005", str(e.exception))

    def test_una_mencion_sin_destino_se_rechaza(self):
        spec = self.entorno.spec()
        del spec["mentions"]["FIX-Beta"]
        with self.assertRaises(SystemExit) as e:
            self.entorno.construir(spec)
        self.assertIn("menciones sin destino: FIX-Beta", str(e.exception))

    def test_una_clave_sin_definir_se_rechaza(self):
        spec = self.entorno.spec()
        spec["records"][2]["record"]["object"]["entity_id"] = "@Gamma"
        with self.assertRaises(SystemExit) as e:
            self.entorno.construir(spec)
        self.assertIn("@Gamma", str(e.exception))

    def test_otra_version_del_corpus_se_rechaza(self):
        spec = self.entorno.spec(freeze={"version": "x", "fingerprint": "sha256:" + "0" * 64})
        with self.assertRaises(SystemExit) as e:
            self.entorno.construir(spec)
        self.assertIn("otra versión", str(e.exception))

    def test_una_seccion_sin_ingerir_no_se_convierte(self):
        with self.assertRaises(SystemExit) as e:
            self.entorno.construir(self.entorno.spec(section="01"))
        self.assertIn("no se ha ingerido", str(e.exception))

    def test_una_fuente_que_ya_existe_se_reutiliza(self):
        (self.entorno.records / "sources.jsonl").write_text(json.dumps({
            "id": "SRC-000007", "citation_key": "S01", "title": "Trabajo ficticio uno",
            "source_type": "primary_research", "verification_status": "pending_verification",
            "record_status": "active"}) + "\n", encoding="utf-8")
        r = self.entorno.construir(self.entorno.spec())
        recs = self.registros(r)
        self.assertFalse([s for s in recs if s.startswith("SRC-")])
        [claim] = [c for c in recs.values() if c["id"].startswith("CLAIM-")]
        self.assertEqual(claim["provenance"]["source_ids"], ["SRC-000007"])

    def test_una_seccion_no_se_convierte_dos_veces(self):
        r = self.entorno.construir(self.entorno.spec())
        (self.entorno.tmp / "deltas" / "SEC-000001-conversion.json").write_text(
            json.dumps(r["delta"]), encoding="utf-8")
        with self.assertRaises(SystemExit) as e:
            self.entorno.construir(self.entorno.spec())
        self.assertIn("ya se convirtió", str(e.exception))

    def test_la_conversion_va_detras_del_delta_de_la_seccion(self):
        r = self.entorno.construir(self.entorno.spec())
        self.assertEqual(r["rev"], ("REV-000001", "REV-000002"))
        self.assertEqual(r["pendientes"], ["SEC-000001.json"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
