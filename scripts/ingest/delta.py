#!/usr/bin/env python3
"""Deltas: aplicar y revertir (§16.4, §17 paso 13).

El criterio de aceptación de la Fase 2 es literal: *el delta puede aplicarse y
revertirse*. Sin eso, ingerir sería un viaje de ida y equivocarse costaría
reconstruir el dataset a mano.

Las quince operaciones de §16.4. Ninguna borra información: `DEPRECATE_RECORD` y
`SUPERSEDE_RECORD` cambian `record_status` y dejan la línea donde estaba, que es
lo que exige §0.1. Revertir un delta sí retira lo que ese delta añadió — eso no
es borrar historia, es deshacer una operación registrada, y el propio delta
queda en `knowledge/deltas/` como constancia de que ocurrió.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECORDS = ROOT / "knowledge" / "records"
DELTAS = ROOT / "knowledge" / "deltas"
MANIFEST = ROOT / "knowledge" / "corpus" / "manifests" / "dataset.json"

# §16.4. El valor indica si la operación añade, modifica o marca.
OPERATIONS = {
    "ADD_RECORD": "add",
    "UPDATE_RECORD": "update",
    "ADD_ALIAS": "update",
    "ADD_CLAIM": "add",
    "ADD_EVIDENCE": "add",
    "ADD_EVENT": "add",
    "ADD_HYPOTHESIS": "add",
    "ADD_SOURCE": "add",
    "ADD_ISSUE": "add",
    "RESOLVE_ISSUE": "update",
    "DEPRECATE_RECORD": "update",
    "SUPERSEDE_RECORD": "update",
    "MERGE_CONFIRMED_IDENTITIES": "update",
    "MIGRATE_SCHEMA": "update",
    "BUILD_VIEW": "add",
}


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records),
        encoding="utf-8",
    )


def apply_ops(ops: list[dict], reverse: bool = False) -> list[str]:
    """Aplica (o revierte) las operaciones. Devuelve el diario de lo hecho."""
    diario: list[str] = []
    secuencia = list(reversed(ops)) if reverse else ops

    por_fichero: dict[str, list[dict]] = {}

    def cargar(fichero: str) -> list[dict]:
        if fichero not in por_fichero:
            por_fichero[fichero] = read_jsonl(RECORDS / fichero)
        return por_fichero[fichero]

    for op in secuencia:
        tipo = op["operation"]
        if tipo not in OPERATIONS:
            raise ValueError(f"operación desconocida: {tipo}")
        fichero = op["file"]
        rid = op["record_id"]
        recs = cargar(fichero)
        idx = next((i for i, r in enumerate(recs) if r.get("id") == rid), None)
        modo = OPERATIONS[tipo]

        if modo == "add":
            if not reverse:
                if idx is not None:
                    raise ValueError(f"{tipo}: {rid} ya existe en {fichero}")
                recs.append(op["after"])
                diario.append(f"+ {tipo} {rid}")
            else:
                if idx is None:
                    diario.append(f"~ {tipo} {rid} no estaba; nada que revertir")
                else:
                    recs.pop(idx)
                    diario.append(f"- {tipo} {rid} retirado")
        else:  # update
            estado = op["before"] if reverse else op["after"]
            if idx is None:
                raise ValueError(f"{tipo}: {rid} no existe en {fichero}")
            recs[idx] = estado
            diario.append(f"{'<' if reverse else '>'} {tipo} {rid}")

    for fichero, recs in por_fichero.items():
        write_jsonl(RECORDS / fichero, recs)

    return diario


def bump_revision(delta: dict, reverse: bool) -> None:
    if not MANIFEST.exists():
        return
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    m["dataset_revision"] = (
        delta["dataset_revision_before"] if reverse else delta["dataset_revision_after"]
    )
    MANIFEST.write_text(json.dumps(m, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def cmd(path: Path, reverse: bool, dry: bool) -> int:
    delta = json.loads(path.read_text(encoding="utf-8"))
    ops = delta.get("operations", [])
    verbo = "REVERTIR" if reverse else "APLICAR"
    print(f"{verbo} {path.name} · {len(ops)} operaciones")
    print(f"  revisión {delta['dataset_revision_before']} -> {delta['dataset_revision_after']}")

    if dry:
        for op in (reversed(ops) if reverse else ops):
            print(f"    {op['operation']:28} {op['record_id']:18} {op['file']}")
        print("\n(en seco: no se ha escrito nada)")
        return 0

    try:
        diario = apply_ops(ops, reverse)
    except ValueError as exc:
        print(f"ERROR {exc}")
        return 1

    for linea in diario:
        print(f"    {linea}")
    bump_revision(delta, reverse)
    print(f"\n{len(diario)} operaciones {'revertidas' if reverse else 'aplicadas'}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Aplica o revierte un delta (§16.4)")
    ap.add_argument("delta", help="ruta al delta, o su nombre dentro de knowledge/deltas/")
    ap.add_argument("--revert", action="store_true", help="revertir en vez de aplicar")
    ap.add_argument("--dry-run", action="store_true", help="mostrar sin escribir")
    args = ap.parse_args()

    path = Path(args.delta)
    if not path.exists():
        path = DELTAS / args.delta
    if not path.exists():
        print(f"ERROR no existe el delta: {args.delta}")
        return 1
    return cmd(path, args.revert, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
