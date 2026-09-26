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
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECORDS = ROOT / "knowledge" / "records"
DELTAS = ROOT / "knowledge" / "deltas"
MANIFEST = ROOT / "knowledge" / "corpus" / "manifests" / "dataset.json"
# Qué se aplicó y qué se revirtió, en orden. El delta revertido sigue en
# knowledge/deltas/ como constancia, y sin esto no se distinguiría de uno que
# nadie ha aplicado todavía. Sólo se añaden líneas.
HISTORIAL = DELTAS / "historial.jsonl"

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


# Un delta de una sección entera trae miles de operaciones. Volcarlas una por
# línea no es revisarlo: son miles de líneas idénticas salvo el identificador, y
# lo que hay que mirar antes de aplicar —qué clases de operación entran, sobre
# qué ficheros, y si alguna toca algo que ya existía— no se ve en ninguna de
# ellas. El resumen va primero y el volcado completo queda tras --full.
TOPE_LISTADO = 40


def resumen(ops: list[dict]) -> list[str]:
    """Qué hace este delta, en una tabla que cabe en pantalla."""
    grupos: dict[tuple[str, str], list[dict]] = {}
    for op in ops:
        grupos.setdefault((op["operation"], op["file"]), []).append(op)
    lineas = ["", "  qué toca este delta:"]
    for (tipo, fichero), miembros in sorted(grupos.items(), key=lambda x: -len(x[1])):
        modo = OPERATIONS.get(tipo, "?")
        ids = [m["record_id"] for m in miembros]
        rango = ids[0] if len(ids) == 1 else f"{ids[0]} … {ids[-1]}"
        lineas.append(f"    {len(miembros):7}  {tipo:28} {fichero:24} {rango}")
        lineas.append(f"    {'':7}  ({modo}; ejemplo: "
                      + ", ".join(sorted(_muestra(miembros))) + ")")
    return lineas


def _muestra(miembros: list[dict], n: int = 3) -> list[str]:
    """Tres valores reales del contenido, repartidos, para juzgarlo sin abrir el JSON.

    Repartidos y no los tres primeros: el primer registro de un delta de ocho mil
    suele ser la cabecera del documento y no dice nada del resto.
    """
    paso = max(1, len(miembros) // n)
    out = []
    for m in miembros[::paso][:n]:
        cuerpo = m.get("after") or m.get("before") or {}
        pista = None
        if isinstance(cuerpo, dict):
            for k in ("original_text", "preferred_label", "label", "title", "text"):
                if cuerpo.get(k):
                    pista = str(cuerpo[k])[:40]
                    break
        out.append(repr(pista) if pista else m["record_id"])
    return out


def huella(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def numero(revision) -> int:
    m = re.fullmatch(r"REV-(\d+)", revision or "") if isinstance(revision, str) else None
    return int(m.group(1)) if m else -1


def fuera_de_orden(path: Path, origen: str, reverse: bool) -> str | None:
    """Por qué este delta no se puede aplicar o revertir ahora, o None."""
    # El historial y el snapshot sólo conocen los deltas de knowledge/deltas/:
    # una copia con el mismo nombre en otro sitio no es el delta registrado.
    if path.resolve() != (DELTAS / path.name).resolve():
        return f"{path} no está en knowledge/deltas/, que es donde el historial y el snapshot lo buscan"
    # La cadena de revisiones es el orden: un delta se aplica sobre la revisión
    # de la que parte y sólo se revierte el último aplicado. Revertir la sección
    # antes que su conversión, por ejemplo, borraría las menciones que la
    # conversión actualizó y dejaría sus registros sin procedencia. La revisión
    # no basta para saber cuál es el último: una conversión revertida y la que
    # la sustituye recorren las mismas revisiones. Lo dice el historial.
    actual = (json.loads(MANIFEST.read_text(encoding="utf-8")).get("dataset_revision")
              if MANIFEST.exists() else None)
    pila = aplicados()
    if reverse and HISTORIAL.exists() and (not pila or pila[-1] != path.name):
        return (f"{path.name} no es el último delta aplicado"
                + (f": antes hay que revertir {pila[-1]}" if pila else ": no hay ninguno aplicado"))
    if not reverse and path.name in pila:
        return f"{path.name} ya está aplicado"
    if reverse:
        # Revertir escribe los `before` del fichero: tienen que ser los del
        # delta que se aplicó, no los de una versión editada después.
        registrada = next((h.get("sha256") for h in reversed(read_jsonl(HISTORIAL))
                           if h.get("delta") == path.name and h.get("accion") == "aplicar"), None)
        if HISTORIAL.exists() and not registrada:
            return (f"el historial no guarda la huella de {path.name} cuando se aplicó: "
                    "no se puede comprobar que sea el mismo contenido")
        if registrada and registrada != huella(path):
            return f"{path.name} cambió desde que se aplicó ({registrada}); no se revierte otro contenido"
        # Un delta generado detrás de este y sin aplicar parte de la revisión que
        # este deja: revertirlo lo dejaría colgando de una que ya no existe, y lo
        # que se generase después se encadenaría detrás de él.
        ultima = {h.get("delta"): h.get("accion") for h in read_jsonl(HISTORIAL)}
        detras = []
        for otro in sorted(DELTAS.glob("*.json")):
            if otro.name == path.name or otro.name in pila or ultima.get(otro.name) == "revertir":
                continue
            try:
                parte = json.loads(otro.read_text(encoding="utf-8")).get("dataset_revision_before")
            except (OSError, json.JSONDecodeError, AttributeError):
                continue
            if numero(parte) >= numero(origen):
                detras.append(otro.name)
        if detras:
            return (f"{', '.join(detras)} va detrás de {path.name} y está sin aplicar: antes hay que "
                    "aplicarlo y revertirlo, o retirarlo de knowledge/deltas/ si no se va a aplicar")
    if actual is not None and actual != origen:
        if reverse:
            return (f"el dataset está en {actual}, no en {origen}: antes hay que revertir "
                    f"{pila[-1] if pila else 'el delta que lo llevó ahí'}")
        return (f"el dataset está en {actual} y este delta parte de {origen}: "
                "hay que aplicar los deltas en el orden de la cadena")
    return None


def cmd(path: Path, reverse: bool, dry: bool, full: bool = False) -> int:
    delta = json.loads(path.read_text(encoding="utf-8"))
    ops = delta.get("operations", [])
    verbo = "REVERTIR" if reverse else "APLICAR"
    print(f"{verbo} {path.name} · {len(ops)} operaciones")
    # La revisión se recorre al revés cuando se revierte: decir siempre
    # `before -> after` haría creer que revertir avanza el dataset.
    origen, destino = delta["dataset_revision_before"], delta["dataset_revision_after"]
    if reverse:
        origen, destino = destino, origen
    print(f"  revisión {origen} -> {destino}")

    # Antes del ensayo en seco: es el paso previo documentado, y tiene que
    # negarse igual que la orden de verdad.
    problema = fuera_de_orden(path, origen, reverse)
    if problema:
        print(f"ERROR {problema}")
        return 1

    if dry:
        for linea in resumen(ops):
            print(linea)
        secuencia = list(reversed(ops)) if reverse else ops
        print("")
        for op in secuencia[: len(secuencia) if full else TOPE_LISTADO]:
            print(f"    {op['operation']:28} {op['record_id']:18} {op['file']}")
        if not full and len(secuencia) > TOPE_LISTADO:
            print(f"    … y {len(secuencia) - TOPE_LISTADO} operaciones más "
                  f"(--full para verlas todas)")
        print("\n(en seco: no se ha escrito nada)")
        return 0

    try:
        diario = apply_ops(ops, reverse)
    except ValueError as exc:
        print(f"ERROR {exc}")
        return 1

    for linea in diario[: len(diario) if full else TOPE_LISTADO]:
        print(f"    {linea}")
    if not full and len(diario) > TOPE_LISTADO:
        print(f"    … y {len(diario) - TOPE_LISTADO} más (--full para verlas todas)")
    bump_revision(delta, reverse)
    registrar(path.name, "revertir" if reverse else "aplicar",
              delta["dataset_revision_before"] if reverse else delta["dataset_revision_after"],
              huella(path))
    print(f"\n{len(diario)} operaciones {'revertidas' if reverse else 'aplicadas'}")
    return 0


def aplicados() -> list[str]:
    """Los deltas aplicados y sin revertir, en el orden en que se aplicaron."""
    pila: list[str] = []
    for h in read_jsonl(HISTORIAL):
        if h.get("accion") == "aplicar":
            pila.append(h.get("delta"))
        elif h.get("accion") == "revertir" and h.get("delta") in pila:
            del pila[len(pila) - 1 - pila[::-1].index(h["delta"])]
    return pila


def registrar(nombre: str, accion: str, revision: str, sha256: str | None = None) -> None:
    HISTORIAL.parent.mkdir(parents=True, exist_ok=True)
    entrada = {"delta": nombre, "accion": accion, "revision": revision,
               "fecha": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    # El contenido exacto que se aplicó: revertir otro sería escribir `before`
    # que nadie aplicó.
    if sha256:
        entrada["sha256"] = sha256
    with HISTORIAL.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entrada, ensure_ascii=False) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="Aplica o revierte un delta (§16.4)")
    ap.add_argument("delta", help="ruta al delta, o su nombre dentro de knowledge/deltas/")
    ap.add_argument("--revert", action="store_true", help="revertir en vez de aplicar")
    ap.add_argument("--dry-run", action="store_true", help="mostrar sin escribir")
    ap.add_argument("--full", action="store_true",
                    help="listar todas las operaciones, sin el corte de 40")
    args = ap.parse_args()

    path = Path(args.delta)
    if not path.exists():
        path = DELTAS / args.delta
    if not path.exists():
        print(f"ERROR no existe el delta: {args.delta}")
        return 1
    return cmd(path, args.revert, args.dry_run, args.full)


if __name__ == "__main__":
    sys.exit(main())
