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
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from entorno import MINI, ROOT, Entorno  # noqa: E402

import absorber  # noqa: E402
import convertir  # noqa: E402
import corredor  # noqa: E402
import delta as delta_mod  # noqa: E402
import freeze  # noqa: E402
import ingest  # noqa: E402

sys.path.insert(0, str(ROOT / "scripts" / "snapshot"))
import snapshot  # noqa: E402

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

    def con_registro_viejo(self, viejo: dict[str, list[str]]):
        """corredor-mini no trae registro de sucesiones: éste hace de registro de antes."""
        leer = absorber.leer_sucesiones
        return mock.patch.object(absorber, "leer_sucesiones",
                                 lambda raiz: viejo if Path(raiz).resolve() == MINI.resolve() else leer(raiz))

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

    def test_un_fichero_de_conversion_editado_no_da_primeras_filas(self):
        # Las filas de cada registro salen del fichero que se convirtió; si
        # cambió después, ya no se sabe de qué fila salen sus ejes.
        ruta = absorber.base.ROOT / self.conversion["conversion"]["spec"]["path"]
        original = ruta.read_bytes()
        ruta.write_bytes(original + b"\n")
        try:
            r = absorber.informe(str(MINI), str(MINI_V2))
        finally:
            ruta.write_bytes(original)
        [f] = [f for f in r["sections"]["00"]["rows"] if f["row"] == "C-001"]
        self.assertEqual(f["first_row_of"], [])
        self.assertTrue(any("primera fila" in a for a in r["warnings"]))

    def test_una_sucesora_retirada_no_es_la_fila_nueva_que_reutiliza_su_numero(self):
        # Antes, C-002 → C-005. C-005 se retira y una fila nueva de la sección 1
        # ocupa su número: el registro nuevo apunta a otra afirmación.
        fila = ('"C-005","FIX-Zeta tiene otra edad.","FIX-Zeta","tiene_edad_estimada","n/a","expresa",'
                '"S01 x","no evaluado","baja","m","resuelta","vigente"\n')
        suc = self.texto("data/auditoria/sucesiones_afirmaciones.csv") + '"C-002","C-005","Otra.","2026-09-27T00:00:00Z"\n'
        v = self.version({"data/afirmaciones/01.csv": self.texto("data/afirmaciones/01.csv") + fila,
                          "data/auditoria/sucesiones_afirmaciones.csv": suc})
        with self.con_registro_viejo({"C-002": ["C-005"]}):
            r = absorber.informe(str(MINI), str(v))
        self.assertIn("C-005", {n["row"] for n in r["sections"]["01"]["new_rows"]})
        self.assertEqual(r["sections"]["00"]["successions"]["C-002"],
                         {"to": "C-002", "before": ["C-005[retirada]"], "after": ["C-005"]})

    def test_una_fila_que_cambia_conserva_sus_sucesoras_de_antes(self):
        with self.con_registro_viejo({"C-003": ["C-004"]}):
            r = absorber.informe(str(MINI), str(MINI_V2))
        [f] = [f for f in r["sections"]["00"]["rows"] if f["row"] == "C-003"]
        self.assertEqual((f["successors"], f["successors_before"]), (["C-007", "C-008"], ["C-004"]))
        self.assertEqual(absorber.esqueleto(r)["sections"]["00"]["rows"]["C-003"]["successors_before"], ["C-004"])
        # Si el registro nuevo la borra, lo de antes sigue ahí y se avisa.
        cabecera = self.texto("data/auditoria/sucesiones_afirmaciones.csv").splitlines(keepends=True)[0]
        with self.con_registro_viejo({"C-003": ["C-004"]}):
            r = absorber.informe(str(MINI), str(self.version({"data/auditoria/sucesiones_afirmaciones.csv": cabecera})))
        [f] = [f for f in r["sections"]["00"]["rows"] if f["row"] == "C-003"]
        self.assertNotIn("successors", f)
        self.assertEqual(f["successors_before"], ["C-004"])
        self.assertIn("le quita sus sucesoras", f["aviso"])

    def test_dos_ficheros_de_prosa_para_una_seccion_se_rechazan(self):
        with self.assertRaises(SystemExit) as e:
            absorber.informe(str(MINI), str(self.version({"docs/secciones/002-00-1-otra.md": "# Otra\n\nC-001.\n"})))
        self.assertIn("ficheros de prosa", str(e.exception))

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

    def test_un_fichero_de_absorcion_revisado_no_se_sobrescribe(self):
        salida = self.tmp / "absorcion-revisada"
        args = argparse.Namespace(anterior=str(MINI), nueva=str(MINI_V2), salida=str(salida), sobrescribir=False)
        with contextlib.redirect_stdout(io.StringIO()):
            absorber.cmd_informe(args)
        fichero = salida / f"corredor-{self.r['suffix']}.json"
        revisado = json.loads(fichero.read_text(encoding="utf-8"))
        revisado["sections"]["00"]["rows"]["C-001"]["decision"] = "corregir"
        fichero.write_text(json.dumps(revisado), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as e:
            absorber.cmd_informe(args)
        self.assertIn("sobrescribir", str(e.exception))
        self.assertEqual(json.loads(fichero.read_text(encoding="utf-8")), revisado)
        # Pedido a propósito, se reescribe.
        with contextlib.redirect_stdout(io.StringIO()):
            absorber.cmd_informe(argparse.Namespace(**{**vars(args), "sobrescribir": True}))
        self.assertIsNone(json.loads(fichero.read_text(encoding="utf-8"))["sections"]["00"]["rows"]["C-001"]["decision"])

    def test_un_numero_reutilizado_no_pisa_la_decision_de_la_fila_vieja(self):
        fila = ('"C-006","FIX-Zeta tiene una edad.","FIX-Zeta","tiene_edad_estimada","n/a","expresa",'
                '"S01 x","no evaluado","baja","m","resuelta","vigente"\n')
        v = self.version({"data/afirmaciones/01.csv": self.texto("data/afirmaciones/01.csv") + fila})
        e = absorber.esqueleto(absorber.informe(str(MINI), str(v)))["sections"]["01"]
        self.assertEqual((e["rows"]["C-006"]["class"], e["rows"]["C-006"]["to"]), ("renumerada", "C-010"))
        self.assertIsNone(e["new_rows"]["C-006"]["destination"])

    def test_un_marcador_de_tabla_fuera_del_indice_se_rechaza(self):
        prosa = self.texto("docs/secciones/001-00-0-arranque.md") + "\n<!-- TABLE:no-indexada -->\n"
        with self.assertRaises(SystemExit) as e:
            absorber.informe(str(MINI), str(self.version({"docs/secciones/001-00-0-arranque.md": prosa})))
        self.assertIn("no-indexada", str(e.exception))
        indice = json.loads(self.texto("data/table_index.json"))
        indice["tables"].append(dict(indice["tables"][0]))
        with self.assertRaises(SystemExit) as e:
            absorber.informe(str(MINI), str(self.version({"data/table_index.json": json.dumps(indice)})))
        self.assertIn("claims-00", str(e.exception))

    def test_una_fuente_que_cambia_de_clave_propone_su_pareja(self):
        a = self.texto("data/apendices/A_fuentes.csv").replace('"S01",', '"S99",')
        r = absorber.informe(str(MINI), str(self.version({"data/apendices/A_fuentes.csv": a})))
        [f] = [f for f in r["sources"] if f["key"] == "S01"]
        self.assertEqual((f["state"], f["candidates"]), ("retirada", ["S99"]))
        fuente = absorber.esqueleto(r)["sources"]["S01"]
        self.assertEqual((fuente["candidates"], fuente["pair_with"]), (["S99"], None))

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
        filas, nuevas = e["sections"]["00"]["rows"], e["sections"]["00"]["new_rows"]
        self.assertEqual(set(filas), {"C-001", "C-003", "C-005"})
        self.assertTrue(all(f["decision"] is None for f in filas.values()))
        self.assertEqual(set(nuevas), {"C-007", "C-008", "C-009"})
        self.assertTrue(all(f["destination"] is None for f in nuevas.values()))
        self.assertEqual(filas["C-003"]["successors"], {"C-007": [], "C-008": []})
        # Su entrada del registro de sucesiones es nueva: antes no tenía ninguna.
        self.assertEqual(filas["C-003"]["successors_before"], [])
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
            absorber.cmd_informe(argparse.Namespace(anterior=str(MINI), nueva=str(MINI_V2), salida=str(salida),
                                                    sobrescribir=False))
        self.assertEqual(sorted(p.name for p in (self.tmp / "deltas").iterdir()), antes)
        diff = json.loads((salida / "diff.json").read_text(encoding="utf-8"))
        self.assertIn({"de": "C-006", "a": "C-010", "via": "contenido"}, diff["afirmaciones"]["correspondencia"])
        esqueleto = json.loads((salida / f"corredor-{self.r['suffix']}.json").read_text(encoding="utf-8"))
        self.assertEqual(esqueleto["decision"], "DEC-059")
        texto = (salida / "informe.md").read_text(encoding="utf-8")
        self.assertIn("C-003", texto)
        self.assertIn("C-004", texto)


def rellenar(r: dict, esq: dict, to: str) -> dict:
    """El esqueleto con una decisión de la primera fase en cada punto, como lo rellenaría un revisor."""
    esq["to"]["path"] = to
    esq["received_at"] = "2026-09-28"
    for sec, s in esq["sections"].items():
        citadas = {m["mention"]: m["cited_in"] for m in r["sections"][sec]["mentions"]}
        for f in s["rows"].values():
            if f["class"] != "renumerada":
                f.update(decision="retirar" if f["class"] == "retirada" else "conservar", reason="prueba")
            for m in (f.get("new_mentions") or {}).values():
                m.update(mention_type="unresolved", disposition="discarded_with_reason", reason="prueba")
        for f in s["new_rows"].values():
            f["destination"] = "H"
        for mid, m in s["mentions"].items():
            m.update(decision="reanclar" if citadas.get(mid) else "retirar", reason="prueba")
        for x in s["provenance"].values():
            x["decision"] = "aceptar"
        for x in s["successions"].values():
            x.update(decision="conservar", reason="prueba")
    for f in esq["sources"].values():
        f["decision"] = "actualizar"
    for x in esq["entities"]:
        x.update(decision="conservar", reason="prueba")
    for xs in esq["appendices"].values():
        for x in xs:
            x.update(decision="conservar", reason="prueba")
    return esq


@unittest.skipUnless(importlib.util.find_spec("jsonschema"), "convertir.py exige jsonschema")
class Construir(unittest.TestCase):
    """El delta de absorción: un libro mayor con la sección 0 convertida, frente a corredor-mini-v2.

    Cada prueba parte de un libro mayor nuevo: aplican y revierten.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.entorno = Entorno(self.tmp).__enter__()
        self.addCleanup(self._tmp.cleanup)
        self.addCleanup(self.entorno.__exit__, None, None, None)
        deltas = self.tmp / "deltas"
        with contextlib.redirect_stdout(io.StringIO()):
            assert delta_mod.cmd(deltas / "SEC-000001.json", False, False) == 0
            spec = self.tmp / "corredor-00.json"
            spec.write_text(json.dumps(self.entorno.spec(), ensure_ascii=False), encoding="utf-8")
            assert convertir.convertir(spec, str(MINI), False) == 0
            assert delta_mod.cmd(deltas / "SEC-000001-conversion.json", False, False) == 0
        (self.tmp / "absorptions").mkdir()

    def congelar(self, corpus: Path) -> Path:
        ruta = self.tmp / f"{corpus.parent.name}-{corpus.name}.json"
        with contextlib.redirect_stdout(io.StringIO()):
            freeze.cmd_create(argparse.Namespace(fuente=str(corpus), salida=str(ruta), repositorio="x",
                                                 decision="DEC-059", sustituye=None, fecha="2026-09-28"))
        return ruta

    def version(self, cambios: dict[str, str | None]) -> Path:
        copia = Path(tempfile.mkdtemp(dir=self.tmp)) / "corpus"
        shutil.copytree(MINI_V2, copia)
        for ruta, texto in cambios.items():
            if texto is None:
                (copia / ruta).unlink()
            else:
                (copia / ruta).write_text(texto, encoding="utf-8")
        return copia

    def absorcion(self, corpus: Path = MINI_V2, ajustar=None) -> Path:
        r = absorber.informe(str(MINI), str(corpus))
        self.nueva = self.congelar(corpus)
        esq = rellenar(r, absorber.esqueleto(r), str(self.nueva))
        if ajustar:
            ajustar(esq)
        ruta = self.tmp / "absorptions" / "corredor-v2.json"
        ruta.write_text(json.dumps(esq, ensure_ascii=False, indent=1), encoding="utf-8")
        return ruta

    def construir(self, ruta: Path, corpus: Path = MINI_V2) -> str:
        with contextlib.redirect_stdout(io.StringIO()):
            assert absorber.cmd_construir(argparse.Namespace(fichero=str(ruta), anterior=str(MINI),
                                                             nueva=str(corpus), dry_run=False)) == 0
        return next(p.name for p in (self.tmp / "deltas").glob("ABS-*.json"))

    def aplicar(self, nombre: str, revertir: bool = False) -> int:
        with contextlib.redirect_stdout(io.StringIO()):
            return delta_mod.cmd(self.tmp / "deltas" / nombre, revertir, False)

    def registro(self, rid: str) -> dict:
        return absorber.registros_actuales()[rid][1]

    def texto(self, ruta: str) -> str:
        return (MINI_V2 / ruta).read_text(encoding="utf-8")

    def activa(self) -> str:
        return json.loads((self.tmp / "dataset.json").read_text(encoding="utf-8"))["corpus_freeze"]["fingerprint"]

    def test_aplicar_cambia_la_congelacion_y_revertir_deja_todo_como_estaba(self):
        antes = {p.name: p.read_bytes() for p in self.entorno.records.glob("*.jsonl")}
        nombre = self.construir(self.absorcion())
        nueva = json.loads(self.nueva.read_text(encoding="utf-8"))
        self.assertEqual(self.aplicar(nombre), 0)
        self.assertEqual(self.activa(), nueva["fingerprint"])
        s = corredor.correspondencia()["00"]
        self.assertEqual((s["freeze"]["fingerprint"], s["absorption"]), (nueva["fingerprint"], nombre))
        self.assertEqual(sorted(s["rows"]), ["C-001", "C-002", "C-003", "C-004", "C-007", "C-008", "C-009"])
        # El informe siguiente parte de la versión absorbida: con ella no hay nada que absorber.
        r = absorber.informe(str(MINI_V2), str(MINI_V2))
        self.assertEqual((r["sections"]["00"]["rows"], r["sections"]["00"]["passages"]), ([], []))
        self.assertEqual(self.aplicar(nombre, revertir=True), 0)
        self.assertEqual(self.activa(), self.entorno.huella)
        self.assertEqual({p.name: p.read_bytes() for p in self.entorno.records.glob("*.jsonl")}, antes)

    def test_una_absorcion_no_se_aplica_sobre_otra_congelacion(self):
        nombre = self.construir(self.absorcion())
        manifiesto = json.loads((self.tmp / "dataset.json").read_text(encoding="utf-8"))
        manifiesto["corpus_freeze"]["fingerprint"] = "sha256:" + "0" * 64
        (self.tmp / "dataset.json").write_text(json.dumps(manifiesto), encoding="utf-8")
        self.assertEqual(self.aplicar(nombre), 1)

    def test_los_pasajes_viejos_siguen_y_los_nuevos_cuadran_con_su_copia(self):
        viejos = (self.tmp / "passages" / "SEC-000001.json").read_bytes()
        nombre = self.construir(self.absorcion())
        suf = nombre[len("ABS-"):-len(".json")]
        self.assertEqual((self.tmp / "passages" / "SEC-000001.json").read_bytes(), viejos)
        copia = (self.tmp / "sections" / f"SEC-000001.{suf}.md").read_text(encoding="utf-8")
        self.assertEqual(copia, (MINI_V2 / "docs" / "secciones" / "001-00-0-arranque.md").read_text(encoding="utf-8"))
        nuevos = json.loads((self.tmp / "passages" / f"SEC-000001.{suf}.json").read_text(encoding="utf-8"))
        for p in nuevos:
            self.assertEqual(copia[p["character_offsets"]["start"]:p["character_offsets"]["end"]], p["text"])
        self.assertFalse({p["id"] for p in nuevos} & {p["id"] for p in json.loads(viejos)})

    def test_cada_mencion_reanclada_senala_su_etiqueta_en_la_prosa_nueva(self):
        nombre = self.construir(self.absorcion())
        self.aplicar(nombre)
        s = corredor.correspondencia()["00"]
        pasajes = {p["id"]: p for p in json.loads(absorber.pasajes_vigentes(s).read_text(encoding="utf-8"))}
        copia = (self.tmp / "sections" / Path(s["files"]["prose"]["copy"]).name).read_text(encoding="utf-8")
        activas = [m for f, m in absorber.registros_actuales().values()
                   if f == "mentions.jsonl" and m.get("record_status") == "active"]
        self.assertTrue(activas)
        for m in activas:
            self.assertIn(m["passage_id"], pasajes)
            o, p = m["character_offsets"], pasajes[m["passage_id"]]["character_offsets"]
            # Dentro de su pasaje nuevo: la que no aparece literal lo cubre entero,
            # la que sí señala su etiqueta.
            self.assertTrue(p["start"] <= o["start"] <= o["end"] <= p["end"], m["id"])
            if any("no aparece literal" in n for n in m["notes"]):
                self.assertEqual((o["start"], o["end"]), (p["start"], p["end"]), m["id"])
            else:
                self.assertEqual(copia[o["start"]:o["end"]].casefold(), m["original_text"].casefold(), m["id"])
        # Las que se retiraron conservan su pasaje de antes.
        retiradas = [m for f, m in absorber.registros_actuales().values()
                     if f == "mentions.jsonl" and m.get("record_status") == "deprecated"]
        self.assertTrue(retiradas and all(m["passage_id"] not in pasajes for m in retiradas))

    def test_los_ejes_y_la_fuente_salen_de_la_version_nueva(self):
        self.aplicar(self.construir(self.absorcion()))
        claim = "CLAIM-000001"  # la afirmación de C-001, cuya fuerza y motivo cambian
        dims = self.registro(claim)["epistemic_dimensions"]
        self.assertEqual((dims["evidence_strength"], dims["evidence_strength_reason"]),
                         ("high", "Lo confirman el resumen y la figura 2."))
        fuente = next(r for f, r in absorber.registros_actuales().values() if f == "sources.jsonl")
        filas = {f["clave"]: f for f in freeze.leer_csv(MINI_V2 / "data" / "apendices" / "A_fuentes.csv")[1]}
        self.assertEqual((fuente["title"], fuente["consulted_at"]),
                         (filas["S01"]["título"], filas["S01"]["fecha de consulta"]))
        self.assertEqual(self.registro(claim)["provenance"]["dataset_revision"], "REV-000003")

    def test_las_etiquetas_nuevas_dan_menciones_con_su_decision(self):
        self.aplicar(self.construir(self.absorcion()))
        nuevas = [m for f, m in absorber.registros_actuales().values()
                  if f == "mentions.jsonl" and any("etiqueta nueva de C-003" in n for n in m["notes"])]
        self.assertEqual(sorted(m["original_text"] for m in nuevas),
                         ["registro C-003", "retirado por no atomicidad y sustituido por dos premisas"])
        self.assertTrue(all(m["disposition"] == "discarded_with_reason" for m in nuevas))
        filas = corredor.correspondencia()["00"]["rows"]
        self.assertTrue({m["id"] for m in nuevas} <= set(filas["C-003"]["mention_ids"]))

    def test_dos_construcciones_dan_el_mismo_delta(self):
        ruta = self.absorcion()
        uno = absorber.construir(ruta, str(MINI), str(MINI_V2))["delta"]
        dos = absorber.construir(ruta, str(MINI), str(MINI_V2))["delta"]
        self.assertEqual(json.dumps(uno, sort_keys=True), json.dumps(dos, sort_keys=True))

    def test_una_fila_retirada_con_decision_retirar_depreca_sus_registros(self):
        filas = self.texto("data/afirmaciones/00.csv")
        sin_c001 = "".join(l for l in filas.splitlines(keepends=True) if not l.startswith('"C-001"'))
        v = self.version({"data/afirmaciones/00.csv": sin_c001})
        self.aplicar(self.construir(self.absorcion(v), v))
        for rid in ("CLAIM-000001", "EVID-000001"):
            self.assertEqual(self.registro(rid)["record_status"], "deprecated", rid)
            self.assertTrue(any("C-001" in n for n in self.registro(rid)["notes"]))

    def test_un_parche_corrige_un_registro_y_pasa_por_la_validacion(self):
        def corregir(esq, parche):
            esq["sections"]["00"]["rows"]["C-001"].update(decision="corregir", patches={"CLAIM-000001": parche})

        self.aplicar(self.construir(self.absorcion(ajustar=lambda e: corregir(e, {"notes": ["revisada"]}))))
        self.assertEqual(self.registro("CLAIM-000001")["notes"], ["revisada"])

    def test_un_parche_no_toca_lo_que_se_deduce_ni_los_enlaces_ni_rompe_el_esquema(self):
        for parche, dice in (({"epistemic_dimensions": {}}, "se deduce"),
                             ({"subject_id": "CLADE-000002"}, "otro lado del enlace"),
                             ({"claim_type": "no-existe"}, "dejaría de validar"),
                             ({"inventado": 1}, "no es un campo")):
            ruta = self.absorcion(ajustar=lambda e, p=parche: e["sections"]["00"]["rows"]["C-001"].update(
                decision="corregir", patches={"CLAIM-000001": p}))
            with self.assertRaises(SystemExit) as e:
                absorber.construir(ruta, str(MINI), str(MINI_V2))
            self.assertIn(dice, str(e.exception), parche)

    def test_lo_que_crea_registros_nuevos_se_niega_con_su_motivo(self):
        ajustes = (lambda e: e["sections"]["00"]["new_rows"]["C-009"].update(destination="A", keys=["@X"]),
                   lambda e: e["sections"]["00"]["rows"]["C-003"].update(decision="dividir"),
                   lambda e: e.update(pairing={"C-001": "C-009"}),
                   lambda e: e["sections"]["00"]["rows"]["C-003"]["new_mentions"]["registro C-003"].update(
                       disposition="new_entity", targets=["@Nuevo"]))
        for ajustar in ajustes:
            with self.assertRaises(SystemExit) as e:
                absorber.construir(self.absorcion(ajustar=ajustar), str(MINI), str(MINI_V2))
            self.assertIn("constructor de registros nuevos", str(e.exception))

    def test_el_fichero_tiene_que_cubrir_justo_lo_que_pide_el_informe(self):
        for ajustar, dice in (
                (lambda e: e["sections"]["00"]["rows"]["C-001"].update(decision=None), "sin decisión"),
                (lambda e: e["sections"]["00"]["rows"]["C-001"].update(reason=None), "sin `reason`"),
                (lambda e: e["sections"]["00"]["rows"]["C-001"].update(**{"class": "renumerada"}), "no es lo que dice"),
                (lambda e: e["sections"]["00"]["mentions"].pop("MENTION-000003"), "falta MENTION-000003"),
                (lambda e: e["sections"]["00"]["rows"].update({"C-002": {"decision": "conservar"}}),
                 "no es un cambio de esta versión"),
                (lambda e: e.update(received_at=None), "received_at")):
            with self.assertRaises(SystemExit) as e:
                absorber.construir(self.absorcion(ajustar=ajustar), str(MINI), str(MINI_V2))
            self.assertIn(dice, str(e.exception))

    def test_se_niega_fuera_de_su_carpeta_con_deltas_pendientes_o_sin_la_congelacion_nueva(self):
        ruta = self.absorcion()
        fuera = self.tmp / "corredor-v2.json"
        fuera.write_bytes(ruta.read_bytes())
        with self.assertRaises(SystemExit) as e:
            absorber.construir(fuera, str(MINI), str(MINI_V2))
        self.assertIn("knowledge/corpus/absorptions/", str(e.exception))
        esq = json.loads(ruta.read_text(encoding="utf-8"))
        Path(esq["to"]["path"]).unlink()
        with self.assertRaises(SystemExit) as e:
            absorber.construir(ruta, str(MINI), str(MINI_V2))
        self.assertIn("se congela antes de absorberla", str(e.exception))
        ruta = self.absorcion()
        self.construir(ruta)
        with self.assertRaises(SystemExit) as e:
            absorber.construir(ruta, str(MINI), str(MINI_V2))
        self.assertIn("deltas sin aplicar", str(e.exception))

    def test_una_seccion_ingerida_sin_convertir_se_convierte_antes(self):
        with contextlib.redirect_stdout(io.StringIO()):
            corredor.ingerir(str(MINI), "01", None, False)
            assert delta_mod.cmd(self.tmp / "deltas" / "SEC-000002.json", False, False) == 0
        with self.assertRaises(SystemExit) as e:
            absorber.construir(self.absorcion(), str(MINI), str(MINI_V2))
        self.assertIn("sin convertir: 01", str(e.exception))

    def test_el_snapshot_ve_una_congelacion_editada_a_mano_y_un_fichero_de_absorcion_alterado(self):
        ruta = self.absorcion()
        self.aplicar(self.construir(ruta))
        # snapshot.py resuelve sus rutas desde ROOT: se le da un árbol con los
        # deltas y el manifiesto de este libro mayor.
        raiz = self.tmp / "raiz"
        shutil.copytree(self.tmp / "deltas", raiz / "knowledge" / "deltas")
        manifiesto = raiz / "knowledge" / "corpus" / "manifests" / "dataset.json"
        manifiesto.parent.mkdir(parents=True)
        shutil.copy(self.tmp / "dataset.json", manifiesto)
        with mock.patch.object(snapshot, "ROOT", raiz), mock.patch.object(snapshot, "MANIFEST", manifiesto):
            self.assertEqual((snapshot.congelacion_incoherente(), snapshot.conversiones_alteradas()), ([], []))
            datos = json.loads(manifiesto.read_text(encoding="utf-8"))
            datos["corpus_freeze"]["fingerprint"] = self.entorno.huella
            manifiesto.write_text(json.dumps(datos), encoding="utf-8")
            self.assertIn("los deltas aplicados dejan", "\n".join(snapshot.congelacion_incoherente()))
            ruta.write_text(ruta.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            self.assertIn("no es el que guardó", "\n".join(snapshot.conversiones_alteradas()))

    def test_reconstruir_tras_revertir_reutiliza_los_pasajes(self):
        ruta = self.absorcion()
        nombre = self.construir(ruta)
        self.aplicar(nombre)
        self.aplicar(nombre, revertir=True)
        otro = absorber.construir(ruta, str(MINI), str(MINI_V2))["delta"]
        primero = json.loads((self.tmp / "deltas" / nombre).read_text(encoding="utf-8"))
        self.assertEqual(otro["absorption"]["sections"]["00"]["passages"],
                         primero["absorption"]["sections"]["00"]["passages"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
