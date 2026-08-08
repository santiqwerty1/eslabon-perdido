#!/usr/bin/env python3
"""Validador del núcleo científico.

Implementa las once familias obligatorias de §19.2. Las que dependen de tipos
todavía no implementados se declaran pendientes con su fase, en vez de pasar en
verde por vacuidad: un validador que no distingue "correcto" de "no comprobado"
no sirve para nada.

Severidades de §19.1: ERROR impide aceptar el delta, WARNING exige issue o
justificación, INFO no bloquea.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECORDS = ROOT / "knowledge" / "records"
SCHEMAS = ROOT / "schemas" / "json-schema"
MANIFEST = ROOT / "knowledge" / "corpus" / "manifests" / "dataset.json"

ID_RE = re.compile(
    r"^(SEC|PASSAGE|MENTION|SRC|NAME|TAXCONCEPT|CLADE|LINEAGE|POP|SPECIMEN|SITE|"
    r"REGION|OCC|TRAIT|TRAITOBS|GENE|ALLELE|EVENT|CLAIM|EVID|DATASET|ANALYSIS|"
    r"RESULT|HYP|TAXVIEW|PHYVIEW|CAMP|CHAPTER|MECH|GAME|ISSUE|TERM|TIME)-[0-9]{6}$"
)

# Fichero JSONL -> esquema. Los tipos sin esquema todavía llegan en su fase.
SCHEMA_BY_FILE = {
    "mentions.jsonl": "mention.json",
    "sources.jsonl": "source.json",
    "issues.jsonl": "issue.json",
}

# Familias de §19.2 que aún no pueden comprobarse, con la fase que las habilita.
PENDING = {
    "identity": "Fase 3 — requiere TaxonomicName, TaxonConcept, CladeConcept, Lineage",
    "time": "Fase 4 — requiere expresiones temporales",
    "geography": "Fase 4 — requiere Region y Occurrence",
    "hypotheses": "Fase 5 — requiere Hypothesis y vistas",
    "evidence": "Fase 4 — requiere EvidenceItem, Dataset, Analysis, Result",
    "state": "Fase 4 — requiere registros con dimensiones epistemológicas",
    "separation": "Fase 8 — requiere GameProjection",
}


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    infos: list[str] = field(default_factory=list)

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def info(self, msg: str) -> None:
        self.infos.append(msg)

    @property
    def ok(self) -> bool:
        return not self.errors


def load_jsonl(path: Path, rep: Report) -> list[dict]:
    records = []
    if not path.exists():
        rep.error(f"{path.name}: no existe")
        return records
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            rep.error(f"{path.name}:{n}: JSON inválido — {exc.msg}")
    return records


def all_records(rep: Report) -> dict[str, list[dict]]:
    return {p.name: load_jsonl(p, rep) for p in sorted(RECORDS.glob("*.jsonl"))}


# --- familias ---------------------------------------------------------------

def v_schema(data: dict[str, list[dict]], rep: Report) -> None:
    """Campos requeridos, tipos, enumeraciones, versión compatible."""
    try:
        from jsonschema import Draft202012Validator
        from referencing import Registry, Resource
    except ImportError:
        rep.warn("schema: jsonschema no instalado; sólo se comprobó JSON bien formado")
        return

    resources = []
    for f in SCHEMAS.glob("*.json"):
        doc = json.loads(f.read_text(encoding="utf-8"))
        resources.append((f.name, Resource.from_contents(doc)))
    registry = Registry().with_resources(resources)

    for fname, schema_name in SCHEMA_BY_FILE.items():
        schema = json.loads((SCHEMAS / schema_name).read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema, registry=registry)
        for i, rec in enumerate(data.get(fname, []), 1):
            for err in validator.iter_errors(rec):
                loc = "/".join(str(p) for p in err.absolute_path) or "(raíz)"
                rep.error(f"{fname}:{i}: {loc}: {err.message}")

    sin_esquema = sorted(set(data) - set(SCHEMA_BY_FILE))
    if sin_esquema:
        rep.info(f"schema: {len(sin_esquema)} ficheros sin esquema todavía (llegan en su fase)")


def v_references(data: dict[str, list[dict]], rep: Report) -> None:
    """Todo ID referenciado existe; no hay IDs duplicados."""
    seen: dict[str, str] = {}
    for fname, recs in data.items():
        for rec in recs:
            rid = rec.get("id")
            if not rid:
                continue
            if not ID_RE.match(rid):
                rep.error(f"{fname}: identificador con formato inválido: {rid!r} (DEC-052)")
            if rid in seen:
                rep.error(f"{fname}: identificador duplicado {rid} (ya en {seen[rid]})")
            seen[rid] = fname

    for fname, recs in data.items():
        for rec in recs:
            for key, val in rec.items():
                if not key.endswith("_ids") or not isinstance(val, list):
                    continue
                for ref in val:
                    if isinstance(ref, str) and ID_RE.match(ref) and ref not in seen:
                        rep.error(f"{fname}: {rec.get('id')}.{key} apunta a {ref}, que no existe")


def v_coverage(data: dict[str, list[dict]], rep: Report) -> None:
    """Toda mención tiene destino; todo descarte está justificado."""
    for m in data.get("mentions.jsonl", []):
        mid = m.get("id", "?")
        if m.get("disposition") is None:
            rep.error(f"cobertura: {mid} no tiene destino (§17 paso 10)")
        if m.get("disposition") == "discarded_with_reason" and not m.get("notes"):
            rep.error(f"cobertura: {mid} descartada sin justificación")


def v_provenance(data: dict[str, list[dict]], rep: Report) -> None:
    """La cadena de §4.5 está completa, no sólo presente."""
    for s in data.get("sources.jsonl", []):
        if s.get("source_type") == "section_provided" and s.get("verification_status") != "pending_verification":
            rep.error(
                f"procedencia: {s.get('id')} procede de la sección sin fuente externa "
                "y debe quedar marcada pending_verification (§17 paso 7)"
            )
        if s.get("source_type") != "section_provided" and not (s.get("doi") or s.get("url")):
            rep.warn(f"procedencia: {s.get('id')} no tiene DOI ni URL resoluble")

    for m in data.get("mentions.jsonl", []):
        if not m.get("passage_id"):
            rep.error(f"procedencia: {m.get('id')} no enlaza pasaje (§17 paso 2)")


def v_pending(name: str, rep: Report) -> None:
    rep.info(f"{name}: pendiente — {PENDING[name]}")


FAMILIES = {
    "schema": v_schema,
    "references": v_references,
    "coverage": v_coverage,
    "identity": None,
    "time": None,
    "geography": None,
    "hypotheses": None,
    "evidence": None,
    "provenance": v_provenance,
    "state": None,
    "separation": None,
}


def run(names: list[str]) -> Report:
    rep = Report()
    data = all_records(rep)

    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        for label, entry in [("activa", manifest["guides"]["active"])] + [
            ("archivada", g) for g in manifest["guides"]["archived"]
        ]:
            path = ROOT / entry["path"]
            if not path.exists():
                rep.error(f"preservación: falta la guía {label} en {entry['path']}")
                continue
            import hashlib

            digest = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
            if digest != entry["content_hash"]:
                sev = rep.error if label == "archivada" else rep.warn
                sev(f"preservación: la guía {label} no coincide con su hash registrado")
    else:
        rep.error("no existe el manifiesto del dataset")

    for name in names:
        fn = FAMILIES[name]
        if fn is None:
            v_pending(name, rep)
        else:
            fn(data, rep)
    return rep


def main() -> int:
    ap = argparse.ArgumentParser(description="Validador del núcleo científico (§19)")
    ap.add_argument(
        "family",
        nargs="?",
        default="all",
        choices=["all", *FAMILIES],
        help="familia de §19.2 a ejecutar",
    )
    args = ap.parse_args()
    names = list(FAMILIES) if args.family == "all" else [args.family]

    rep = run(names)

    for msg in rep.errors:
        print(f"ERROR   {msg}")
    for msg in rep.warnings:
        print(f"WARNING {msg}")
    for msg in rep.infos:
        print(f"INFO    {msg}")

    print(
        f"\n{len(rep.errors)} errores, {len(rep.warnings)} advertencias, "
        f"{len(rep.infos)} informativos"
    )
    if rep.warnings:
        print("Recuerda: §19.1 exige que todo WARNING lleve issue o justificación.")
    print("VALIDACIÓN CORRECTA" if rep.ok else "VALIDACIÓN FALLIDA")
    return 0 if rep.ok else 1


if __name__ == "__main__":
    sys.exit(main())
