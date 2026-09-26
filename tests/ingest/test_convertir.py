#!/usr/bin/env python3
"""Pruebas de scripts/ingest/convertir.py sobre tests/fixtures/corredor-mini.

Todo ocurre en un directorio temporal: el dataset, las congelaciones, los deltas
y los registros se reapuntan a él, así que el libro mayor real no se toca.
"""

from __future__ import annotations

import argparse
import contextlib
import csv
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
        spec["rows"]["C-001"]["destination"] = "J"
        with self.assertRaises(SystemExit) as e:
            self.entorno.construir(spec)
        self.assertIn("C-001", str(e.exception))
        self.assertIn("J", str(e.exception))

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
