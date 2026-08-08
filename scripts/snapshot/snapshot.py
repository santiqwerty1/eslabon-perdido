#!/usr/bin/env python3
"""Snapshots del dataset (§16.6).

Un snapshot es un estado completo reconstruible. `verify` comprueba que el
estado del repositorio coincide con el snapshot registrado, que es el criterio
de aceptación del paso 15 de §17: el estado debe poder reconstruirse sin la
conversación.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECORDS = ROOT / "knowledge" / "records"
SNAPSHOTS = ROOT / "knowledge" / "snapshots"
MANIFEST = ROOT / "knowledge" / "corpus" / "manifests" / "dataset.json"

COUNT_MAP = {
    "sections": None,
    "passages": None,
    "mentions": "mentions.jsonl",
    "claims": "claims.jsonl",
    "events": "events.jsonl",
    "hypotheses": "hypotheses.jsonl",
    "sources": "sources.jsonl",
    "issues": "issues.jsonl",
}
ENTITY_FILES = [
    "taxonomic-names.jsonl", "taxon-concepts.jsonl", "clades.jsonl", "lineages.jsonl",
    "populations.jsonl", "specimens.jsonl", "sites.jsonl", "regions.jsonl",
    "occurrences.jsonl", "traits.jsonl", "trait-observations.jsonl",
]
VIEW_DIR = ROOT / "knowledge" / "views"


def count_lines(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def gather() -> dict:
    corpus = ROOT / "knowledge" / "corpus"
    counts = {
        "sections": len(list((corpus / "sections").glob("*.md"))),
        "passages": len(list((corpus / "passages").glob("*.json"))),
    }
    for key, fname in COUNT_MAP.items():
        if fname:
            counts[key] = count_lines(RECORDS / fname)
    counts["entities"] = sum(count_lines(RECORDS / f) for f in ENTITY_FILES)
    counts["views"] = len([p for p in VIEW_DIR.rglob("*.json")])

    files = {}
    for p in sorted(RECORDS.glob("*.jsonl")):
        files[str(p.relative_to(ROOT))] = digest(p)
    files[str(MANIFEST.relative_to(ROOT))] = digest(MANIFEST)
    return {"counts": counts, "files": files}


def next_id() -> str:
    existing = sorted(SNAPSHOTS.glob("SNAP-*.json"))
    n = int(existing[-1].stem.split("-")[1]) + 1 if existing else 0
    return f"SNAP-{n:06d}"


def create(label: str | None) -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    state = gather()
    snap_id = next_id()

    # El manifiesto se actualiza ANTES de fijar los hashes: si se hiciera después,
    # el snapshot guardaría el hash previo del manifiesto y `verify` fallaría
    # siempre contra su propio snapshot.
    manifest["snapshot_id"] = snap_id
    manifest["counts"] = state["counts"]
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    state["files"][str(MANIFEST.relative_to(ROOT))] = digest(MANIFEST)

    snapshot = {
        "snapshot_id": snap_id,
        "label": label,
        "guide_version": manifest["guide_version"],
        "schema_version": manifest["schema_version"],
        "dataset_revision": manifest["dataset_revision"],
        "active_campaign": manifest["active_campaign"],
        **state,
    }
    out = SNAPSHOTS / f"{snap_id}.json"
    out.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"{snap_id} creado en {out.relative_to(ROOT)}")
    print(f"  registros: {sum(state['counts'].values())} | ficheros: {len(state['files'])}")
    return 0


def verify(snap_id: str | None) -> int:
    snaps = sorted(SNAPSHOTS.glob("SNAP-*.json"))
    if not snaps:
        print("no hay snapshots que verificar")
        return 1
    path = SNAPSHOTS / f"{snap_id}.json" if snap_id else snaps[-1]
    if not path.exists():
        print(f"no existe {path.name}")
        return 1

    snapshot = json.loads(path.read_text(encoding="utf-8"))
    state = gather()
    problems = []

    for k, v in snapshot["counts"].items():
        if state["counts"].get(k) != v:
            problems.append(f"recuento {k}: snapshot {v}, actual {state['counts'].get(k)}")
    for f, h in snapshot["files"].items():
        if state["files"].get(f) != h:
            problems.append(f"contenido cambiado: {f}")
    for f in set(state["files"]) - set(snapshot["files"]):
        problems.append(f"fichero nuevo no registrado: {f}")

    print(f"verificando {snapshot['snapshot_id']}")
    for p in problems:
        print(f"  DIFIERE {p}")
    print("SNAPSHOT ÍNTEGRO" if not problems else f"SNAPSHOT DESVIADO ({len(problems)} diferencias)")
    return 0 if not problems else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Snapshots del dataset (§16.6)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("create", help="crear un snapshot del estado actual")
    c.add_argument("--label", default=None)
    v = sub.add_parser("verify", help="comprobar que el estado coincide con un snapshot")
    v.add_argument("snapshot_id", nargs="?", default=None)
    args = ap.parse_args()
    return create(args.label) if args.cmd == "create" else verify(args.snapshot_id)


if __name__ == "__main__":
    sys.exit(main())
