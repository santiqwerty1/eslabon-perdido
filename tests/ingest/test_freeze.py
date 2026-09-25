#!/usr/bin/env python3
"""Casos límite de `scripts/ingest/freeze.py`.

El fixture `corpus-versions` prueba el caso normal de una pasada de auditoría.
Éstos prueban los bordes donde un diff equivocado no avisa: una fila que
desaparece del informe, una afirmación que cambia de sección sin que nadie la
reingiera, una cita que apunta a otra afirmación y se da por buena. Cada uno
construye dos versiones mínimas en un directorio temporal.

Uso:
    python3 tests/ingest/test_freeze.py
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("freeze", ROOT / "scripts" / "ingest" / "freeze.py")
freeze = importlib.util.module_from_spec(_spec)
sys.modules["freeze"] = freeze  # dataclass necesita el módulo registrado
_spec.loader.exec_module(freeze)

CAB = ["#", "Afirmación", "Sujeto", "Predicado", "Objeto", "Atribución", "Fuente",
       "Aceptación", "Fuerza", "Motivo", "Resolución", "Vigencia"]


def fila(cid: str, texto: str, atribucion: str = "expresa", fuente: str = "S01 resumen") -> list[str]:
    return [cid, texto, "FIX-Alfa", "es_hermano_de", "FIX-Beta", atribucion, fuente,
            "no evaluado", "media", "motivo", "resuelta", "vigente"]


def csv_texto(cab: list[str], filas: list[list[str]]) -> str:
    q = lambda v: '"' + v.replace('"', '""') + '"'
    return "".join(",".join(q(c) for c in f) + "\n" for f in [cab, *filas])


def corpus(base: Path, secciones: dict[str, list[list[str]]],
           registros: dict[str, tuple[list[str], list[list[str]]]] | None = None,
           prosa: str = "Prosa.\n") -> Path:
    (base / "data" / "afirmaciones").mkdir(parents=True)
    (base / "data" / "apendices").mkdir(parents=True)
    (base / "docs" / "secciones").mkdir(parents=True)
    (base / "docs" / "secciones" / "001-00-0-prosa.md").write_text(prosa, encoding="utf-8")
    for sec, filas in secciones.items():
        (base / "data" / "afirmaciones" / f"{sec}.csv").write_text(csv_texto(CAB, filas), encoding="utf-8")
    for nombre, (cab, filas) in (registros or {}).items():
        (base / "data" / "apendices" / nombre).write_text(csv_texto(cab, filas), encoding="utf-8")
    return base


class Afirmaciones(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def diff(self, v1: dict, v2: dict) -> dict:
        a = corpus(self.tmp / "a", v1)
        b = corpus(self.tmp / "b", v2)
        return freeze.comparar_afirmaciones(a, b)

    def test_mover_una_afirmacion_identica_no_es_sin_cambios(self):
        r = self.diff({"00": [fila("C-001", "Uno.")], "01": [fila("C-002", "Dos.")]},
                      {"00": [], "01": [fila("C-001", "Uno."), fila("C-002", "Dos.")]})
        self.assertEqual(r["sin_cambios"], 1)
        [m] = r["modificadas"]
        self.assertEqual(m["columnas"]["(sección)"], ["00", "01"])

    def test_mover_marca_las_dos_secciones(self):
        r = self.diff({"00": [fila("C-001", "Uno.")], "01": [fila("C-002", "Dos.")]},
                      {"00": [], "01": [fila("C-001", "Uno.", fuente="S02 discusión"), fila("C-002", "Dos.")]})
        self.assertIn("00", r["secciones_afectadas"])
        self.assertIn("01", r["secciones_afectadas"])

    def test_cita_sin_actualizar_tras_renumerar_es_modificacion(self):
        # C-002 pasa a C-003 al insertarse una fila; C-004 sigue citando C-002,
        # que ahora es la fila insertada: su cita apunta a otra afirmación.
        v1 = {"00": [fila("C-001", "Uno."), fila("C-002", "Dos."),
                     fila("C-003", "Síntesis.", atribucion="sintesis(C-002)")]}
        v2 = {"00": [fila("C-001", "Uno."), fila("C-002", "Insertada."), fila("C-003", "Dos."),
                     fila("C-004", "Síntesis.", atribucion="sintesis(C-002)")]}
        r = self.diff(v1, v2)
        modificadas = {m["a"]: m for m in r["modificadas"]}
        self.assertIn("C-004", modificadas)
        self.assertIn("Atribución", modificadas["C-004"]["columnas"])

    def test_fila_identica_con_cita_desplazada_es_modificacion(self):
        # C-001 no cambia ni de número ni de bytes, pero cita C-003, que tras la
        # inserción pasa a C-004: la cita sin actualizar apunta a otra fila.
        v1 = {"00": [fila("C-001", "Síntesis.", atribucion="sintesis(C-003)"),
                     fila("C-002", "Dos."), fila("C-003", "Tres.")]}
        v2 = {"00": [fila("C-001", "Síntesis.", atribucion="sintesis(C-003)"),
                     fila("C-002", "Insertada."), fila("C-003", "Dos."), fila("C-004", "Tres.")]}
        r = self.diff(v1, v2)
        self.assertEqual(r["sin_cambios"], 0)
        self.assertIn("C-001", {m["a"] for m in r["modificadas"]})

    def test_cita_a_un_numero_retirado_y_reutilizado_es_modificacion(self):
        # Se retira C-001 y C-002 pasa a ocuparlo. La síntesis sigue citando
        # C-001, que ahora es la antigua C-002: no puede darse por buena.
        v1 = {"00": [fila("C-001", "Uno."), fila("C-002", "Dos."),
                     fila("C-003", "Síntesis.", atribucion="sintesis(C-001)")]}
        v2 = {"00": [fila("C-001", "Dos."), fila("C-002", "Síntesis.", atribucion="sintesis(C-001)")]}
        r = self.diff(v1, v2)
        self.assertEqual([x["id"] for x in r["retiradas"]], ["C-001"])
        self.assertIn("C-002", {m["a"] for m in r["modificadas"]})

    def test_un_rango_que_gana_una_fila_no_es_renumeracion(self):
        # La fila insertada cae dentro del rango: «C-001–C-003» pasa a
        # «C-001–C-004», que traduciendo sólo los extremos parece renumeración,
        # pero ahora cita también la fila nueva.
        v1 = {"00": [fila("C-001", "Uno."), fila("C-002", "Dos."), fila("C-003", "Tres."),
                     fila("C-004", "Síntesis.", atribucion="sintesis(C-001–C-003)")]}
        v2 = {"00": [fila("C-001", "Uno."), fila("C-002", "Insertada."), fila("C-003", "Dos."),
                     fila("C-004", "Tres."), fila("C-005", "Síntesis.", atribucion="sintesis(C-001–C-004)")]}
        r = self.diff(v1, v2)
        self.assertIn("C-005", {m["a"] for m in r["modificadas"]})

    def test_un_rango_que_solo_se_desplaza_es_renumeracion(self):
        v1 = {"00": [fila("C-001", "Uno."), fila("C-002", "Dos."), fila("C-003", "Tres."),
                     fila("C-004", "Síntesis.", atribucion="sintesis(C-001–C-003)")]}
        v2 = {"00": [fila("C-001", "Insertada."), fila("C-002", "Uno."), fila("C-003", "Dos."),
                     fila("C-004", "Tres."), fila("C-005", "Síntesis.", atribucion="sintesis(C-002–C-004)")]}
        r = self.diff(v1, v2)
        self.assertNotIn("C-005", {m["a"] for m in r["modificadas"]})

    def test_numero_repetido_aborta(self):
        a = corpus(self.tmp / "a", {"00": [fila("C-001", "Uno.")], "01": [fila("C-001", "Otra.")]})
        with self.assertRaises(SystemExit):
            freeze.leer_afirmaciones(a)


class Informe(unittest.TestCase):
    """El informe completo de `diff`, no sólo la comparación de filas."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def informe(self, a: Path, b: Path) -> dict:
        salida = self.tmp / "diff.json"
        with contextlib.redirect_stdout(io.StringIO()):
            freeze.cmd_diff(argparse.Namespace(anterior=str(a), nueva=str(b), detalle=False, json=str(salida)))
        return json.loads(salida.read_text(encoding="utf-8"))

    def test_prosa_intacta_con_citas_desfasadas(self):
        # Se inserta una fila antes de C-002, que pasa a C-003; la prosa no se
        # tocó y sigue citando C-002, que ahora es la insertada.
        prosa = "Dos. [C-002]\n"
        a = corpus(self.tmp / "a", {"00": [fila("C-001", "Uno."), fila("C-002", "Dos.")]}, prosa=prosa)
        b = corpus(self.tmp / "b", {"00": [fila("C-001", "Uno."), fila("C-002", "Nueva."),
                                           fila("C-003", "Dos.")]}, prosa=prosa)
        inf = self.informe(a, b)
        self.assertEqual([x["estado"] for x in inf["prosa"]], ["citas desactualizadas"])
        self.assertIn("prosa", inf["afirmaciones"]["secciones_afectadas"]["00"])

    def test_un_cambio_solo_de_prosa_manda_reingerir_la_seccion(self):
        filas = {"00": [fila("C-001", "Uno.")]}
        a = corpus(self.tmp / "a", filas, prosa="Uno. [C-001]\n")
        b = corpus(self.tmp / "b", filas, prosa="Uno, dicho de otro modo. [C-001]\n")
        inf = self.informe(a, b)
        self.assertEqual(inf["afirmaciones"]["secciones_afectadas"], {"00": {"prosa": 1}})


    def test_un_cambio_solo_del_apendice_b_manda_reingerir_su_seccion(self):
        filas = {"00": [fila("C-001", "Uno.")], "01": [fila("C-002", "Dos.")]}
        cab = ["etiqueta preferida", "tipo", "# de la fila del registro donde aparece por primera vez"]
        a = corpus(self.tmp / "a", filas, {"B_entidades.csv": (cab, [["FIX-Alfa", "clado", "C-002"]])})
        b = corpus(self.tmp / "b", filas, {"B_entidades.csv": (cab, [["FIX-Alfa", "taxón", "C-002"]])})
        inf = self.informe(a, b)
        self.assertEqual(inf["afirmaciones"]["secciones_afectadas"], {"01": {"apéndices": 1}})


    def test_un_cambio_del_indice_de_tablas_manda_reingerir_su_seccion(self):
        filas = {"00": [fila("C-001", "Uno.")], "01": [fila("C-002", "Dos.")]}
        a = corpus(self.tmp / "a", filas)
        b = corpus(self.tmp / "b", filas)
        for base, categoria in ((a, "synthesis"), (b, "claims")):
            (base / "data" / "table_index.json").write_text(json.dumps({"tables": [
                {"id": "t-01", "category": categoria, "csv_path": "data/tablas/01/t-01.csv"}]}),
                encoding="utf-8")
        inf = self.informe(a, b)
        self.assertEqual(inf["afirmaciones"]["secciones_afectadas"], {"01": {"índice": 1}})

    def test_una_tabla_que_cambia_de_seccion_marca_las_dos(self):
        filas = {"00": [fila("C-001", "Uno.")], "01": [fila("C-002", "Dos.")]}
        a = corpus(self.tmp / "a", filas)
        b = corpus(self.tmp / "b", filas)
        for base, sec in ((a, "00"), (b, "01")):
            (base / "data" / "table_index.json").write_text(json.dumps({"tables": [
                {"id": "t-01", "category": "synthesis", "csv_path": f"data/tablas/{sec}/t-01.csv"}]}),
                encoding="utf-8")
        inf = self.informe(a, b)
        self.assertEqual(inf["afirmaciones"]["secciones_afectadas"],
                         {"00": {"índice": 1}, "01": {"índice": 1}})


class Registros(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def escribir(self, nombre: str, cab: list[str], filas: list[list[str]]) -> Path:
        p = self.tmp / nombre
        p.write_text(csv_texto(cab, filas), encoding="utf-8")
        return p

    def test_claves_que_colisionan_al_traducir_no_pierden_filas(self):
        # Se retira C-001 y C-002 pasa a ocupar su número.
        cab = ["etiqueta preferida", "#"]
        a = self.escribir("a.csv", cab, [["afirmación C-001", "C-001"], ["afirmación C-002", "C-002"]])
        b = self.escribir("b.csv", cab, [["afirmación C-001", "C-001"]])
        r = freeze.comparar_registro(a, b, {"C-002": "C-001"})
        retiradas = r["retiradas"] if isinstance(r["retiradas"], int) else len(r["retiradas"])
        self.assertEqual(retiradas, 1)

    def test_cabecera_renombrada_en_registro_de_una_fila(self):
        a = self.escribir("a.csv", ["clave", "valor"], [["X", "1"]])
        b = self.escribir("b.csv", ["control", "valor"], [["X", "1"]])
        r = freeze.comparar_registro(a, b, {})
        self.assertTrue(r["cabecera_cambiada"])

    def test_una_fila_mas_ancha_que_su_cabecera_aborta(self):
        p = self.tmp / "a.csv"
        p.write_text('"clave","valor"\n"X","1","sobra"\n', encoding="utf-8")
        with self.assertRaises(SystemExit):
            freeze.leer_csv(p)

    def test_sin_clave_unica_nunca_da_recuentos_negativos(self):
        cab = ["magnitud", "#"]
        filas = [["m", "C-001"], ["m", "C-001"]]
        a = self.escribir("a.csv", cab, filas)
        b = self.escribir("b.csv", cab, filas)
        r = freeze.comparar_registro(a, b, {"C-001": "C-002"})
        self.assertGreaterEqual(r["solo_renumeracion"], 0)
        self.assertEqual((r["nuevas"], r["retiradas"]), (2, 2))


class Congelacion(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def ejecutar(self, funcion, **kw) -> int:
        with contextlib.redirect_stdout(io.StringIO()):
            return funcion(argparse.Namespace(**kw))

    def test_verify_rechaza_un_manifiesto_con_huella_incoherente(self):
        c = corpus(self.tmp / "c", {"00": [fila("C-001", "Uno.")]})
        m = self.tmp / "m.json"
        self.assertEqual(self.ejecutar(freeze.cmd_create, fuente=str(c), salida=str(m), repositorio="x",
                                       decision=None, sustituye=None, fecha="2026-09-25"), 0)
        registro = json.loads(m.read_text(encoding="utf-8"))
        registro["fingerprint"] = "sha256:" + "0" * 64
        m.write_text(json.dumps(registro), encoding="utf-8")
        self.assertNotEqual(self.ejecutar(freeze.cmd_verify, fuente=str(c), manifiesto=str(m)), 0)

    def test_un_enlace_simbolico_en_la_capa_canonica_se_rechaza(self):
        c = corpus(self.tmp / "c", {"00": [fila("C-001", "Uno.")]})
        fuera = self.tmp / "fuera.csv"
        fuera.write_text("x\n", encoding="utf-8")
        (c / "data" / "afirmaciones" / "enlace.csv").symlink_to(fuera)
        with self.assertRaises(SystemExit):
            freeze.ficheros(c)

    def test_el_snapshot_cubre_la_congelacion_activa(self):
        spec = importlib.util.spec_from_file_location("snapshot", ROOT / "scripts" / "snapshot" / "snapshot.py")
        snapshot = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(snapshot)
        activa = json.loads((ROOT / "knowledge" / "corpus" / "manifests" / "dataset.json")
                            .read_text(encoding="utf-8"))["corpus_freeze"]["path"]
        self.assertIn(activa, snapshot.gather()["files"])

    def test_sin_la_congelacion_activa_no_se_crea_snapshot(self):
        spec = importlib.util.spec_from_file_location("snapshot", ROOT / "scripts" / "snapshot" / "snapshot.py")
        snapshot = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(snapshot)
        # Todo en una copia: si create no se negara, escribiría aquí.
        snapshot.ROOT = self.tmp
        snapshot.SNAPSHOTS = self.tmp / "snapshots"
        snapshot.SNAPSHOTS.mkdir()
        snapshot.MANIFEST = self.tmp / "dataset.json"
        snapshot.MANIFEST.write_text(json.dumps({"guide_version": "x", "schema_version": "x",
                                                 "dataset_revision": "REV-000001", "active_campaign": "C01",
                                                 "corpus_freeze": {"path": "falta.json"}}), encoding="utf-8")
        snapshot.gather = lambda: {"counts": {}, "files": {"falta.json": "ausente"}}
        self.assertEqual(self.ejecutar(lambda a: snapshot.create(None)), 1)
        self.assertEqual(list(snapshot.SNAPSHOTS.iterdir()), [])

    def test_fichero_ignorado_en_la_capa_canonica_no_es_copia_limpia(self):
        c = corpus(self.tmp / "c", {"00": [fila("C-001", "Uno.")]})
        (c / ".gitignore").write_text("*.tmp\n", encoding="utf-8")
        git = lambda *a: subprocess.run(["git", "-C", str(c), *a], check=True, capture_output=True)
        git("init", "-q")
        git("add", "-A")
        git("-c", "user.name=t", "-c", "user.email=t@t.invalid", "commit", "-qm", "v1")
        (c / "data" / "afirmaciones" / "sobrante.tmp").write_text("x\n", encoding="utf-8")
        self.assertIs(freeze.abrir(str(c)).limpia, False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
