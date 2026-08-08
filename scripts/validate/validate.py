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
    r"RESULT|HYP|TAXVIEW|PHYVIEW|CAMP|CHAPTER|MECH|GAME|ISSUE|TERM|TIME|"
    r"TECH|ECOSYS|METHOD|RESEARCHER|CONFLICT)-[0-9]{6}$"
)

# Fichero JSONL -> esquema. Cubre los veintiún ficheros de knowledge/records/
# listados en §16.2. Las ocho entidades biológicas comunes comparten entity.json
# (Apéndice E.5): su entity_type discrimina, y el propio esquema exige que el
# prefijo del identificador concuerde con él.
#
# Tres esquemas no aparecen aquí porque su registro no vive en records/:
#   - game-projection.json  la capa 8 vive en game/projections/ (§6.8).
# Las expresiones temporales y las vistas ya tienen fichero desde que se
# resolvio ISSUE-000033.
SCHEMA_BY_FILE = {
    "mentions.jsonl": "mention.json",
    "sources.jsonl": "source.json",
    "issues.jsonl": "issue.json",
    "taxonomic-names.jsonl": "taxonomic-name.json",
    "taxon-concepts.jsonl": "taxon-concept.json",
    "clades.jsonl": "entity.json",
    "lineages.jsonl": "entity.json",
    "populations.jsonl": "entity.json",
    "specimens.jsonl": "entity.json",
    "sites.jsonl": "entity.json",
    "regions.jsonl": "entity.json",
    "occurrences.jsonl": "entity.json",
    "traits.jsonl": "entity.json",
    "trait-observations.jsonl": "trait-observation.json",
    "claims.jsonl": "claim.json",
    "evidence.jsonl": "evidence.json",
    "datasets.jsonl": "dataset.json",
    "analyses.jsonl": "analysis.json",
    "results.jsonl": "result.json",
    "events.jsonl": "event.json",
    "hypotheses.jsonl": "hypothesis.json",
    "temporal-expressions.jsonl": "temporal-expression.json",
    "classification-views.jsonl": "classification-view.json",
    "phylogenetic-views.jsonl": "phylogenetic-view.json",
}

# Orden canónico de §19.2. Las familias se cargan desde families/.
FAMILY_ORDER = [
    "schema", "references", "coverage", "identity", "time", "geography",
    "hypotheses", "evidence", "provenance", "state", "separation",
]


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    infos: list[str] = field(default_factory=list)
    # Directorio de registros en curso. None = dataset real. Las familias que
    # comparan contra el estado global (snapshots, manifiesto, guías) deben
    # omitir esa comprobación cuando se está validando un fixture, que es un
    # dataset independiente y no tiene por qué coincidir con el snapshot.
    records_dir: object = None

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


def all_records(rep: Report, records_dir: Path | None = None) -> dict[str, list[dict]]:
    """Carga los JSONL de un directorio de registros.

    Por defecto el dataset real. Los fixtures de §27.9 son datasets completos e
    independientes, asi que se validan apuntando aqui: sin esto, la herramienta
    oficial no puede comprobar sus propios casos de prueba.
    """
    base = records_dir or RECORDS
    return {p.name: load_jsonl(p, rep) for p in sorted(base.glob("*.jsonl"))}


# --- familias ---------------------------------------------------------------

def v_schema(data: dict[str, list[dict]], rep: Report) -> None:
    """Campos requeridos, tipos, enumeraciones, versión compatible."""
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        rep.warn(
            "schema: jsonschema no instalado; sólo se comprobó JSON bien formado. "
            "Ver ISSUE-000029 y el README"
        )
        return

    docs = {f.name: json.loads(f.read_text(encoding="utf-8")) for f in SCHEMAS.glob("*.json")}

    # Resolución de $ref entre esquemas. jsonschema >= 4.18 usa `referencing`;
    # las versiones anteriores, incluida la 4.10 que empaqueta Debian 12, usan
    # RefResolver. Se admiten ambas para no atar el proyecto a una distribución.
    def make_validator(schema: dict):
        try:
            from referencing import Registry, Resource

            registry = Registry().with_resources(
                [(name, Resource.from_contents(doc)) for name, doc in docs.items()]
            )
            return Draft202012Validator(schema, registry=registry)
        except ImportError:
            from jsonschema import RefResolver

            resolver = RefResolver(base_uri="", referrer=schema, store=dict(docs))
            return Draft202012Validator(schema, resolver=resolver)

    for fname, schema_name in SCHEMA_BY_FILE.items():
        if schema_name not in docs:
            rep.error(f"schema: falta el esquema {schema_name} declarado para {fname}")
            continue
        validator = make_validator(docs[schema_name])
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


BUILTIN = {
    "schema": v_schema,
    "references": v_references,
    "coverage": v_coverage,
    "provenance": v_provenance,
}


def load_families() -> dict[str, object]:
    """Carga las familias de families/ y las combina con las integradas."""
    import importlib.util

    out: dict[str, object] = dict(BUILTIN)
    fam_dir = Path(__file__).parent / "families"
    for f in sorted(fam_dir.glob("*.py")):
        if f.stem.startswith("_"):
            continue
        spec = importlib.util.spec_from_file_location(f"families.{f.stem}", f)
        if spec is None or spec.loader is None:
            continue
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        name = getattr(mod, "NAME", f.stem)
        out[name] = mod
    return out


FAMILIES = load_families()


def run(names: list[str], records_dir: Path | None = None) -> Report:
    rep = Report()
    rep.records_dir = records_dir
    data = all_records(rep, records_dir)

    # La preservacion de las guias solo aplica al dataset real, no a un fixture.
    if records_dir is None and MANIFEST.exists():
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
    elif records_dir is None:
        rep.error("no existe el manifiesto del dataset")

    for name in names:
        fam = FAMILIES.get(name)
        if fam is None:
            rep.info(f"{name}: sin implementar todavía")
        elif callable(fam):
            fam(data, rep)
        else:
            phase = getattr(fam, "PHASE", None)
            if phase:
                rep.info(f"{name}: pendiente — {phase}")
            else:
                fam.check(data, rep)
    return rep


def main() -> int:
    ap = argparse.ArgumentParser(description="Validador del núcleo científico (§19)")
    ap.add_argument(
        "family",
        nargs="?",
        default="all",
        choices=["all", *FAMILY_ORDER],
        help="familia de §19.2 a ejecutar",
    )
    ap.add_argument(
        "--records",
        metavar="DIR",
        default=None,
        help="directorio de registros a validar; por defecto knowledge/records/. "
             "Apunta a un fixture de tests/fixtures/ para validarlo.",
    )
    args = ap.parse_args()
    names = list(FAMILY_ORDER) if args.family == "all" else [args.family]

    records_dir = Path(args.records).resolve() if args.records else None
    if records_dir is not None and not records_dir.is_dir():
        print(f"ERROR   no existe el directorio de registros: {records_dir}")
        return 1

    rep = run(names, records_dir)

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
