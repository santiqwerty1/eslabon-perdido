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

    def test_la_mencion_del_apendice_b_queda_en_su_fila(self):
        # FIX-Omega sólo existe en el apéndice B, con primera fila C-003: la
        # procedencia de C-003 tiene que llevar su mención.
        self.assertIn(self.menciones["FIX-Omega"]["id"], self.filas["C-003"]["mention_ids"])

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


    def test_una_ruta_del_indice_fuera_de_la_congelacion_se_rechaza(self):
        otra = self.tmp / "otra"
        shutil.copytree(MINI, otra)
        (self.tmp / "fuera.csv").write_text('"x"\n"C-004"\n', encoding="utf-8")
        indice = json.loads((otra / "data" / "table_index.json").read_text(encoding="utf-8"))
        indice["tables"][1]["csv_path"] = "../fuera.csv"
        (otra / "data" / "table_index.json").write_text(json.dumps(indice), encoding="utf-8")
        congelacion = congelar(otra, self.tmp / "otra.json")
        with self.assertRaises(SystemExit) as e:
            corredor.construir(str(otra), "00", congelacion)
        self.assertIn("no es un fichero de la versión congelada", str(e.exception))

    def test_un_delta_sin_aplicar_reserva_sus_identificadores_y_su_revision(self):
        # Ingerir escribe el delta pero no lo aplica: la sección siguiente no
        # puede volver a emitir sus MENTION ni llevar el dataset a la misma
        # revisión.
        deltas = self.tmp / "deltas"
        deltas.mkdir()
        (deltas / "SEC-000001.json").write_text(json.dumps({
            "dataset_revision_before": "REV-000000", "dataset_revision_after": "REV-000001",
            "records_added": ["MENTION-000001", "MENTION-000007"],
            "corpus_origin": {"section": "01"}}), encoding="utf-8")
        original, ingest.DELTAS = ingest.DELTAS, deltas
        try:
            r = corredor.construir(str(MINI), "00", self.congelacion)
        finally:
            ingest.DELTAS = original
        self.assertEqual(r["menciones"][0]["id"], "MENTION-000008")
        self.assertEqual(r["rev"], ("REV-000001", "REV-000002"))
        self.assertEqual(r["pendientes"], ["SEC-000001.json"])


    @contextlib.contextmanager
    def revertida(self, con_ficheros: bool):
        """Un almacén donde la sección 00 se ingirió como SEC-000001 y se revirtió."""
        k = self.tmp / "knowledge"
        dirs = {"DELTAS": k / "deltas", "SECTIONS": k / "sections", "PASSAGES": k / "passages",
                "REPORTS": k / "reports"}
        for d in dirs.values():
            d.mkdir(parents=True)
        (dirs["DELTAS"] / "SEC-000001.json").write_text(json.dumps({
            "dataset_revision_before": "REV-000000", "dataset_revision_after": "REV-000001",
            "records_added": ["MENTION-000001"], "corpus_origin": {"section": "00", "rows": {
                "C-001": {"passage_ids": ["PASSAGE-000001", "PASSAGE-000005"]}}}}), encoding="utf-8")
        (dirs["DELTAS"] / "historial.jsonl").write_text("".join(json.dumps(e) + "\n" for e in [
            {"delta": "SEC-000001.json", "accion": "aplicar", "revision": "REV-000001"},
            {"delta": "SEC-000001.json", "accion": "revertir", "revision": "REV-000000"}]), encoding="utf-8")
        if con_ficheros:
            (dirs["SECTIONS"] / "SEC-000001.md").write_text("x\n", encoding="utf-8")
            (dirs["PASSAGES"] / "SEC-000001.json").write_text("[]\n", encoding="utf-8")
        originales = {n: getattr(ingest, n) for n in dirs}
        for n, d in dirs.items():
            setattr(ingest, n, d)
        try:
            yield dirs
        finally:
            for n, d in originales.items():
                setattr(ingest, n, d)

    def test_un_delta_revertido_no_reserva_la_revision_pero_si_la_seccion(self):
        # Se aplicó y se revirtió: el manifiesto volvió a REV-000000 y el delta
        # queda como constancia. Nada se encadena detrás de él, pero mientras
        # queden sus ficheros la sección no se vuelve a ingerir: saldría duplicada.
        with self.revertida(con_ficheros=True):
            self.assertEqual(ingest.revision_siguiente({"dataset_revision": "REV-000000"}),
                             ("REV-000000", "REV-000001", []))
            # Los identificadores del delta revertido siguen reservados.
            self.assertIn("MENTION-000001", ingest.reservados_por_deltas("MENTION"))
            with self.assertRaises(SystemExit) as e:
                corredor.construir(str(MINI), "00", self.congelacion)
        self.assertIn("se revirtió", str(e.exception))
        self.assertIn("passages/SEC-000001.json", str(e.exception))

    def test_retirados_sus_ficheros_la_seccion_revertida_se_reingiere_con_otro_numero(self):
        # El número SEC-000001 no se reutiliza: si saliera otra vez, el delta
        # nuevo heredaría el «revertir» del historial y no contaría como pendiente.
        with self.revertida(con_ficheros=False) as dirs:
            r = corredor.construir(str(MINI), "00", self.congelacion)
            self.assertEqual(r["sec_id"], "SEC-000002")
            self.assertEqual(r["rev"], ("REV-000000", "REV-000001"))
            self.assertEqual(r["menciones"][0]["id"], "MENTION-000002")
            # Los pasajes retirados siguen citados por el delta revertido.
            self.assertEqual(r["pasajes"][0]["id"], "PASSAGE-000006")
            (dirs["DELTAS"] / f"{r['sec_id']}.json").write_text(json.dumps(r["delta"]), encoding="utf-8")
            self.assertEqual(ingest.revision_siguiente({"dataset_revision": "REV-000000"})[2],
                             ["SEC-000002.json"])

    def test_el_contraste_lee_la_entrada_del_registro_que_se_usa(self):
        # La entrada del registro no se llama claims-00: la procedencia la
        # encuentra por categoría, y el recuento declarado tiene que salir de ella.
        otra = self.tmp / "otra"
        shutil.copytree(MINI, otra)
        indice = json.loads((otra / "data" / "table_index.json").read_text(encoding="utf-8"))
        for e in indice["tables"]:
            if e["id"] == "claims-00":
                e["id"], e["row_count"] = "registro-00", 99
        (otra / "data" / "table_index.json").write_text(json.dumps(indice), encoding="utf-8")
        prosa = otra / "docs" / "secciones" / "001-00-0-arranque.md"
        prosa.write_text(prosa.read_text(encoding="utf-8").replace("TABLE:claims-00", "TABLE:registro-00"),
                         encoding="utf-8")
        r = corredor.construir(str(otra), "00", congelar(otra, self.tmp / "otra.json"))
        self.assertEqual(r["contraste"][0][1], 99)

    def test_sin_la_columna_de_primera_aparicion_del_apendice_b_no_se_ingiere(self):
        otra = self.tmp / "otra"
        shutil.copytree(MINI, otra)
        b = otra / "data" / "apendices" / "B_entidades.csv"
        b.write_text(b.read_text(encoding="utf-8").replace(
            corredor.COL_PRIMERA, "primera aparición", 1), encoding="utf-8")
        with self.assertRaises(SystemExit) as e:
            corredor.construir(str(otra), "00", congelar(otra, self.tmp / "otra.json"))
        self.assertIn(corredor.COL_PRIMERA, str(e.exception))

    def test_una_barra_en_una_celda_no_desplaza_las_columnas(self):
        otra = self.tmp / "otra"
        shutil.copytree(MINI, otra)
        registro = otra / "data" / "afirmaciones" / "00.csv"
        texto = registro.read_text(encoding="utf-8")
        self.assertIn("FIX-Alfa", texto)
        registro.write_text(texto.replace("FIX-Alfa", "FIX-Alfa | alias", 1), encoding="utf-8")
        datos, h = parse(otra)
        self.assertEqual(h.errores, [])

    def test_un_marcador_de_tabla_sin_indice_se_rechaza(self):
        otra = self.tmp / "otra"
        shutil.copytree(MINI, otra)
        indice = json.loads((otra / "data" / "table_index.json").read_text(encoding="utf-8"))
        indice["tables"] = [e for e in indice["tables"] if e["id"] != "table-01-00-edades"]
        (otra / "data" / "table_index.json").write_text(json.dumps(indice), encoding="utf-8")
        congelacion = congelar(otra, self.tmp / "otra.json")
        with self.assertRaises(SystemExit) as e:
            corredor.construir(str(otra), "00", congelacion)
        self.assertIn("table-01-00-edades", str(e.exception))

    def test_la_declaracion_del_dataset_tiene_que_describir_su_manifiesto(self):
        registro = json.loads(self.congelacion.read_text(encoding="utf-8"))
        dataset = self.tmp / "dataset.json"
        dataset.write_text(json.dumps({"corpus_freeze": {
            "path": str(self.congelacion), "version": registro["version"],
            "fingerprint": "sha256:" + "0" * 64}}), encoding="utf-8")
        original, ingest.MANIFEST = ingest.MANIFEST, dataset
        try:
            with self.assertRaises(SystemExit) as e:
                corredor.construir(str(MINI), "00")
        finally:
            ingest.MANIFEST = original
        self.assertIn("fingerprint", str(e.exception))


    def test_un_identificador_repetido_en_el_indice_se_rechaza(self):
        otra = self.tmp / "otra"
        shutil.copytree(MINI, otra)
        indice = json.loads((otra / "data" / "table_index.json").read_text(encoding="utf-8"))
        indice["tables"].append(dict(indice["tables"][1]))
        (otra / "data" / "table_index.json").write_text(json.dumps(indice), encoding="utf-8")
        congelacion = congelar(otra, self.tmp / "otra.json")
        with self.assertRaises(SystemExit) as e:
            corredor.construir(str(otra), "00", congelacion)
        self.assertIn("repite identificadores", str(e.exception))

    def test_un_parrafo_con_marcador_y_prosa_tambien_cita(self):
        # C-005 no la cita nadie en el fixture; aquí la cita una frase que
        # comparte párrafo con el marcador del registro.
        otra = self.tmp / "otra"
        shutil.copytree(MINI, otra)
        prosa = otra / "docs" / "secciones" / "001-00-0-arranque.md"
        prosa.write_text(prosa.read_text(encoding="utf-8").replace(
            "<!-- TABLE:claims-00 -->", "Cierre del arranque. [C-005]\n<!-- TABLE:claims-00 -->"),
            encoding="utf-8")
        r = corredor.construir(str(otra), "00", congelar(otra, self.tmp / "otra.json"))
        self.assertEqual(r["delta"]["corpus_origin"]["rows"]["C-005"]["via"], "prosa")

    def test_una_fila_mas_ancha_que_su_cabecera_no_pasa_la_conformidad(self):
        otra = self.tmp / "otra"
        shutil.copytree(MINI, otra)
        registro = otra / "data" / "afirmaciones" / "01.csv"
        registro.write_text(registro.read_text(encoding="utf-8").rstrip("\n") + ',"sobra"\n', encoding="utf-8")
        datos, h = parse(otra)
        self.assertTrue(any("celdas" in e for e in h.errores))


class Citas(unittest.TestCase):
    def test_conserva_la_forma_del_corpus(self):
        self.assertEqual(corredor.citas("[C-0412; C-0001–C-0003]"),
                         {"C-0412", "C-0001", "C-0002", "C-0003"})

    def test_un_rango_que_cruza_el_millar(self):
        self.assertEqual(corredor.citas("C-998–C-1001"), {"C-998", "C-999", "C-1000", "C-1001"})


class Localizar(unittest.TestCase):
    pasaje = {"text": "Se habla de fix-alfa aquí.", "character_offsets": {"start": 100, "end": 126}}

    def test_literal(self):
        self.assertEqual(corredor.localizar("habla", self.pasaje), (103, 108, None))

    def test_otra_capitalizacion_lo_dice(self):
        ini, fin, nota = corredor.localizar("FIX-Alfa", self.pasaje)
        self.assertEqual((ini, fin), (112, 120))
        self.assertIn("«fix-alfa»", nota)

    def test_dentro_de_otra_palabra_no_es_literal(self):
        pasaje = {"text": "Los Eutheria tienen placenta.", "character_offsets": {"start": 0, "end": 29}}
        ini, fin, nota = corredor.localizar("Theria", pasaje)
        self.assertEqual((ini, fin), (0, 29))
        self.assertIn("no aparece literal", nota)

    def test_ausente_cubre_el_pasaje(self):
        ini, fin, nota = corredor.localizar("FIX-Beta", self.pasaje)
        self.assertEqual((ini, fin), (100, 126))
        self.assertIn("no aparece literal", nota)


class Identidad(unittest.TestCase):
    def test_una_revision_existente_no_se_sobrescribe(self):
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            orden = [sys.executable, str(ROOT / "scripts" / "ingest" / "resolve_identity.py"),
                     "propose", str(MINI), "--out", tmp]
            self.assertEqual(subprocess.run(orden, capture_output=True).returncode, 0)
            revision = Path(tmp) / "identity-review.md"
            revision.write_text(revision.read_text(encoding="utf-8") + "\nmarca humana\n", encoding="utf-8")
            segunda = subprocess.run(orden, capture_output=True, text=True)
            self.assertNotEqual(segunda.returncode, 0)
            self.assertIn("marca humana", revision.read_text(encoding="utf-8"))

    def test_sobrescribir_retira_los_productos_de_la_revision_anterior(self):
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            orden = [sys.executable, str(ROOT / "scripts" / "ingest" / "resolve_identity.py"),
                     "propose", str(MINI), "--out", tmp]
            subprocess.run(orden, capture_output=True)
            final = Path(tmp) / "identity-map-final.json"
            final.write_text("{}", encoding="utf-8")
            r = subprocess.run([*orden, "--sobrescribir"], capture_output=True)
            self.assertEqual(r.returncode, 0)
            self.assertFalse(final.exists())

    def test_la_salida_por_defecto_lleva_la_huella(self):
        import resolve_identity
        _, huella, _ = resolve_identity.abrir_documento(str(MINI))
        destino = resolve_identity.salida_por_defecto(str(MINI), huella)
        self.assertEqual(destino.name, "corredor-mini-" + huella.split(":")[1][:12])


class Doi(unittest.TestCase):
    def test_la_cabecera_larga_del_doi_se_lee(self):
        datos, h = parse(MINI)
        self.assertEqual(h.errores, [])
        self.assertEqual([f["doi"] for f in datos["sources"]],
                         ["https://doi.org/10.0000/fixture.1", "https://doi.org/10.0000/fixture.2"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
