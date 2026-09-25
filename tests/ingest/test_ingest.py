#!/usr/bin/env python3
"""Ingestión de una sección del corredor, sobre `tests/fixtures/corredor-mini`.

El fixture tiene una fila de cada clase que importa: citada en un párrafo,
citada por un rango «C-002–C-003», citada sólo por una tabla y no citada en
ningún sitio; etiquetas que aparecen literales en su pasaje y otras que no; una
entidad del apéndice B que no es sujeto ni objeto de nada; y el apéndice A con la
cabecera larga del DOI, que es la del corpus real.

Nada de esto escribe en knowledge/: se prueba `construir`, que no escribe, con
los directorios de pasajes y deltas redirigidos a un temporal cuando hace falta.

Uso:
    python3 tests/ingest/test_ingest.py
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

import corredor  # noqa: E402
import freeze  # noqa: E402
import ingest  # noqa: E402
from parse_research import parse  # noqa: E402

MINI = ROOT / "tests" / "fixtures" / "corredor-mini"


def congelar(directorio: Path, destino: Path) -> Path:
    with contextlib.redirect_stdout(io.StringIO()):
        freeze.cmd_create(argparse.Namespace(fuente=str(directorio), salida=str(destino), repositorio="x",
                                             decision=None, sustituye=None, fecha="2026-09-25"))
    return destino


class Seccion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.tmp = Path(cls._tmp.name)
        cls.congelacion = congelar(MINI, cls.tmp / "mini.json")
        cls.r = corredor.construir(str(MINI), "0", cls.congelacion)
        cls.texto = cls.r["texto"]
        cls.menciones = {m["original_text"]: m for m in cls.r["menciones"]}
        cls.filas = cls.r["delta"]["corpus_origin"]["rows"]
        cls.ordinal = {p["id"]: p["ordinal"] for p in cls.r["pasajes"]}

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_solo_las_filas_de_la_seccion(self):
        self.assertEqual(list(self.filas), ["C-001", "C-002", "C-003", "C-004", "C-005"])
        self.assertNotIn("FIX-Zeta", self.menciones)

    def test_offsets_de_pasaje_reales(self):
        for p in self.r["pasajes"]:
            o = p["character_offsets"]
            self.assertEqual(self.texto[o["start"]:o["end"]], p["text"])

    def test_cada_fila_vuelve_a_su_pasaje(self):
        ordinal = lambda fila: [self.ordinal[p] for p in self.filas[fila]["passage_ids"]]
        self.assertEqual((self.filas["C-001"]["via"], ordinal("C-001")), ("prosa", [2]))
        # El rango C-002–C-003 cita las dos.
        self.assertEqual(ordinal("C-002"), [3])
        self.assertEqual(ordinal("C-003"), [3])
        self.assertTrue(self.filas["C-004"]["via"].startswith("tabla"))
        self.assertIn("TABLE:table-01", self.r["pasajes"][ordinal("C-004")[0] - 1]["text"])
        self.assertEqual(self.filas["C-005"]["via"], "sólo el registro")
        self.assertIn("TABLE:claims-00", self.r["pasajes"][ordinal("C-005")[0] - 1]["text"])

    def test_menciones_con_literal_y_sin_el(self):
        alfa = self.menciones["FIX-Alfa"]
        o = alfa["character_offsets"]
        self.assertEqual(self.texto[o["start"]:o["end"]], "FIX-Alfa")
        self.assertEqual(self.ordinal[alfa["passage_id"]], 2)
        # FIX-Delta no aparece en el párrafo que cita C-002: los offsets cubren
        # el pasaje entero y una nota lo dice.
        delta = self.menciones["FIX-Delta"]
        p = next(p for p in self.r["pasajes"] if p["id"] == delta["passage_id"])
        self.assertEqual(delta["character_offsets"], p["character_offsets"])
        self.assertTrue(any("no aparece literal" in n for n in delta["notes"]))

    def test_entidad_del_apendice_b_que_no_es_sujeto_ni_objeto(self):
        omega = self.menciones["FIX-Omega"]
        self.assertTrue(any("apéndice B" in n for n in omega["notes"]))
        self.assertEqual(self.ordinal[omega["passage_id"]], 3)  # su primera fila es C-003

    def test_celdas_que_no_nombran_nada_no_son_menciones(self):
        self.assertNotIn("n/a", self.menciones)
        self.assertIn("n/a", self.r["descartadas"])

    def test_todo_queda_pendiente_de_identidad(self):
        for m in self.r["menciones"]:
            self.assertEqual(m["mention_type"], "unresolved")
            self.assertEqual(m["resolution"]["status"], "pending")

    def test_el_delta_lleva_el_rastro_de_la_congelacion(self):
        origen = self.r["delta"]["corpus_origin"]
        registro = json.loads(self.congelacion.read_text(encoding="utf-8"))
        self.assertEqual(origen["freeze"]["fingerprint"], registro["fingerprint"])
        self.assertEqual(origen["section"], "00")
        menciones_de_c001 = {m for m in origen["rows"]["C-001"]["mention_ids"]}
        self.assertEqual(menciones_de_c001, {self.menciones["FIX-Alfa"]["id"], self.menciones["FIX-Beta"]["id"]})

    def test_contraste_cuadra(self):
        for etiqueta, declarado, ingerido in self.r["contraste"]:
            self.assertEqual(declarado, ingerido, etiqueta)

    def test_registros_validos_contra_el_esquema(self):
        try:
            import validate
            from jsonschema import Draft202012Validator  # noqa: F401
        except ImportError:
            self.skipTest("jsonschema no instalado")
        rep = validate.Report()
        validate.v_schema({"mentions.jsonl": self.r["menciones"]}, rep)
        self.assertEqual(rep.errors, [])


class Barreras(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.congelacion = congelar(MINI, self.tmp / "mini.json")

    def tearDown(self):
        self._tmp.cleanup()

    def test_una_copia_que_no_es_la_congelada_no_se_ingiere(self):
        otra = self.tmp / "otra"
        shutil.copytree(MINI, otra)
        (otra / "docs" / "secciones" / "001-00-0-arranque.md").write_text("# 0. Otra cosa\n", encoding="utf-8")
        with self.assertRaises(SystemExit) as e:
            corredor.construir(str(otra), "00", self.congelacion)
        self.assertIn("no es la versión congelada", str(e.exception))

    def test_una_seccion_ya_ingerida_no_se_repite(self):
        deltas = self.tmp / "deltas"
        deltas.mkdir()
        (deltas / "SEC-000001.json").write_text(json.dumps({"corpus_origin": {"section": "00"}}), encoding="utf-8")
        original, ingest.DELTAS = ingest.DELTAS, deltas
        try:
            with self.assertRaises(SystemExit) as e:
                corredor.construir(str(MINI), "00", self.congelacion)
            self.assertIn("ya se ingirió", str(e.exception))
        finally:
            ingest.DELTAS = original

    def test_los_pasajes_siguen_la_numeracion_existente(self):
        # Antes se buscaban en mentions.jsonl, donde no están, y cada sección
        # volvía a empezar en PASSAGE-000001.
        pasajes = self.tmp / "passages"
        pasajes.mkdir()
        (pasajes / "SEC-000001.json").write_text(json.dumps([{"id": "PASSAGE-000041"}]), encoding="utf-8")
        original, ingest.PASSAGES = ingest.PASSAGES, pasajes
        try:
            r = corredor.construir(str(MINI), "00", self.congelacion)
        finally:
            ingest.PASSAGES = original
        self.assertEqual(r["pasajes"][0]["id"], "PASSAGE-000042")

    def test_seccion_sin_registro(self):
        with self.assertRaises(SystemExit):
            corredor.construir(str(MINI), "17", self.congelacion)


class Doi(unittest.TestCase):
    def test_la_cabecera_larga_del_doi_se_lee(self):
        datos, h = parse(MINI)
        self.assertEqual(h.errores, [])
        self.assertEqual([f["doi"] for f in datos["sources"]],
                         ["https://doi.org/10.0000/fixture.1", "https://doi.org/10.0000/fixture.2"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
