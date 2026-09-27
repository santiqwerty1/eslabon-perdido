#!/usr/bin/env python3
"""Pruebas de `scripts/ingest/absorber.py informe` (DEC-059).

Un libro mayor de prueba con la sección 0 de `corredor-mini` ingerida y
convertida y la 1 sólo ingerida, frente a `corredor-mini-v2`, que trae un caso
de cada clase (su README los lista). Todo ocurre en un directorio temporal.
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from entorno import MINI, ROOT, Entorno  # noqa: E402

import absorber  # noqa: E402
import convertir  # noqa: E402
import corredor  # noqa: E402
import delta as delta_mod  # noqa: E402

MINI_V2 = ROOT / "tests" / "fixtures" / "corredor-mini-v2"


# Convertir la sección 0 exige jsonschema, como en test_convertir.py.
@unittest.skipUnless(importlib.util.find_spec("jsonschema"), "convertir.py exige jsonschema")
class Informe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.tmp = Path(cls._tmp.name)
        cls.entorno = Entorno(cls.tmp).__enter__()
        deltas = cls.tmp / "deltas"
        with contextlib.redirect_stdout(io.StringIO()):
            assert delta_mod.cmd(deltas / "SEC-000001.json", False, False) == 0
            spec = cls.tmp / "corredor-00.json"
            spec.write_text(json.dumps(cls.entorno.spec(), ensure_ascii=False), encoding="utf-8")
            assert convertir.convertir(spec, str(MINI), False) == 0
            assert delta_mod.cmd(deltas / "SEC-000001-conversion.json", False, False) == 0
            corredor.ingerir(str(MINI), "01", None, False)
            assert delta_mod.cmd(deltas / "SEC-000002.json", False, False) == 0
        cls.conversion = json.loads((deltas / "SEC-000001-conversion.json").read_text(encoding="utf-8"))
        cls.r = absorber.informe(str(MINI), str(MINI_V2))
        cls.filas = {f["row"]: f for f in cls.r["sections"]["00"]["rows"]}

    @classmethod
    def tearDownClass(cls):
        cls.entorno.__exit__(None, None, None)
        cls._tmp.cleanup()

    def test_cada_fila_que_cambia_tiene_su_clase(self):
        self.assertEqual({c: f["class"] for c, f in self.filas.items()},
                         {"C-001": "modificada", "C-003": "modificada", "C-005": "retirada"})
        self.assertEqual(self.r["sections"]["00"]["unchanged"], 2)

    def test_una_fila_modificada_lleva_sus_registros_y_si_es_su_primera_fila(self):
        f = self.filas["C-001"]
        registros = self.conversion["conversion"]["rows"]["C-001"]["record_ids"]
        self.assertEqual(f["record_ids"], registros)
        # Todos salen sólo de C-001: es su primera fila, y de ella salen sus ejes.
        self.assertEqual(f["first_row_of"], registros)
        self.assertEqual(sorted(f["columns"]), ["Fuerza", "Motivo"])
        self.assertTrue(any("ejes" in t for t in f["touches"]))

    def test_la_division_sale_del_fichero_de_sucesiones(self):
        self.assertEqual(self.filas["C-003"]["successors"], ["C-007", "C-008"])
        nuevas = {n["row"]: n["successor_of"] for n in self.r["sections"]["00"]["new_rows"]}
        self.assertEqual(nuevas, {"C-007": ["C-003"], "C-008": ["C-003"], "C-009": []})

    def test_una_retirada_sin_sucesoras_se_avisa(self):
        self.assertIn("sin sucesoras", self.filas["C-005"]["aviso"])

    def test_la_renumeracion_de_una_seccion_ingerida_sin_convertir(self):
        s = self.r["sections"]["01"]
        self.assertFalse(s["converted"])
        self.assertEqual([(f["row"], f["class"], f["to"]) for f in s["rows"]], [("C-006", "renumerada", "C-010")])
        self.assertTrue(any("01" in a and "sin convertir" in a for a in self.r["warnings"]))

    def test_una_fuente_que_ya_es_registro_y_cambia(self):
        [f] = self.r["sources"]
        self.assertEqual((f["key"], f["state"], f["fields"]), ("S01", "modificada", ["title"]))
        self.assertTrue(f["record_id"].startswith("SRC-"))

    def test_una_entidad_retirada_lleva_sus_menciones(self):
        [e] = self.r["entities"]
        self.assertEqual((e["label"], e["state"], e["section"], e["row"]), ("FIX-Omega", "retirada", "00", "C-003"))
        self.assertEqual(len(e["mention_ids"]), 1)

    def test_los_pasajes_que_cambian_y_donde_se_cita_ahora_cada_fila(self):
        s = self.r["sections"]["00"]
        self.assertEqual(Counter(p["estado"] for p in s["passages"]),
                         Counter({"retirado": 1, "nuevo": 3, "desplazado": 3}))
        # FIX-Gamma colgaba del párrafo de C-002–C-003, que se reescribe: C-002
        # se cita ahora en el tercer párrafo.
        [m] = [m for m in s["mentions"] if m["label"] == "FIX-Gamma"]
        self.assertEqual((m["state"], m["cited_in"]), ("retirado", [3]))
        self.assertIn("su pasaje desaparece", m["what"])

    def test_una_mencion_de_un_pasaje_reescrito_dice_si_su_etiqueta_sigue(self):
        # El párrafo de la sección 1 sólo cambia su cita, de C-006 a C-010.
        menciones = {m["label"]: m for m in self.r["sections"]["01"]["mentions"]}
        self.assertIn("la etiqueta sigue en él", menciones["FIX-Zeta"]["what"])
        self.assertIn("no aparecía literal y sigue sin aparecer", menciones["taxón histórico"]["what"])
        # Y se busca por su número nuevo: la prosa nueva cita C-010, no C-006.
        self.assertEqual(menciones["FIX-Zeta"]["cited_in"], [2])

    def test_el_esqueleto_pide_una_decision_por_cambio(self):
        e = absorber.esqueleto(self.r)
        filas = e["sections"]["00"]["rows"]
        self.assertEqual(set(filas), {"C-001", "C-003", "C-005", "C-007", "C-008", "C-009"})
        self.assertTrue(all(f.get("decision", "sin decisión") is None for c, f in filas.items()
                            if c in ("C-001", "C-003", "C-005")))
        self.assertTrue(all(filas[c]["destination"] is None for c in ("C-007", "C-008", "C-009")))
        self.assertEqual(filas["C-003"]["successors"], {"C-007": [], "C-008": []})
        self.assertEqual(set(e["sections"]["01"]["rows"]), {"C-006"})
        self.assertEqual(list(e["sources"]), ["S01"])
        self.assertEqual(e["from"]["fingerprint"], self.entorno.huella)

    def test_antes_tiene_que_ser_la_congelacion_activa(self):
        with self.assertRaises(SystemExit) as e:
            absorber.informe(str(MINI_V2), str(MINI))
        self.assertIn("no es la versión congelada", str(e.exception))

    def test_el_informe_se_escribe_fuera_del_libro_mayor(self):
        antes = sorted(p.name for p in (self.tmp / "deltas").iterdir())
        salida = self.tmp / "absorcion"
        with contextlib.redirect_stdout(io.StringIO()):
            absorber.cmd_informe(argparse.Namespace(anterior=str(MINI), nueva=str(MINI_V2), salida=str(salida)))
        self.assertEqual(sorted(p.name for p in (self.tmp / "deltas").iterdir()), antes)
        diff = json.loads((salida / "diff.json").read_text(encoding="utf-8"))
        self.assertIn({"de": "C-006", "a": "C-010", "via": "contenido"}, diff["afirmaciones"]["correspondencia"])
        esqueleto = json.loads((salida / f"corredor-{self.r['suffix']}.json").read_text(encoding="utf-8"))
        self.assertEqual(esqueleto["decision"], "DEC-059")
        self.assertIn("C-003", (salida / "informe.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
