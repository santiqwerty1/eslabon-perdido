"""El libro mayor de prueba de las pruebas de ingestión, conversión y absorción.

Todo ocurre en un directorio temporal: el dataset, las congelaciones, los deltas
y los registros se reapuntan a él, así que el libro mayor real no se toca.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "ingest"))
sys.path.insert(0, str(ROOT / "scripts" / "validate"))

import absorber  # noqa: E402
import convertir  # noqa: E402
import corredor  # noqa: E402
import delta as delta_mod  # noqa: E402
import freeze  # noqa: E402
import ingest  # noqa: E402

MINI = ROOT / "tests" / "fixtures" / "corredor-mini"

class Entorno:
    """Un libro mayor vacío, con la sección 00 del fixture ya ingerida."""

    def __init__(self, tmp: Path):
        self.tmp = tmp
        self.records = tmp / "records"
        shutil.copytree(ROOT / "knowledge" / "records", self.records)
        for f in self.records.glob("*.jsonl"):
            f.write_text("", encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            freeze.cmd_create(argparse.Namespace(fuente=str(MINI), salida=str(tmp / "mini.json"), repositorio="x",
                                                 decision=None, sustituye=None, fecha="2026-09-25"))
        registro = json.loads((tmp / "mini.json").read_text(encoding="utf-8"))
        self.huella = registro["fingerprint"]
        (tmp / "dataset.json").write_text(json.dumps({
            "dataset_revision": "REV-000000",
            "corpus_freeze": {"path": str(tmp / "mini.json"), "fingerprint": self.huella}}), encoding="utf-8")
        self.parches = {
            (ingest, "MANIFEST"): tmp / "dataset.json",
            (ingest, "DELTAS"): tmp / "deltas",
            (ingest, "SECTIONS"): tmp / "sections",
            (ingest, "PASSAGES"): tmp / "passages",
            (ingest, "REPORTS"): tmp / "reports",
            (ingest, "RECORDS"): self.records,
            (convertir, "VIEWS"): tmp / "views",
            (delta_mod, "RECORDS"): self.records,
            (delta_mod, "MANIFEST"): tmp / "dataset.json",
            (delta_mod, "DELTAS"): tmp / "deltas",
            (delta_mod, "HISTORIAL"): tmp / "deltas" / "historial.jsonl",
            (convertir, "CONVERSIONS"): tmp,
            (absorber, "ABSORCIONES"): tmp / "absorptions",
        }

    def __enter__(self):
        self.originales = {k: getattr(*k) for k in self.parches}
        for (mod, nombre), valor in self.parches.items():
            setattr(mod, nombre, valor)
        with contextlib.redirect_stdout(io.StringIO()):
            corredor.ingerir(str(MINI), "00", None, False)
        self.delta_sec = json.loads((self.tmp / "deltas" / "SEC-000001.json").read_text(encoding="utf-8"))
        self.etiquetas = sorted({op["after"]["original_text"] for op in self.delta_sec["operations"]
                                 if op["file"] == "mentions.jsonl"})
        return self

    def __exit__(self, *exc):
        for (mod, nombre), valor in self.originales.items():
            setattr(mod, nombre, valor)

    def spec(self, **cambios) -> dict:
        s = {
            "freeze": {"version": "x", "fingerprint": self.huella},
            "section": "00",
            "decision": "DEC-057",
            "records": [
                {"key": "@Alfa", "file": "clades.jsonl", "rows": ["C-001"],
                 "record": {"preferred_label": "FIX-Alfa", "description": "Clado de prueba."}},
                {"key": "@Beta", "file": "clades.jsonl", "rows": ["C-001"],
                 "record": {"preferred_label": "FIX-Beta", "description": "Clado de prueba."}},
                {"key": "@CL1", "file": "claims.jsonl", "rows": ["C-001"],
                 "record": {"claim_type": "relational", "subject_id": "@Alfa", "predicate": "sister_group_of",
                            "object": {"entity_id": "@Beta"}}},
                {"key": "@EV1", "file": "evidence.jsonl", "rows": ["C-001"],
                 "record": {"evidence_type": "molecular", "description": "Lo dice el resumen.",
                            "source_id": "@S01", "locator": "resumen",
                            "supports_claim_ids": ["@CL1"], "challenges_claim_ids": []}},
            ],
            "rows": {"C-001": {"destination": "B", "keys": ["@CL1", "@EV1", "@Alfa", "@Beta"]},
                     **{f"C-00{n}": {"destination": "H", "keys": [], "note": "fuera de la prueba"} for n in range(2, 6)}},
            "mentions": {e: {"mention_type": "unresolved", "disposition": "discarded_with_reason", "targets": [],
                             "reason": "fuera de la prueba"} for e in self.etiquetas},
        }
        s["mentions"]["FIX-Alfa"] = {"mention_type": "clade", "disposition": "new_entity",
                                     "targets": ["@Alfa"], "reason": "clado de la prueba"}
        s.update(cambios)
        return s

    def construir(self, spec: dict) -> dict:
        ruta = self.tmp / "spec.json"
        ruta.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            return convertir.construir(ruta, str(MINI))
