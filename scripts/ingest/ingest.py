#!/usr/bin/env python3
"""Protocolo de ingestión de una sección (§17).

Automatiza lo mecánico y **se niega a automatizar lo que es juicio**. De los
quince pasos:

    1  registrar la sección          automático
    2  segmentar en pasajes          automático
    3  extraer menciones             automático, propone candidatas
    4  normalizar sin borrar         automático, propone forma normalizada
    5  resolver identidad            HUMANO — sólo se marcan como pendientes
    6  extraer afirmaciones          HUMANO — depende del paso 5
    7  registrar evidencia           HUMANO
    8  crear eventos                 HUMANO
    9  integrar hipótesis            HUMANO
    10 auditar cobertura             automático, es el criterio de terminado
    11 actualizar vistas             scripts/build_views/
    12 validar                       scripts/validate/
    13 generar delta                 automático
    14 informe humano                automático
    15 confirmar persistencia        automático

Marcar como automático el paso 5 sería mentir sobre la cobertura: decidir si dos
menciones son la misma entidad es exactamente el juicio que §27.12 reserva a una
persona. Lo que sí se hace es dejar cada mención con `resolution.status:
"pending"` y su destino sin fijar, de modo que la auditoría del paso 10 falle
mientras queden sin resolver.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "knowledge" / "corpus"
SECTIONS = CORPUS / "sections"
PASSAGES = CORPUS / "passages"
MANIFEST = CORPUS / "manifests" / "dataset.json"
DELTAS = ROOT / "knowledge" / "deltas"
REPORTS = ROOT / "generated" / "reports"

# La del contrato vigente (schemas/migrations/1.0.0-a-1.1.0.md). Escribir 1.0.0
# en registros nuevos los declararía anteriores a DEC-054 y DEC-055.
SCHEMA_VERSION = "1.1.0"

# Heurísticas del paso 3. Proponen, no deciden: cada acierto y cada falso
# positivo acaban igualmente en el libro mayor de menciones, y es el paso 5 quien
# los resuelve. Preferimos sobre-extraer: §17 dice que no se omite un elemento
# porque parezca secundario, y una mención de más se descarta con justificación,
# mientras que una de menos rompe la cobertura sin que nadie se entere.
PATRONES = [
    ("taxonomic_name", re.compile(r"\b[A-Z][a-z]{2,}(?:\s+[a-z]{3,})?\b")),
    ("date", re.compile(r"\b\d{1,4}[,.]?\d*\s*(?:Ma|Ga|ka|millones de años|años)\b")),
    ("source", re.compile(r"\(([A-Z][A-Za-z\-]+(?:\s+(?:et\s+al\.|y\s+[A-Z][a-z]+))?),?\s*\d{4}\)")),
    ("historical_term", re.compile(r"«([^»]{3,40})»")),
]

# Palabras que la heurística confundiría con nombres científicos.
RUIDO = {
    "Los", "Las", "Una", "Uno", "Por", "Para", "Como", "Este", "Esta", "Esto",
    "Pero", "Cuando", "Donde", "Aunque", "Sin", "Con", "Desde", "Hasta", "Entre",
    "Sobre", "Bajo", "Ademas", "Además", "También", "Tambien", "Segun", "Según",
    "Figura", "Tabla", "Sección", "Seccion", "Apéndice", "Apendice",
}


def sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def siguiente_id(prefijo: str, existentes: set[str]) -> str:
    n = 0
    for i in existentes:
        if i.startswith(prefijo + "-"):
            try:
                n = max(n, int(i.split("-")[1]))
            except (IndexError, ValueError):
                pass
    return f"{prefijo}-{n + 1:06d}"


def normalizar(texto: str) -> str:
    """Propone una forma normalizada. Nunca sustituye al original (§17 paso 4)."""
    plano = unicodedata.normalize("NFC", texto.strip())
    return re.sub(r"\s+", " ", plano)


def segmentar(texto: str) -> list[tuple[int, int, str]]:
    """Divide en pasajes localizables. Un pasaje = un párrafo no vacío."""
    pasajes = []
    pos = 0
    for bloque in re.split(r"\n\s*\n", texto):
        inicio = texto.find(bloque, pos)
        if inicio < 0:
            inicio = pos
        fin = inicio + len(bloque)
        pos = fin
        if bloque.strip():
            pasajes.append((inicio, fin, bloque))
    return pasajes


def extraer_menciones(pasaje: str, offset: int) -> list[dict]:
    vistas: set[tuple[int, int]] = set()
    salida = []
    for tipo, patron in PATRONES:
        for m in patron.finditer(pasaje):
            txt = m.group(1) if m.groups() else m.group(0)
            ini, fin = m.span(1) if m.groups() else m.span(0)
            if txt.split()[0] in RUIDO or len(txt) < 3:
                continue
            if (ini, fin) in vistas:
                continue
            vistas.add((ini, fin))
            salida.append(
                {
                    "tipo": tipo,
                    "texto": txt,
                    "start": offset + ini,
                    "end": offset + fin,
                }
            )
    return sorted(salida, key=lambda x: x["start"])


def ids_en_uso(fichero: str, prefijo: str) -> set[str]:
    """Identificadores ya presentes en el libro mayor.

    Sin esto, cada sección reinicia la numeración en 000001 y el segundo delta
    aborta con «ya existe». El manual manda una SEC- por sección de nivel 2, así
    que ese caso no es raro: es el normal.
    """
    ruta = ROOT / "knowledge" / "records" / fichero
    if not ruta.exists():
        return set()
    out = set()
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        if linea.strip():
            try:
                rid = json.loads(linea).get("id", "")
            except json.JSONDecodeError:
                continue
            if isinstance(rid, str) and rid.startswith(prefijo + "-"):
                out.add(rid)
    return out


def ids_de_pasajes() -> set[str]:
    """Pasajes ya emitidos. Viven en corpus/passages/, no en el libro mayor:
    buscarlos en mentions.jsonl no encontraba ninguno y cada sección volvía a
    empezar en PASSAGE-000001."""
    out: set[str] = set()
    for p in PASSAGES.glob("*.json"):
        try:
            for rec in json.loads(p.read_text(encoding="utf-8")):
                if isinstance(rec, dict) and isinstance(rec.get("id"), str):
                    out.add(rec["id"])
        except (json.JSONDecodeError, TypeError):
            continue
    return out


def reservados_por_deltas(prefijo: str) -> set[str]:
    """Identificadores que algún delta ya emitió, se haya aplicado o no.

    Ingerir escribe el delta pero no lo aplica. Sin esto, una segunda sección
    ingerida antes de aplicar la primera repetía sus MENTION-…, y al aplicar
    una la otra abortaba. Un identificador emitido no se reutiliza nunca.
    """
    out: set[str] = set()
    for p in DELTAS.glob("*.json"):
        try:
            delta = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        candidatos = list(delta.get("records_added") or [])
        candidatos += [op.get("record_id") for op in delta.get("operations") or [] if isinstance(op, dict)]
        out.update(i for i in candidatos if isinstance(i, str) and i.startswith(prefijo + "-"))
    return out


def revision_siguiente(manifiesto: dict) -> tuple[str, str, list[str]]:
    """Revisión de partida y de llegada para un delta nuevo, y deltas pendientes.

    La de partida es la última que algún delta ya declara, no la del manifiesto:
    dos deltas sin aplicar no pueden llevar el dataset a la misma revisión. El
    orden queda escrito en la cadena y hay que respetarlo al aplicar.
    """
    num = lambda r: int(str(r).split("-")[1])
    actual = manifiesto.get("dataset_revision", "REV-000000")
    revertidos = {d for d, a in ultima_accion().items() if a == "revertir"}
    antes, pendientes = actual, []
    for p in sorted(DELTAS.glob("*.json")):
        if p.name in revertidos:
            # Revertido a propósito: sigue ahí como constancia, pero nada nuevo
            # se encadena detrás de él.
            continue
        try:
            despues = json.loads(p.read_text(encoding="utf-8")).get("dataset_revision_after")
        except json.JSONDecodeError:
            continue
        if despues and num(despues) > num(actual):
            pendientes.append(p.name)
            if num(despues) > num(antes):
                antes = despues
    return antes, f"REV-{num(antes) + 1:06d}", pendientes


def ids_de_secciones() -> set[str]:
    """Todo SEC ya emitido: el de cada sección, cada delta y cada línea del historial.

    Un SEC no se reutiliza nunca. El historial va por nombre de fichero: si,
    tras retirar los ficheros de una sección revertida, su número volviera a
    salir, el delta nuevo heredaría el «revertir» del viejo y se daría por no
    pendiente.
    """
    return ({p.name.split(".")[0] for p in SECTIONS.glob("SEC-*")}
            | {p.stem for p in DELTAS.glob("SEC-*.json")}
            | {Path(n).stem for n in ultima_accion() if n})


def ultima_accion() -> dict[str, str]:
    """Lo último que delta.py hizo con cada delta, según su historial."""
    historial = DELTAS / "historial.jsonl"
    estado: dict[str, str] = {}
    if historial.exists():
        for linea in historial.read_text(encoding="utf-8").splitlines():
            if linea.strip():
                try:
                    e = json.loads(linea)
                except json.JSONDecodeError:
                    continue
                estado[e.get("delta")] = e.get("accion")
    return estado


def siguiente_libre(prefijo: str, usados: set[str]) -> int:
    n = 0
    for i in usados:
        try:
            n = max(n, int(i.split("-")[1]))
        except (IndexError, ValueError):
            pass
    return n + 1


def ingerir(origen: Path, titulo: str | None, dry: bool) -> int:
    texto = origen.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    rev_antes, rev_despues, pendientes = revision_siguiente(manifest)
    if pendientes:
        print(f"aviso: hay deltas sin aplicar ({', '.join(pendientes)}); éste va detrás "
              f"({rev_antes} → {rev_despues}) y se aplica después de ellos")

    sec_id = siguiente_id("SEC", ids_de_secciones())

    # --- paso 1: registrar la sección -------------------------------------
    seccion = {
        "id": sec_id,
        "title": titulo or origen.stem,
        "received_at": date.today().isoformat(),
        "original_content_path": f"knowledge/corpus/sections/{sec_id}.md",
        "content_hash": sha256(texto.encode("utf-8")),
        "approximate_period": None,
        "topics": [],
        "source_ids": [],
        "schema_version": SCHEMA_VERSION,
        "dataset_revision": rev_despues,
        "record_status": "active",
    }

    # ¿Es un documento con capa de registro? Si lo es, las menciones salen de
    # ahí y NO del regex: el apéndice B y la tabla de afirmaciones ya traen las
    # etiquetas reales con su fila como localizador. Regexear un documento
    # estructurado produce prosa capturada —«Estudio», «Ninguna fuente»— que no
    # coincide con ninguna entidad declarada, y la ingestión termina en verde
    # habiendo versionado ruido.
    estructurado = None
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from parse_research import parse as parse_registro

        datos, conformidad = parse_registro(origen)
        if datos.get("claims"):
            estructurado = (datos, conformidad)
    except Exception:
        estructurado = None

    base_mention = siguiente_libre("MENTION", ids_en_uso("mentions.jsonl", "MENTION")
                                   | reservados_por_deltas("MENTION"))
    base_passage = siguiente_libre("PASSAGE", ids_de_pasajes())

    # --- paso 2: segmentar en pasajes -------------------------------------
    pasajes, menciones = [], []
    for i, (ini, fin, cuerpo) in enumerate(segmentar(texto), 1):
        pid = f"PASSAGE-{base_passage + i - 1:06d}"
        pasajes.append(
            {
                "id": pid,
                "section_id": sec_id,
                "ordinal": i,
                "text": cuerpo,
                "character_offsets": {"start": ini, "end": fin},
                "record_status": "active",
            }
        )
        # --- pasos 3 y 4: extraer y normalizar ----------------------------
        if estructurado is not None:
            continue  # las menciones salen de la capa de registro, más abajo
        for cand in extraer_menciones(cuerpo, ini):
            mid = f"MENTION-{base_mention + len(menciones):06d}"
            menciones.append(
                {
                    "id": mid,
                    "section_id": sec_id,
                    "passage_id": pid,
                    "original_text": cand["texto"],
                    "normalized_form": normalizar(cand["texto"]),
                    "mention_type": cand["tipo"],
                    "character_offsets": {"start": cand["start"], "end": cand["end"]},
                    # --- paso 5: NO se resuelve aquí. Es juicio humano.
                    "resolution": {"status": "pending", "target_ids": [], "reason": None},
                    "disposition": None,
                    "issue_ids": [],
                    "notes": [],
                    "record_status": "active",
                }
            )

    # --- pasos 3 y 4 sobre la capa de registro -----------------------------
    contraste: list[tuple[str, int, int]] = []
    if estructurado is not None:
        datos, conformidad = estructurado
        por_pasaje = {p["ordinal"]: p["id"] for p in pasajes}
        primero = por_pasaje.get(1, f"PASSAGE-{base_passage:06d}")

        # Una mención por etiqueta distinta del registro, con su fila como
        # localizador. La fila ES el pasaje: el prompt exige que cada afirmación
        # se pueda ubicar, y `C-0042` la ubica mejor que un offset de carácter.
        vistas: dict[str, dict] = {}
        for c in datos["claims"]:
            for campo, tipo in (("subject_label", "taxonomic_name"),
                                ("object_label", "taxonomic_name")):
                etq = (c.get(campo) or "").strip()
                if not etq or etq in ("n/a", "-"):
                    continue
                if etq not in vistas:
                    vistas[etq] = {"texto": etq, "tipo": tipo, "filas": []}
                vistas[etq]["filas"].append(c["local_id"])

        for e in datos.get("entities", []):
            etq = (e.get("etiqueta preferida") or "").strip()
            if etq and etq not in vistas:
                vistas[etq] = {"texto": etq, "tipo": "taxonomic_name", "filas": []}

        for n, (etq, info) in enumerate(sorted(vistas.items())):
            menciones.append({
                "id": f"MENTION-{base_mention + n:06d}",
                "section_id": sec_id,
                "passage_id": primero,
                "original_text": etq,
                "normalized_form": normalizar(etq),
                "mention_type": info["tipo"],
                "character_offsets": {"start": 0, "end": len(etq)},
                "resolution": {"status": "pending", "target_ids": [], "reason": None},
                "disposition": None,
                "issue_ids": [],
                "notes": [f"capa de registro, filas: {', '.join(info['filas'][:8])}"
                          + ("…" if len(info["filas"]) > 8 else "")] if info["filas"] else [],
                "record_status": "active",
            })

        # El contraste que puede parar una ingestión: declarado frente a extraído.
        declaradas = len({(e.get("etiqueta preferida") or "").strip()
                          for e in datos.get("entities", []) if e.get("etiqueta preferida")})
        extraidas = len(vistas)
        coinciden = len({(e.get("etiqueta preferida") or "").strip()
                         for e in datos.get("entities", [])} & set(vistas))
        contraste = [
            ("afirmaciones del registro", len(datos["claims"]), len(datos["claims"])),
            ("entidades del apéndice B", declaradas, coinciden),
            ("fuentes del apéndice A", len(datos["sources"]), len(datos["sources"])),
            ("eventos", len(datos["events"]), len(datos["events"])),
            ("hipótesis", len(datos["hypotheses"]), len(datos["hypotheses"])),
            ("fechas", len(datos["dates"]), len(datos["dates"])),
            ("magnitudes", len(datos["magnitudes"]), len(datos["magnitudes"])),
        ]

    # --- paso 10: auditar cobertura ---------------------------------------
    sin_destino = [m for m in menciones if m["disposition"] is None]

    # --- paso 13: generar delta -------------------------------------------
    operaciones = [
        {
            "operation": "ADD_RECORD",
            "file": "mentions.jsonl",
            "record_id": m["id"],
            "before": None,
            "after": m,
        }
        for m in menciones
    ]
    delta = {
        "section_id": sec_id,
        "schema_version": SCHEMA_VERSION,
        "dataset_revision_before": rev_antes,
        "dataset_revision_after": rev_despues,
        "operations": operaciones,
        "records_added": [m["id"] for m in menciones],
        "records_updated": [],
        "claims_added": [],
        "events_added": [],
        "hypotheses_added": [],
        "issues_added": [],
        "issues_resolved": [],
        "records_deprecated": [],
        "views_invalidated": [],
        "views_built": [],
        "validation_results": {},
    }

    # --- paso 14: informe humano (Apéndice F.1) ---------------------------
    tipos: dict[str, int] = {}
    for m in menciones:
        tipos[m["mention_type"]] = tipos.get(m["mention_type"], 0) + 1
    informe = [
        f"# Informe de ingestión · {sec_id}",
        "",
        f"**Origen:** `{origen}`  ",
        f"**Título:** {seccion['title']}  ",
        f"**Hash:** `{seccion['content_hash']}`  ",
        f"**Revisión:** {rev_antes} → {rev_despues}",
        "",
        "## Contraste con lo que el documento declara",
        "",
        "**El apartado que puede parar una ingestión.** Si una fila no cuadra, no",
        "se aplica el delta: se averigua por qué.",
        "",
    ] + ([
        "| Lo que declara el documento | Declarado | Ingerido |",
        "|---|---:|---:|",
    ] + [
        f"| {etq} | {dec} | {ing} |"
        + ("  ⚠" if dec and ing != dec else "")
        for etq, dec, ing in contraste
    ] + [""] if contraste else [
        "El documento **no trae capa de registro**: las menciones se han extraído",
        "del texto con heurísticas, que capturan prosa además de nombres. Revisa",
        "la lista de textos más frecuentes antes de aplicar nada.",
        "",
    ]) + [
        "## Cobertura y excepciones",
        "",
        f"- pasajes segmentados: **{len(pasajes)}**",
        f"- menciones extraídas: **{len(menciones)}**",
        f"- sin destino asignado: **{len(sin_destino)}**",
        "",
        "| Tipo de mención | Nº |",
        "|---|---:|",
        *[f"| `{t}` | {n} |" for t, n in sorted(tipos.items(), key=lambda x: -x[1])],
        "",
        "### Los veinte textos más extraídos",
        "",
        "Si aquí aparecen palabras de prosa —«Estudio», «Sostiene que»— la",
        "extracción capturó texto en vez de entidades y el delta es ruido.",
        "",
        "| Texto | Veces |",
        "|---|---:|",
        *[f"| `{t}` | {n} |" for t, n in sorted(
            {m["original_text"]: sum(1 for x in menciones if x["original_text"] == m["original_text"])
             for m in menciones[:400]}.items(), key=lambda x: -x[1])[:20]],
        "",
        "## Cuestiones pendientes",
        "",
        "Los pasos 5 a 9 del protocolo son **juicio humano** y no se han ejecutado:",
        "",
        "- **paso 5, resolución de identidad**: todas las menciones quedan en",
        "  `pending`. Decidir si dos menciones son la misma entidad no se",
        "  automatiza (§27.12), y la resolución debe ser conservadora: no se",
        "  fusionan entidades por parecido nominal.",
        "- **pasos 6 a 9**: afirmaciones, evidencia, eventos e hipótesis dependen",
        "  del paso 5.",
        "",
        "## Resumen del delta",
        "",
        f"- operaciones: **{len(operaciones)}**, todas `ADD_RECORD` sobre `mentions.jsonl`",
        f"- reversible con `python scripts/ingest/delta.py {sec_id}.json --revert`",
        "",
        "## Estado",
        "",
        f"**La sección NO está terminada.** §28.1 exige cobertura completa, y",
        f"quedan {len(sin_destino)} menciones sin destino.",
    ]

    print(f"{sec_id} · {len(pasajes)} pasajes · {len(menciones)} menciones")
    for t, n in sorted(tipos.items(), key=lambda x: -x[1]):
        print(f"    {t:20} {n}")
    if contraste:
        print("\n  contraste con lo declarado:")
        for etq, dec, ing in contraste:
            marca = "  <-- NO CUADRA" if dec and ing != dec else ""
            print(f"    {etq:28} declarado {dec:5}  ingerido {ing:5}{marca}")
    else:
        print("\n  el documento no trae capa de registro: menciones por heurística")
    print(f"\n  sin destino: {len(sin_destino)} — la cobertura del paso 10 no se cumple todavía")

    return escribir(sec_id, texto, seccion, pasajes, delta, informe, dry)


def escribir(sec_id: str, texto: str, seccion: dict, pasajes: list[dict], delta: dict,
             informe: list[str], dry: bool, extras: dict[Path, bytes] | None = None) -> int:
    """Escribe la sección, sus pasajes, el delta y el informe. No aplica nada."""
    if dry:
        print("\n(en seco: no se ha escrito nada)")
        return 0

    SECTIONS.mkdir(parents=True, exist_ok=True)
    PASSAGES.mkdir(parents=True, exist_ok=True)
    DELTAS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    # El original es inmutable (§6.1): se copia tal cual, en bytes, para que su
    # hash sea el de la fuente, y no se vuelve a tocar.
    (SECTIONS / f"{sec_id}.md").write_bytes(texto.encode("utf-8"))
    for ruta, contenido in (extras or {}).items():
        ruta.write_bytes(contenido)
    (SECTIONS / f"{sec_id}.json").write_text(
        json.dumps(seccion, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (PASSAGES / f"{sec_id}.json").write_text(
        json.dumps(pasajes, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (DELTAS / f"{sec_id}.json").write_text(
        json.dumps(delta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (REPORTS / f"{sec_id}.md").write_text("\n".join(informe) + "\n", encoding="utf-8")

    print(f"\n  sección   knowledge/corpus/sections/{sec_id}.md")
    for ruta in extras or {}:
        print(f"            {ruta.relative_to(ROOT)}")
    print(f"  pasajes   knowledge/corpus/passages/{sec_id}.json")
    print(f"  delta     knowledge/deltas/{sec_id}.json")
    print(f"  informe   generated/reports/{sec_id}.md")
    print(f"\n  el delta NO se ha aplicado. Revísalo y después:")
    print(f"    python scripts/ingest/delta.py {sec_id}.json")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Ingiere una sección de investigación (§17)")
    ap.add_argument("origen", help="fichero de texto o Markdown, o el directorio del corredor "
                                   "(o directorio@ref) con --seccion")
    ap.add_argument("--seccion", default=None, help="sección del corredor: 03, 11…")
    ap.add_argument("--congelacion", default=None,
                    help="manifiesto de congelación (por defecto, el activo de dataset.json)")
    ap.add_argument("--title", default=None)
    ap.add_argument("--dry-run", action="store_true", help="analizar sin escribir")
    args = ap.parse_args()

    directorio = args.origen.rpartition("@")[0] if "@" in args.origen else args.origen
    if Path(directorio).is_dir():
        # Un repositorio de CSV no es un documento: va por el modo corredor.
        if not args.seccion:
            print("ERROR el corredor se ingiere por secciones: añade --seccion NN")
            return 1
        import corredor
        return corredor.ingerir(args.origen, args.seccion,
                                Path(args.congelacion) if args.congelacion else None, args.dry_run)

    origen = Path(args.origen)
    if not origen.exists():
        print(f"ERROR no existe: {origen}")
        return 1
    return ingerir(origen, args.title, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
