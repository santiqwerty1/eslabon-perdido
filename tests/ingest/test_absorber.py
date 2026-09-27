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
import shutil
import subprocess
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

    def version(self, cambios: dict[str, str | None]) -> Path:
        """Una copia de corredor-mini-v2 con ficheros reescritos (None: se borra)."""
        copia = Path(tempfile.mkdtemp(dir=self.tmp)) / "corpus"
        shutil.copytree(MINI_V2, copia)
        for ruta, texto in cambios.items():
            if texto is None:
                (copia / ruta).unlink()
            else:
                (copia / ruta).write_text(texto, encoding="utf-8")
        return copia

    def texto(self, ruta: str) -> str:
        return (MINI_V2 / ruta).read_text(encoding="utf-8")

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
        # También lo que el registro guarda fuera de la bibliografía: la fecha de
        # consulta y las notas de calidad.
        [f] = self.r["sources"]
        self.assertEqual((f["key"], f["state"], f["fields"]), ("S01", "modificada", ["title", "consulted_at"]))
        self.assertTrue(f["record_id"].startswith("SRC-"))

    def test_una_entidad_retirada_lleva_sus_menciones(self):
        [e] = self.r["entities"]
        self.assertEqual((e["label"], e["state"], e["section"], e["row_before"], e["row_after"]),
                         ("FIX-Omega", "retirada", "00", "C-003", None))
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

    def test_una_tabla_que_deja_de_citar_una_fila_cambia_su_procedencia(self):
        # C-004 no cambia, pero la tabla de edades deja de citarla: al ingerirla
        # colgaría del registro y no de la tabla, como decide corredor.construir.
        p = self.r["sections"]["00"]["provenance"]["C-004"]
        self.assertEqual((p["via_before"], p["via_after"]), ("tabla table-01-00-edades", "sólo el registro"))
        self.assertFalse(p["mechanical"])
        e = absorber.esqueleto(self.r)
        self.assertIsNone(e["sections"]["00"]["provenance"]["C-004"]["decision"])

    def test_las_entidades_del_apendice_b_piden_decision(self):
        e = absorber.esqueleto(self.r)
        [omega] = [x for x in e["entities"] if x["label"] == "FIX-Omega"]
        self.assertEqual((omega["state"], omega["section"]), ("retirada", "00"))
        self.assertIsNone(omega["decision"])

    def test_una_seccion_cuya_prosa_desaparece_pide_decisiones(self):
        v = self.version({"docs/secciones/002-01-1-historia.md": None})
        r = absorber.informe(str(MINI), str(v))
        s = r["sections"]["01"]
        self.assertEqual({p["estado"] for p in s["passages"]}, {"retirado"})
        [zeta] = [m for m in s["mentions"] if m["label"] == "FIX-Zeta"]
        self.assertEqual(zeta["state"], "retirado")
        self.assertFalse(s["provenance"]["C-006"]["mechanical"])
        e = absorber.esqueleto(r)
        self.assertIsNone(e["sections"]["01"]["provenance"]["C-006"]["decision"])

    def test_una_fila_nueva_que_reutiliza_un_numero_no_se_atribuye_a_la_vieja(self):
        # C-006 se renumeró a C-010; una fila nueva ocupa el número C-006 y un
        # apéndice la cita. Esa cita no es de la C-006 que se ingirió.
        fila = ('"C-006","FIX-Zeta tiene una edad.","FIX-Zeta","tiene_edad_estimada","n/a","expresa",'
                '"S01 x","no evaluado","baja","m","resuelta","vigente"\n')
        v = self.version({"data/afirmaciones/01.csv": self.texto("data/afirmaciones/01.csv") + fila,
                          "data/apendices/D_fechas.csv": '"evento","filas"\n"edad de FIX-Zeta","C-006"\n'})
        r = absorber.informe(str(MINI), str(v))
        # El cambio del apéndice no desaparece: va con la fila nueva, sin
        # registros de la vieja.
        [d] = [x for x in r["appendices"] if x["path"].endswith("D_fechas.csv")]
        self.assertEqual((d["rows"], d["new_rows"], d["record_ids"], d["sections"]), ([], ["C-006"], [], ["01"]))
        self.assertEqual(absorber.esqueleto(r)["appendices"][d["path"]][0]["new_rows"], ["C-006"])
        self.assertIn("C-006", [n["row"] for n in r["sections"]["01"]["new_rows"]])

    def test_una_entidad_que_cambia_de_primera_fila_afecta_a_las_dos_secciones(self):
        b = self.texto("data/apendices/B_entidades.csv").replace('"FIX-Delta","clado","n/a","n/a","C-002"',
                                                                  '"FIX-Delta","clado","n/a","n/a","C-010"')
        r = absorber.informe(str(MINI), str(self.version({"data/apendices/B_entidades.csv": b})))
        delta = {e["section"]: e for e in r["entities"] if e["label"] == "FIX-Delta"}
        self.assertEqual(set(delta), {"00", "01"})
        self.assertTrue(delta["00"]["mention_ids"])
        self.assertEqual(delta["01"]["mention_ids"], [])

    def test_una_entidad_que_cambia_de_primera_fila_en_su_seccion_conserva_las_dos(self):
        b = self.texto("data/apendices/B_entidades.csv").replace('"FIX-Gamma","clado","n/a","n/a","C-002"',
                                                                  '"FIX-Gamma","clado","n/a","n/a","C-009"')
        r = absorber.informe(str(MINI), str(self.version({"data/apendices/B_entidades.csv": b})))
        [gamma] = [e for e in r["entities"] if e["label"] == "FIX-Gamma"]
        self.assertEqual((gamma["section"], gamma["side"], gamma["row_before"], gamma["row_after"]),
                         ("00", "ambos", "C-002", "C-009"))
        [x] = [x for x in absorber.esqueleto(r)["entities"] if x["label"] == "FIX-Gamma"]
        self.assertEqual((x["row_before"], x["row_after"]), ("C-002", "C-009"))

    def test_un_delta_aplicado_y_editado_no_da_correspondencia(self):
        # Los registros salieron del delta que se aplicó; si el fichero cambió,
        # su mapa de filas ya no los describe.
        ruta = self.tmp / "deltas" / "SEC-000002.json"
        original = ruta.read_bytes()
        ruta.write_bytes(original + b"\n")
        try:
            with self.assertRaises(SystemExit) as e:
                absorber.informe(str(MINI), str(MINI_V2))
        finally:
            ruta.write_bytes(original)
        self.assertIn("SEC-000002.json", str(e.exception))

    def test_una_columna_nueva_del_apendice_b_cuenta_solo_donde_tiene_valor(self):
        lineas = self.texto("data/apendices/B_entidades.csv").splitlines()
        b = [lineas[0] + ',"notas"'] + [l + (',"revisada"' if l.startswith('"FIX-Gamma"') else ',""')
                                          for l in lineas[1:]]
        r = absorber.informe(str(MINI), str(self.version({"data/apendices/B_entidades.csv": "\n".join(b) + "\n"})))
        self.assertEqual({e["label"] for e in r["entities"]}, {"FIX-Omega", "FIX-Gamma"})
        [gamma] = [e for e in r["entities"] if e["label"] == "FIX-Gamma"]
        self.assertEqual(gamma["columns"], ["notas"])

    def test_las_sucesiones_se_buscan_por_el_numero_nuevo(self):
        # C-005 vuelve como C-013, superada y con su sucesora declarada por el
        # número nuevo.
        c013 = ('"C-013","FIX-Alfa y FIX-Gamma son el arranque del corredor.","FIX-Alfa","forma_con*","FIX-Gamma",'
                '"sintesis(C-001; C-002)","n/a","no evaluado","media","Se sigue de C-001 y C-002.","resuelta",'
                '"superada"\n')
        suc = self.texto("data/auditoria/sucesiones_afirmaciones.csv") + '"C-013","C-009","Superada.","2026-09-27T00:00:00Z"\n'
        v = self.version({"data/afirmaciones/00.csv": self.texto("data/afirmaciones/00.csv") + c013,
                          "data/auditoria/sucesiones_afirmaciones.csv": suc})
        r = absorber.informe(str(MINI), str(v))
        [f] = [f for f in r["sections"]["00"]["rows"] if f["row"] == "C-005"]
        self.assertEqual((f["to"], f["successors"]), ("C-013", ["C-009"]))
        self.assertNotIn("aviso", f)

    def test_una_sucesion_nueva_sin_cambio_de_fila_pide_decision(self):
        suc = self.texto("data/auditoria/sucesiones_afirmaciones.csv") + '"C-002","C-009","Otra.","2026-09-27T00:00:00Z"\n'
        r = absorber.informe(str(MINI), str(self.version({"data/auditoria/sucesiones_afirmaciones.csv": suc})))
        s = r["sections"]["00"]["successions"]
        self.assertEqual(s["C-002"], {"to": "C-002", "before": [], "after": ["C-009"]})
        self.assertNotIn("C-003", s)  # ya sale en sus filas, con sus sucesoras
        self.assertIsNone(absorber.esqueleto(r)["sections"]["00"]["successions"]["C-002"]["decision"])

    def test_una_tabla_fuera_de_la_capa_canonica_se_rechaza(self):
        indice = self.texto("data/table_index.json").replace("data/tablas/00/table-01-00-edades.csv",
                                                             "data/tablas/00/no-existe.csv")
        with self.assertRaises(SystemExit) as e:
            absorber.informe(str(MINI), str(self.version({"data/table_index.json": indice})))
        self.assertIn("no-existe.csv", str(e.exception))

    def test_una_fila_que_cambia_de_seccion_desfasa_los_dos_borradores(self):
        seccion0 = self.texto("data/afirmaciones/00.csv").splitlines(keepends=True)
        [c004] = [l for l in seccion0 if l.startswith('"C-004"')]
        v = self.version({"data/afirmaciones/00.csv": "".join(l for l in seccion0 if l != c004),
                          "data/afirmaciones/01.csv": self.texto("data/afirmaciones/01.csv")
                          + c004.replace('"C-004"', '"C-011"')})
        borradores = {"00": self.tmp / "corredor-00-borrador.json", "01": self.tmp / "corredor-01.json"}
        for sec, ruta in borradores.items():
            ruta.write_text(json.dumps({"freeze": {"fingerprint": self.entorno.huella}, "section": sec}),
                            encoding="utf-8")
        try:
            r = absorber.informe(str(MINI), str(v))
        finally:
            for ruta in borradores.values():
                ruta.unlink()
        cambiadas = {d["section"]: d["changed_rows"] for d in r["drafts"]}
        self.assertIn("C-004", cambiadas["00"])
        self.assertIn("C-011", cambiadas["01"])
        self.assertNotIn("C-004", cambiadas["01"])

    def test_un_borrador_de_una_seccion_solo_renumerada_se_senala(self):
        borrador = self.tmp / "corredor-01.json"
        borrador.write_text(json.dumps({"freeze": {"fingerprint": self.entorno.huella}, "section": "01"}),
                            encoding="utf-8")
        try:
            r = absorber.informe(str(MINI), str(MINI_V2))
        finally:
            borrador.unlink()
        self.assertEqual([(d["section"], d["changed_rows"]) for d in r["drafts"]], [("01", ["C-006"])])

    def test_un_delta_pendiente_no_cuenta_como_libro_mayor(self):
        # Un delta sin aplicar que ya pusiera S01 al día no puede hacer creer al
        # informe que el registro está al día.
        rid = self.r["sources"][0]["record_id"]
        antes = next(json.loads(l) for l in (self.entorno.records / "sources.jsonl").read_text(
            encoding="utf-8").splitlines() if json.loads(l)["id"] == rid)
        despues = {**antes, "title": "Trabajo ficticio número uno", "consulted_at": "2026-09-27"}
        pendiente = self.tmp / "deltas" / "SEC-000099.json"
        pendiente.write_text(json.dumps({
            "dataset_revision_before": "REV-000003", "dataset_revision_after": "REV-000004",
            "operations": [{"operation": "UPDATE_RECORD", "file": "sources.jsonl", "record_id": rid,
                            "before": antes, "after": despues}]}), encoding="utf-8")
        try:
            r = absorber.informe(str(MINI), str(MINI_V2))
        finally:
            pendiente.unlink()
        self.assertEqual(r["sources"][0]["fields"], ["title", "consulted_at"])
        self.assertTrue(any("sin aplicar" in a for a in r["warnings"]))

    def test_una_copia_con_cambios_sin_confirmar_se_nombra_por_su_huella(self):
        # Su commit no describe lo que se compara: dos copias distintas no pueden
        # compartir carpeta de salida ni nombre de congelación.
        copia = self.tmp / "copia"
        shutil.copytree(MINI_V2, copia)
        git = ["git", "-C", str(copia), "-c", "user.name=x", "-c", "user.email=x@x"]
        for orden in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "v2"]):
            subprocess.run(git + orden, check=True, capture_output=True)
        with (copia / "data" / "afirmaciones" / "01.csv").open("a", encoding="utf-8") as fh:
            fh.write('"C-011","Otra.","FIX-Zeta","es","otra","expresa","S01 x","no evaluado","baja","m","resuelta","vigente"\n')
        r = absorber.informe(str(MINI), str(copia))
        self.assertIsNone(r["to"]["commit"])
        self.assertEqual(r["suffix"], r["to"]["fingerprint"].split(":")[1][:7])

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
        texto = (salida / "informe.md").read_text(encoding="utf-8")
        self.assertIn("C-003", texto)
        self.assertIn("C-004", texto)


if __name__ == "__main__":
    unittest.main(verbosity=2)
