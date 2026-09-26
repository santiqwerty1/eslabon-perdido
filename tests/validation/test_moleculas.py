#!/usr/bin/env python3
"""Pruebas del esquema 1.3.0 (DEC-058): moléculas, `biomarker_of` y evidencia geoquímica.

Dos mitades. La familia «identidad» tiene que distinguir una molécula de quien
la produce, y los esquemas tienen que aceptar lo que la migración añade. Los
registros de prueba parten del fixture de referencia eukarya-minimal, no del
libro mayor, para que la prueba no dependa de lo que se haya ingerido.

Uso:
    python3 tests/validation/test_moleculas.py
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "validate"))

import validate  # noqa: E402
from families import identity  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "eukarya-minimal"


def primero(fichero: str) -> dict:
    return json.loads((FIXTURE / fichero).read_text(encoding="utf-8").splitlines()[0])


def afirmacion(cid: str, sujeto: str, predicado: str, objeto: dict) -> dict:
    return {"id": cid, "subject_id": sujeto, "predicate": predicado, "object": objeto}


class Identidad(unittest.TestCase):
    def errores(self, afirmaciones: list[dict]) -> list[str]:
        rep = validate.Report()
        identity.check({"claims.jsonl": afirmaciones}, rep)
        return rep.errors

    def test_biomarcador_de_un_grupo_pasa(self):
        self.assertEqual(self.errores([
            afirmacion("CLAIM-000901", "MOL-000901", "biomarker_of", {"entity_id": "CLADE-000901"}),
            afirmacion("CLAIM-000902", "MOL-000901", "biomarker_of", {"entity_id": "TRAIT-000901"}),
        ]), [])

    def test_biomarcador_con_sujeto_que_no_es_molecula_falla(self):
        [e] = self.errores([afirmacion("CLAIM-000901", "SPECIMEN-000901", "biomarker_of",
                                       {"entity_id": "CLADE-000901"})])
        self.assertIn("CLAIM-000901", e)
        self.assertIn("no es una molécula", e)

    def test_biomarcador_de_un_yacimiento_falla(self):
        [e] = self.errores([afirmacion("CLAIM-000901", "MOL-000901", "biomarker_of",
                                       {"entity_id": "SITE-000901"})])
        self.assertIn("SITE-000901", e)

    def test_una_molecula_asignada_a_un_taxon_falla(self):
        [e] = self.errores([afirmacion("CLAIM-000901", "MOL-000901", "assigned_to",
                                       {"entity_id": "CLADE-000901"})])
        self.assertIn("biomarker_of", e)

    def test_una_molecula_como_taxon_falla(self):
        [e] = self.errores([afirmacion("CLAIM-000901", "CLADE-000901", "descends_from",
                                       {"entity_id": "MOL-000901"})])
        self.assertIn("MOL-000901", e)

    def test_una_molecula_asignada_a_una_poblacion_falla(self):
        [e] = self.errores([afirmacion("CLAIM-000901", "MOL-000901", "assigned_to",
                                       {"entity_id": "POP-000901"})])
        self.assertIn("MOL-000901", e)

    def test_algo_asignado_a_una_molecula_falla(self):
        [e] = self.errores([afirmacion("CLAIM-000901", "SPECIMEN-000901", "assigned_to",
                                       {"entity_id": "MOL-000901"})])
        self.assertIn("objeto", e)

    def test_una_molecula_con_alias_a_un_taxon_falla(self):
        rep = validate.Report()
        identity.check({"molecules.jsonl": [{"id": "MOL-000901", "entity_type": "molecule",
                                             "preferred_label": "esterano", "alias_ids": ["CLADE-000901"]}]}, rep)
        self.assertTrue(any("alias" in e and "MOL-000901" in e for e in rep.errors), rep.errors)

    def test_una_molecula_no_es_ancestro_ni_miembro_de_nada(self):
        # Los predicados que la lista de especímenes deja pasar tampoco valen.
        for pred in ("possible_ancestor_of", "possible_sampled_ancestor_of", "member_of",
                     "chronological_continuation_of", "acquires_trait"):
            [e] = self.errores([afirmacion("CLAIM-000901", "MOL-000901", pred, {"entity_id": "CLADE-000901"})])
            self.assertIn(pred, e)

    def test_una_molecula_en_un_ambiente_pasa(self):
        self.assertEqual(self.errores([afirmacion("CLAIM-000901", "MOL-000901", "occurs_in",
                                                  {"category": "rocas arcaicas"})]), [])

    def test_una_molecula_clasificada_en_una_categoria_pasa(self):
        # «interpretados como biomarcadores singenéticos» (C-741): una
        # categoría, no un taxón.
        self.assertEqual(self.errores([afirmacion("CLAIM-000901", "MOL-000901", "classified_as_by",
                                                  {"category": "biomarcadores singenéticos"})]), [])

    def test_el_prefijo_de_una_molecula_es_MOL(self):
        rep = validate.Report()
        identity.check({"molecules.jsonl": [{"id": "CLADE-000901", "entity_type": "molecule",
                                             "preferred_label": "esterano"}]}, rep)
        self.assertTrue(any("MOL-" in e for e in rep.errors), rep.errors)


@unittest.skipUnless(importlib.util.find_spec("jsonschema"), "la familia schema necesita jsonschema")
class Esquemas(unittest.TestCase):
    def validar(self, ficheros: dict[str, list[dict]]) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            for fichero, recs in ficheros.items():
                (Path(tmp) / fichero).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in recs),
                                                 encoding="utf-8")
            return validate.run(["schema"], records_dir=Path(tmp)).errors

    def test_lo_que_añade_la_migracion_valida(self):
        molecula = {**primero("clades.jsonl"), "id": "MOL-000901", "entity_type": "molecule",
                    "preferred_label": "24-isopropilcolestano", "claim_ids": ["CLAIM-000901"]}
        claim = {**primero("claims.jsonl"), "id": "CLAIM-000901", "claim_type": "relational",
                 "subject_id": "MOL-000901", "predicate": "biomarker_of", "object": {"entity_id": "CLADE-000001"}}
        evid = {"id": "EVID-000901", "evidence_type": "geochemical", "description": "Esteranos en una roca.",
                "source_id": "SRC-000100", "supports_claim_ids": ["CLAIM-000901"], "challenges_claim_ids": [],
                "provenance": claim["provenance"], "record_status": "active"}
        occ = {"id": "OCC-000901", "entity_id": "MOL-000901", "temporal_expression_id": None, "site_id": None,
               "region_id": None, "location_precision": "unknown", "evidence_basis": "observed",
               "record_status": "active"}
        mencion = {**primero("mentions.jsonl"), "id": "MENTION-000901", "mention_type": "molecule"}
        self.assertEqual(self.validar({"molecules.jsonl": [molecula], "claims.jsonl": [claim],
                                       "evidence.jsonl": [evid], "occurrences.jsonl": [occ],
                                       "mentions.jsonl": [mencion]}), [])

    def test_una_molecula_con_otro_prefijo_no_valida(self):
        molecula = {**primero("clades.jsonl"), "id": "CLADE-000901", "entity_type": "molecule"}
        self.assertNotEqual(self.validar({"molecules.jsonl": [molecula]}), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
