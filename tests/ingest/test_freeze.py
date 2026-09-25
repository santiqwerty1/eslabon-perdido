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
           registros: dict[str, tuple[list[str], list[list[str]]]] | None = None) -> Path:
    (base / "data" / "afirmaciones").mkdir(parents=True)
    (base / "data" / "apendices").mkdir(parents=True)
    (base / "docs" / "secciones").mkdir(parents=True)
    (base / "docs" / "secciones" / "001-prosa.md").write_text("Prosa.\n", encoding="utf-8")
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

    def test_numero_repetido_aborta(self):
        a = corpus(self.tmp / "a", {"00": [fila("C-001", "Uno.")], "01": [fila("C-001", "Otra.")]})
        with self.assertRaises(SystemExit):
            freeze.leer_afirmaciones(a)


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
