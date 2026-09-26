#!/usr/bin/env python3
"""Paso 6 de §17 para el corredor: convierte las filas de una sección en registros.

La correspondencia es por fila, no por predicado (DEC-057). El corredor usa el
mismo predicado para cosas distintas —`pierde_rasgo` sirve para un orgánulo que
se pierde y para la señal temporal de unas secuencias—, así que traducir
predicados produciría afirmaciones falsas. Un fichero de conversión por sección,
`knowledge/corpus/conversions/<corpus>-<sección>.json`, fija qué registros salen
de cada fila y qué destino tiene cada mención, con claves locales («@LECA») en
vez de identificadores. Es juicio y se revisa como tal
(`docs/campaigns/C01-PREDICADOS.md`).

Este script hace lo mecánico, y se niega antes de escribir nada si:

- la copia del corpus no es la versión congelada que declara el fichero;
- la sección no se ha ingerido, o ya se convirtió;
- alguna fila de la sección o alguna de sus menciones queda sin destino, o el
  fichero nombra filas o menciones que la sección no tiene;
- alguna clave se usa sin definir o se define dos veces.

Después asigna identificadores opacos sin reutilizar ninguno ya emitido, crea
las fuentes del apéndice A que se citan y no existen, y rellena lo que se deduce
de la fila: procedencia (sección, pasajes, fuentes y revisión), ejes
epistemológicos desde sus columnas, `claim_ids` de entidades y eventos y
`evidence_ids` de las afirmaciones. Escribe un delta que añade los registros y
da destino a las menciones, y un informe. **No aplica nada**: el delta va detrás
del de la sección y se aplica con delta.py.

Formato del fichero de conversión:

    {
      "freeze": {"version": "...", "fingerprint": "sha256:..."},
      "section": "06",
      "decision": "DEC-057",
      "records": [
        {"key": "@LECA", "file": "populations.jsonl", "rows": ["C-760"],
         "sources": ["S139"], "record": {...}}
      ],
      "rows": {"C-757": {"destination": "A", "keys": ["@..."], "note": "..."}},
      "mentions": {"LECA": {"mention_type": "...", "disposition": "...",
                            "targets": ["@LECA"], "reason": "..."}}
    }

Las fuentes se nombran por su clave del apéndice A con arroba («@S139») y no se
declaran en `records`: se crean al citarlas o se reutilizan si ya existen. Los
ejes epistemológicos de afirmaciones e hipótesis salen siempre de su primera fila.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

sys.path.insert(0, str(HERE.parent / "validate"))

import corredor  # noqa: E402
import freeze  # noqa: E402
import ingest as base  # noqa: E402
import validate  # noqa: E402
from parse_research import ACEPTACION, FUERZA, RESOLUCION, TIPO_FUENTE, VIGENCIA  # noqa: E402

SCHEMAS = base.ROOT / "schemas" / "json-schema"
VIEWS = base.ROOT / "knowledge" / "views"
CONVERSIONS = base.CORPUS / "conversions"

# Fichero -> prefijo de §16.3. Sólo los ficheros que una conversión puede escribir.
PREFIJO = {
    "sources.jsonl": "SRC",
    "taxonomic-names.jsonl": "NAME",
    "taxon-concepts.jsonl": "TAXCONCEPT",
    "clades.jsonl": "CLADE",
    "lineages.jsonl": "LINEAGE",
    "populations.jsonl": "POP",
    "specimens.jsonl": "SPECIMEN",
    "sites.jsonl": "SITE",
    "regions.jsonl": "REGION",
    "occurrences.jsonl": "OCC",
    "traits.jsonl": "TRAIT",
    "trait-observations.jsonl": "TRAITOBS",
    "methods.jsonl": "METHOD",
    "claims.jsonl": "CLAIM",
    "evidence.jsonl": "EVID",
    "datasets.jsonl": "DATASET",
    "analyses.jsonl": "ANALYSIS",
    "results.jsonl": "RESULT",
    "events.jsonl": "EVENT",
    "hypotheses.jsonl": "HYP",
    "temporal-expressions.jsonl": "TIME",
    "conflict-groups.jsonl": "CONFLICT",
    "issues.jsonl": "ISSUE",
}
# Fichero -> esquema (el mismo reparto que scripts/validate/validate.py).
ESQUEMA = {
    "sources.jsonl": "source.json", "taxonomic-names.jsonl": "taxonomic-name.json",
    "taxon-concepts.jsonl": "taxon-concept.json", "occurrences.jsonl": "occurrence.json",
    "trait-observations.jsonl": "trait-observation.json", "claims.jsonl": "claim.json",
    "evidence.jsonl": "evidence.json", "datasets.jsonl": "dataset.json",
    "analyses.jsonl": "analysis.json", "results.jsonl": "result.json",
    "events.jsonl": "event.json", "hypotheses.jsonl": "hypothesis.json",
    "temporal-expressions.jsonl": "temporal-expression.json",
    "conflict-groups.jsonl": "conflict-group.json", "issues.jsonl": "issue.json",
}
TIPO_ENTIDAD = {
    "clades.jsonl": "clade", "lineages.jsonl": "biological_lineage",
    "populations.jsonl": "population", "specimens.jsonl": "specimen",
    "sites.jsonl": "site", "regions.jsonl": "region", "traits.jsonl": "trait",
    "methods.jsonl": "method",
}
for _f in TIPO_ENTIDAD:
    ESQUEMA[_f] = "entity.json"

CLAVE = re.compile(r"^@[A-Za-z0-9_.\-]+$")
# Un identificador opaco escrito tal cual, con los prefijos de §16.3.
LITERAL = re.compile(json.loads((base.ROOT / "schemas" / "json-schema" / "common.json")
                                .read_text(encoding="utf-8"))["$defs"]["id"]["pattern"])
FUENTE = re.compile(r"^@(S\d+)$")
CITA = re.compile(r"\bS\d+\b")
# Los destinos de fila de docs/campaigns/C01-PREDICADOS.md, A–I. Sólo la
# glosa (H) puede no producir registros: las demás filas son contenido.
DESTINOS = set("ABCDEFGHI")
SIN_REGISTROS = {"H"}
# Sólo una mención descartada puede quedarse sin registro al que apunte.
SIN_OBJETIVO = {"discarded_with_reason"}
# Lo que convertir.py deduce y el fichero de conversión no puede fijar: escrito
# a mano podría contradecir las filas, el fichero de destino, los enlaces de
# vuelta o el ciclo de vida (un registro nuevo nace activo; deprecarlo es otra
# operación de §16.4).
DERIVADOS = ("id", "provenance", "source_ids", "first_introduced_in", "introduced_in", "raised_in",
             "entity_type", "claim_ids", "record_status")
# Y por fichero: en las afirmaciones, lo que se deduce de las evidencias que
# las citan; en afirmaciones e hipótesis, los ejes, que salen de su fila.
DERIVADOS_POR_FICHERO = {"claims.jsonl": ("evidence_ids", "counterevidence_ids", "epistemic_dimensions"),
                         "hypotheses.jsonl": ("epistemic_dimensions",)}
# Lo que identifica la obra. Si el apéndice activo lo corrigió, la fuente que ya
# existe no es la que cita el corpus congelado.
BIBLIOGRAFIA = ("authors", "year", "title", "container", "doi", "url", "source_type")


def propiedades(fichero: str) -> set[str]:
    esquema = json.loads((SCHEMAS / ESQUEMA[fichero]).read_text(encoding="utf-8"))
    return set(esquema.get("properties", {}))


def sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# Lo que ya existe
# ---------------------------------------------------------------------------

def delta_de_seccion(sec: str) -> tuple[Path, dict]:
    """El delta de ingestión de la sección, que no esté revertido."""
    revertidos = {d for d, a in base.ultima_accion().items() if a == "revertir"}
    for p in sorted(base.DELTAS.glob("*.json")):
        if p.name in revertidos:
            continue
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if (d.get("corpus_origin") or {}).get("section") == sec:
            return p, d
    raise SystemExit(f"ERROR la sección {sec} no se ha ingerido: la conversión parte de su delta "
                     "(make ingest CORPUS=… SECCION=…)")


def ya_convertida(sec_id: str) -> str | None:
    revertidos = {d for d, a in base.ultima_accion().items() if a == "revertir"}
    for p in sorted(base.DELTAS.glob("*.json")):
        if p.name in revertidos:
            continue
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if (d.get("conversion") or {}).get("of") == sec_id:
            return p.name
    return None


def registros(fichero: str) -> list[dict]:
    ruta = base.RECORDS / fichero
    if not ruta.exists():
        return []
    return [json.loads(l) for l in ruta.read_text(encoding="utf-8").splitlines() if l.strip()]


def proyeccion() -> dict[str, tuple[str, dict]]:
    """Cada registro como quedará tras aplicar los deltas pendientes, por identificador.

    Los pendientes se reproducen en el orden de la cadena, altas y
    actualizaciones: si dos conversiones sin aplicar enlazan el mismo registro,
    la segunda tiene que partir del estado que deja la primera, o al aplicarlas
    pisaría su enlace.
    """
    out: dict[str, tuple[str, dict]] = {}
    for ruta in sorted(base.RECORDS.glob("*.jsonl")):
        for r in registros(ruta.name):
            if isinstance(r.get("id"), str):
                out[r["id"]] = (ruta.name, r)
    manifiesto = json.loads(base.MANIFEST.read_text(encoding="utf-8")) if base.MANIFEST.exists() else {}
    _, _, sin_aplicar = base.revision_siguiente(manifiesto)
    for nombre in sin_aplicar:
        d = json.loads((base.DELTAS / nombre).read_text(encoding="utf-8"))
        for op in d.get("operations", []):
            if isinstance(op.get("record_id"), str) and isinstance(op.get("after"), dict):
                out[op["record_id"]] = (op.get("file"), op["after"])
    return out


def ids_de_vistas() -> set[str]:
    """Las vistas viven en knowledge/views/, no en records/, y también se citan."""
    out: set[str] = set()
    if not VIEWS.exists():
        return out
    for ruta in sorted(VIEWS.rglob("*.json*")):
        texto = ruta.read_text(encoding="utf-8")
        docs = ([json.loads(l) for l in texto.splitlines() if l.strip()] if ruta.suffix == ".jsonl"
                else [json.loads(texto)] if texto.strip() else [])
        for doc in docs:
            for r in (doc if isinstance(doc, list) else [doc]):
                if isinstance(r, dict) and isinstance(r.get("id"), str):
                    out.add(r["id"])
    return out


def literales(valor) -> set[str]:
    if isinstance(valor, str):
        return {valor} if LITERAL.match(valor) else set()
    if isinstance(valor, list):
        return set().union(*(literales(v) for v in valor)) if valor else set()
    if isinstance(valor, dict):
        return set().union(*(literales(v) for v in valor.values())) if valor else set()
    return set()


def usados(prefijo: str) -> set[str]:
    """Todo identificador con ese prefijo ya emitido: en registros, en deltas o reservado."""
    out = set(base.reservados_por_deltas(prefijo))
    for fichero, p in PREFIJO.items():
        if p == prefijo:
            out |= {r.get("id") for r in registros(fichero) if isinstance(r.get("id"), str)}
    if prefijo == "PASSAGE":
        out |= base.ids_de_pasajes()
    manifiesto = json.loads(base.MANIFEST.read_text(encoding="utf-8")) if base.MANIFEST.exists() else {}
    rango = ((manifiesto.get("id_allocation") or {}).get("reserved") or {}).get(prefijo)
    if rango:
        desde, hasta = (int(rango[k].split("-")[1]) for k in ("from", "to"))
        out |= {f"{prefijo}-{n:06d}" for n in range(desde, hasta + 1)}
    return out


# ---------------------------------------------------------------------------
# Construcción
# ---------------------------------------------------------------------------

def ejes(fila: dict) -> dict:
    def mapa(tabla: dict, columna: str) -> str:
        valor = (fila.get(columna) or "").strip().lower()
        if valor not in tabla:
            raise SystemExit(f"ERROR {fila['#']}: «{fila.get(columna)}» en la columna {columna} "
                             "no tiene equivalente en §10")
        return tabla[valor]
    motivo = (fila.get("Motivo") or "").strip()
    return {
        "acceptance": mapa(ACEPTACION, "Aceptación"),
        "evidence_strength": mapa(FUERZA, "Fuerza"),
        "evidence_strength_reason": motivo or None,
        "resolution": mapa(RESOLUCION, "Resolución"),
        "historical_status": mapa(VIGENCIA, "Vigencia"),
    }


def fuente_de_apendice(fila: dict, col_doi: str) -> dict:
    enlace = (fila.get(col_doi) or "").strip()
    doi = enlace if enlace.startswith("https://doi.org/") else None
    url = enlace if enlace.startswith("http") and not doi else None
    anio = (fila.get("año") or "").strip()
    tipo = (fila.get("tipo") or "").strip().lower()
    return {
        "citation_key": fila["clave"].strip(),
        "authors": [a.strip() for a in (fila.get("autores") or "").split(";") if a.strip()],
        "year": int(anio) if anio.isdigit() else None,
        "title": (fila.get("título") or "").strip(),
        "container": (fila.get("publicación o repositorio") or "").strip() or None,
        "doi": doi,
        "url": url,
        "source_type": TIPO_FUENTE.get(tipo, "other"),
        "quality_notes": [n] if (n := (fila.get("notas de calidad") or "").strip()) else [],
        "consulted_at": (fila.get("fecha de consulta") or "").strip() or None,
        # La consultó el corredor; eslabón no ha comprobado la referencia.
        "verification_status": "pending_verification",
        "record_status": "active",
    }


def fallos_de_esquema(registros: list[tuple[str, dict]]) -> tuple[dict[str, set[str]], list[str]]:
    """Los fallos de esquema de cada registro, por «fichero id», y los avisos."""
    por_fichero: dict[str, list[dict]] = {}
    for fichero, rec in registros:
        por_fichero.setdefault(fichero, []).append(rec)
    rep = validate.Report()
    validate.v_schema(por_fichero, rep)
    fallos: dict[str, set[str]] = {}
    for error in rep.errors:
        m = re.match(r"([^:]+):(\d+): (.*)", error, re.S)
        if m and m.group(1) in por_fichero:
            rec = por_fichero[m.group(1)][int(m.group(2)) - 1]
            fallos.setdefault(f"{m.group(1)} {rec.get('id')}", set()).add(m.group(3))
        else:
            fallos.setdefault("esquemas", set()).add(error)
    return fallos, rep.warnings


def valores_de(valor, campo: str) -> set[str]:
    """Los valores de `campo` a cualquier profundidad, fuera de la procedencia."""
    if isinstance(valor, list):
        return set().union(*(valores_de(v, campo) for v in valor)) if valor else set()
    if not isinstance(valor, dict):
        return set()
    hallados = {valor[campo]} if isinstance(valor.get(campo), str) else set()
    for k, v in valor.items():
        if k != "provenance":
            hallados |= valores_de(v, campo)
    return hallados


def sustituir(valor, ids: dict[str, str], faltan: set[str]):
    if isinstance(valor, str) and CLAVE.match(valor):
        if valor in ids:
            return ids[valor]
        faltan.add(valor)
        return valor
    if isinstance(valor, list):
        return [sustituir(v, ids, faltan) for v in valor]
    if isinstance(valor, dict):
        return {k: sustituir(v, ids, faltan) for k, v in valor.items()}
    return valor


def claves_usadas(valor) -> set[str]:
    if isinstance(valor, str):
        return {valor} if CLAVE.match(valor) else set()
    if isinstance(valor, list):
        return set().union(*(claves_usadas(v) for v in valor)) if valor else set()
    if isinstance(valor, dict):
        return set().union(*(claves_usadas(v) for v in valor.values())) if valor else set()
    return set()


def construir(spec_path: Path, corpus: str) -> dict:
    # La entrada revisada tiene que quedar donde el snapshot la registra: fuera
    # de ahí, cambiarla o perderla no lo detectaría nadie y un clon limpio no
    # podría reconstruir de dónde salieron los registros.
    if spec_path.resolve().parent != CONVERSIONS.resolve() or spec_path.suffix != ".json":
        raise SystemExit(f"ERROR el fichero de conversión tiene que estar en knowledge/corpus/conversions/ "
                         f"({spec_path})")
    spec_bytes = spec_path.read_bytes()
    spec = json.loads(spec_bytes)
    sec = spec["section"]

    # --- el corpus es el congelado ------------------------------------------
    src = freeze.abrir(corpus)
    ruta, congelada = corredor.congelacion(None)
    if spec.get("freeze", {}).get("fingerprint") != congelada["fingerprint"]:
        raise SystemExit("ERROR el fichero de conversión se escribió para otra versión del corpus "
                         f"({spec.get('freeze', {}).get('fingerprint')}); la activa es "
                         f"{congelada['fingerprint']}. Una versión nueva entra por diferencia")
    corredor.verificar(src, ruta, congelada)

    # --- la sección ya se ingirió ---------------------------------------------
    delta_path, delta_sec = delta_de_seccion(sec)
    sec_id = delta_sec["section_id"]
    huella_sec = ((delta_sec.get("corpus_origin") or {}).get("freeze") or {}).get("fingerprint")
    if huella_sec != congelada["fingerprint"]:
        # Sus pasajes y menciones son de otra versión: convertir con las filas de
        # la activa mezclaría las dos.
        raise SystemExit(f"ERROR {delta_path.name} se ingirió de otra versión del corpus ({huella_sec}); "
                         f"la activa es {congelada['fingerprint']}. Una versión nueva entra por diferencia")
    previa = ya_convertida(sec_id)
    if previa:
        raise SystemExit(f"ERROR {sec_id} ya se convirtió ({previa})")
    origen = delta_sec["corpus_origin"]["rows"]
    menciones = {op["after"]["id"]: op["after"] for op in delta_sec["operations"]
                 if op.get("file") == "mentions.jsonl"}

    _, registro_csv = corredor.ficheros_de_seccion(src.base, sec)
    with registro_csv.open(encoding="utf-8", newline="") as fh:
        filas = {f["#"].strip(): f for f in csv.DictReader(fh) if (f.get("#") or "").strip()}

    # --- cobertura -----------------------------------------------------------
    errores: list[str] = []
    sin_destino = sorted(set(filas) - set(spec.get("rows", {})))
    if sin_destino:
        errores.append(f"filas sin destino: {', '.join(sin_destino)}")
    ajenas = sorted(set(spec.get("rows", {})) - set(filas))
    if ajenas:
        errores.append(f"filas que la sección {sec} no tiene: {', '.join(ajenas)}")
    etiquetas = {m["original_text"] for m in menciones.values()}
    sin_mencion = sorted(etiquetas - set(spec.get("mentions", {})))
    if sin_mencion:
        errores.append(f"menciones sin destino: {'; '.join(sin_mencion)}")
    sobran = sorted(set(spec.get("mentions", {})) - etiquetas)
    if sobran:
        errores.append(f"menciones que la sección no tiene: {'; '.join(sobran)}")
    for etiqueta, destino in spec.get("mentions", {}).items():
        if not destino.get("disposition"):
            # El esquema admite null para la mención sin resolver; convertir es
            # justo darle destino.
            errores.append(f"mención {etiqueta}: sin `disposition`")
        elif destino.get("disposition") not in SIN_OBJETIVO and not destino.get("targets"):
            errores.append(f"mención {etiqueta}: {destino.get('disposition')} sin `targets`; "
                           "sólo una descartada puede quedarse sin registro")
        if destino.get("disposition") in SIN_OBJETIVO and not (destino.get("reason") or "").strip():
            errores.append(f"mención {etiqueta}: descartada sin `reason`; la cobertura exige justificarla")

    definidas: dict[str, dict] = {}
    for r in spec.get("records", []):
        if r["key"] in definidas:
            errores.append(f"clave definida dos veces: {r['key']}")
        if not CLAVE.match(r["key"]) or FUENTE.match(r["key"]):
            errores.append(f"clave inválida: {r['key']} (las fuentes no se declaran: se citan)")
        for campo in DERIVADOS + DERIVADOS_POR_FICHERO.get(r["file"], ()):
            if campo in r.get("record", {}):
                errores.append(f"{r['key']}: el fichero de conversión no fija `{campo}`; "
                               "lo deduce convertir.py de la sección, las filas y los enlaces")
        if r["file"] not in PREFIJO or r["file"] == "sources.jsonl":
            errores.append(f"{r['key']}: fichero {r['file']} fuera de lo que convierte este paso")
        if not r.get("rows"):
            errores.append(f"{r['key']}: sin fila de origen (`rows`); la procedencia sale de ahí")
        if r["file"] == "issues.jsonl" and (r.get("record", {}).get("resolution") or {"status": "open"}).get(
                "status") != "open":
            errores.append(f"{r['key']}: una incidencia nueva nace abierta (`resolution`); cerrarla es "
                           "RESOLVE_ISSUE, otra operación de §16.4")
        for fila in r.get("rows", []):
            if fila not in filas:
                errores.append(f"{r['key']}: la fila {fila} no es de la sección {sec}")
        definidas[r["key"]] = r
    for fila, destino in spec.get("rows", {}).items():
        if destino.get("destination") not in DESTINOS:
            errores.append(f"{fila}: destino {destino.get('destination')!r} fuera de A–I")
        elif destino["destination"] not in SIN_REGISTROS and not destino.get("keys"):
            errores.append(f"{fila}: destino {destino['destination']} sin registros (`keys`); "
                           "sólo una glosa (H) puede no producirlos")
        for k in destino.get("keys", []):
            if k not in definidas:
                errores.append(f"{fila}: la clave {k} no está definida")
    if errores:
        raise SystemExit("ERROR el fichero de conversión no cubre la sección:\n  " + "\n  ".join(errores))

    # --- fuentes citadas ---------------------------------------------------------
    citadas = set()
    for r in spec.get("records", []):
        citadas |= {m.group(1) for k in claves_usadas(r["record"]) if (m := FUENTE.match(k))}
        citadas |= set(r.get("sources", []))
    for destino in spec.get("mentions", {}).values():
        citadas |= {m.group(1) for k in destino.get("targets", []) if (m := FUENTE.match(k))}
    # Y las de la columna Fuente de las filas de cada registro que no las declara:
    # son las que irán a su procedencia.
    for r in spec.get("records", []):
        if r.get("sources") is None:
            for fila in r.get("rows", []):
                citadas |= set(CITA.findall(filas[fila].get("Fuente", "")))

    apendice = src.base / "data" / "apendices" / "A_fuentes.csv"
    with apendice.open(encoding="utf-8", newline="") as fh:
        lector = list(csv.DictReader(fh))
    col_doi = next(c for c in lector[0] if c.strip().lower().startswith("doi"))
    por_clave = {f["clave"].strip(): f for f in lector}
    no_estan = sorted(citadas - set(por_clave), key=lambda s: int(s[1:]))
    if no_estan:
        raise SystemExit(f"ERROR fuentes citadas que el apéndice A no tiene: {', '.join(no_estan)}")

    proy = proyeccion()
    existentes = {r.get("citation_key"): rid for rid, (f, r) in proy.items()
                  if f == "sources.jsonl" and r.get("citation_key")}

    # --- identificadores -----------------------------------------------------------
    rev_antes, rev_despues, sin_aplicar = base.revision_siguiente(
        json.loads(base.MANIFEST.read_text(encoding="utf-8")) if base.MANIFEST.exists() else {})
    ids: dict[str, str] = {}
    contador: dict[str, int] = {}

    def nuevo(prefijo: str) -> str:
        if prefijo not in contador:
            contador[prefijo] = base.siguiente_libre(prefijo, usados(prefijo))
        n = contador[prefijo]
        contador[prefijo] += 1
        return f"{prefijo}-{n:06d}"

    fuentes_nuevas: list[dict] = []
    distintas = []
    for clave in sorted(citadas, key=lambda s: int(s[1:])):
        if clave in existentes:
            previa = proy[existentes[clave]][1]
            activa = fuente_de_apendice(por_clave[clave], col_doi)
            cambios = [k for k in BIBLIOGRAFIA if previa.get(k) != activa[k]]
            if cambios:
                distintas.append(f"{existentes[clave]} ({clave}): {', '.join(cambios)}")
            ids[f"@{clave}"] = existentes[clave]
        else:
            rid = nuevo("SRC")
            ids[f"@{clave}"] = rid
            fuentes_nuevas.append({"id": rid, **fuente_de_apendice(por_clave[clave], col_doi)})
    if distintas:
        raise SystemExit("ERROR fuentes que ya existen y el apéndice A activo describe de otra manera; "
                         "hay que actualizarlas antes de convertir:\n  " + "\n  ".join(distintas))
    for r in spec.get("records", []):
        ids[r["key"]] = nuevo(PREFIJO[r["file"]])

    # --- registros -----------------------------------------------------------------
    faltan: set[str] = set()
    ajenas_a_la_procedencia: list[str] = []
    salida: list[tuple[str, dict]] = [("sources.jsonl", f) for f in fuentes_nuevas]
    for r in spec.get("records", []):
        fichero = r["file"]
        props = propiedades(fichero)
        rec = {"id": ids[r["key"]], **sustituir(r["record"], ids, faltan)}
        filas_r = r.get("rows", [])
        if fichero in TIPO_ENTIDAD:
            rec["entity_type"] = TIPO_ENTIDAD[fichero]
        if "first_introduced_in" in props:
            rec["first_introduced_in"] = sec_id
        if "introduced_in" in props:
            rec["introduced_in"] = sec_id
        if "raised_in" in props:
            rec["raised_in"] = sec_id
        claves_fuente = r.get("sources")
        if claves_fuente is None:
            claves_fuente = sorted({s for f in filas_r for s in CITA.findall(filas[f].get("Fuente", ""))},
                                   key=lambda s: int(s[1:]))
        fuentes_r = [ids[f"@{s}"] for s in claves_fuente]
        if "provenance" in props:
            pasajes = []
            for f in filas_r:
                for p in origen.get(f, {}).get("passage_ids", []):
                    if p not in pasajes:
                        pasajes.append(p)
            # Una afirmación con regla de derivación no es expresa de la fuente
            # (§9.4): su origen lo dice.
            rec["provenance"] = {"section_ids": [sec_id], "passage_ids": pasajes, "source_ids": fuentes_r,
                                 "operation_id": None, "dataset_revision": rev_despues,
                                 "origin": "derived" if rec.get("derivation") else "ingestion"}
        if "source_ids" in props:
            rec["source_ids"] = fuentes_r
        # Un `source_id` dice de qué obra sale el registro (una evidencia, un
        # apoyo cuantitativo): tiene que ser una de las de su procedencia. Las
        # fuentes a favor o en contra de una hipótesis son argumentos, no origen.
        if "provenance" in rec:
            propias = valores_de(rec, "source_id") - set(fuentes_r)
            if propias:
                ajenas_a_la_procedencia.append(
                    f"{r['key']}: `source_id` {', '.join(sorted(propias))} no está entre las fuentes "
                    f"de su procedencia ({', '.join(fuentes_r) or 'ninguna'})")
        if "epistemic_dimensions" in props and fichero in ("claims.jsonl", "hypotheses.jsonl"):
            if not filas_r:
                raise SystemExit(f"ERROR {r['key']}: sin filas no hay de dónde sacar los ejes epistemológicos")
            rec["epistemic_dimensions"] = ejes(filas[filas_r[0]])
        if fichero == "claims.jsonl":
            rec.setdefault("scope", {})
            for k in ("hypothesis_ids", "classification_view_ids", "temporal_expression_ids", "region_ids"):
                rec["scope"].setdefault(k, [])
            rec.setdefault("quantitative_support", [])
            rec["evidence_ids"] = []
            rec["counterevidence_ids"] = []
            rec.setdefault("derivation", None)
        if fichero == "issues.jsonl":
            rec.setdefault("affects", {})
            for k in ("record_ids", "claim_ids", "mention_ids"):
                rec["affects"].setdefault(k, [])
            rec.setdefault("resolution", {"status": "open"})
        if "notes" in props:
            rec.setdefault("notes", [])
        rec["record_status"] = "active"
        salida.append((fichero, rec))
    if faltan:
        raise SystemExit(f"ERROR claves usadas sin definir: {', '.join(sorted(faltan))}")
    if ajenas_a_la_procedencia:
        raise SystemExit("ERROR atribuciones que contradicen la procedencia:\n  "
                         + "\n  ".join(ajenas_a_la_procedencia))

    # --- enlaces que se deducen -----------------------------------------------------
    por_id = {rec["id"]: (fichero, rec) for fichero, rec in salida}
    afirmaciones = [rec for fichero, rec in salida if fichero == "claims.jsonl"]
    for fichero, rec in salida:
        if fichero == "evidence.jsonl":
            for cid in rec.get("supports_claim_ids", []):
                if cid in por_id and rec["id"] not in por_id[cid][1]["evidence_ids"]:
                    por_id[cid][1]["evidence_ids"].append(rec["id"])
            for cid in rec.get("challenges_claim_ids", []):
                if cid in por_id and rec["id"] not in por_id[cid][1]["counterevidence_ids"]:
                    por_id[cid][1]["counterevidence_ids"].append(rec["id"])
    for fichero, rec in salida:
        if fichero == "claims.jsonl" or "claim_ids" not in propiedades(fichero):
            continue
        propias = [c["id"] for c in afirmaciones
                   if c.get("subject_id") == rec["id"] or (c.get("object") or {}).get("entity_id") == rec["id"]]
        rec["claim_ids"] = sorted(set(propias))
    # Un resultado dice de qué análisis sale; el análisis lista sus resultados.
    # Los dos lados tienen que coincidir: si el fichero lista los resultados,
    # tienen que ser justo los que lo nombran, y si no, se deducen.
    clave_de = {rid: clave for clave, rid in ids.items()}
    asimetricos = []
    for fichero, rec in salida:
        if fichero != "analyses.jsonl":
            continue
        suyos = [x["id"] for f, x in salida if f == "results.jsonl" and x.get("analysis_id") == rec["id"]]
        if "result_ids" in rec and set(rec["result_ids"]) != set(suyos):
            asimetricos.append(f"{clave_de.get(rec['id'], rec['id'])}: `result_ids` "
                               f"{sorted(rec['result_ids'])} no son los resultados que lo nombran {sorted(suyos)}")
        rec.setdefault("result_ids", suyos)
    if asimetricos:
        raise SystemExit("ERROR análisis y resultados que no se enlazan en los dos sentidos:\n  "
                         + "\n  ".join(asimetricos))

    # --- menciones ----------------------------------------------------------------------
    actualizadas: list[tuple[dict, dict]] = []
    for mid, ingerida in sorted(menciones.items()):
        # El estado del que parte es el proyectado: un delta intermedio pudo
        # anotar la mención, y el UPDATE no puede deshacerlo.
        antes = proy.get(mid, (None, ingerida))[1]
        destino = spec["mentions"][ingerida["original_text"]]
        objetivos = sustituir(destino.get("targets", []), ids, faltan)
        if faltan:
            raise SystemExit(f"ERROR claves usadas sin definir: {', '.join(sorted(faltan))}")
        despues = dict(antes)
        despues["mention_type"] = destino["mention_type"]
        despues["disposition"] = destino["disposition"]
        despues["resolution"] = {"status": "resolved", "target_ids": objetivos,
                                 "reason": destino.get("reason")}
        if destino.get("reason"):
            despues["notes"] = list(antes.get("notes", [])) + [f"destino: {destino['reason']}"]
        actualizadas.append((antes, despues))

    # --- identificadores escritos tal cual ----------------------------------------------------
    # Un registro de otra sección se cita por su identificador. Si no existe, el
    # validador sólo lo detectaría en los `*_ids` de primer nivel: un sujeto, un
    # objeto o un participante colgando pasarían.
    existentes_id = proy
    conocidos = (set(por_id) | set(existentes_id) | base.ids_de_pasajes() | base.ids_de_secciones()
                 | set(menciones) | ids_de_vistas())
    colgando = []
    for fichero, rec in salida:
        colgando += [f"{rec['id']} → {x}" for x in sorted(literales(rec) - conocidos)]
    for _, d in actualizadas:
        colgando += [f"{d['id']} → {x}" for x in sorted(literales(d["resolution"]["target_ids"]) - conocidos)]
    if colgando:
        raise SystemExit("ERROR identificadores que no existen: " + "; ".join(colgando))

    # --- enlaces de vuelta en registros que ya existían ------------------------------------
    # Una afirmación sobre una entidad de otra sección, o una evidencia de una
    # afirmación que ya existía, tiene que quedar enlazada también desde allí.
    cambios: dict[str, tuple[str, dict, dict]] = {}

    def enlazar(rid: str, campo: str, nuevo_id: str) -> None:
        if rid in por_id or rid not in existentes_id:
            return
        fichero, antes = existentes_id[rid]
        if fichero not in ESQUEMA or campo not in propiedades(fichero):
            return
        _, _, despues = cambios.setdefault(rid, (fichero, antes, json.loads(json.dumps(antes))))
        if nuevo_id not in despues.setdefault(campo, []):
            despues[campo].append(nuevo_id)

    for c in afirmaciones:
        for rid in (c.get("subject_id"), (c.get("object") or {}).get("entity_id")):
            if isinstance(rid, str):
                enlazar(rid, "claim_ids", c["id"])
    for fichero, rec in salida:
        if fichero == "evidence.jsonl":
            for cid in rec.get("supports_claim_ids", []):
                enlazar(cid, "evidence_ids", rec["id"])
            for cid in rec.get("challenges_claim_ids", []):
                enlazar(cid, "counterevidence_ids", rec["id"])
        if fichero == "results.jsonl" and isinstance(rec.get("analysis_id"), str):
            enlazar(rec["analysis_id"], "result_ids", rec["id"])

    # --- esquemas ----------------------------------------------------------------------------
    # Lo que va a escribir el delta tiene que validar ya: descubrirlo con
    # `make check` después de aplicarlo dejaría el libro mayor inválido hasta
    # revertir. Se validan los registros nuevos y las menciones; de los que ya
    # existían, sólo lo que el enlace de vuelta estropea, no lo que ya traían.
    escritos, avisos = fallos_de_esquema([*salida, *(("mentions.jsonl", d) for _, d in actualizadas),
                                          *((f, despues) for f, _, despues in cambios.values())])
    previos, _ = fallos_de_esquema([(f, antes) for f, antes, _ in cambios.values()])
    for aviso in avisos:
        print(f"AVISO {aviso}")
    invalidos = [f"{donde}: {fallo}" for donde, fallos in sorted(escritos.items())
                 for fallo in sorted(fallos - previos.get(donde, set()))]
    if invalidos:
        raise SystemExit("ERROR registros que no validan contra su esquema:\n  " + "\n  ".join(invalidos))

    # --- delta ------------------------------------------------------------------------------
    operaciones = [{"operation": "ADD_RECORD", "file": fichero, "record_id": rec["id"], "before": None, "after": rec}
                   for fichero, rec in salida]
    operaciones += [{"operation": "UPDATE_RECORD", "file": "mentions.jsonl", "record_id": d["id"],
                     "before": a, "after": d} for a, d in actualizadas]
    operaciones += [{"operation": "UPDATE_RECORD", "file": fichero, "record_id": rid,
                     "before": antes, "after": despues} for rid, (fichero, antes, despues) in sorted(cambios.items())]
    de = lambda f: [rec["id"] for fichero, rec in salida if fichero == f]
    filas_destino = {}
    for fila, destino in spec["rows"].items():
        filas_destino[fila] = {"destination": destino["destination"],
                               "record_ids": [ids[k] for k in destino.get("keys", [])],
                               **({"note": destino["note"]} if destino.get("note") else {})}
    delta = {
        "section_id": sec_id,
        "schema_version": base.SCHEMA_VERSION,
        "dataset_revision_before": rev_antes,
        "dataset_revision_after": rev_despues,
        "operations": operaciones,
        "records_added": [rec["id"] for _, rec in salida],
        "records_updated": [d["id"] for _, d in actualizadas] + sorted(cambios),
        "claims_added": de("claims.jsonl"),
        "events_added": de("events.jsonl"),
        "hypotheses_added": de("hypotheses.jsonl"),
        "issues_added": de("issues.jsonl"),
        "issues_resolved": [], "records_deprecated": [], "views_invalidated": [], "views_built": [],
        "validation_results": {},
        "conversion": {
            "of": sec_id,
            "section_delta": delta_path.name,
            "spec": {"path": corredor._rel(spec_path), "sha256": sha256(spec_bytes)},
            "decision": spec.get("decision"),
            "freeze": {"path": corredor._rel(Path(ruta)), "fingerprint": congelada["fingerprint"]},
            "rows": filas_destino,
        },
    }
    return {"sec": sec, "sec_id": sec_id, "delta": delta, "salida": salida, "actualizadas": actualizadas,
            "filas": filas, "spec": spec, "rev": (rev_antes, rev_despues), "pendientes": sin_aplicar,
            "fuentes_reutilizadas": sorted(set(citadas) & set(existentes))}


# ---------------------------------------------------------------------------
# Informe y escritura
# ---------------------------------------------------------------------------

def informe(r: dict) -> list[str]:
    spec, delta = r["spec"], r["delta"]
    por_fichero: dict[str, int] = {}
    for fichero, _ in r["salida"]:
        por_fichero[fichero] = por_fichero.get(fichero, 0) + 1
    por_destino: dict[str, list[str]] = {}
    for fila, d in spec["rows"].items():
        por_destino.setdefault(d["destination"], []).append(fila)
    disposiciones: dict[str, int] = {}
    for _, d in r["actualizadas"]:
        disposiciones[d["disposition"]] = disposiciones.get(d["disposition"], 0) + 1
    lineas = [
        f"# Conversión de {r['sec_id']} · sección {r['sec']} del corredor",
        "",
        f"- Fecha: {date.today().isoformat()}",
        f"- Revisión: {r['rev'][0]} → {r['rev'][1]}",
        f"- Fichero de conversión: `{delta['conversion']['spec']['path']}` ({delta['conversion']['spec']['sha256'][:19]}…)",
        f"- Decisión: {spec.get('decision')}",
        "",
        "## Filas por destino",
        "",
        "| Destino | Filas |",
        "|---|---|",
    ]
    lineas += [f"| {k} | {', '.join(sorted(v))} |" for k, v in sorted(por_destino.items())]
    lineas += ["", "## Registros nuevos", "", "| Fichero | Registros |", "|---|---:|"]
    lineas += [f"| `{f}` | {n} |" for f, n in sorted(por_fichero.items())]
    if r["fuentes_reutilizadas"]:
        lineas += ["", f"Fuentes que ya existían y se reutilizan: {', '.join(r['fuentes_reutilizadas'])}."]
    lineas += ["", "## Menciones", "", "| Destino | Menciones |", "|---|---:|"]
    lineas += [f"| `{k}` | {n} |" for k, n in sorted(disposiciones.items())]
    notas = [(fila, d["note"]) for fila, d in spec["rows"].items() if d.get("note")]
    if notas:
        lineas += ["", "## Notas de conversión", ""]
        lineas += [f"- **{fila}**: {nota}" for fila, nota in notas]
    if r["pendientes"]:
        lineas += ["", f"Va detrás de deltas sin aplicar: {', '.join(r['pendientes'])}."]
    return lineas


def convertir(spec_path: Path, corpus: str, dry: bool) -> int:
    r = construir(spec_path, corpus)
    lineas = informe(r)
    print("\n".join(lineas))
    if dry:
        print("\n(en seco: no se ha escrito nada)")
        return 0
    nombre = f"{r['sec_id']}-conversion"
    # Una conversión revertida se queda como constancia: reserva sus
    # identificadores y el historial la nombra. La nueva lleva otro nombre.
    n = 2
    while (base.DELTAS / f"{nombre}.json").exists():
        nombre = f"{r['sec_id']}-conversion-{n}"
        n += 1
    base.DELTAS.mkdir(parents=True, exist_ok=True)
    base.REPORTS.mkdir(parents=True, exist_ok=True)
    (base.DELTAS / f"{nombre}.json").write_text(
        json.dumps(r["delta"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (base.REPORTS / f"{nombre}.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"\n  delta     knowledge/deltas/{nombre}.json")
    print(f"  informe   generated/reports/{nombre}.md")
    print(f"\n  el delta NO se ha aplicado. Va detrás del de la sección:")
    print(f"    python scripts/ingest/delta.py {nombre}.json")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Convierte las filas de una sección del corredor en registros (§17 paso 6, DEC-057)")
    ap.add_argument("spec", help="fichero de conversión de la sección")
    ap.add_argument("--corpus", required=True, help="copia del corredor, o directorio@commit")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    return convertir(Path(a.spec).resolve(), a.corpus, a.dry_run)


if __name__ == "__main__":
    sys.exit(main())
