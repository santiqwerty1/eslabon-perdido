#!/usr/bin/env python3
"""Correcciones editoriales del libro mayor sobre la congelación activa (DEC-062).

Una conversión da de alta lo que dicen las filas de una sección; una absorción
lleva el libro mayor de una versión del corpus a otra. Ninguna de las dos
corrige lo que la conversión dejó sin declarar cuando el corpus no ha cambiado:
un clado compuesto sin sus miembros, una hipótesis que no dice qué afirmaciones
del tronco contradice. Eso es una corrección editorial, y sigue el mismo
patrón: un fichero revisable en `knowledge/corpus/editorials/`, que este script
convierte en un delta `ED-<nombre>` que aplica `delta.py`.

**Registros nuevos** (`records`). Cada uno dice de qué sección y de qué filas
sale (`section`, `rows`) y por qué (`reason`). De ahí se deducen, como en una
conversión, su procedencia (pasajes de sus filas, fuentes de su columna Fuente,
origen `editorial`) y sus ejes (los de la primera fila). Una corrección
editorial no da de alta fuentes: si una fila cita una que no existe, eso es
trabajo de una conversión o de una absorción.

**Parches** (`patches`). De registro a `{reason, set, add}`: `set` sustituye
campos, `add` añade a una lista sin repetir. Pueden citar registros nuevos por
su `@clave`. No tocan lo que se deduce (identificador, procedencia, ejes,
enlaces de vuelta, estado).

Los enlaces de vuelta se rehacen en los dos extremos: la afirmación nueva queda
en el `claim_ids` de su sujeto y su objeto, y una evidencia parcheada para
apoyar una afirmación queda en su `evidence_ids`. Antes de escribir se validan
el esquema de lo que cambia y el estado entero tal como quedaría: el delta no
puede añadir errores.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "scripts" / "validate"))

import absorber  # noqa: E402
import convertir  # noqa: E402
import corredor  # noqa: E402
import ingest as base  # noqa: E402

EDITORIALES = base.CORPUS / "editorials"
NOMBRE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
CAMPOS_REGISTRO = {"key", "file", "section", "rows", "reason", "record"}
CAMPOS_PARCHE = {"reason", "set", "add"}
# Lo que un parche no toca: se deduce o tiene su propia operación de §16.4.
INTOCABLES = set(convertir.DERIVADOS) | {"evidence_ids", "counterevidence_ids", "result_ids",
                                         "temporal_expression_ids", "epistemic_dimensions"}


def leer_filas(s: dict) -> dict[str, dict]:
    """Las filas del registro de la sección, tal como se ingirió (su copia)."""
    # La copia vive en knowledge/corpus/sections/ con el nombre que dice el delta
    # (el de una absorción lleva el commit de la versión absorbida).
    ruta = base.SECTIONS / Path(s["files"]["registry"]["copy"]).name
    with ruta.open(encoding="utf-8", newline="") as fh:
        return {f["#"].strip(): f for f in csv.DictReader(fh) if (f.get("#") or "").strip()}


def construir(ruta_spec: Path) -> dict:
    if ruta_spec.resolve().parent != EDITORIALES.resolve() or ruta_spec.suffix != ".json" \
            or not NOMBRE.match(ruta_spec.stem):
        raise SystemExit(f"ERROR el fichero editorial tiene que estar en {corredor._rel(EDITORIALES)}/ y "
                         "llamarse <nombre>.json (minúsculas, cifras y guiones): el snapshot lo registra ahí")
    datos = ruta_spec.read_bytes()
    spec = json.loads(datos)
    nombre = f"ED-{ruta_spec.stem}.json"
    if (base.DELTAS / nombre).exists():
        raise SystemExit(f"ERROR ya existe knowledge/deltas/{nombre}; un fichero editorial da un solo delta")

    manifiesto = json.loads(base.MANIFEST.read_text(encoding="utf-8")) if base.MANIFEST.exists() else {}
    rev_antes, rev_despues, pendientes = base.revision_siguiente(manifiesto)
    if pendientes:
        raise SystemExit(f"ERROR hay deltas sin aplicar ({', '.join(pendientes)}): una corrección editorial "
                         "parte del libro mayor tal como está")
    secciones = corredor.correspondencia()
    sin_convertir = sorted(s["section_id"] for s in secciones.values() if not s["conversion"])
    if sin_convertir:
        raise SystemExit(f"ERROR secciones ingeridas sin convertir ({', '.join(sin_convertir)}): primero se "
                         "convierten")
    por_sec_id = {s["section_id"]: s for s in secciones.values()}

    errores: list[str] = []
    for campo in ("decision", "reason"):
        if not (spec.get(campo) or "").strip():
            errores.append(f"falta `{campo}`: una corrección editorial dice cuál es y por qué")
    registros_spec = spec.get("records") or []
    parches_spec = spec.get("patches") or {}
    if not registros_spec and not parches_spec:
        errores.append("no hay `records` ni `patches`: el delta no haría nada")

    proy = convertir.proyeccion()
    filas_de: dict[str, dict[str, dict]] = {}
    claves: dict[str, dict] = {}
    for r in registros_spec:
        k = r.get("key", "?")
        ajenos = sorted(set(r) - CAMPOS_REGISTRO)
        if ajenos:
            errores.append(f"{k}: campos que un registro editorial no lleva: {', '.join(ajenos)}")
        if not convertir.CLAVE.match(k) or convertir.FUENTE.match(k):
            errores.append(f"clave inválida: {k}")
        if k in claves:
            errores.append(f"clave definida dos veces: {k}")
        claves[k] = r
        fichero = r.get("file")
        if fichero not in convertir.PREFIJO or fichero == "sources.jsonl":
            errores.append(f"{k}: fichero {fichero} fuera de lo que da de alta una corrección editorial")
            continue
        fijados = sorted(set(r.get("record") or {}) & {*convertir.DERIVADOS,
                                                         *convertir.DERIVADOS_POR_FICHERO.get(fichero, ())})
        if fijados:
            errores.append(f"{k}: fija {', '.join(fijados)}, que se deduce de sus filas y sus enlaces")
        if not (r.get("reason") or "").strip():
            errores.append(f"{k}: sin `reason`")
        sec = r.get("section")
        if sec not in por_sec_id:
            errores.append(f"{k}: la sección {sec} no está ingerida")
            continue
        if sec not in filas_de:
            filas_de[sec] = leer_filas(por_sec_id[sec])
        if not r.get("rows"):
            errores.append(f"{k}: sin filas (`rows`); la procedencia y los ejes salen de ahí")
        for fila in r.get("rows") or []:
            if fila not in filas_de[sec]:
                errores.append(f"{k}: la fila {fila} no es de {sec}")
    for rid, p in sorted(parches_spec.items()):
        if rid not in proy:
            errores.append(f"parche de {rid}: el registro no existe")
            continue
        fichero = proy[rid][0]
        ajenos = sorted(set(p) - CAMPOS_PARCHE)
        if ajenos:
            errores.append(f"parche de {rid}: campos que un parche no lleva: {', '.join(ajenos)}")
        if not (p.get("reason") or "").strip():
            errores.append(f"parche de {rid}: sin `reason`")
        if not p.get("set") and not p.get("add"):
            errores.append(f"parche de {rid}: sin `set` ni `add`")
        tocados = set(p.get("set") or {}) | set(p.get("add") or {})
        prohibidos = sorted(tocados & INTOCABLES)
        if prohibidos:
            errores.append(f"parche de {rid}: toca {', '.join(prohibidos)}, que se deduce o tiene su propia "
                           "operación")
        fuera_de_esquema = sorted(tocados - convertir.propiedades(fichero)) if fichero in convertir.ESQUEMA else []
        if fuera_de_esquema:
            errores.append(f"parche de {rid}: {', '.join(fuera_de_esquema)} no es un campo de {fichero}")
        for campo, valor in (p.get("add") or {}).items():
            if not isinstance(valor, list):
                errores.append(f"parche de {rid}: `add.{campo}` añade una lista")
    if errores:
        raise SystemExit("ERROR el fichero editorial no se puede aplicar:\n  " + "\n  ".join(errores))

    # --- identificadores y registros nuevos ----------------------------------------------
    nuevo = convertir.asignador()
    ids = {r["key"]: nuevo(convertir.PREFIJO[r["file"]]) for r in registros_spec}
    fuentes = {r.get("citation_key"): rid for rid, (f, r) in proy.items()
               if f == "sources.jsonl" and r.get("citation_key")}
    faltan: set[str] = set()
    altas: list[tuple[str, dict]] = []
    filas_por_sec: dict[str, dict[str, list[str]]] = {}
    for r in registros_spec:
        fichero, sec, filas = r["file"], r["section"], r["rows"]
        props = convertir.propiedades(fichero)
        rec = {"id": ids[r["key"]], **convertir.sustituir(json.loads(json.dumps(r["record"])), ids, faltan)}
        if fichero in convertir.TIPO_ENTIDAD:
            rec["entity_type"] = convertir.TIPO_ENTIDAD[fichero]
        for campo in ("first_introduced_in", "introduced_in", "raised_in"):
            if campo in props:
                rec[campo] = sec
        s = por_sec_id[sec]
        claves_fuente = sorted({x for f in filas for x in convertir.CITA.findall(filas_de[sec][f].get("Fuente", ""))},
                               key=lambda x: int(x[1:]))
        sin_ficha = [x for x in claves_fuente if x not in fuentes]
        if sin_ficha:
            raise SystemExit(f"ERROR {r['key']}: sus filas citan {', '.join(sin_ficha)}, que no tiene ficha; una "
                             "corrección editorial no da de alta fuentes")
        fuentes_r = [fuentes[x] for x in claves_fuente]
        if "provenance" in props:
            pasajes = []
            for f in filas:
                for pid in s["rows"].get(f, {}).get("passage_ids", []):
                    if pid not in pasajes:
                        pasajes.append(pid)
            rec["provenance"] = {"section_ids": [sec], "passage_ids": pasajes, "source_ids": fuentes_r,
                                 "operation_id": None, "dataset_revision": rev_despues, "origin": "editorial"}
        if "source_ids" in props:
            rec["source_ids"] = fuentes_r
        if "epistemic_dimensions" in props and fichero in ("claims.jsonl", "hypotheses.jsonl"):
            rec["epistemic_dimensions"] = convertir.ejes(filas_de[sec][filas[0]])
        if fichero == "claims.jsonl":
            rec.setdefault("scope", {})
            for k in ("hypothesis_ids", "classification_view_ids", "temporal_expression_ids", "region_ids"):
                rec["scope"].setdefault(k, [])
            rec.setdefault("quantitative_support", [])
            rec["evidence_ids"] = []
            rec["counterevidence_ids"] = []
            rec.setdefault("derivation", None)
        if "claim_ids" in props and fichero != "claims.jsonl":
            rec["claim_ids"] = []
        if "notes" in props:
            rec["notes"] = [*(rec.get("notes") or []),
                            f"Corrección editorial ({spec['decision']}, {ruta_spec.stem}): {r['reason']}"]
        rec["record_status"] = "active"
        altas.append((fichero, rec))
        for f in filas:
            filas_por_sec.setdefault(sec, {}).setdefault(f, []).append(rec["id"])

    # --- parches ------------------------------------------------------------------------
    estado: dict[str, tuple[str, dict]] = {rid: (f, json.loads(json.dumps(r))) for rid, (f, r) in proy.items()}
    for fichero, rec in altas:
        estado[rec["id"]] = (fichero, rec)
    cambios: dict[str, tuple[str, dict, dict]] = {}

    def tocar(rid: str) -> dict:
        fichero, actual = estado[rid]
        if rid not in cambios and rid in proy:
            cambios[rid] = (fichero, proy[rid][1], actual)
        return actual

    for rid, p in sorted(parches_spec.items()):
        rec = tocar(rid)
        for campo, valor in (p.get("set") or {}).items():
            rec[campo] = convertir.sustituir(json.loads(json.dumps(valor)), ids, faltan)
        for campo, valor in (p.get("add") or {}).items():
            lista = rec.setdefault(campo, [])
            if not isinstance(lista, list):
                raise SystemExit(f"ERROR parche de {rid}: `{campo}` no es una lista y `add` sólo añade a listas")
            for v in convertir.sustituir(json.loads(json.dumps(valor)), ids, faltan):
                if v not in lista:
                    lista.append(v)
        if "notes" in convertir.propiedades(estado[rid][0]):
            rec["notes"] = [*(rec.get("notes") or []),
                            f"Corrección editorial ({spec['decision']}, {ruta_spec.stem}): {p['reason']}"]
    if faltan:
        raise SystemExit(f"ERROR claves usadas sin definir: {', '.join(sorted(faltan))}")

    # --- enlaces de vuelta, en los dos extremos ------------------------------------------------
    # De lo nuevo y de lo parcheado: adónde apuntaba antes y adónde apunta ahora.
    origenes = [rec["id"] for _, rec in altas] + sorted(parches_spec)
    destinos: dict[tuple[str, str], None] = {}
    for rid in origenes:
        fichero, rec = estado[rid]
        antes = absorber.punteros(proy[rid][1], fichero) if rid in proy else {}
        for campo in set(absorber.punteros(rec, fichero)) | set(antes):
            for d in absorber.punteros(rec, fichero).get(campo, set()) | antes.get(campo, set()):
                destinos[(campo, d)] = None
    colgando = []
    for campo, d in sorted(destinos):
        if d not in estado:
            colgando.append(d)
            continue
        fichero, rec = estado[d]
        if campo not in convertir.propiedades(fichero):
            continue
        debe = absorber.valor_de_vuelta(campo, d, estado)
        actual = list(rec.get(campo) or [])
        nuevo_valor = [x for x in actual if x in debe] + [x for x in debe if x not in actual]
        if nuevo_valor != actual:
            tocar(d)[campo] = nuevo_valor
    conocidos = set(estado) | base.ids_de_pasajes() | base.ids_de_secciones() | convertir.ids_de_vistas()
    for _, rec in altas:
        colgando += [x for x in sorted(convertir.literales(rec) - conocidos)]
    for rid in parches_spec:
        colgando += [x for x in sorted(convertir.literales(estado[rid][1]) - conocidos)]
    if colgando:
        raise SystemExit(f"ERROR identificadores que no existen: {', '.join(sorted(set(colgando)))}")

    # --- validación ---------------------------------------------------------------------------
    try:
        import jsonschema  # noqa: F401
    except ImportError:
        raise SystemExit("ERROR jsonschema no está instalado: editorial.py no escribe un delta sin validarlo "
                         "contra los esquemas (make setup)")
    escritos, _ = convertir.fallos_de_esquema([*altas, *((f, d) for f, _, d in cambios.values())])
    previos, _ = convertir.fallos_de_esquema([(f, a) for f, a, _ in cambios.values()])
    invalidos = [f"{donde}: {fallo}" for donde, fallos in sorted(escritos.items())
                 for fallo in sorted(fallos - previos.get(donde, set()))]
    if invalidos:
        raise SystemExit("ERROR registros que no validan contra su esquema:\n  " + "\n  ".join(invalidos))
    nuevos_errores = absorber.validar_estado(cambios, altas)
    if nuevos_errores:
        raise SystemExit("ERROR el delta dejaría errores de validación nuevos:\n  " + "\n  ".join(nuevos_errores))

    # --- delta --------------------------------------------------------------------------------
    operaciones = [{"operation": "ADD_RECORD", "file": f, "record_id": rec["id"], "before": None, "after": rec}
                   for f, rec in altas]
    operaciones += [{"operation": "UPDATE_RECORD", "file": f, "record_id": rid, "before": antes, "after": despues}
                    for rid, (f, antes, despues) in sorted(cambios.items())]
    de = lambda fichero: [rec["id"] for f, rec in altas if f == fichero]
    delta = {
        "section_id": None,
        "schema_version": base.SCHEMA_VERSION,
        "dataset_revision_before": rev_antes,
        "dataset_revision_after": rev_despues,
        "operations": operaciones,
        "records_added": [rec["id"] for _, rec in altas],
        "records_updated": sorted(cambios),
        "claims_added": de("claims.jsonl"),
        "events_added": de("events.jsonl"),
        "hypotheses_added": de("hypotheses.jsonl"),
        "issues_added": de("issues.jsonl"),
        "issues_resolved": [], "records_deprecated": [], "views_invalidated": [], "views_built": [],
        "validation_results": {},
        "editorial": {
            "spec": {"path": corredor._rel(ruta_spec), "sha256": convertir.sha256(datos)},
            "decision": spec["decision"],
            "reason": spec["reason"],
            "keys": {k: ids[k] for k in sorted(ids)},
            "rows": filas_por_sec,
        },
    }
    return {"nombre": nombre, "delta": delta, "altas": altas, "cambios": cambios, "ids": ids,
            "parches": sorted(parches_spec)}


def informe(c: dict) -> list[str]:
    d = c["delta"]
    lineas = [f"# {c['nombre']} · {d['editorial']['decision']}", "",
              d["editorial"]["reason"], "",
              f"{d['dataset_revision_before']} → {d['dataset_revision_after']} · "
              f"{len(c['altas'])} altas · {len(c['cambios'])} registros actualizados", ""]
    for clave, rid in sorted(c["ids"].items(), key=lambda kv: kv[1]):
        lineas.append(f"- + {rid} ({clave})")
    for rid in sorted(c["cambios"]):
        motivo = "parche" if rid in c["parches"] else "enlace de vuelta"
        lineas.append(f"- > {rid} ({motivo})")
    return lineas


def main() -> int:
    ap = argparse.ArgumentParser(description="Construye el delta de una corrección editorial (DEC-062)")
    sub = ap.add_subparsers(dest="orden", required=True)
    c = sub.add_parser("construir", help="fichero editorial → knowledge/deltas/ED-<nombre>.json")
    c.add_argument("fichero")
    c.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    r = construir(Path(a.fichero).resolve())
    lineas = informe(r)
    print("\n".join(lineas))
    if a.dry_run:
        print("\n(en seco: no se ha escrito nada)")
        return 0
    base.DELTAS.mkdir(parents=True, exist_ok=True)
    (base.DELTAS / r["nombre"]).write_text(json.dumps(r["delta"], indent=2, ensure_ascii=False) + "\n",
                                           encoding="utf-8")
    print(f"\n  delta     knowledge/deltas/{r['nombre']}")
    print(f"  el delta NO se ha aplicado:  python scripts/ingest/delta.py {r['nombre']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
