#!/usr/bin/env python3
"""La familia «estado» ante una reversión posterior al último snapshot.

Revertir un delta retira lo que añadió, y `delta.py` lo permite. Si el último
snapshot se tomó con ese delta aplicado, sus recuentos lo incluyen, y comparar
contra ellos sin más haría que una reversión legítima pareciera un borrado. El
historial sólo crece y el snapshot guarda su hash: lo posterior al snapshot se
sabe, y lo que retiraron sus reversiones se descuenta. Nada más.

Uso:
    python3 tests/validation/test_reversiones.py
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "validate"))

import validate  # noqa: E402

SECCION = {"delta": "SEC-000001.json", "accion": "aplicar", "revision": "REV-000001"}
CONVERSION = {"delta": "SEC-000001-conversion.json", "accion": "aplicar", "revision": "REV-000002"}
REVERSION = {"delta": "SEC-000001-conversion.json", "accion": "revertir", "revision": "REV-000001"}


def linea(h: dict) -> str:
    return json.dumps(h) + "\n"


class Reversiones(unittest.TestCase):
    def caso(self, tmp: Path, *, historial: list[dict], conocido: int, claims: list[str], contaba: int = 2,
             alta: str = "ADD_RECORD") -> list[str]:
        """Un snapshot que conoce las `conocido` primeras líneas del historial y contaba `contaba` afirmaciones."""
        (tmp / "deltas").mkdir()
        (tmp / "snapshots").mkdir()
        (tmp / "claims.jsonl").write_text(
            "".join(json.dumps({"id": c, "record_status": "active"}) + "\n" for c in claims), encoding="utf-8")
        (tmp / "deltas" / "SEC-000001.json").write_text(json.dumps({
            "dataset_revision_before": "REV-000000", "dataset_revision_after": "REV-000001",
            "operations": [{"operation": "ADD_RECORD", "file": "claims.jsonl", "record_id": "CLAIM-000001",
                            "before": None, "after": {"id": "CLAIM-000001"}}]}), encoding="utf-8")
        (tmp / "deltas" / "SEC-000001-conversion.json").write_text(json.dumps({
            "dataset_revision_before": "REV-000001", "dataset_revision_after": "REV-000002",
            "operations": [{"operation": alta, "file": "claims.jsonl", "record_id": "CLAIM-000002",
                            "before": None, "after": {"id": "CLAIM-000002"}}]}), encoding="utf-8")
        texto = "".join(linea(h) for h in historial)
        (tmp / "deltas" / "historial.jsonl").write_text(texto, encoding="utf-8")
        prefijo = "".join(linea(h) for h in historial[:conocido]).encode("utf-8")
        (tmp / "snapshots" / "SNAP-000001.json").write_text(json.dumps({
            "snapshot_id": "SNAP-000001", "dataset_revision": "REV-000002", "counts": {"claims": contaba},
            "files": {"knowledge/deltas/historial.jsonl": "sha256:" + hashlib.sha256(prefijo).hexdigest()}}),
            encoding="utf-8")
        return validate.run(["state"], records_dir=tmp).errors

    def recuento(self, errores: list[str]) -> list[str]:
        return [e for e in errores if "claims: SNAP-000001" in e]

    def test_una_reversion_posterior_al_snapshot_no_es_un_borrado(self):
        with tempfile.TemporaryDirectory() as tmp:
            errores = self.caso(Path(tmp), historial=[SECCION, CONVERSION, REVERSION], conocido=2,
                                claims=["CLAIM-000001"])
        self.assertEqual(self.recuento(errores), [])

    def test_sin_reversion_la_afirmacion_que_falta_se_denuncia(self):
        with tempfile.TemporaryDirectory() as tmp:
            errores = self.caso(Path(tmp), historial=[SECCION, CONVERSION], conocido=2, claims=["CLAIM-000001"])
        self.assertEqual(len(self.recuento(errores)), 1)

    def test_una_reversion_que_el_snapshot_ya_conocia_no_descuenta(self):
        # El snapshot se tomó después de revertir: sus recuentos ya no incluían
        # lo revertido, y lo que falte ahora es un borrado.
        with tempfile.TemporaryDirectory() as tmp:
            errores = self.caso(Path(tmp), historial=[SECCION, CONVERSION, REVERSION], conocido=3,
                                claims=["CLAIM-000001"])
        self.assertEqual(len(self.recuento(errores)), 1)

    def test_la_reversion_no_tapa_otro_borrado(self):
        with tempfile.TemporaryDirectory() as tmp:
            errores = self.caso(Path(tmp), historial=[SECCION, CONVERSION, REVERSION], conocido=2, claims=[])
        [e] = self.recuento(errores)
        self.assertIn("retiraron 1", e)

    def test_aplicar_y_revertir_despues_del_snapshot_no_abre_margen(self):
        # El snapshot no incluía la conversión: revertirla no le quita nada, y
        # la afirmación de la sección que falta es un borrado.
        with tempfile.TemporaryDirectory() as tmp:
            errores = self.caso(Path(tmp), historial=[SECCION, CONVERSION, REVERSION], conocido=1, claims=[],
                                contaba=1)
        self.assertEqual(len(self.recuento(errores)), 1)

    def test_cuenta_toda_operacion_de_alta(self):
        # ADD_CLAIM también es un alta: revertirla la retira igual que ADD_RECORD.
        with tempfile.TemporaryDirectory() as tmp:
            errores = self.caso(Path(tmp), historial=[SECCION, CONVERSION, REVERSION], conocido=2,
                                claims=["CLAIM-000001"], alta="ADD_CLAIM")
        self.assertEqual(self.recuento(errores), [])

    def test_las_altas_son_las_de_delta_py(self):
        sys.path.insert(0, str(ROOT / "scripts" / "ingest"))
        import delta  # noqa: E402
        from families import state  # noqa: E402
        self.assertEqual(state.ADD_OPERATIONS, {op for op, modo in delta.OPERATIONS.items() if modo == "add"})

    def test_un_recuento_en_lugar_de_identificadores_es_un_error_y_no_un_fallo(self):
        with tempfile.TemporaryDirectory() as tmp:
            caso = Path(tmp)
            (caso / "deltas").mkdir()
            (caso / "claims.jsonl").write_text("", encoding="utf-8")
            (caso / "deltas" / "SEC-000001.json").write_text(json.dumps({
                "dataset_revision_before": "REV-000000", "dataset_revision_after": "REV-000001",
                "records_updated": 2}), encoding="utf-8")
            errores = validate.run(["state"], records_dir=caso).errors
        self.assertTrue(any("records_updated" in e and "lista" in e for e in errores), errores)


if __name__ == "__main__":
    unittest.main(verbosity=2)
