#!/usr/bin/env python3
"""Pruebas de scripts/ingest/convertir.py sobre tests/fixtures/corredor-mini.

Todo ocurre en un directorio temporal: el dataset, las congelaciones, los deltas
y los registros se reapuntan a él, así que el libro mayor real no se toca.
"""

from __future__ import annotations

import argparse
import contextlib
import csv
import importlib.util
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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
            (convertir, "VIEWS"): tmp / "views",
            (delta_mod, "RECORDS"): self.records,
            (delta_mod, "MANIFEST"): tmp / "dataset.json",
            (delta_mod, "DELTAS"): tmp / "deltas",
            (delta_mod, "HISTORIAL"): tmp / "deltas" / "historial.jsonl",
            (convertir, "CONVERSIONS"): tmp,
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


# convertir.py no escribe un delta sin validarlo contra los esquemas: sin
# jsonschema se niega, así que sus pruebas lo necesitan (la CI lo instala).
@unittest.skipUnless(importlib.util.find_spec("jsonschema"), "convertir.py exige jsonschema")
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

    def fuente_del_apendice(self, clave: str) -> dict:
        with (MINI / "data" / "apendices" / "A_fuentes.csv").open(encoding="utf-8", newline="") as fh:
            filas = list(csv.DictReader(fh))
        col_doi = next(c for c in filas[0] if c.strip().lower().startswith("doi"))
        return convertir.fuente_de_apendice(next(f for f in filas if f["clave"].strip() == clave), col_doi)

    def test_una_fuente_que_ya_existe_se_reutiliza(self):
        (self.entorno.records / "sources.jsonl").write_text(json.dumps({
            "id": "SRC-000007", **self.fuente_del_apendice("S01")}) + "\n", encoding="utf-8")
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

    def test_un_id_en_el_fichero_de_conversion_se_rechaza(self):
        spec = self.entorno.spec()
        spec["records"][0]["record"]["id"] = "CLADE-000001"
        with self.assertRaises(SystemExit) as e:
            self.entorno.construir(spec)
        self.assertIn("@Alfa", str(e.exception))
        self.assertIn("id", str(e.exception))

    def test_una_procedencia_en_el_fichero_de_conversion_se_rechaza(self):
        # La procedencia se deduce de las filas del registro; una copiada a mano
        # podría señalar otra sección u otros pasajes que los de sus filas.
        spec = self.entorno.spec()
        spec["records"][2]["record"]["provenance"] = {
            "section_ids": ["SEC-000001"], "passage_ids": [], "source_ids": [], "operation_id": None,
            "dataset_revision": "REV-000002", "origin": "ingestion"}
        with self.assertRaises(SystemExit) as e:
            self.entorno.construir(spec)
        self.assertIn("@CL1", str(e.exception))
        self.assertIn("provenance", str(e.exception))

    def test_un_identificador_literal_que_no_existe_se_rechaza(self):
        spec = self.entorno.spec()
        spec["records"][2]["record"]["object"]["entity_id"] = "CLADE-999999"
        with self.assertRaises(SystemExit) as e:
            self.entorno.construir(spec)
        self.assertIn("CLADE-999999", str(e.exception))

    def test_los_registros_existentes_reciben_sus_enlaces_de_vuelta(self):
        # Una sección posterior afirma algo de una entidad que ya existe y
        # respalda una afirmación que ya existe: las dos tienen que enlazarlo.
        (self.entorno.records / "clades.jsonl").write_text(json.dumps({
            "id": "CLADE-000050", "entity_type": "clade", "preferred_label": "FIX-Previo",
            "claim_ids": [], "first_introduced_in": None, "record_status": "active"}) + "\n", encoding="utf-8")
        (self.entorno.records / "claims.jsonl").write_text(json.dumps({
            "id": "CLAIM-000050", "claim_type": "relational", "subject_id": "CLADE-000050",
            "predicate": "member_of", "object": {"entity_id": "CLADE-000050"}, "evidence_ids": [],
            "counterevidence_ids": [], "record_status": "active"}) + "\n", encoding="utf-8")
        spec = self.entorno.spec()
        spec["records"][2]["record"]["object"]["entity_id"] = "CLADE-000050"
        spec["records"][3]["record"]["supports_claim_ids"] = ["@CL1", "CLAIM-000050"]
        r = self.entorno.construir(spec)
        nuevas = {op["record_id"]: op for op in r["delta"]["operations"] if op["operation"] == "UPDATE_RECORD"}
        [claim] = [rec["id"] for _, rec in r["salida"] if rec["id"].startswith("CLAIM-")]
        [ev] = [rec["id"] for _, rec in r["salida"] if rec["id"].startswith("EVID-")]
        self.assertEqual(nuevas["CLADE-000050"]["after"]["claim_ids"], [claim])
        self.assertEqual(nuevas["CLADE-000050"]["before"]["claim_ids"], [])
        self.assertEqual(nuevas["CLAIM-000050"]["after"]["evidence_ids"], [ev])

    def test_el_delta_de_la_seccion_tiene_que_ser_de_la_version_congelada(self):
        ruta = self.entorno.tmp / "deltas" / "SEC-000001.json"
        d = json.loads(ruta.read_text(encoding="utf-8"))
        d["corpus_origin"]["freeze"]["fingerprint"] = "sha256:" + "1" * 64
        ruta.write_text(json.dumps(d), encoding="utf-8")
        with self.assertRaises(SystemExit) as e:
            self.entorno.construir(self.entorno.spec())
        self.assertIn("otra versión", str(e.exception))

    def test_una_conversion_revertida_no_se_sobrescribe(self):
        deltas = self.entorno.tmp / "deltas"
        ruta = self.entorno.tmp / "spec.json"
        ruta.write_text(json.dumps(self.entorno.spec(), ensure_ascii=False), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            convertir.convertir(ruta, str(MINI), False)
        primera = (deltas / "SEC-000001-conversion.json").read_bytes()
        (deltas / "historial.jsonl").write_text(json.dumps(
            {"delta": "SEC-000001-conversion.json", "accion": "revertir", "revision": "REV-000001"}) + "\n",
            encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            convertir.convertir(ruta, str(MINI), False)
        self.assertEqual((deltas / "SEC-000001-conversion.json").read_bytes(), primera)
        segunda = json.loads((deltas / "SEC-000001-conversion-2.json").read_text(encoding="utf-8"))
        # Los identificadores del revertido siguen reservados.
        reservados = set(json.loads(primera)["records_added"])
        self.assertFalse(reservados & set(segunda["records_added"]))

    def test_los_enlaces_de_vuelta_parten_de_las_actualizaciones_pendientes(self):
        # Otra conversión sin aplicar ya añadió evidencia a CLAIM-000050: la
        # nueva tiene que partir de ese estado, o al aplicar la cadena lo pisaría.
        base_claim = {"id": "CLAIM-000050", "claim_type": "relational", "subject_id": "CLAIM-000050",
                      "predicate": "member_of", "object": {"entity_id": "CLAIM-000050"}, "evidence_ids": [],
                      "counterevidence_ids": [], "record_status": "active"}
        (self.entorno.records / "claims.jsonl").write_text(json.dumps(base_claim) + "\n", encoding="utf-8")
        (self.entorno.tmp / "deltas" / "SEC-000009-conversion.json").write_text(json.dumps({
            "dataset_revision_before": "REV-000001", "dataset_revision_after": "REV-000002",
            "records_added": ["EVID-000900"],
            "operations": [
                {"operation": "ADD_RECORD", "file": "evidence.jsonl", "record_id": "EVID-000900",
                 "before": None, "after": {"id": "EVID-000900"}},
                {"operation": "UPDATE_RECORD", "file": "claims.jsonl", "record_id": "CLAIM-000050",
                 "before": base_claim, "after": {**base_claim, "evidence_ids": ["EVID-000900"]}}]}),
            encoding="utf-8")
        spec = self.entorno.spec()
        spec["records"][3]["record"]["supports_claim_ids"] = ["@CL1", "CLAIM-000050"]
        r = self.entorno.construir(spec)
        [op] = [o for o in r["delta"]["operations"] if o["record_id"] == "CLAIM-000050"]
        [ev] = [rec["id"] for _, rec in r["salida"] if rec["id"].startswith("EVID-")]
        self.assertEqual(op["before"]["evidence_ids"], ["EVID-000900"])
        self.assertEqual(op["after"]["evidence_ids"], ["EVID-000900", ev])

    def test_los_pendientes_se_listan_en_el_orden_de_la_cadena(self):
        ruta = self.entorno.tmp / "spec.json"
        ruta.write_text(json.dumps(self.entorno.spec(), ensure_ascii=False), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            convertir.convertir(ruta, str(MINI), False)
        _, _, pendientes = ingest.revision_siguiente({"dataset_revision": "REV-000000"})
        self.assertEqual(pendientes, ["SEC-000001.json", "SEC-000001-conversion.json"])

    def test_una_vista_existente_se_puede_citar(self):
        vistas = self.entorno.tmp / "views"
        vistas.mkdir()
        (vistas / "classification-views.jsonl").write_text(json.dumps({"id": "TAXVIEW-000001"}) + "\n",
                                                          encoding="utf-8")
        spec = self.entorno.spec()
        spec["records"][2]["record"]["scope"] = {"classification_view_ids": ["TAXVIEW-000001"]}
        r = self.entorno.construir(spec)
        [claim] = [rec for _, rec in r["salida"] if rec["id"].startswith("CLAIM-")]
        self.assertEqual(claim["scope"]["classification_view_ids"], ["TAXVIEW-000001"])

    def test_un_registro_sin_fila_de_origen_se_rechaza(self):
        spec = self.entorno.spec()
        spec["records"][0]["rows"] = []
        with self.assertRaises(SystemExit) as e:
            self.entorno.construir(spec)
        self.assertIn("@Alfa", str(e.exception))
        self.assertIn("fila", str(e.exception))

    def test_un_destino_fuera_del_vocabulario_se_rechaza(self):
        spec = self.entorno.spec()
        spec["rows"]["C-001"]["destination"] = "Z"
        with self.assertRaises(SystemExit) as e:
            self.entorno.construir(spec)
        self.assertIn("C-001", str(e.exception))
        self.assertIn("Z", str(e.exception))

    def contraevidencia(self, spec: dict, afirmaciones: list[str], fichero: str = "evidence.jsonl") -> dict:
        """La fila C-002 pasa a J: una evidencia de S02 que cuestiona `afirmaciones`."""
        registro = {"evidence_type": "morphological", "description": "Otra lectura.", "source_id": "@S02",
                    "locator": "resultados", "supports_claim_ids": [], "challenges_claim_ids": afirmaciones}
        if fichero != "evidence.jsonl":
            registro = {"preferred_label": "FIX-Gamma", "description": "No es una evidencia."}
        spec["records"].append({"key": "@EVJ", "file": fichero, "rows": ["C-002"], "record": registro})
        spec["rows"]["C-002"] = {"destination": "J", "keys": ["@EVJ"]}
        return spec

    def test_una_fila_J_registra_contraevidencia_de_otra_fila(self):
        r = self.entorno.construir(self.contraevidencia(self.entorno.spec(), ["@CL1"]))
        recs = self.registros(r)
        [claim] = [c for c in recs.values() if c["id"].startswith("CLAIM-")]
        [ev] = [e for e in recs.values() if e["id"].startswith("EVID-") and e["challenges_claim_ids"]]
        self.assertEqual(claim["counterevidence_ids"], [ev["id"]])
        self.assertEqual(r["delta"]["conversion"]["rows"]["C-002"]["destination"], "J")

    def test_una_fila_J_sobre_una_afirmacion_existente_la_enlaza(self):
        existente = {"id": "CLAIM-000050", "claim_type": "relational", "subject_id": "CLADE-000050",
                     "predicate": "sister_group_of", "object": {"entity_id": "CLADE-000051"},
                     "evidence_ids": [], "counterevidence_ids": [], "record_status": "active"}
        (self.entorno.records / "claims.jsonl").write_text(json.dumps(existente) + "\n", encoding="utf-8")
        r = self.entorno.construir(self.contraevidencia(self.entorno.spec(), ["CLAIM-000050"]))
        [ev] = [e["id"] for _, e in r["salida"] if e["id"].startswith("EVID-") and e["challenges_claim_ids"]]
        [op] = [o for o in r["delta"]["operations"] if o["record_id"] == "CLAIM-000050"]
        self.assertEqual(op["after"]["counterevidence_ids"], [ev])

    def test_una_fila_J_con_un_registro_que_no_es_evidencia_se_rechaza(self):
        with self.assertRaises(SystemExit) as e:
            self.entorno.construir(self.contraevidencia(self.entorno.spec(), ["@CL1"], fichero="clades.jsonl"))
        self.assertIn("C-002", str(e.exception))
        self.assertIn("@EVJ", str(e.exception))

    def test_una_fila_J_sin_afirmacion_de_otra_fila_se_rechaza(self):
        # Cuestionar una afirmación que sale de la propia fila no es
        # contraevidencia de otra fila: sería una afirmación con su evidencia.
        spec = self.contraevidencia(self.entorno.spec(), ["@CLJ"])
        spec["records"].append({"key": "@CLJ", "file": "claims.jsonl", "rows": ["C-002"], "record": {
            "claim_type": "relational", "subject_id": "@Alfa", "predicate": "sister_group_of",
            "object": {"entity_id": "@Beta"}}})
        with self.assertRaises(SystemExit) as e:
            self.entorno.construir(spec)
        self.assertIn("C-002", str(e.exception))
        self.assertIn("@CLJ", str(e.exception))

    def test_una_fila_J_sin_afirmaciones_se_rechaza(self):
        with self.assertRaises(SystemExit) as e:
            self.entorno.construir(self.contraevidencia(self.entorno.spec(), []))
        self.assertIn("@EVJ", str(e.exception))

    def ocurrencia(self, spec: dict, fecha_propia: str | None) -> dict:
        """Una ocurrencia de @Alfa y una afirmación `dated_to` que la fecha."""
        occ = {"entity_id": "@Alfa", "location_precision": "unknown", "evidence_basis": "observed",
               "notes": []}
        if fecha_propia is not None:
            occ["temporal_expression_id"] = fecha_propia
        tiempo = self.tiempo(1000, 900)
        tiempo.update({"temporal_type": "occurrence_date", "determination": "observed", "method_type": "other",
                       "calibration": {"system": "geological_timescale", "curve_or_timescale": None}})
        spec["records"] += [
            {"key": "@TO", "file": "temporal-expressions.jsonl", "rows": ["C-001"], "record": tiempo},
            {"key": "@OCC", "file": "occurrences.jsonl", "rows": ["C-001"], "record": occ},
            {"key": "@CLO", "file": "claims.jsonl", "rows": ["C-001"], "record": {
                "claim_type": "temporal", "subject_id": "@OCC", "predicate": "dated_to",
                "object": {"temporal_expression_id": "@TO"}}},
        ]
        spec["rows"]["C-001"]["keys"] += ["@TO", "@OCC", "@CLO"]
        return spec

    def test_la_fecha_de_una_ocurrencia_se_deduce_de_su_datacion(self):
        r = self.entorno.construir(self.ocurrencia(self.entorno.spec(), None))
        recs = self.registros(r)
        [occ] = [x for x in recs.values() if x["id"].startswith("OCC-")]
        [t] = [x for x in recs.values() if x["id"].startswith("TIME-")]
        self.assertEqual(occ["temporal_expression_id"], t["id"])

    def test_la_fecha_de_una_ocurrencia_que_no_sale_de_su_datacion_se_rechaza(self):
        spec = self.ocurrencia(self.entorno.spec(), "@T2")
        spec["records"].append({"key": "@T2", "file": "temporal-expressions.jsonl", "rows": ["C-001"],
                                "record": self.tiempo(800, 700)})
        spec["rows"]["C-001"]["keys"].append("@T2")
        with self.assertRaises(SystemExit) as e:
            self.entorno.construir(spec)
        self.assertIn("@OCC", str(e.exception))
        self.assertIn("temporal_expression_id", str(e.exception))

    def ocurrencia_existente(self, fecha: str | None) -> dict:
        occ = {"id": "OCC-000050", "entity_id": "CLADE-000050", "temporal_expression_id": fecha,
               "location_precision": "unknown", "evidence_basis": "observed", "record_status": "active"}
        (self.entorno.records / "occurrences.jsonl").write_text(json.dumps(occ) + "\n", encoding="utf-8")
        spec = self.ocurrencia(self.entorno.spec(), None)
        spec["records"] = [r for r in spec["records"] if r["key"] != "@OCC"]
        spec["rows"]["C-001"]["keys"].remove("@OCC")
        spec["records"][-1]["record"]["subject_id"] = "OCC-000050"
        return spec

    def test_la_datacion_de_una_ocurrencia_existente_la_fecha(self):
        r = self.entorno.construir(self.ocurrencia_existente(None))
        [t] = [x["id"] for _, x in r["salida"] if x["id"].startswith("TIME-")]
        [op] = [o for o in r["delta"]["operations"] if o["record_id"] == "OCC-000050"]
        self.assertEqual(op["after"]["temporal_expression_id"], t)

    def test_una_datacion_nueva_de_una_ocurrencia_fechada_no_la_cambia(self):
        # Otra fuente la data distinto: es una afirmación que compite, no una
        # razón para rehacer la ocurrencia ni para negarse.
        r = self.entorno.construir(self.ocurrencia_existente("TIME-000050"))
        [op] = [o for o in r["delta"]["operations"] if o["record_id"] == "OCC-000050"]
        self.assertEqual(op["after"]["temporal_expression_id"], "TIME-000050")  # sólo gana el enlace a la afirmación
        [claim] = [x for _, x in r["salida"] if x.get("subject_id") == "OCC-000050"]
        self.assertEqual(claim["predicate"], "dated_to")

    def dos_dataciones(self, fija: str | None) -> dict:
        spec = self.ocurrencia(self.entorno.spec(), fija)
        spec["records"] += [
            {"key": "@T2", "file": "temporal-expressions.jsonl", "rows": ["C-001"], "record": self.tiempo(800, 700)},
            {"key": "@CLO2", "file": "claims.jsonl", "rows": ["C-001"], "record": {
                "claim_type": "temporal", "subject_id": "@OCC", "predicate": "dated_to",
                "object": {"temporal_expression_id": "@T2"}}}]
        spec["rows"]["C-001"]["keys"] += ["@T2", "@CLO2"]
        return spec

    def test_dos_dataciones_de_una_ocurrencia_exigen_elegir_su_fecha(self):
        with self.assertRaises(SystemExit) as e:
            self.entorno.construir(self.dos_dataciones(None))
        self.assertIn("@OCC", str(e.exception))
        self.assertIn("temporal_expression_id", str(e.exception))

    def test_dos_dataciones_que_compiten_conviven_si_se_elige_la_fecha(self):
        r = self.entorno.construir(self.dos_dataciones("@T2"))
        recs = self.registros(r)
        [occ] = [x for x in recs.values() if x["id"].startswith("OCC-")]
        fechas = [c["object"]["temporal_expression_id"] for c in recs.values()
                  if c.get("predicate") == "dated_to" and c.get("subject_id") == occ["id"]]
        self.assertEqual(len(fechas), 2)
        # La elegida es @T2, la segunda: no se pisa con la primera.
        t2 = next(x["id"] for x in recs.values() if x["id"].startswith("TIME-")
                  and (x.get("interval") or {}).get("oldest_bound") == 800)
        self.assertEqual(occ["temporal_expression_id"], t2)

    def test_una_evidencia_J_con_listas_nulas_da_un_error_legible(self):
        spec = self.contraevidencia(self.entorno.spec(), ["@CL1"])
        spec["records"][-1]["record"]["supports_claim_ids"] = None
        with self.assertRaises(SystemExit):
            self.entorno.construir(spec)

    def test_una_mencion_resuelta_sin_destino_se_rechaza(self):
        spec = self.entorno.spec()
        spec["mentions"]["FIX-Alfa"]["targets"] = []
        with self.assertRaises(SystemExit) as e:
            self.entorno.construir(spec)
        self.assertIn("FIX-Alfa", str(e.exception))

    def test_una_fuente_que_difiere_del_apendice_se_rechaza(self):
        # La versión activa del apéndice corrigió la referencia: reutilizar la
        # fuente vieja haría citar datos que el corpus congelado ya no dice.
        (self.entorno.records / "sources.jsonl").write_text(json.dumps({
            "id": "SRC-000007", **self.fuente_del_apendice("S01"),
            "title": "Un título que el apéndice no tiene"}) + "\n", encoding="utf-8")
        with self.assertRaises(SystemExit) as e:
            self.entorno.construir(self.entorno.spec())
        self.assertIn("SRC-000007", str(e.exception))
        self.assertIn("title", str(e.exception))

    def test_delta_no_se_revierte_fuera_del_orden_de_la_cadena(self):
        ruta = self.entorno.tmp / "spec.json"
        ruta.write_text(json.dumps(self.entorno.spec(), ensure_ascii=False), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            convertir.convertir(ruta, str(MINI), False)
        deltas = self.entorno.tmp / "deltas"
        with contextlib.redirect_stdout(io.StringIO()):
            # Aplicar la conversión antes que la sección tampoco vale.
            self.assertEqual(delta_mod.cmd(deltas / "SEC-000001-conversion.json", False, False), 1)
            self.assertEqual(delta_mod.cmd(deltas / "SEC-000001.json", False, False), 0)
            self.assertEqual(delta_mod.cmd(deltas / "SEC-000001-conversion.json", False, False), 0)
            antes = {f.name: f.read_bytes() for f in self.entorno.records.glob("*.jsonl")}
            salida = io.StringIO()
            with contextlib.redirect_stdout(salida):
                self.assertEqual(delta_mod.cmd(deltas / "SEC-000001.json", True, False), 1)
            self.assertIn("SEC-000001-conversion.json", salida.getvalue())
            self.assertEqual({f.name: f.read_bytes() for f in self.entorno.records.glob("*.jsonl")}, antes)
            self.assertEqual(delta_mod.cmd(deltas / "SEC-000001-conversion.json", True, False), 0)
            self.assertEqual(delta_mod.cmd(deltas / "SEC-000001.json", True, False), 0)
        self.assertEqual(json.loads((self.entorno.tmp / "dataset.json").read_text(encoding="utf-8"))
                         ["dataset_revision"], "REV-000000")

    def test_delta_solo_revierte_el_ultimo_aplicado(self):
        # Revertir y reintentar deja dos conversiones con la misma revisión:
        # la vieja no se puede revertir encima de la nueva.
        ruta = self.entorno.tmp / "spec.json"
        ruta.write_text(json.dumps(self.entorno.spec(), ensure_ascii=False), encoding="utf-8")
        deltas = self.entorno.tmp / "deltas"
        with contextlib.redirect_stdout(io.StringIO()):
            convertir.convertir(ruta, str(MINI), False)
            self.assertEqual(delta_mod.cmd(deltas / "SEC-000001.json", False, False), 0)
            self.assertEqual(delta_mod.cmd(deltas / "SEC-000001-conversion.json", False, False), 0)
            self.assertEqual(delta_mod.cmd(deltas / "SEC-000001-conversion.json", True, False), 0)
            convertir.convertir(ruta, str(MINI), False)
            self.assertEqual(delta_mod.cmd(deltas / "SEC-000001-conversion-2.json", False, False), 0)
            antes = {f.name: f.read_bytes() for f in self.entorno.records.glob("*.jsonl")}
            salida = io.StringIO()
            with contextlib.redirect_stdout(salida):
                self.assertEqual(delta_mod.cmd(deltas / "SEC-000001-conversion.json", True, False), 1)
            self.assertIn("SEC-000001-conversion-2.json", salida.getvalue())
            self.assertEqual({f.name: f.read_bytes() for f in self.entorno.records.glob("*.jsonl")}, antes)
            self.assertEqual(delta_mod.cmd(deltas / "SEC-000001-conversion-2.json", True, False), 0)

    def test_delta_en_seco_comprueba_el_orden(self):
        # El ensayo es el paso previo documentado: tiene que negarse igual que
        # la orden de verdad.
        ruta = self.entorno.tmp / "spec.json"
        ruta.write_text(json.dumps(self.entorno.spec(), ensure_ascii=False), encoding="utf-8")
        deltas = self.entorno.tmp / "deltas"
        with contextlib.redirect_stdout(io.StringIO()):
            convertir.convertir(ruta, str(MINI), False)
            self.assertEqual(delta_mod.cmd(deltas / "SEC-000001-conversion.json", False, True), 1)
            self.assertEqual(delta_mod.cmd(deltas / "SEC-000001.json", False, True), 0)
            self.assertEqual(delta_mod.cmd(deltas / "SEC-000001.json", False, False), 0)
            self.assertEqual(delta_mod.cmd(deltas / "SEC-000001.json", False, True), 1)
            self.assertEqual(delta_mod.cmd(deltas / "SEC-000001-conversion.json", False, False), 0)
            self.assertEqual(delta_mod.cmd(deltas / "SEC-000001-conversion.json", True, True), 0)
            self.assertEqual(delta_mod.cmd(deltas / "SEC-000001.json", True, True), 1)

    def test_delta_solo_revierte_el_fichero_que_se_aplico(self):
        # Una copia con el mismo nombre, o el mismo fichero editado después de
        # aplicarlo, no es el delta que el historial registró.
        deltas = self.entorno.tmp / "deltas"
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(delta_mod.cmd(deltas / "SEC-000001.json", False, False), 0)
            copia = self.entorno.tmp / "otra" / "SEC-000001.json"
            copia.parent.mkdir()
            shutil.copy(deltas / "SEC-000001.json", copia)
            self.assertEqual(delta_mod.cmd(copia, True, False), 1)
            original = (deltas / "SEC-000001.json").read_bytes()
            d = json.loads(original)
            d["operations"][0]["before"] = {"id": d["operations"][0]["record_id"], "inventado": True}
            (deltas / "SEC-000001.json").write_text(json.dumps(d), encoding="utf-8")
            salida = io.StringIO()
            with contextlib.redirect_stdout(salida):
                self.assertEqual(delta_mod.cmd(deltas / "SEC-000001.json", True, False), 1)
            self.assertIn("cambió", salida.getvalue())
            (deltas / "SEC-000001.json").write_bytes(original)
            self.assertEqual(delta_mod.cmd(deltas / "SEC-000001.json", True, False), 0)

    def test_la_seccion_de_introduccion_no_se_fija_en_el_fichero(self):
        spec = self.entorno.spec()
        spec["records"][0]["record"]["first_introduced_in"] = "SEC-000001"
        with self.assertRaises(SystemExit) as e:
            self.entorno.construir(spec)
        self.assertIn("@Alfa", str(e.exception))
        self.assertIn("first_introduced_in", str(e.exception))

    def test_delta_no_revierte_sin_la_huella_de_cuando_se_aplico(self):
        deltas = self.entorno.tmp / "deltas"
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(delta_mod.cmd(deltas / "SEC-000001.json", False, False), 0)
        historial = deltas / "historial.jsonl"
        entradas = [json.loads(l) for l in historial.read_text(encoding="utf-8").splitlines()]
        self.assertTrue(entradas[-1]["sha256"].startswith("sha256:"))
        del entradas[-1]["sha256"]
        historial.write_text("".join(json.dumps(e) + "\n" for e in entradas), encoding="utf-8")
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            self.assertEqual(delta_mod.cmd(deltas / "SEC-000001.json", True, False), 1)
        self.assertIn("huella", salida.getvalue())

    def test_las_fuentes_del_registro_no_se_fijan_en_el_fichero(self):
        spec = self.entorno.spec()
        spec["records"][3]["record"]["source_ids"] = ["@S01"]
        with self.assertRaises(SystemExit) as e:
            self.entorno.construir(spec)
        self.assertIn("@EV1", str(e.exception))
        self.assertIn("source_ids", str(e.exception))

    def test_delta_no_revierte_con_deltas_pendientes_detras(self):
        # La conversión generada y sin aplicar parte de la revisión que deja la
        # sección: revertir la sección la dejaría colgando de una que no existe.
        ruta = self.entorno.tmp / "spec.json"
        ruta.write_text(json.dumps(self.entorno.spec(), ensure_ascii=False), encoding="utf-8")
        deltas = self.entorno.tmp / "deltas"
        with contextlib.redirect_stdout(io.StringIO()):
            convertir.convertir(ruta, str(MINI), False)
            self.assertEqual(delta_mod.cmd(deltas / "SEC-000001.json", False, False), 0)
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            self.assertEqual(delta_mod.cmd(deltas / "SEC-000001.json", True, False), 1)
        self.assertIn("SEC-000001-conversion.json", salida.getvalue())

    def test_la_fuente_de_una_evidencia_tiene_que_estar_en_su_procedencia(self):
        # La evidencia dice venir de S01 y su procedencia, de S02: una de las
        # dos atribuciones es falsa.
        spec = self.entorno.spec()
        spec["records"][3]["sources"] = ["S02"]
        with self.assertRaises(SystemExit) as e:
            self.entorno.construir(spec)
        self.assertIn("@EV1", str(e.exception))
        self.assertIn("source_id", str(e.exception))

    def test_los_campos_deducidos_no_se_fijan_en_el_fichero(self):
        # Cada uno de estos lo deduce convertir.py; escrito a mano podría
        # contradecir el fichero de destino, los enlaces o el ciclo de vida.
        casos = [
            (0, "entity_type", "technology"),
            (0, "claim_ids", ["@CL1"]),
            (0, "record_status", "deprecated"),
            (2, "evidence_ids", ["@EV1"]),
            (2, "counterevidence_ids", []),
            (2, "epistemic_dimensions", {}),
        ]
        for i, campo, valor in casos:
            with self.subTest(campo=campo):
                spec = self.entorno.spec()
                spec["records"][i]["record"][campo] = valor
                with self.assertRaises(SystemExit) as e:
                    self.entorno.construir(spec)
                self.assertIn(spec["records"][i]["key"], str(e.exception))
                self.assertIn(campo, str(e.exception))

    def test_una_mencion_descartada_sin_razon_se_rechaza(self):
        spec = self.entorno.spec()
        etiqueta = next(e for e, d in spec["mentions"].items() if d["disposition"] == "discarded_with_reason")
        del spec["mentions"][etiqueta]["reason"]
        with self.assertRaises(SystemExit) as e:
            self.entorno.construir(spec)
        self.assertIn(etiqueta, str(e.exception))
        self.assertIn("reason", str(e.exception))

    def test_delta_no_revierte_sin_historial(self):
        # Sin historial no hay prueba de que se aplicara ni de qué contenido.
        deltas = self.entorno.tmp / "deltas"
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(delta_mod.cmd(deltas / "SEC-000001.json", False, False), 0)
        (deltas / "historial.jsonl").unlink()
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            self.assertEqual(delta_mod.cmd(deltas / "SEC-000001.json", True, False), 1)
        self.assertIn("no es el último delta aplicado", salida.getvalue())

    def test_delta_revertido_solo_se_reaplica_con_el_mismo_contenido(self):
        # El revertido se queda como constancia de lo que se aplicó: volver a
        # aplicarlo editado borraría esa constancia. Otro contenido, otro nombre.
        deltas = self.entorno.tmp / "deltas"
        ruta = deltas / "SEC-000001.json"
        original = ruta.read_bytes()
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(delta_mod.cmd(ruta, False, False), 0)
            self.assertEqual(delta_mod.cmd(ruta, True, False), 0)
        d = json.loads(original)
        d["operations"] = d["operations"][:-1]
        ruta.write_text(json.dumps(d), encoding="utf-8")
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            self.assertEqual(delta_mod.cmd(ruta, False, False), 1)
        self.assertIn("otro contenido", salida.getvalue())
        ruta.write_bytes(original)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(delta_mod.cmd(ruta, False, False), 0)

    def test_delta_no_opera_sin_manifiesto(self):
        # Sin manifiesto no hay revisión autorizada que comprobar ni que avanzar.
        deltas = self.entorno.tmp / "deltas"
        (self.entorno.tmp / "dataset.json").unlink()
        antes = {f.name: f.read_bytes() for f in self.entorno.records.glob("*.jsonl")}
        for seco in (True, False):
            with self.subTest(en_seco=seco):
                salida = io.StringIO()
                with contextlib.redirect_stdout(salida):
                    self.assertEqual(delta_mod.cmd(deltas / "SEC-000001.json", False, seco), 1)
                self.assertIn("manifiesto", salida.getvalue())
        self.assertEqual({f.name: f.read_bytes() for f in self.entorno.records.glob("*.jsonl")}, antes)

    def test_un_registro_que_no_valida_contra_su_esquema_se_rechaza(self):
        try:
            import jsonschema  # noqa: F401
        except ImportError:
            self.skipTest("jsonschema no instalado")
        spec = self.entorno.spec()
        spec["records"][2]["record"]["claim_type"] = "inventado"
        spec["mentions"]["FIX-Alfa"]["mention_type"] = "tampoco_existe"
        with self.assertRaises(SystemExit) as e:
            self.entorno.construir(spec)
        self.assertIn("claims.jsonl", str(e.exception))
        self.assertIn("inventado", str(e.exception))
        self.assertIn("mentions.jsonl", str(e.exception))

    def test_una_fila_que_no_es_glosa_sin_registros_se_rechaza(self):
        spec = self.entorno.spec()
        spec["rows"]["C-002"] = {"destination": "A", "keys": []}
        with self.assertRaises(SystemExit) as e:
            self.entorno.construir(spec)
        self.assertIn("C-002", str(e.exception))

    def test_una_mencion_sin_disposicion_se_rechaza(self):
        spec = self.entorno.spec()
        spec["mentions"]["FIX-Alfa"]["disposition"] = None
        with self.assertRaises(SystemExit) as e:
            self.entorno.construir(spec)
        self.assertIn("FIX-Alfa", str(e.exception))
        self.assertIn("disposition", str(e.exception))

    def test_las_menciones_parten_del_estado_proyectado(self):
        # Un delta sin aplicar, detrás de la sección, ya anotó una mención: la
        # conversión tiene que partir de esa nota, o al aplicarla la pisaría.
        [op] = [o for o in self.entorno.delta_sec["operations"]
                if o["file"] == "mentions.jsonl" and o["after"]["original_text"] == "FIX-Alfa"]
        anotada = {**op["after"], "notes": list(op["after"].get("notes", [])) + ["nota intermedia"]}
        (self.entorno.tmp / "deltas" / "SEC-000009-conversion.json").write_text(json.dumps({
            "dataset_revision_before": "REV-000001", "dataset_revision_after": "REV-000002",
            "operations": [{"operation": "UPDATE_RECORD", "file": "mentions.jsonl", "record_id": op["record_id"],
                            "before": op["after"], "after": anotada}]}), encoding="utf-8")
        r = self.entorno.construir(self.entorno.spec())
        [act] = [o for o in r["delta"]["operations"] if o["record_id"] == op["record_id"]]
        self.assertIn("nota intermedia", act["before"]["notes"])
        self.assertIn("nota intermedia", act["after"]["notes"])

    def estudio(self, spec: dict, result_ids: list[str] | None) -> dict:
        """Añade al spec la cadena datos → análisis → resultado de la fila C-001."""
        analisis = {"analysis_type": "molecular_clock_dating", "method": "reloj", "dataset_ids": ["@D1"]}
        if result_ids is not None:
            analisis["result_ids"] = result_ids
        spec["records"] += [
            {"key": "@D1", "file": "datasets.jsonl", "rows": ["C-001"],
             "record": {"dataset_type": "other", "title": "Datos", "description": "De prueba."}},
            {"key": "@A1", "file": "analyses.jsonl", "rows": ["C-001"], "record": analisis},
            {"key": "@R1", "file": "results.jsonl", "rows": ["C-001"],
             "record": {"analysis_id": "@A1", "result_type": "other", "description": "De prueba."}},
        ]
        spec["rows"]["C-001"]["keys"] += ["@D1", "@A1", "@R1"]
        return spec

    def test_los_resultados_de_un_analisis_se_deducen(self):
        r = self.entorno.construir(self.estudio(self.entorno.spec(), None))
        recs = self.registros(r)
        [an] = [x for x in recs.values() if x["id"].startswith("ANALYSIS-")]
        [res] = [x for x in recs.values() if x["id"].startswith("RESULT-")]
        self.assertEqual(an["result_ids"], [res["id"]])

    def test_un_analisis_que_no_lista_sus_resultados_se_rechaza(self):
        with self.assertRaises(SystemExit) as e:
            self.entorno.construir(self.estudio(self.entorno.spec(), []))
        self.assertIn("@A1", str(e.exception))
        self.assertIn("result_ids", str(e.exception))

    def test_un_resultado_de_un_analisis_existente_lo_enlaza(self):
        existente = {"id": "ANALYSIS-000050", "analysis_type": "other", "method": "x", "dataset_ids": [],
                     "result_ids": [], "record_status": "active"}
        (self.entorno.records / "analyses.jsonl").write_text(json.dumps(existente) + "\n", encoding="utf-8")
        spec = self.entorno.spec()
        spec["records"].append({"key": "@R1", "file": "results.jsonl", "rows": ["C-001"],
                                "record": {"analysis_id": "ANALYSIS-000050", "result_type": "other",
                                           "description": "De prueba."}})
        spec["rows"]["C-001"]["keys"].append("@R1")
        r = self.entorno.construir(spec)
        [res] = [rec["id"] for _, rec in r["salida"] if rec["id"].startswith("RESULT-")]
        [op] = [o for o in r["delta"]["operations"] if o["record_id"] == "ANALYSIS-000050"]
        self.assertEqual(op["after"]["result_ids"], [res])

    def test_una_afirmacion_derivada_tiene_procedencia_derivada(self):
        spec = self.entorno.spec()
        spec["records"][2]["record"]["derivation"] = {"rule": "de prueba", "depends_on_ids": [],
                                                      "derived_in_view_id": None}
        r = self.entorno.construir(spec)
        [claim] = [rec for _, rec in r["salida"] if rec["id"].startswith("CLAIM-")]
        self.assertEqual(claim["provenance"]["origin"], "derived")

    def test_una_incidencia_nueva_nace_abierta(self):
        spec = self.entorno.spec()
        spec["records"].append({"key": "@I1", "file": "issues.jsonl", "rows": ["C-001"], "record": {
            "issue_type": "pending_question", "title": "Prueba", "severity": "INFO",
            "resolution": {"status": "resolved"}}})
        spec["rows"]["C-001"]["keys"].append("@I1")
        with self.assertRaises(SystemExit) as e:
            self.entorno.construir(spec)
        self.assertIn("@I1", str(e.exception))
        self.assertIn("resolution", str(e.exception))

    def test_el_mapa_por_fila_incluye_los_registros_que_la_declaran(self):
        # @Beta declara la fila C-001 en `rows` aunque la fila no la liste: el
        # delta tiene que decir que salió de ahí.
        spec = self.entorno.spec()
        spec["rows"]["C-001"]["keys"].remove("@Beta")
        r = self.entorno.construir(spec)
        beta = next(rec["id"] for _, rec in r["salida"] if rec.get("preferred_label") == "FIX-Beta")
        self.assertIn(beta, r["delta"]["conversion"]["rows"]["C-001"]["record_ids"])

    def test_una_etiqueta_suplementaria_no_es_una_fuente(self):
        # «S07 supl. fig. S3»: S3 es una figura suplementaria de S07. Las claves
        # del apéndice A tienen al menos dos dígitos, como en parse_research.py.
        self.assertEqual(convertir.CITA.findall("S07 supl. fig. S3; S139 tabla 2"), ["S07", "S139"])
        self.assertIsNone(convertir.FUENTE.match("@S3"))

    def test_una_fila_no_lista_un_registro_que_no_la_declara(self):
        # La procedencia sale de las filas del registro: si la fila C-001 lo
        # lista y el registro no la declara, el mapa y la procedencia discrepan.
        spec = self.entorno.spec()
        spec["records"][0]["rows"] = ["C-002"]
        with self.assertRaises(SystemExit) as e:
            self.entorno.construir(spec)
        self.assertIn("C-001", str(e.exception))
        self.assertIn("@Alfa", str(e.exception))

    def test_una_mencion_se_puede_decidir_por_su_identificador(self):
        # Dos menciones con el mismo texto pueden ser cosas distintas: la que se
        # nombra por su identificador no sigue la regla de su texto.
        [op] = [o for o in self.entorno.delta_sec["operations"]
                if o["file"] == "mentions.jsonl" and o["after"]["original_text"] == "FIX-Alfa"]
        spec = self.entorno.spec()
        spec["mentions"][op["record_id"]] = {"mention_type": "clade", "disposition": "new_entity",
                                             "targets": ["@Beta"], "reason": "esta aparición es Beta"}
        r = self.entorno.construir(spec)
        beta = next(rec["id"] for _, rec in r["salida"] if rec.get("preferred_label") == "FIX-Beta")
        [act] = [o for o in r["delta"]["operations"] if o["record_id"] == op["record_id"]]
        self.assertEqual(act["after"]["resolution"]["target_ids"], [beta])

    def cuestion_de_mencion(self, spec: dict, objetivo: str) -> tuple[dict, str]:
        """La mención FIX-Beta pasa a señalar la incidencia `objetivo`."""
        [op] = [o for o in self.entorno.delta_sec["operations"]
                if o["file"] == "mentions.jsonl" and o["after"]["original_text"] == "FIX-Beta"]
        spec["mentions"]["FIX-Beta"] = {"mention_type": "controversy", "disposition": "pending_question",
                                        "targets": [objetivo], "reason": "pregunta abierta"}
        return spec, op["record_id"]

    def test_una_mencion_que_senala_una_incidencia_la_enlaza_en_los_dos_sentidos(self):
        spec = self.entorno.spec()
        spec["records"].append({"key": "@I1", "file": "issues.jsonl", "rows": ["C-001"], "record": {
            "issue_type": "pending_question", "title": "Prueba", "severity": "INFO"}})
        spec["rows"]["C-001"]["keys"].append("@I1")
        spec, mid = self.cuestion_de_mencion(spec, "@I1")
        r = self.entorno.construir(spec)
        [iss] = [x for _, x in r["salida"] if x["id"].startswith("ISSUE-")]
        [(_, mencion)] = [(a, d) for a, d in r["actualizadas"] if d["id"] == mid]
        self.assertEqual(mencion["issue_ids"], [iss["id"]])
        self.assertEqual(iss["affects"]["mention_ids"], [mid])

    def test_una_mencion_que_senala_una_incidencia_existente_la_enlaza(self):
        existente = {"id": "ISSUE-000050", "issue_type": "pending_question", "title": "X", "severity": "INFO",
                     "raised_in": "SEC-000001", "affects": {"record_ids": [], "claim_ids": [], "mention_ids": []},
                     "resolution": {"status": "open"}, "record_status": "active"}
        (self.entorno.records / "issues.jsonl").write_text(json.dumps(existente) + "\n", encoding="utf-8")
        spec, mid = self.cuestion_de_mencion(self.entorno.spec(), "ISSUE-000050")
        r = self.entorno.construir(spec)
        [op] = [o for o in r["delta"]["operations"] if o["record_id"] == "ISSUE-000050"]
        self.assertEqual(op["after"]["affects"]["mention_ids"], [mid])
        [(_, mencion)] = [(a, d) for a, d in r["actualizadas"] if d["id"] == mid]
        self.assertEqual(mencion["issue_ids"], ["ISSUE-000050"])

    def test_una_incidencia_enlaza_lo_que_afecta(self):
        # Nueva o existente, cada registro que la incidencia afecta la lista en
        # su `issue_ids`.
        existente = {"id": "EVENT-000050", "event_type": "divergence", "label": "X",
                     "participants": [{"entity_id": "CLADE-000050", "role": "participant", "notes": []}],
                     "result_entity_ids": [], "temporal_expression_ids": [], "region_ids": [],
                     "record_status": "active"}
        (self.entorno.records / "events.jsonl").write_text(json.dumps(existente) + "\n", encoding="utf-8")
        spec = self.entorno.spec()
        spec["records"].append({"key": "@I1", "file": "issues.jsonl", "rows": ["C-001"], "record": {
            "issue_type": "pending_question", "title": "Prueba", "severity": "INFO",
            "affects": {"record_ids": ["@Alfa", "EVENT-000050"], "claim_ids": ["@CL1"], "mention_ids": []}}})
        spec["rows"]["C-001"]["keys"].append("@I1")
        r = self.entorno.construir(spec)
        recs = self.registros(r)
        [iss] = [x for x in recs.values() if x["id"].startswith("ISSUE-")]
        alfa = next(e for e in recs.values() if e.get("preferred_label") == "FIX-Alfa")
        [claim] = [c for c in recs.values() if c["id"].startswith("CLAIM-")]
        self.assertEqual(alfa["issue_ids"], [iss["id"]])
        self.assertEqual(claim["issue_ids"], [iss["id"]])
        [op] = [o for o in r["delta"]["operations"] if o["record_id"] == "EVENT-000050"]
        self.assertEqual(op["after"]["issue_ids"], [iss["id"]])

    def test_un_registro_que_nombra_una_incidencia_queda_en_su_affects(self):
        # El otro sentido: el registro lista la incidencia y ella no lo lista.
        existente = {"id": "ISSUE-000050", "issue_type": "pending_question", "title": "X", "severity": "INFO",
                     "raised_in": "SEC-000001", "affects": {"record_ids": [], "claim_ids": [], "mention_ids": []},
                     "resolution": {"status": "open"}, "record_status": "active"}
        (self.entorno.records / "issues.jsonl").write_text(json.dumps(existente) + "\n", encoding="utf-8")
        spec = self.entorno.spec()
        spec["records"][2]["record"]["issue_ids"] = ["ISSUE-000050"]
        spec["records"].append({"key": "@I1", "file": "issues.jsonl", "rows": ["C-001"], "record": {
            "issue_type": "pending_question", "title": "Prueba", "severity": "INFO"}})
        spec["rows"]["C-001"]["keys"].append("@I1")
        spec["records"][0]["record"]["issue_ids"] = ["@I1"]
        r = self.entorno.construir(spec)
        recs = self.registros(r)
        [claim] = [c for c in recs.values() if c["id"].startswith("CLAIM-")]
        [iss] = [x for x in recs.values() if x["id"].startswith("ISSUE-")]
        alfa = next(e for e in recs.values() if e.get("preferred_label") == "FIX-Alfa")
        self.assertEqual(iss["affects"]["record_ids"], [alfa["id"]])
        [op] = [o for o in r["delta"]["operations"] if o["record_id"] == "ISSUE-000050"]
        self.assertEqual(op["after"]["affects"]["claim_ids"], [claim["id"]])

    def test_el_siguiente_del_manifiesto_reserva_los_anteriores(self):
        # Un identificador por debajo del siguiente que declara el manifiesto
        # ya se asignó aunque no esté en ningún fichero.
        manifiesto = self.entorno.tmp / "dataset.json"
        d = json.loads(manifiesto.read_text(encoding="utf-8"))
        d["id_allocation"] = {"next": {"CLAIM": "CLAIM-000007"}}
        manifiesto.write_text(json.dumps(d), encoding="utf-8")
        with mock.patch.object(convertir.base, "MANIFEST", manifiesto):
            r = self.entorno.construir(self.entorno.spec())
        [claim] = [x["id"] for _, x in r["salida"] if x["id"].startswith("CLAIM-")]
        self.assertEqual(claim, "CLAIM-000007")

    def test_aplicar_un_delta_avanza_el_siguiente_del_manifiesto(self):
        manifiesto = self.entorno.tmp / "dataset.json"
        d = json.loads(manifiesto.read_text(encoding="utf-8"))
        d["id_allocation"] = {"next": {"MENTION": "MENTION-000001"}}
        manifiesto.write_text(json.dumps(d), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(delta_mod.cmd(self.entorno.tmp / "deltas" / "SEC-000001.json", False, False), 0)
        menciones = [o["record_id"] for o in self.entorno.delta_sec["operations"] if o["file"] == "mentions.jsonl"]
        siguiente = json.loads(manifiesto.read_text(encoding="utf-8"))["id_allocation"]["next"]["MENTION"]
        self.assertEqual(int(siguiente.split("-")[1]), max(int(m.split("-")[1]) for m in menciones) + 1)
        # Al revertir no retrocede: los identificadores siguen reservados.
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(delta_mod.cmd(self.entorno.tmp / "deltas" / "SEC-000001.json", True, False), 0)
        self.assertEqual(json.loads(manifiesto.read_text(encoding="utf-8"))["id_allocation"]["next"]["MENTION"],
                         siguiente)

    def test_una_clave_de_mencion_desconocida_se_rechaza(self):
        spec = self.entorno.spec()
        spec["mentions"]["MENTION-999999"] = {"mention_type": "clade", "disposition": "discarded_with_reason",
                                              "targets": [], "reason": "no existe"}
        with self.assertRaises(SystemExit) as e:
            self.entorno.construir(spec)
        self.assertIn("MENTION-999999", str(e.exception))

    @staticmethod
    def tiempo(antiguo: int, reciente: int) -> dict:
        return {"temporal_type": "divergence_estimate", "label": f"{antiguo}–{reciente} Ma",
                "interval": {"oldest_bound": antiguo, "youngest_bound": reciente, "unit": "million_years",
                             "reference_point": "before_present", "original_expression": f"{reciente}–{antiguo} Ma"},
                "uncertainty": {"kind": "range_only", "description": "De prueba."},
                "calibration": {"system": "molecular_clock", "curve_or_timescale": None},
                "method": "reloj", "method_type": "molecular_clock", "determination": "modelled", "notes": []}

    def datacion(self, spec: dict, tiempos_del_evento: list[str] | None) -> dict:
        """Un evento de divergencia y una afirmación `dated_to` que lo fecha."""
        evento = {"event_type": "divergence", "label": "Divergencia de prueba",
                  "participants": [{"entity_id": "@Alfa", "role": "participant", "notes": []}],
                  "result_entity_ids": [], "region_ids": [], "notes": []}
        if tiempos_del_evento is not None:
            evento["temporal_expression_ids"] = tiempos_del_evento
        spec["records"] += [
            {"key": "@T1", "file": "temporal-expressions.jsonl", "rows": ["C-001"], "record": self.tiempo(1000, 900)},
            {"key": "@E1", "file": "events.jsonl", "rows": ["C-001"], "record": evento},
            {"key": "@CLT", "file": "claims.jsonl", "rows": ["C-001"], "record": {
                "claim_type": "temporal", "subject_id": "@E1", "predicate": "dated_to",
                "object": {"temporal_expression_id": "@T1"}}},
        ]
        spec["rows"]["C-001"]["keys"] += ["@T1", "@E1", "@CLT"]
        return spec

    def test_las_fechas_de_un_evento_se_deducen_de_sus_dataciones(self):
        r = self.entorno.construir(self.datacion(self.entorno.spec(), []))
        recs = self.registros(r)
        [ev] = [x for x in recs.values() if x["id"].startswith("EVENT-")]
        [t] = [x for x in recs.values() if x["id"].startswith("TIME-")]
        self.assertEqual(ev["temporal_expression_ids"], [t["id"]])

    def test_una_fecha_de_evento_sin_datacion_se_rechaza(self):
        spec = self.datacion(self.entorno.spec(), None)
        spec["records"].append({"key": "@T2", "file": "temporal-expressions.jsonl", "rows": ["C-001"],
                                "record": self.tiempo(800, 700)})
        spec["rows"]["C-001"]["keys"].append("@T2")
        spec["records"][-3]["record"]["temporal_expression_ids"] = ["@T2"]
        with self.assertRaises(SystemExit) as e:
            self.entorno.construir(spec)
        self.assertIn("@E1", str(e.exception))
        self.assertIn("temporal_expression_ids", str(e.exception))

    def test_la_cadena_de_una_evidencia_tiene_que_ser_coherente(self):
        # La evidencia cita un resultado de un análisis que no es el que lista.
        spec = self.estudio(self.entorno.spec(), None)
        spec["records"] += [
            {"key": "@A2", "file": "analyses.jsonl", "rows": ["C-001"], "record": {
                "analysis_type": "other", "method": "otro", "dataset_ids": ["@D1"]}}]
        spec["rows"]["C-001"]["keys"].append("@A2")
        spec["records"][3]["record"].update({"dataset_ids": ["@D1"], "analysis_ids": ["@A2"], "result_ids": ["@R1"]})
        with self.assertRaises(SystemExit) as e:
            self.entorno.construir(spec)
        self.assertIn("@EV1", str(e.exception))
        self.assertIn("@R1", str(e.exception))

    def test_una_evidencia_con_datos_y_sin_analisis_se_rechaza(self):
        # Sin un análisis citado, los datos no tienen de dónde salir: la cadena
        # datos → análisis está rota aunque el esquema acepte la forma.
        spec = self.estudio(self.entorno.spec(), None)
        spec["records"][3]["record"].update({"dataset_ids": ["@D1"], "analysis_ids": []})
        with self.assertRaises(SystemExit) as e:
            self.entorno.construir(spec)
        self.assertIn("@EV1", str(e.exception))
        self.assertIn("@D1", str(e.exception))

    def test_delta_exige_revisiones_consecutivas(self):
        deltas = self.entorno.tmp / "deltas"
        ruta = deltas / "SEC-000001.json"
        d = json.loads(ruta.read_text(encoding="utf-8"))
        d["dataset_revision_after"] = "REV-999999"
        ruta.write_text(json.dumps(d), encoding="utf-8")
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            self.assertEqual(delta_mod.cmd(ruta, False, True), 1)
        self.assertIn("REV-999999", salida.getvalue())

    def test_delta_exige_el_historial_de_los_anteriores(self):
        # El manifiesto dice REV-000001 pero el historial no registra quién lo
        # dejó ahí: aplicar encima dejaría una pila que no se puede deshacer.
        (self.entorno.tmp / "dataset.json").write_text(json.dumps({"dataset_revision": "REV-000001"}),
                                                       encoding="utf-8")
        deltas = self.entorno.tmp / "deltas"
        (deltas / "SEC-000009-conversion.json").write_text(json.dumps({
            "dataset_revision_before": "REV-000001", "dataset_revision_after": "REV-000002",
            "operations": []}), encoding="utf-8")
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            self.assertEqual(delta_mod.cmd(deltas / "SEC-000009-conversion.json", False, True), 1)
        self.assertIn("historial", salida.getvalue())

    def test_delta_exige_revisiones_de_seis_digitos(self):
        ruta = self.entorno.tmp / "deltas" / "SEC-000001.json"
        d = json.loads(ruta.read_text(encoding="utf-8"))
        d["dataset_revision_after"] = "REV-1"
        ruta.write_text(json.dumps(d), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(delta_mod.cmd(ruta, False, True), 1)

    def test_delta_comprueba_el_estado_previo_de_cada_registro(self):
        # Si el registro ya no está como el delta espera, aplicar o revertir
        # pisaría un cambio que el delta no conoce. No se escribe nada.
        ruta = self.entorno.tmp / "spec.json"
        ruta.write_text(json.dumps(self.entorno.spec(), ensure_ascii=False), encoding="utf-8")
        deltas = self.entorno.tmp / "deltas"
        menciones = self.entorno.records / "mentions.jsonl"
        with contextlib.redirect_stdout(io.StringIO()):
            convertir.convertir(ruta, str(MINI), False)
            self.assertEqual(delta_mod.cmd(deltas / "SEC-000001.json", False, False), 0)
        original = menciones.read_bytes()
        lineas = [json.loads(l) for l in original.decode("utf-8").splitlines()]
        lineas[0]["notes"] = list(lineas[0].get("notes", [])) + ["cambio que el delta no conoce"]
        menciones.write_text("".join(json.dumps(l, ensure_ascii=False) + "\n" for l in lineas), encoding="utf-8")
        tocado = menciones.read_bytes()
        for seco in (True, False):
            salida = io.StringIO()
            with contextlib.redirect_stdout(salida):
                self.assertEqual(delta_mod.cmd(deltas / "SEC-000001-conversion.json", False, seco), 1)
            self.assertIn(lineas[0]["id"], salida.getvalue())
        self.assertEqual(menciones.read_bytes(), tocado)
        # Y al revertir: el registro tiene que estar como lo dejó el delta.
        menciones.write_bytes(original)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(delta_mod.cmd(deltas / "SEC-000001-conversion.json", False, False), 0)
        convertida = menciones.read_bytes()
        lineas = [json.loads(l) for l in convertida.decode("utf-8").splitlines()]
        lineas[0]["notes"] = list(lineas[0].get("notes", [])) + ["otro cambio que el delta no conoce"]
        menciones.write_text("".join(json.dumps(l, ensure_ascii=False) + "\n" for l in lineas), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(delta_mod.cmd(deltas / "SEC-000001-conversion.json", True, False), 1)
        menciones.write_bytes(convertida)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(delta_mod.cmd(deltas / "SEC-000001-conversion.json", True, False), 0)
            self.assertEqual(delta_mod.cmd(deltas / "SEC-000001.json", True, False), 0)

    def test_un_alta_parte_de_la_ausencia_del_registro(self):
        # Un alta con `before` igual a un registro que ya existe pasaría la
        # comprobación de estado previo y duplicaría el identificador.
        existente = {"id": "CLADE-000050", "entity_type": "clade", "preferred_label": "X",
                     "record_status": "active"}
        clades = self.entorno.records / "clades.jsonl"
        clades.write_text(json.dumps(existente) + "\n", encoding="utf-8")
        op = {"operation": "ADD_RECORD", "file": "clades.jsonl", "record_id": "CLADE-000050",
              "before": existente, "after": {**existente, "preferred_label": "Y"}}
        with self.assertRaises(ValueError) as e:
            delta_mod.apply_ops([op])
        self.assertIn("CLADE-000050", str(e.exception))
        self.assertEqual(clades.read_text(encoding="utf-8").count("CLADE-000050"), 1)

    def test_el_contenido_de_una_operacion_lleva_su_identificador(self):
        # Un alta con otro `id` quedaría en el fichero con ese otro, y revertirla
        # buscaría el de la operación sin encontrarlo.
        clades = self.entorno.records / "clades.jsonl"
        clades.write_text(json.dumps({"id": "CLADE-000060", "record_status": "active"}) + "\n", encoding="utf-8")
        original = clades.read_bytes()
        for op in ({"operation": "ADD_RECORD", "file": "clades.jsonl", "record_id": "CLADE-000061",
                    "before": None, "after": {"id": "CLADE-000062"}},
                   {"operation": "UPDATE_RECORD", "file": "clades.jsonl", "record_id": "CLADE-000060",
                    "before": {"id": "CLADE-000060", "record_status": "active"},
                    "after": {"id": "CLADE-000063", "record_status": "active"}}):
            with self.assertRaises(ValueError) as e:
                delta_mod.apply_ops([op])
            self.assertIn(op["record_id"], str(e.exception))
            self.assertEqual(clades.read_bytes(), original)

    def test_una_actualizacion_necesita_el_registro(self):
        op = {"operation": "UPDATE_RECORD", "file": "clades.jsonl", "record_id": "CLADE-000051",
              "before": None, "after": {"id": "CLADE-000051"}}
        with self.assertRaises(ValueError) as e:
            delta_mod.apply_ops([op])
        self.assertIn("CLADE-000051", str(e.exception))

    def test_no_se_aplica_encima_de_un_delta_aplicado_que_cambio(self):
        # Los registros salieron de lo que el delta decía cuando se aplicó. Si
        # el fichero cambió, apilar otro encima dejaría una pila que no se
        # reconstruye desde sus deltas.
        ruta = self.entorno.tmp / "spec.json"
        ruta.write_text(json.dumps(self.entorno.spec(), ensure_ascii=False), encoding="utf-8")
        deltas = self.entorno.tmp / "deltas"
        with contextlib.redirect_stdout(io.StringIO()):
            convertir.convertir(ruta, str(MINI), False)
            self.assertEqual(delta_mod.cmd(deltas / "SEC-000001.json", False, False), 0)
        seccion = deltas / "SEC-000001.json"
        d = json.loads(seccion.read_text(encoding="utf-8"))
        d["nota"] = "editado después de aplicarlo"
        seccion.write_text(json.dumps(d), encoding="utf-8")
        for seco in (True, False):
            salida = io.StringIO()
            with contextlib.redirect_stdout(salida):
                self.assertEqual(delta_mod.cmd(deltas / "SEC-000001-conversion.json", False, seco), 1)
            self.assertIn("SEC-000001.json", salida.getvalue())

    def test_sin_jsonschema_no_se_convierte(self):
        # Sin jsonschema la validación no corre: se niega en vez de escribir
        # un delta sin validar.
        with mock.patch.dict(sys.modules, {"jsonschema": None}):
            with self.assertRaises(SystemExit) as e:
                self.entorno.construir(self.entorno.spec())
        self.assertIn("jsonschema", str(e.exception))

    def test_el_fichero_de_conversion_tiene_que_estar_en_conversions(self):
        # El snapshot sólo registra knowledge/corpus/conversions/*.json: una
        # entrada revisada fuera de ahí no se podría recuperar ni verificar.
        fuera = self.entorno.tmp / "otra" / "spec.json"
        fuera.parent.mkdir()
        fuera.write_text(json.dumps(self.entorno.spec(), ensure_ascii=False), encoding="utf-8")
        with self.assertRaises(SystemExit) as e, contextlib.redirect_stdout(io.StringIO()):
            convertir.construir(fuera, str(MINI))
        self.assertIn("knowledge/corpus/conversions/", str(e.exception))

    def test_la_conversion_va_detras_del_delta_de_la_seccion(self):
        r = self.entorno.construir(self.entorno.spec())
        self.assertEqual(r["rev"], ("REV-000001", "REV-000002"))
        self.assertEqual(r["pendientes"], ["SEC-000001.json"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
