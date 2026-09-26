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


def apply_ops(ops: list[dict], reverse: bool = False, escribir: bool = True) -> list[str]:
    """Aplica (o revierte) las operaciones. Devuelve el diario de lo hecho.

    Con `escribir=False` sólo comprueba que se pueden aplicar: el ensayo en
    seco se niega en los mismos casos que la orden de verdad.
    """
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

        # El registro tiene que estar como el delta espera: al aplicar, como su
        # `before`; al revertir, como su `after`. Si otro cambio lo tocó entre
        # medias, escribir encima lo borraría sin que nadie lo decidiera. Nada
        # se escribe hasta el final, así que negarse aquí no deja nada a medias.
        esperado = op["after"] if reverse else op["before"]
        actual = recs[idx] if idx is not None else None
        # El contenido tiene que ser el del registro que nombra la operación: un
        # alta con otro `id` quedaría en el fichero con ese otro, y revertirla
        # buscaría `record_id` sin encontrarlo.
        ajenos = [lado for lado in ("before", "after")
                  if op.get(lado) is not None and (op[lado] or {}).get("id") != rid]
        if ajenos:
            raise ValueError(f"{tipo}: {rid} en {fichero}: el `id` de {' y '.join(ajenos)} no es {rid}")
        # Un alta parte de que el registro no exista: con un `before` igual a
        # uno que ya está, la comparación pasaría y el identificador se duplicaría.
        if modo == "add" and not reverse and (idx is not None or op["before"] is not None):
            raise ValueError(f"{tipo}: {rid} ya está en {fichero}, o el delta no parte de su "
                             "ausencia (`before` no es null); un alta no duplica un identificador")
        if modo == "update" and idx is None:
            raise ValueError(f"{tipo}: {rid} no está en {fichero}; no hay registro que actualizar")
        if actual != esperado:
            raise ValueError(f"{tipo}: {rid} en {fichero} no está como "
                             f"{'lo dejó este delta' if reverse else 'lo espera este delta'}; "
                             "otro cambio lo tocó entre medias")
        if modo == "add":
            if not reverse:
                recs.append(op["after"])
                diario.append(f"+ {tipo} {rid}")
            else:
                recs.pop(idx)
                diario.append(f"- {tipo} {rid} retirado")
        else:  # update
            recs[idx] = op["before"] if reverse else op["after"]
            diario.append(f"{'<' if reverse else '>'} {tipo} {rid}")

    if escribir:
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
    m = re.fullmatch(r"REV-(\d{6})", revision or "") if isinstance(revision, str) else None
    return int(m.group(1)) if m else -1


def fuera_de_orden(path: Path, delta: dict, reverse: bool) -> str | None:
    """Por qué este delta no se puede aplicar o revertir ahora, o None."""
    antes, despues = delta.get("dataset_revision_before"), delta.get("dataset_revision_after")
    # Un delta avanza la revisión en uno: ni la repite, ni retrocede, ni salta.
    # Un salto quedaría grabado en el manifiesto y todo lo posterior partiría de él.
    if numero(antes) < 0 or numero(despues) < 0 or numero(despues) != numero(antes) + 1:
        return (f"{path.name} va de {antes} a {despues}: un delta avanza la revisión "
                "exactamente en uno (REV-NNNNNN → la siguiente)")
    origen = despues if reverse else antes
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
    # Sin manifiesto no hay revisión que comprobar ni que avanzar: aplicar o
    # revertir dejaría el libro mayor sin revisión autorizada.
    if not MANIFEST.exists():
        return f"falta el manifiesto ({MANIFEST}): sin él no hay revisión con la que encadenar"
    actual = json.loads(MANIFEST.read_text(encoding="utf-8")).get("dataset_revision")
    if not actual:
        return f"el manifiesto ({MANIFEST}) no declara `dataset_revision`"
    pila = aplicados()
    # Lo que se aplicó con este nombre. Sin historial no hay prueba de nada:
    # ni de que se aplicara ni de con qué contenido.
    previas = [h for h in read_jsonl(HISTORIAL) if h.get("delta") == path.name and h.get("accion") == "aplicar"]
    if reverse and (not pila or pila[-1] != path.name):
        return (f"{path.name} no es el último delta aplicado"
                + (f": antes hay que revertir {pila[-1]}" if pila else ": el historial no registra ninguno aplicado"))
    if not reverse and path.name in pila:
        return f"{path.name} ya está aplicado"
    # Encima de la revisión de partida tiene que estar, en el historial, el
    # delta que llevó el dataset hasta ella; si no, la pila no se podría
    # deshacer ni reconstruir. Sólo REV-000000 no tiene predecesor.
    if not reverse and numero(origen) > 0:
        llego = next((h.get("revision") for h in reversed(read_jsonl(HISTORIAL))
                      if pila and h.get("delta") == pila[-1] and h.get("accion") == "aplicar"), None)
        if llego != origen:
            return (f"el historial no registra qué delta llevó el dataset a {origen}"
                    + (f" (el último aplicado, {pila[-1]}, dejó {llego})" if pila else "")
                    + ": no se aplica encima de una revisión sin constancia")
        # Y los aplicados tienen que seguir siendo lo que se aplicó: si uno
        # cambió, los registros no salieron de lo que dice y la pila no se
        # reconstruiría desde sus deltas. El mismo criterio que el snapshot.
        for anterior in pila:
            primera = next((h.get("sha256") for h in read_jsonl(HISTORIAL)
                            if h.get("delta") == anterior and h.get("accion") == "aplicar"), None)
            ruta = DELTAS / anterior
            if not primera or not ruta.exists() or huella(ruta) != primera:
                return (f"{anterior}, ya aplicado, no es el que se aplicó"
                        + (f" ({primera})" if primera else " (el historial no guarda su huella)")
                        + ": no se apila otro delta encima")
    # El contenido tiene que ser el que se aplicó la primera vez: revertir
    # escribe sus `before`, y un revertido que vuelve a aplicarse editado
    # borraría la constancia de lo que se aplicó. Otro contenido, otro nombre.
    if previas:
        registrada = previas[0].get("sha256")
        if not registrada:
            return (f"el historial no guarda la huella de {path.name} cuando se aplicó: "
                    "no se puede comprobar que sea el mismo contenido")
        if registrada != huella(path):
            if reverse:
                return f"{path.name} cambió desde que se aplicó ({registrada}); no se revierte otro contenido"
            return (f"{path.name} se aplicó antes con otro contenido ({registrada}); "
                    "un delta distinto tiene que llevar otro nombre")
    if reverse:
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
    if actual != origen:
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
    problema = fuera_de_orden(path, delta, reverse)
    if problema:
        print(f"ERROR {problema}")
        return 1

    if dry:
        try:
            apply_ops(ops, reverse, escribir=False)
        except ValueError as exc:
            print(f"ERROR {exc}")
            return 1
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
