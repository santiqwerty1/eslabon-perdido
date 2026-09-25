#!/usr/bin/env python3
"""Una sección del corredor como sección de ingestión (§17, DEC-056).

`ingest.py` nació para un documento Markdown con la capa de registro dentro. El
corpus llegó como repositorio: la prosa por secciones en `docs/secciones/` y las
filas en `data/afirmaciones/NN.csv`. Este módulo construye, para una sección,
lo mismo que el modo documento —sección, pasajes, menciones, delta, informe—, y
lo que ese modo no podía dar:

- **Se ingiere la versión congelada, o nada.** Antes de leer una fila se
  comprueba que la copia tiene la huella de la congelación activa. Una copia que
  no coincide es otra versión del corpus: se congela aparte y se compara con
  `freeze.py diff`.
- **Sólo la sección pedida.** Sus filas y las entidades del apéndice B que
  aparecen en ella por primera vez, no el corpus entero en cada sección.
- **Cada mención vuelve a su pasaje.** La prosa cita cada fila en línea
  —«[C-176; S53 §History of LUCA]»—, así que el pasaje de una fila es el párrafo
  que la cita. Si sólo la cita una tabla, el párrafo donde la tabla se inserta;
  si no la cita nada, el del registro de la sección. La vía queda escrita.
- **El rastro de la congelación viaja en el delta.** Qué versión, qué ficheros
  con qué hash, y qué pasajes y menciones salieron de cada fila `C-…`. Es la
  correspondencia que necesitará la reingestión cuando el corredor renumere.

Lo que sigue sin hacer, igual que en el modo documento: los pasos 5 a 9. Las
menciones quedan `pending` y de tipo `unresolved`; el tipo lo fija quien
resuelve identidad, no una heurística sobre la columna «tipo» del apéndice B,
que es texto libre («concepto o entidad», «magnitud, rasgo o concepto»).
"""

from __future__ import annotations

import csv
import io
import json
import re
import sys
from datetime import date
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import freeze  # noqa: E402
import ingest as base  # noqa: E402
from parse_research import parse  # noqa: E402
from resolve_identity import descartable  # noqa: E402

# «C-176», y rangos «C-148–C-160» con guion o raya. Un rango disparatado —una
# errata que junte C-012 con C-1200— no se expande: se toman sus extremos.
CITA = re.compile(r"\bC-(\d{3,})(?:\s*[–—-]\s*C-(\d{3,}))?")
RANGO_MAX = 400
MARCADOR = re.compile(r"<!--\s*TABLE:([^\s>]+)\s*-->")
COL_PRIMERA = "# de la fila del registro donde aparece por primera vez"


def cid(n: int) -> str:
    return f"C-{n:03d}"


def citas(texto: str) -> set[str]:
    salida: set[str] = set()
    for m in CITA.finditer(texto):
        a = int(m.group(1))
        b = int(m.group(2)) if m.group(2) else a
        if b < a or b - a > RANGO_MAX:
            salida.update({cid(a), cid(b)})
        else:
            salida.update(cid(n) for n in range(a, b + 1))
    return salida


def _rel(p: Path) -> str:
    try:
        return str(p.resolve().relative_to(base.ROOT))
    except ValueError:
        return str(p)


# ---------------------------------------------------------------------------
# Congelación
# ---------------------------------------------------------------------------

def congelacion(ruta: Path | None) -> tuple[Path, dict]:
    if ruta is None:
        manifiesto = json.loads(base.MANIFEST.read_text(encoding="utf-8"))
        activa = (manifiesto.get("corpus_freeze") or {}).get("path")
        if not activa:
            raise SystemExit("ERROR dataset.json no declara congelación activa (`corpus_freeze`, "
                             "DEC-056): no hay versión del corpus que ingerir")
        ruta = base.ROOT / activa
    return ruta, json.loads(Path(ruta).read_text(encoding="utf-8"))


def verificar(src: freeze.Fuente, ruta: Path, registro: dict) -> None:
    if freeze.huella(registro["files"]) != registro.get("fingerprint"):
        raise SystemExit(f"ERROR {ruta.name} es incoherente: su huella no corresponde a sus ficheros")
    actual = freeze.huella(freeze.ficheros(src.base))
    if actual != registro["fingerprint"]:
        raise SystemExit(
            f"ERROR {src.etiqueta} no es la versión congelada en {ruta.name}\n"
            f"      congelada {registro['fingerprint']}\n"
            f"      esta      {actual}\n"
            "      Si es una versión nueva, compárala con `make corpus-diff` y congélala (DEC-056).\n"
            f"      Si quieres la congelada, ingiere su commit: {src.base}@{(registro.get('commit') or '')[:7]}")


# ---------------------------------------------------------------------------
# Construcción, sin escribir nada
# ---------------------------------------------------------------------------

def ficheros_de_seccion(raiz: Path, sec: str) -> tuple[Path, Path]:
    registro = raiz / "data" / "afirmaciones" / f"{sec}.csv"
    if not registro.exists():
        hay = ", ".join(p.stem for p in sorted((raiz / "data" / "afirmaciones").glob("*.csv")))
        raise SystemExit(f"ERROR la sección {sec} no tiene registro de afirmaciones. Hay: {hay}. "
                         "Los apéndices no se ingieren por este camino todavía")
    prosa = [p for p in sorted((raiz / "docs" / "secciones").glob("*.md"))
             if p.name.split("-")[1:2] == [sec]]
    if len(prosa) != 1:
        raise SystemExit(f"ERROR la sección {sec} tiene {len(prosa)} ficheros de prosa en "
                         "docs/secciones/; se esperaba uno")
    return prosa[0], registro


def ya_ingerida(sec: str) -> str | None:
    for p in sorted(base.DELTAS.glob("*.json")):
        try:
            origen = json.loads(p.read_text(encoding="utf-8")).get("corpus_origin") or {}
        except json.JSONDecodeError:
            continue
        if origen.get("section") == sec:
            return p.name
    return None


def localizar(etiqueta: str, pasaje: dict) -> tuple[int, int, str | None]:
    """Offsets de la etiqueta dentro del pasaje, y una nota si no es literal.

    Literal: sus offsets y ninguna nota. Con otra capitalización: los offsets de
    esa aparición y una nota que dice cómo aparece, porque una mención es una
    aparición textual y el texto seleccionado no es el de `original_text`. Si no
    aparece: el pasaje entero, y la nota lo dice.
    """
    texto, ini = pasaje["text"], pasaje["character_offsets"]["start"]
    i = texto.find(etiqueta)
    if i >= 0:
        return ini + i, ini + i + len(etiqueta), None
    if len(texto.casefold()) == len(texto) and len(etiqueta.casefold()) == len(etiqueta):
        i = texto.casefold().find(etiqueta.casefold())
        if i >= 0:
            visto = texto[i:i + len(etiqueta)]
            return (ini + i, ini + i + len(etiqueta),
                    f"en el pasaje aparece como «{visto}», con otra capitalización; "
                    "los offsets señalan esa aparición")
    return (ini, pasaje["character_offsets"]["end"],
            "la etiqueta no aparece literal en el pasaje; los offsets cubren el pasaje entero")


def construir(spec: str, seccion: str, ruta_congelacion: Path | None = None) -> dict:
    sec = f"{int(seccion):02d}" if seccion.isdigit() else seccion
    src = freeze.abrir(spec)
    ruta, congelada = congelacion(ruta_congelacion)
    verificar(src, ruta, congelada)

    datos, conformidad = parse(src.base)
    if conformidad.errores:
        raise SystemExit("ERROR el corpus no pasa la conformidad (parse_research.py): "
                         + "; ".join(conformidad.errores[:5]))

    previa = ya_ingerida(sec)
    if previa:
        raise SystemExit(f"ERROR la sección {sec} ya se ingirió ({previa}). Una versión nueva entra "
                         "por diferencia, no ingiriendo otra vez (INGESTION-C01.md)")

    prosa, registro = ficheros_de_seccion(src.base, sec)
    texto_bytes, registro_bytes = prosa.read_bytes(), registro.read_bytes()
    texto = texto_bytes.decode("utf-8")
    ids = [f["#"] for f in csv.DictReader(io.StringIO(registro_bytes.decode("utf-8")))]
    por_id = {c["local_id"]: c for c in datos["claims"]}
    filas = [por_id[i] for i in ids]

    manifiesto = json.loads(base.MANIFEST.read_text(encoding="utf-8")) if base.MANIFEST.exists() else {}
    rev_antes, rev_despues, pendientes = base.revision_siguiente(manifiesto)
    sec_id = base.siguiente_id("SEC", {p.stem for p in base.SECTIONS.glob("SEC-*")})
    base_pasaje = base.siguiente_libre("PASSAGE", base.ids_de_pasajes())
    base_mencion = base.siguiente_libre("MENTION", base.ids_en_uso("mentions.jsonl", "MENTION")
                                        | base.reservados_por_deltas("MENTION"))

    titulo = next((l.lstrip("#").strip() for l in texto.splitlines() if l.startswith("# ")), prosa.stem)
    seccion_rec = {
        "id": sec_id,
        "title": titulo,
        "received_at": date.today().isoformat(),
        "original_content_path": f"knowledge/corpus/sections/{sec_id}.md",
        "content_hash": base.sha256(texto_bytes),
        "approximate_period": None,
        "topics": [],
        "source_ids": [],
        "schema_version": base.SCHEMA_VERSION,
        "dataset_revision": rev_despues,
        "record_status": "active",
    }

    # --- paso 2: pasajes, y qué cita cada uno ------------------------------
    pasajes, por_marcador, citadas = [], {}, {}
    for n, (ini, fin, cuerpo) in enumerate(base.segmentar(texto), 1):
        pid = f"PASSAGE-{base_pasaje + n - 1:06d}"
        pasajes.append({
            "id": pid, "section_id": sec_id, "ordinal": n, "text": cuerpo,
            "character_offsets": {"start": ini, "end": fin}, "record_status": "active",
        })
        marcas = MARCADOR.findall(cuerpo)
        for tid in marcas:
            por_marcador[tid] = pid
        if not marcas:
            citadas[pid] = citas(cuerpo)
    pasaje = {p["id"]: p for p in pasajes}

    congelados = {f["path"] for f in congelada["files"]}

    def dentro(relativa: str) -> Path:
        # Una ruta del índice que saliera de la capa congelada —absoluta, con
        # «..» o a un fichero sin huella— cambiaría la procedencia sin que la
        # verificación lo notara.
        ruta = (src.base / relativa).resolve()
        try:
            rel = ruta.relative_to(src.base.resolve()).as_posix()
        except ValueError:
            rel = None
        if rel not in congelados:
            raise SystemExit(f"ERROR data/table_index.json apunta a {relativa!r}, que no es un "
                             "fichero de la versión congelada")
        return ruta

    indice = {t["id"]: t for t in json.loads(
        (src.base / "data" / "table_index.json").read_text(encoding="utf-8"))["tables"]}
    por_tabla = {tid: citas(dentro(indice[tid]["csv_path"]).read_text(encoding="utf-8"))
                 for tid in por_marcador if tid in indice and indice[tid].get("category") != "claims"}
    del_registro = next((tid for tid in por_marcador if indice.get(tid, {}).get("category") == "claims"), None)

    origen_filas: dict[str, dict] = {}
    for i in ids:
        pids, via = [pid for pid, cs in citadas.items() if i in cs], "prosa"
        if not pids:
            tablas = [tid for tid, cs in por_tabla.items() if i in cs]
            pids, via = [por_marcador[t] for t in tablas], "tabla " + ", ".join(tablas)
        if not pids:
            if del_registro:
                pids, via = [por_marcador[del_registro]], "sólo el registro"
            else:
                pids, via = [pasajes[0]["id"]], "sólo el registro, sin marcador en la prosa"
        origen_filas[i] = {"passage_ids": pids, "via": via, "mention_ids": []}

    # --- pasos 3 y 4: una mención por etiqueta distinta de la sección ------
    menciones: list[dict] = []
    por_etiqueta: dict[str, dict] = {}
    usos: dict[str, list[str]] = {}
    descartadas: dict[str, str] = {}
    sin_literal: set[str] = set()

    def mencionar(etiqueta: str, fila: str, uso: str) -> dict | None:
        etiqueta = (etiqueta or "").strip()
        motivo = descartable(etiqueta)
        if motivo:
            descartadas.setdefault(etiqueta, motivo)
            return None
        usos.setdefault(etiqueta, []).append(f"{uso} en {fila}")
        if etiqueta in por_etiqueta:
            return por_etiqueta[etiqueta]
        pid = origen_filas[fila]["passage_ids"][0]
        ini, fin, nota = localizar(etiqueta, pasaje[pid])
        m = {
            "id": f"MENTION-{base_mencion + len(menciones):06d}",
            "section_id": sec_id,
            "passage_id": pid,
            "original_text": etiqueta,
            "normalized_form": base.normalizar(etiqueta),
            # El tipo lo fija quien resuelve identidad (paso 5), no una
            # heurística sobre una columna de texto libre.
            "mention_type": "unresolved",
            "character_offsets": {"start": ini, "end": fin},
            "resolution": {"status": "pending", "target_ids": [], "reason": None},
            "disposition": None,
            "issue_ids": [],
            "notes": [nota] if nota else [],
            "record_status": "active",
        }
        menciones.append(m)
        por_etiqueta[etiqueta] = m
        if nota:
            sin_literal.add(m["id"])
        return m

    for c in filas:
        for campo, uso in (("subject_label", "sujeto"), ("object_label", "objeto")):
            m = mencionar(c.get(campo), c["local_id"], uso)
            if m and m["id"] not in origen_filas[c["local_id"]]["mention_ids"]:
                origen_filas[c["local_id"]]["mention_ids"].append(m["id"])

    propias_b = [e for e in datos["entities"] if (e.get(COL_PRIMERA) or "").strip() in origen_filas]
    for e in propias_b:
        fila = e[COL_PRIMERA].strip()
        m = mencionar(e.get("etiqueta preferida"), fila, "apéndice B")
        if m is not None:
            tipo = (e.get("tipo") or "").strip()
            if tipo and not any(n.startswith("apéndice B") for n in m["notes"]):
                m["notes"].append(f"apéndice B: tipo declarado «{tipo}»")

    for m in menciones:
        m["notes"].insert(0, "capa de registro: " + "; ".join(usos[m["original_text"]]))

    # --- paso 10 y contraste ------------------------------------------------
    declaradas = indice.get(f"claims-{sec}", {}).get("row_count")
    con_mencion_b = sum(1 for e in propias_b if (e.get("etiqueta preferida") or "").strip() in por_etiqueta)
    # Filas del apéndice B que no nombran nada: un marcador de hueco o una cifra
    # metidos como entidad. Explican cualquier descuadre del contraste.
    b_descartadas = [((e.get("etiqueta preferida") or "").strip(), e[COL_PRIMERA].strip(),
                      descartadas.get((e.get("etiqueta preferida") or "").strip(), "?"))
                     for e in propias_b if (e.get("etiqueta preferida") or "").strip() not in por_etiqueta]
    vias: dict[str, int] = {}
    for o in origen_filas.values():
        clave = "prosa" if o["via"] == "prosa" else ("tabla" if o["via"].startswith("tabla") else "sólo el registro")
        vias[clave] = vias.get(clave, 0) + 1
    no_literales = len(sin_literal)
    contraste = [
        ("afirmaciones de la sección", declaradas, len(filas)),
        ("entidades del apéndice B que aparecen aquí por primera vez", len(propias_b), con_mencion_b),
    ]

    # --- paso 13: delta -----------------------------------------------------
    delta = {
        "section_id": sec_id,
        "schema_version": base.SCHEMA_VERSION,
        "dataset_revision_before": rev_antes,
        "dataset_revision_after": rev_despues,
        "operations": [{"operation": "ADD_RECORD", "file": "mentions.jsonl", "record_id": m["id"],
                        "before": None, "after": m} for m in menciones],
        "records_added": [m["id"] for m in menciones],
        "records_updated": [], "claims_added": [], "events_added": [], "hypotheses_added": [],
        "issues_added": [], "issues_resolved": [], "records_deprecated": [],
        "views_invalidated": [], "views_built": [], "validation_results": {},
        "corpus_origin": {
            "corpus": congelada.get("corpus"),
            "version": congelada.get("version"),
            "freeze": {"path": _rel(Path(ruta)), "fingerprint": congelada["fingerprint"],
                       "commit": congelada.get("commit")},
            "section": sec,
            "files": {
                "prose": {"path": prosa.relative_to(src.base).as_posix(), "sha256": base.sha256(texto_bytes),
                          "copy": f"knowledge/corpus/sections/{sec_id}.md"},
                "registry": {"path": registro.relative_to(src.base).as_posix(),
                             "sha256": base.sha256(registro_bytes),
                             "copy": f"knowledge/corpus/sections/{sec_id}.registro.csv"},
            },
            "rows": origen_filas,
        },
    }

    return {
        "sec": sec, "sec_id": sec_id, "src": src, "congelacion": ruta, "congelada": congelada,
        "texto": texto, "registro_bytes": registro_bytes, "seccion": seccion_rec,
        "pasajes": pasajes, "menciones": menciones, "delta": delta, "contraste": contraste,
        "vias": vias, "no_literales": no_literales, "descartadas": descartadas,
        "b_descartadas": b_descartadas,
        "rev": (rev_antes, rev_despues), "pendientes": pendientes, "avisos": conformidad.avisos,
    }


# ---------------------------------------------------------------------------
# Informe
# ---------------------------------------------------------------------------

def informe(r: dict) -> list[str]:
    s, c = r["seccion"], r["congelada"]
    origen = r["delta"]["corpus_origin"]
    lineas = [
        f"# Informe de ingestión · {r['sec_id']}",
        "",
        f"**Sección del corredor:** {r['sec']} · {s['title']}  ",
        f"**Versión:** {c.get('version')} · commit `{(c.get('commit') or '—')[:12]}` · "
        f"huella `{c['fingerprint']}`  ",
        f"**Prosa:** `{origen['files']['prose']['path']}` · `{origen['files']['prose']['sha256']}`  ",
        f"**Registro:** `{origen['files']['registry']['path']}` · `{origen['files']['registry']['sha256']}`  ",
        f"**Revisión:** {r['rev'][0]} → {r['rev'][1]}",
        "",
        "## Contraste con lo que el corpus declara",
        "",
        "Si una fila no cuadra, no se aplica el delta: se averigua por qué.",
        "",
        "| Lo que declara el corpus | Declarado | Ingerido |",
        "|---|---:|---:|",
        *[f"| {e} | {d if d is not None else '—'} | {i} |" + ("  ⚠" if d is not None and d != i else "")
          for e, d, i in r["contraste"]],
        "",
    ]
    if r["b_descartadas"]:
        lineas += [
            "Filas del apéndice B que no nombran nada y por eso no dan mención. Son un",
            "hallazgo sobre el corpus: un marcador de hueco o una cifra no son entidades.",
            "",
            "| Etiqueta preferida | Primera fila | Motivo |",
            "|---|---|---|",
            *[f"| `{e}` | {f} | {m} |" for e, f, m in r["b_descartadas"]],
            "",
        ]
    lineas += [
        "## De qué pasaje sale cada fila",
        "",
        "| Vía | Filas |",
        "|---|---:|",
        *[f"| {v} | {n} |" for v, n in sorted(r["vias"].items())],
        "",
        "«Prosa» es un párrafo que cita la fila. «Tabla» es el párrafo donde se inserta la",
        "tabla que la cita. «Sólo el registro» es una fila que ni la prosa ni las tablas de",
        "la sección citan: su pasaje es el marcador del registro, y conviene mirarla.",
        "",
        "## Cobertura",
        "",
        f"- pasajes: **{len(r['pasajes'])}**",
        f"- menciones: **{len(r['menciones'])}**, todas `pending` y de tipo `unresolved`",
        f"- menciones cuya etiqueta no aparece literal en su pasaje: **{r['no_literales']}**",
        f"- celdas descartadas por no nombrar nada: **{len(r['descartadas'])}**",
        "",
    ]
    if r["descartadas"]:
        lineas += ["| Celda | Motivo |", "|---|---|",
                   *[f"| `{t}` | {m} |" for t, m in sorted(r["descartadas"].items())], ""]
    lineas += [
        "## Cuestiones pendientes",
        "",
        "Los pasos 5 a 9 del protocolo son **juicio humano** y no se han ejecutado:",
        "",
        "- **paso 5, identidad**: se resuelve sobre el corpus entero con",
        "  `resolve_identity.py propose`, no sección a sección.",
        "- **pasos 6 a 9**: las filas ya traen sujeto, predicado y objeto, pero el",
        "  vocabulario de predicados del corredor no es el del esquema; convertirlas",
        "  exige decidir la correspondencia antes.",
        "",
        "## Resumen del delta",
        "",
        f"- operaciones: **{len(r['delta']['operations'])}**, todas `ADD_RECORD` sobre `mentions.jsonl`",
        "- `corpus_origin` guarda la versión, los ficheros y, por fila `C-…`, sus pasajes y menciones",
        f"- reversible con `python scripts/ingest/delta.py {r['sec_id']}.json --revert`",
        "",
        "## Estado",
        "",
        "**La sección NO está terminada.** §28.1 exige cobertura completa, y",
        f"quedan {len(r['menciones'])} menciones sin destino.",
    ]
    return lineas


def ingerir(spec: str, seccion: str, ruta_congelacion: Path | None, dry: bool) -> int:
    r = construir(spec, seccion, ruta_congelacion)
    print(f"{r['sec_id']} · sección {r['sec']} del corredor · {r['seccion']['title']}")
    print(f"  versión {r['congelada'].get('version')} · huella verificada")
    if r["pendientes"]:
        print(f"  aviso: hay deltas sin aplicar ({', '.join(r['pendientes'])}); éste va detrás "
              f"({r['rev'][0]} → {r['rev'][1]}) y se aplica después de ellos")
    print(f"  {len(r['pasajes'])} pasajes · {len(r['menciones'])} menciones "
          f"({r['no_literales']} sin literal en su pasaje)")
    print("  filas por vía: " + " · ".join(f"{v} {n}" for v, n in sorted(r["vias"].items())))
    print("\n  contraste con lo declarado:")
    for e, d, i in r["contraste"]:
        marca = "  <-- NO CUADRA" if d is not None and d != i else ""
        print(f"    {e:58} declarado {d if d is not None else '—':>5}  ingerido {i:5}{marca}")
    for e, f, m in r["b_descartadas"]:
        print(f"      apéndice B, «{e}» ({f}): {m}")
    return base.escribir(
        r["sec_id"], r["texto"], r["seccion"], r["pasajes"], r["delta"], informe(r), dry,
        extras={base.SECTIONS / f"{r['sec_id']}.registro.csv": r["registro_bytes"]})
