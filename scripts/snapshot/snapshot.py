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
    "occurrences.jsonl", "traits.jsonl", "trait-observations.jsonl", "methods.jsonl", "molecules.jsonl",
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
        # Cada fichero agrupa los pasajes de una sección: se cuentan los pasajes.
        "passages": sum(len(json.loads(p.read_text(encoding="utf-8")))
                        for p in (corpus / "passages").glob("*.json")),
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
    # La congelación activa del corpus (DEC-056) es parte del estado: sin ella
    # no se puede demostrar qué versión se ingirió. Su ausencia se registra como
    # tal, para que verify la detecte en vez de fallar al leerla.
    # Las secciones ingeridas y sus pasajes son el texto del que citan las
    # menciones y la procedencia; las copias del registro del corredor son la
    # procedencia que declara cada delta (corpus_origin), y el historial de
    # deltas decide qué está pendiente y qué se revirtió: cambiarlos cambia lo
    # que el estado significa, aunque no cambie cuántos son.
    for p in sorted([*(corpus / "sections").glob("*.md"), *(corpus / "sections").glob("*.json"),
                     *(corpus / "sections").glob("*.registro.csv"), *(corpus / "passages").glob("*.json")]):
        files[str(p.relative_to(ROOT))] = digest(p)
    # Y los ficheros de conversión: son la entrada revisada de la que salieron
    # los registros (DEC-057), y su delta sólo guarda su ruta y su hash.
    for p in sorted((corpus / "conversions").glob("*.json")):
        files[str(p.relative_to(ROOT))] = digest(p)
    # Los deltas también: los pendientes reservan revisión e identificadores,
    # y cualquiera de ellos dice qué secciones se ingirieron ya.
    deltas = ROOT / "knowledge" / "deltas"
    for p in sorted([*deltas.glob("*.json"), deltas / "historial.jsonl"]):
        if p.exists():
            files[str(p.relative_to(ROOT))] = digest(p)
    congelada = (json.loads(MANIFEST.read_text(encoding="utf-8")).get("corpus_freeze") or {}).get("path")
    if congelada:
        ruta = ROOT / congelada
        files[congelada] = digest(ruta) if ruta.exists() else "ausente"
    return {"counts": counts, "files": files}


def conversiones_alteradas() -> list[str]:
    """Ficheros de conversión que ya no son los que guardó su delta.

    El delta de una conversión guarda la ruta y el hash del fichero del que
    salió. Si el fichero cambió, un snapshot nuevo registraría el contenido
    nuevo y lo daría por bueno, y la entrada real se habría perdido. Vale
    también para una conversión revertida, que sigue siendo constancia, con una
    excepción: que una conversión posterior, el reintento tras revertir, use la
    misma ruta. Revertir sirve para corregir el fichero y reintentar, y entonces
    manda el hash del reintento.
    """
    deltas = ROOT / "knowledge" / "deltas"
    historial = deltas / "historial.jsonl"
    orden: dict[str, int] = {}
    if historial.exists():
        for n, linea in enumerate(historial.read_text(encoding="utf-8").splitlines()):
            if linea.strip():
                h = json.loads(linea)
                if h.get("accion") == "aplicar":
                    orden.setdefault(h.get("delta"), n)
    fichas = []
    for p in sorted(deltas.glob("*.json")) if deltas.exists() else []:
        ficha = (json.loads(p.read_text(encoding="utf-8")).get("conversion") or {}).get("spec") or {}
        if ficha.get("path"):
            fichas.append((p.name, ficha))
    # Sin aplicar, un delta va detrás de todos los aplicados.
    posicion = lambda nombre: orden.get(nombre, len(orden) + 1)
    problemas = []
    for nombre, ficha in fichas:
        sustituida = any(otra["path"] == ficha["path"] and posicion(otro) > posicion(nombre)
                         for otro, otra in fichas if otro != nombre)
        if sustituida:
            continue
        ruta = ROOT / ficha["path"]
        if not ruta.exists():
            problemas.append(f"{ficha['path']}: falta, y {nombre} salió de él")
        elif digest(ruta) != ficha.get("sha256"):
            problemas.append(f"{ficha['path']}: no es el que guardó {nombre} ({ficha.get('sha256')})")
    return problemas


def cadena_rota(entradas: list[dict]) -> list[str]:
    """Lo que falta para que el historial reconstruya la revisión del manifiesto.

    Se rehace la pila: cada aplicación encima de la anterior y cada reversión
    del último aplicado. Los aplicados tienen que ir de REV-000001 en adelante
    sin huecos y terminar en la revisión que declara el manifiesto. Un historial
    vaciado o recortado deja revisiones sin delta que las explique, y un
    snapshot que lo diera por bueno no se podría reconstruir ni deshacer.
    """
    problemas, pila = [], []
    for h in entradas:
        if h.get("accion") == "aplicar":
            pila.append((h.get("delta"), h.get("revision")))
        elif h.get("accion") == "revertir":
            if pila and pila[-1][0] == h.get("delta"):
                pila.pop()
            else:
                problemas.append(f"historial.jsonl: revierte {h.get('delta')}, que no es el último aplicado")
    revisiones = [r for _, r in pila]
    esperadas = [f"REV-{n:06d}" for n in range(1, len(pila) + 1)]
    if revisiones != esperadas:
        problemas.append("historial.jsonl: los deltas aplicados no recorren las revisiones desde REV-000001 sin "
                         f"huecos ({', '.join(f'{d} → {r}' for d, r in pila) or 'ninguno'})")
    declarada = (json.loads(MANIFEST.read_text(encoding="utf-8")).get("dataset_revision")
                 if MANIFEST.exists() else None)
    if declarada and declarada != (revisiones[-1] if revisiones else "REV-000000"):
        problemas.append(f"historial.jsonl: sus deltas aplicados dejan el dataset en "
                         f"{revisiones[-1] if revisiones else 'REV-000000'}, y el manifiesto dice {declarada}")
    return problemas


def deltas_alterados() -> list[str]:
    """Deltas que ya no son los que se aplicaron, estén aplicados o revertidos.

    El historial guarda el hash de cada aplicación, y delta.py sólo acepta el
    contenido de la primera: al revertir y al reaplicar. Un delta revertido
    sigue siendo constancia y sigue reservando identificadores, así que también
    tiene que ser el que se aplicó. Si uno cambió, un snapshot que lo registrara
    daría por bueno un estado que no se reconstruye. Sin historial no hay prueba
    de qué se aplicó, y fuera de la revisión inicial eso también es un problema.
    """
    deltas = ROOT / "knowledge" / "deltas"
    historial = deltas / "historial.jsonl"
    if not historial.exists():
        revision = (json.loads(MANIFEST.read_text(encoding="utf-8")).get("dataset_revision")
                    if MANIFEST.exists() else None) or "REV-000000"
        if revision != "REV-000000":
            return [f"historial.jsonl: falta, y el dataset está en {revision}: no hay constancia de qué "
                    "deltas lo dejaron ahí ni con qué contenido"]
        return []
    primera: dict[str, str | None] = {}
    entradas = [json.loads(l) for l in historial.read_text(encoding="utf-8").splitlines() if l.strip()]
    for h in entradas:
        if h.get("accion") == "aplicar":
            primera.setdefault(h.get("delta"), h.get("sha256"))
    problemas = cadena_rota(entradas)
    for nombre, registrada in sorted(primera.items(), key=lambda par: str(par[0])):
        ruta = deltas / str(nombre)
        if not ruta.exists():
            problemas.append(f"{nombre}: se aplicó según el historial, pero falta")
        elif not registrada:
            problemas.append(f"{nombre}: se aplicó sin hash en el historial")
        elif digest(ruta) != registrada:
            problemas.append(f"{nombre}: no es el que se aplicó ({registrada})")
    return problemas


def next_id() -> str:
    existing = sorted(SNAPSHOTS.glob("SNAP-*.json"))
    n = int(existing[-1].stem.split("-")[1]) + 1 if existing else 0
    return f"SNAP-{n:06d}"


def create(label: str | None) -> int:
    alteradas = conversiones_alteradas()
    if alteradas:
        print("ERROR ficheros de conversión que no son los que se aplicaron; "
              "no se crea un snapshot que los dé por buenos:\n  " + "\n  ".join(alteradas))
        return 1
    alterados = deltas_alterados()
    if alterados:
        print("ERROR deltas que no son los que se aplicaron; "
              "no se crea un snapshot que los dé por buenos:\n  " + "\n  ".join(alterados))
        return 1
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    state = gather()
    ausentes = [f for f, h in state["files"].items() if h == "ausente"]
    if ausentes:
        # Un snapshot que registrara la ausencia la daría por buena en cada
        # verify posterior: no reconstruiría la versión del corpus que declara.
        print(f"ERROR falta {', '.join(ausentes)}, la congelación activa que declara dataset.json. "
              "No se crea un snapshot que no pueda verificarla")
        return 1
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
    problems += [f"conversión alterada: {a}" for a in conversiones_alteradas()]
    problems += [f"delta alterado: {a}" for a in deltas_alterados()]

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
