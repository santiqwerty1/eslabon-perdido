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

SCHEMA_VERSION = "1.0.0"

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


def ingerir(origen: Path, titulo: str | None, dry: bool) -> int:
    texto = origen.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    rev_antes = manifest.get("dataset_revision", "REV-000000")
    rev_despues = f"REV-{int(rev_antes.split('-')[1]) + 1:06d}"

    existentes = {p.stem for p in SECTIONS.glob("SEC-*")}
    sec_id = siguiente_id("SEC", existentes)

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

    # --- paso 2: segmentar en pasajes -------------------------------------
    pasajes, menciones = [], []
    for i, (ini, fin, cuerpo) in enumerate(segmentar(texto), 1):
        pid = f"PASSAGE-{i:06d}"
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
        for cand in extraer_menciones(cuerpo, ini):
            mid = f"MENTION-{len(menciones) + 1:06d}"
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
    print(f"\n  sin destino: {len(sin_destino)} — la cobertura del paso 10 no se cumple todavía")

    if dry:
        print("\n(en seco: no se ha escrito nada)")
        return 0

    SECTIONS.mkdir(parents=True, exist_ok=True)
    PASSAGES.mkdir(parents=True, exist_ok=True)
    DELTAS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    # El original es inmutable (§6.1): se copia tal cual y no se vuelve a tocar.
    (SECTIONS / f"{sec_id}.md").write_text(texto, encoding="utf-8")
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
    print(f"  pasajes   knowledge/corpus/passages/{sec_id}.json")
    print(f"  delta     knowledge/deltas/{sec_id}.json")
    print(f"  informe   generated/reports/{sec_id}.md")
    print(f"\n  el delta NO se ha aplicado. Revísalo y después:")
    print(f"    python scripts/ingest/delta.py {sec_id}.json")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Ingiere una sección de investigación (§17)")
    ap.add_argument("origen", help="fichero de texto o Markdown a ingerir")
    ap.add_argument("--title", default=None)
    ap.add_argument("--dry-run", action="store_true", help="analizar sin escribir")
    args = ap.parse_args()

    origen = Path(args.origen)
    if not origen.exists():
        print(f"ERROR no existe: {origen}")
        return 1
    return ingerir(origen, args.title, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
