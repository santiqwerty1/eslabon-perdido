#!/usr/bin/env python3
"""Pruebas de scripts/build_views/cronologia.py («Relojes y rocas»).

Dos montajes. Sobre el libro mayor real sólo se comprueban invariantes, que no
dependen de cuántas secciones haya convertidas: toda afirmación activa está en
un solo sitio, toda datación tiene su marca y la página sale igual dos veces.
Los casos concretos (cada forma de fecha, el carril, qué entra en una ficha,
una hipótesis sin fecha) van sobre un libro mayor mínimo escrito aquí.
"""

from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "build_views"))

import cronologia  # noqa: E402


def dims(fuerza="high", resolucion="resolved"):
    return {"acceptance": "not_assessed", "evidence_strength": fuerza,
            "resolution": resolucion, "historical_status": "current"}


def afirmacion(cid, sujeto, predicado, objeto, fuerza="high", evid=()):
    return {"id": cid, "claim_type": "relational", "subject_id": sujeto, "predicate": predicado,
            "object": objeto, "notes": [], "epistemic_dimensions": dims(fuerza),
            "provenance": {"section_ids": ["SEC-000001"], "passage_ids": ["PASSAGE-000001"],
                           "source_ids": ["SRC-000001"]},
            "evidence_ids": list(evid), "counterevidence_ids": [], "record_status": "active"}


def fecha(tid, viejo, joven, unidad="million_years", determinacion="observed", original="", nombre=None):
    iv = {"oldest_bound": viejo, "youngest_bound": joven, "unit": unidad, "original_expression": original}
    if nombre:
        iv["geological_interval"] = nombre
    return {"id": tid, "temporal_type": "occurrence_date", "interval": iv, "determination": determinacion,
            "uncertainty": {"kind": "unknown"}, "calibration": {"system": "unknown"}, "record_status": "active"}


class LibroMinimo:
    """Un libro mayor pequeño con un caso de cada cosa."""

    def __init__(self, raiz: Path):
        self.raiz = raiz
        self.base = raiz / "knowledge" / "records"
        self.base.mkdir(parents=True)
        (raiz / "knowledge" / "corpus" / "manifests").mkdir(parents=True)
        (raiz / "knowledge" / "corpus" / "passages").mkdir(parents=True)
        (raiz / "knowledge" / "corpus" / "manifests" / "dataset.json").write_text(json.dumps({
            "dataset_revision": "REV-000001", "snapshot_id": "SNAP-000001",
            "corpus_freeze": {"path": "knowledge/corpus/manifests/corredor.json", "commit": "abcdef0123",
                              "version": "0.1", "decision": "DEC-000"}}), encoding="utf-8")
        (raiz / "knowledge" / "corpus" / "manifests" / "corredor.json").write_text(json.dumps({
            "version": "0.1", "cutoff": "2026-01-01", "frozen_on": "2026-01-02"}), encoding="utf-8")
        (raiz / "knowledge" / "corpus" / "passages" / "SEC-000001.json").write_text(json.dumps([
            {"id": "PASSAGE-000001", "section_id": "SEC-000001", "ordinal": 1,
             "text": "Un pasaje con </script> dentro."}]), encoding="utf-8")
        self.registros = {
            "sources.jsonl": [{"id": "SRC-000001", "citation_key": "S1", "authors": ["Pérez, A.", "Gómez, B."],
                               "year": 2020, "title": "Un título", "record_status": "active"}],
            "evidence.jsonl": [{"id": "EVID-000001", "evidence_type": "molecular", "description": "reloj",
                                "source_id": "SRC-000001", "record_status": "active"}],
            "events.jsonl": [{"id": "EVENT-000001", "label": "diversificación de algo", "record_status": "active"}],
            "clades.jsonl": [{"id": "CLADE-000001", "preferred_label": "Eukaryota", "record_status": "active"}],
            "taxonomic-names.jsonl": [
                {"id": "NAME-000001", "canonical_spelling": "Fosilia datada", "record_status": "active"},
                {"id": "NAME-000002", "canonical_spelling": "Fosilia sin fecha", "record_status": "active"}],
            "taxon-concepts.jsonl": [
                {"id": "TAXCONCEPT-000001", "name_id": "NAME-000001", "record_status": "active"},
                {"id": "TAXCONCEPT-000002", "name_id": "NAME-000002", "record_status": "active"}],
            "molecules.jsonl": [{"id": "MOL-000001", "preferred_label": "esteranos", "record_status": "active"}],
            "lineages.jsonl": [{"id": "LINEAGE-000001", "preferred_label": "un linaje", "record_status": "active"}],
            "methods.jsonl": [{"id": "METHOD-000001", "preferred_label": "un reloj", "record_status": "active"}],
            "occurrences.jsonl": [
                {"id": "OCC-000001", "entity_id": "TAXCONCEPT-000001", "record_status": "active"},
                {"id": "OCC-000002", "entity_id": "MOL-000001", "record_status": "active"}],
            "temporal-expressions.jsonl": [
                fecha("TIME-000001", 1800, 1600, determinacion="modelled", original="1600–1800 Ma"),
                fecha("TIME-000002", None, 1700, determinacion="modelled", original="más de 1700 Ma"),
                fecha("TIME-000003", 1500, 1500, original="aproximadamente 1.5 Ga"),
                fecha("TIME-000004", None, None, unidad="geological_interval", original="Mesoproterozoico",
                      nombre="Mesoproterozoico"),
                fecha("TIME-000005", 1050, None, original="desde 1.05 Ga"),
                fecha("TIME-000006", None, None, unidad="geological_interval", original="Hadeano medio",
                      nombre="Hadeano medio"),
            ],
            "claims.jsonl": [
                afirmacion("CLAIM-000001", "EVENT-000001", "dated_to", {"temporal_expression_id": "TIME-000001"},
                           "low", evid=["EVID-000001"]),
                afirmacion("CLAIM-000002", "EVENT-000001", "dated_to", {"temporal_expression_id": "TIME-000002"}),
                afirmacion("CLAIM-000003", "OCC-000001", "dated_to", {"temporal_expression_id": "TIME-000003"},
                           "medium"),
                afirmacion("CLAIM-000004", "OCC-000002", "dated_to", {"temporal_expression_id": "TIME-000004"}),
                afirmacion("CLAIM-000005", "CLADE-000001", "dated_to", {"temporal_expression_id": "TIME-000005"}),
                # Lo que se dice del fósil datado va a su ficha.
                afirmacion("CLAIM-000006", "TAXCONCEPT-000001", "assigned_to", {"entity_id": "CLADE-000001"}),
                # Un paso: el biomarcador es indicio de un linaje, y lo que se dice del linaje va a su ficha.
                afirmacion("CLAIM-000007", "MOL-000001", "biomarker_of", {"entity_id": "LINEAGE-000001"}),
                afirmacion("CLAIM-000008", "LINEAGE-000001", "stem_lineage_of", {"entity_id": "CLADE-000001"}),
                # Asignar algo a Eukaryota no basta para entrar en la ficha de Eukaryota.
                afirmacion("CLAIM-000009", "TAXCONCEPT-000002", "assigned_to", {"entity_id": "CLADE-000001"}),
                afirmacion("CLAIM-000010", "METHOD-000001", "limits", {"category": "la resolución"}),
                afirmacion("CLAIM-000011", "EVENT-000001", "dated_to", {"temporal_expression_id": "TIME-000006"}),
            ],
            "hypotheses.jsonl": [
                {"id": "HYP-000001", "name": "Fosilia datada es eucariota", "included_claim_ids": ["CLAIM-000006"],
                 "alternative_hypothesis_ids": ["HYP-000002"], "record_status": "active"},
                {"id": "HYP-000002", "name": "Fosilia sin fecha es eucariota", "included_claim_ids": ["CLAIM-000009"],
                 "alternative_hypothesis_ids": ["HYP-000001"], "record_status": "active"}],
            "issues.jsonl": [{"id": "ISSUE-000001", "title": "Sin consenso", "record_status": "active",
                              "affects": {"record_ids": ["EVENT-000001"], "claim_ids": ["CLAIM-000001"]}}],
        }
        for nombre, filas in self.registros.items():
            (self.base / nombre).write_text("".join(json.dumps(f, ensure_ascii=False) + "\n" for f in filas),
                                            encoding="utf-8")

    def construir(self) -> dict:
        return cronologia.construir(self.base, self.raiz)


def reparto(datos: dict) -> list[str]:
    return [m["claim"] for m in datos["marcas"]] + datos["metodo"] + datos["en_fichas"] + [
        f["claim"] for f in datos["fuera"]]


class LibroReal(unittest.TestCase):
    """Invariantes sobre los registros del repositorio."""

    @classmethod
    def setUpClass(cls):
        cls.datos = cronologia.construir()

    def test_cada_afirmacion_activa_esta_en_un_solo_sitio(self):
        activas = {json.loads(l)["id"] for l in (cronologia.RECORDS / "claims.jsonl").read_text(
            encoding="utf-8").splitlines() if l.strip() and json.loads(l).get("record_status") == "active"}
        c = self.datos["vista"]["cuenta"]
        self.assertEqual(c["activas"], len(activas))
        self.assertEqual(c["en_el_eje"] + c["de_metodo"] + c["en_fichas"] + c["fuera"], len(activas))
        todas = reparto(self.datos)
        self.assertEqual(len(todas), len(set(todas)), "una afirmación está en dos sitios")
        self.assertEqual(set(todas), activas)

    def test_cada_datacion_tiene_una_marca_en_el_eje(self):
        eje = cronologia.svg(self.datos)
        for m in self.datos["marcas"]:
            self.assertEqual(eje.count(f'data-claim="{m["claim"]}"'), 1, m["claim"])
        self.assertEqual(len(re.findall(r'class="marca ', eje)), len(self.datos["marcas"]))

    def test_toda_marca_lleva_a_su_fuente_y_su_pasaje(self):
        for m in self.datos["marcas"]:
            f = self.datos["fichas"][m["claim"]]
            self.assertTrue(f["fuentes"], m["claim"])
            self.assertTrue(all(p["texto"] for p in f["pasajes"]), m["claim"])

    def test_la_pagina_sale_igual_dos_veces(self):
        self.assertEqual(cronologia.pagina(self.datos), cronologia.pagina(cronologia.construir()))


class Casos(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.libro = LibroMinimo(Path(self._tmp.name))
        self.datos = self.libro.construir()
        self.marca = {m["claim"]: m for m in self.datos["marcas"]}

    def tearDown(self):
        self._tmp.cleanup()

    def test_la_determinacion_decide_el_carril(self):
        self.assertEqual(self.marca["CLAIM-000001"]["carril"], "reloj")
        self.assertEqual(self.marca["CLAIM-000003"]["carril"], "roca")
        self.assertEqual(self.marca["CLAIM-000003"]["clase"], "fosil")
        self.assertEqual(self.marca["CLAIM-000004"]["clase"], "biomarcador")
        self.assertEqual(self.marca["CLAIM-000005"]["clase"], "registro")

    def test_cada_forma_de_fecha(self):
        formas = {c: (m["forma"], m["desde"], m["hasta"]) for c, m in self.marca.items()}
        self.assertEqual(formas["CLAIM-000001"], ("intervalo", 1800, 1600))
        self.assertEqual(formas["CLAIM-000002"], ("minimo", None, 1700))
        self.assertEqual(formas["CLAIM-000003"], ("punto", 1500, 1500))
        self.assertEqual(formas["CLAIM-000004"], ("geologico", 1600, 1000))
        self.assertEqual(formas["CLAIM-000005"], ("desde", 1050, None))

    def test_un_intervalo_que_la_carta_no_conoce_queda_fuera_con_su_motivo(self):
        self.assertNotIn("CLAIM-000011", self.marca)
        fuera = {f["claim"]: f["motivo"] for f in self.datos["fuera"]}
        self.assertIn("no se puede situar", fuera["CLAIM-000011"])

    def test_las_estimaciones_de_un_evento_no_se_funden(self):
        ev = self.datos["eventos"][0]
        self.assertEqual(ev["claims"], ["CLAIM-000001", "CLAIM-000002"])
        self.assertEqual(ev["rango"], [1800, 1600])
        self.assertEqual(ev["issues"], ["ISSUE-000001"])

    def test_que_entra_en_la_ficha_de_una_marca(self):
        relacionadas = lambda c: [r["id"] for r in self.datos["fichas"][c]["relacionadas"]]
        self.assertEqual(relacionadas("CLAIM-000003"), ["CLAIM-000006"])
        self.assertEqual(relacionadas("CLAIM-000004"), ["CLAIM-000007", "CLAIM-000008"])
        # Asignar a Eukaryota un fósil sin fecha no lo mete en la ficha de Eukaryota.
        self.assertEqual(relacionadas("CLAIM-000005"), [])
        fuera = {f["claim"] for f in self.datos["fuera"]}
        self.assertIn("CLAIM-000009", fuera)
        self.assertEqual(self.datos["metodo"], ["CLAIM-000010"])

    def test_una_hipotesis_sin_fecha_dice_que_no_llega_al_eje(self):
        h = {x["id"]: x for x in self.datos["hipotesis"]}
        self.assertEqual(h["HYP-000001"]["marcas"], ["CLAIM-000003"])
        self.assertEqual(h["HYP-000002"]["marcas"], [])
        self.assertEqual(h["HYP-000002"]["alternativas"], ["HYP-000001"])
        # La rival sale en la ficha del fósil datado, no como otra marca.
        self.assertEqual([x["id"] for x in self.datos["fichas"]["CLAIM-000003"]["hipotesis"]], ["HYP-000001"])

    def test_la_fecha_de_corte_es_la_del_corpus(self):
        v = self.datos["vista"]
        self.assertEqual(v["fecha_de_corte"], "2026-01-01")
        self.assertEqual(v["corpus"]["commit"], "abcdef0")

    def test_los_datos_no_cierran_el_script_que_los_lleva(self):
        # Un pasaje con «</script>» no puede cortar el bloque de datos.
        html = cronologia.pagina(self.datos)
        bloque = html.split('<script type="application/json" id="datos">', 1)[1].split("</script>", 1)[0]
        datos = json.loads(bloque)
        self.assertEqual(datos["fichas"]["CLAIM-000001"]["pasajes"][0]["texto"], "Un pasaje con </script> dentro.")

    def test_documento_y_fragmento(self):
        doc = cronologia.pagina(self.datos)
        frag = cronologia.pagina(self.datos, documento=False)
        self.assertTrue(doc.startswith("<!doctype html>"))
        self.assertIn("<title>Relojes y rocas</title>", doc)
        self.assertTrue(frag.startswith("<title>Relojes y rocas</title>"))
        self.assertNotIn("<html", frag)
        self.assertNotIn("<body", frag)


if __name__ == "__main__":
    unittest.main(verbosity=2)
