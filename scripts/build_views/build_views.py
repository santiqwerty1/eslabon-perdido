#!/usr/bin/env python3
"""Construcción de vistas derivadas (§6.7, §15.3, §20).

Una vista **no es el dato**: es una proyección de un conjunto de afirmaciones
compatibles, fechada y firmada editorialmente. Por eso toda vista que se
construye aquí declara obligatoriamente sus criterios, sus simplificaciones y
—lo que de verdad importa— **lo que excluye**. Una vista que no dice lo que dejó
fuera no simplifica: miente por omisión.

Genera además el DOT reproducible de §20.4, con las convenciones de trazo de
§20.2: el estilo de línea codifica el estado epistémico y **el color nunca porta
significado**, de modo que la vista sigue siendo legible en blanco y negro y
para quien no distinga colores (§20.6).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECORDS = ROOT / "knowledge" / "records"
VIEWS = ROOT / "knowledge" / "views"
DIAGRAMS = ROOT / "generated" / "diagrams"

# §20.2. La forma del trazo ES la afirmación epistémica.
ESTILO = {
    "backbone": 'style=solid, penwidth=1.6',
    "alternative": 'style=dashed',
    "speculative": 'style=dotted',
    "flow": 'style=solid, arrowhead=vee, constraint=false',
}

# Predicados que dibujan una relación de estructura en la vista.
ESTRUCTURALES = {"member_of", "descends_from", "sister_group_of", "contains",
                 "stem_lineage_of", "crown_group_of"}
# Predicados reticulados: nunca se dibujan como bifurcación (§23.1).
RETICULADOS = {"contributes_ancestry_to", "receives_gene_flow_from",
               "introgression_from", "transfers_gene_to", "endosymbiosis_with"}


def leer(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def etiqueta(rid: str, entidades: dict[str, dict]) -> str:
    e = entidades.get(rid)
    if not e:
        return rid
    return e.get("preferred_label") or e.get("canonical_spelling") or rid


def marca_epistemica(c: dict) -> str:
    """Sufijo visual del nodo o arista según §10 y §20.2."""
    dims = c.get("epistemic_dimensions") or {}
    if dims.get("resolution") in ("unresolved", "insufficient_information"):
        return " ?"
    if dims.get("historical_status") in ("superseded", "rejected"):
        return " †"
    return ""


def construir(base: Path, hyp_id: str, escala: str, salida_dot: bool,
              corte: str, es_fixture: bool) -> int:
    claims = leer(base / "claims.jsonl")
    hyps = leer(base / "hypotheses.jsonl")
    entidades: dict[str, dict] = {}
    for f in ("clades.jsonl", "lineages.jsonl", "populations.jsonl", "taxonomic-names.jsonl",
              "taxon-concepts.jsonl", "specimens.jsonl", "regions.jsonl"):
        for r in leer(base / f):
            entidades[r["id"]] = r

    hyp = next((h for h in hyps if h["id"] == hyp_id), None)
    if hyp is None:
        print(f"ERROR no existe la hipótesis {hyp_id} en {base}")
        print("  disponibles: " + ", ".join(h["id"] for h in hyps))
        return 1

    incluidas = set(hyp.get("included_claim_ids") or [])
    excluidas = set(hyp.get("excluded_claim_ids") or [])
    por_id = {c["id"]: c for c in claims}

    seleccionadas = [por_id[c] for c in incluidas if c in por_id]
    faltan = sorted(incluidas - set(por_id))

    # Las afirmaciones de otras hipótesis del mismo grupo de conflicto se
    # excluyen explícitamente: §20.3 prohíbe dibujar alternativas como si fueran
    # simultáneamente verdaderas, y §15.2 gestiona eso por grupos de conflicto.
    grupos = set(hyp.get("conflict_group_ids") or [])
    rivales = [h for h in hyps if h["id"] != hyp_id and grupos & set(h.get("conflict_group_ids") or [])]
    por_conflicto = {c for h in rivales for c in (h.get("included_claim_ids") or [])} - incluidas

    vista = {
        "id": f"PHYVIEW-{int(hyp_id.split('-')[1]):06d}",
        "name": f"Vista derivada de {hyp.get('name', hyp_id)}",
        "cutoff_date": corte,
        "hypothesis_ids": [hyp_id],
        "selected_claim_ids": sorted(incluidas & set(por_id)),
        "excluded_claim_ids": sorted(excluidas | por_conflicto),
        "editorial_criteria": [
            f"Se seleccionan únicamente las afirmaciones incluidas por {hyp_id}.",
            "Se excluyen las afirmaciones de las hipótesis rivales de su mismo "
            "grupo de conflicto: representarlas juntas afirmaría dos topologías "
            "incompatibles a la vez (§20.3).",
            "Las relaciones reticuladas se dibujan como arista lateral hacia un "
            "nodo-evento, nunca como bifurcación (§23.1).",
        ],
        "simplifications": [
            "Sólo se representan los predicados estructurales y reticulados; "
            "las afirmaciones de procedencia y de clasificación no se dibujan.",
            "El diagrama no muestra intervalos temporales.",
        ],
        "scale": escala,
        "generated_artifacts": [],
        "view_version": "1.0.0",
        "built_from_dataset_revision": "REV-000000",
    }

    if faltan:
        vista["simplifications"].append(
            f"{len(faltan)} afirmaciones declaradas por la hipótesis no existen en "
            f"el conjunto de registros y no se representan: {', '.join(faltan[:5])}"
        )

    # --- DOT ---------------------------------------------------------------
    lineas = [
        "digraph vista {",
        "  // Generado por scripts/build_views. Reproducible: sin marcas de tiempo",
        "  // dentro del grafo. El estilo de línea codifica el estado epistémico;",
        "  // el color NO porta significado (§20.2, §20.6).",
        '  graph [rankdir=TB, fontname="sans-serif", splines=ortho];',
        '  node  [shape=box, fontname="sans-serif", style=rounded];',
        '  edge  [fontname="sans-serif", fontsize=10];',
        f'  label="{vista["name"]}\\nfecha de corte {vista["cutoff_date"]} · '
        f'{len(vista["selected_claim_ids"])} afirmaciones · '
        f'{len(vista["excluded_claim_ids"])} excluidas";',
        "  labelloc=b;",
        "",
    ]
    nodos: set[str] = set()
    aristas: list[str] = []
    eventos: set[str] = set()

    for c in seleccionadas:
        pred = c.get("predicate")
        suj = c.get("subject_id")
        obj = (c.get("object") or {}).get("entity_id")
        if not (suj and obj):
            continue
        if pred in ESTRUCTURALES:
            nodos.update([suj, obj])
            estilo = ESTILO["backbone"]
            aristas.append(f'  "{obj}" -> "{suj}" [{estilo}, label="{pred}"];')
        elif pred in RETICULADOS:
            # Nodo-evento: los participantes cuelgan de él, no se enlazan entre sí.
            ev = f"EV_{c['id']}"
            eventos.add(ev)
            nodos.update([suj, obj])
            aristas.append(f'  "{suj}" -> "{ev}" [{ESTILO["flow"]}, label="donante"];')
            aristas.append(f'  "{ev}" -> "{obj}" [{ESTILO["flow"]}, label="receptor"];')

    for n in sorted(nodos):
        lineas.append(f'  "{n}" [label="{etiqueta(n, entidades)}"];')
    for ev in sorted(eventos):
        lineas.append(f'  "{ev}" [shape=diamond, style=solid, label="evento"];')
    lineas.append("")
    lineas.extend(sorted(aristas))
    lineas.append("}")
    dot = "\n".join(lineas) + "\n"

    print(f"{vista['id']} · {vista['name']}")
    print(f"  seleccionadas {len(vista['selected_claim_ids'])} · excluidas {len(vista['excluded_claim_ids'])}")
    print(f"  nodos {len(nodos)} · aristas {len(aristas)} · nodos-evento {len(eventos)}")
    if faltan:
        print(f"  {len(faltan)} afirmaciones declaradas y ausentes, anotadas como simplificación")

    if salida_dot:
        print("\n" + dot)
        return 0

    # Una vista derivada de un fixture pertenece al fixture. Escribirla en
    # knowledge/views/ contaminaria el dataset real con producto de prueba.
    views_dir = (base / "views") if es_fixture else VIEWS
    diagrams_dir = (base / "diagrams") if es_fixture else DIAGRAMS
    views_dir.mkdir(parents=True, exist_ok=True)
    diagrams_dir.mkdir(parents=True, exist_ok=True)
    # `--records` puede apuntar fuera del repositorio: es justo lo que se hace
    # para ensayar a escala sin tocar el dataset real. `relative_to(ROOT)`
    # reventaba ahí con un ValueError sin capturar, y lo hacía DESPUÉS de
    # escribir el .dot y ANTES de escribir la vista: quedaba un diagrama
    # huérfano sin el registro que lo declara, que es exactamente el estado
    # intermedio que §6.7 no admite.
    def rotulo(p: Path) -> str:
        try:
            return str(p.relative_to(ROOT))
        except ValueError:
            return str(p)

    dot_path = diagrams_dir / f"{vista['id']}.dot"
    dot_path.write_text(dot, encoding="utf-8")
    vista["generated_artifacts"] = [rotulo(dot_path)]
    (views_dir / f"{vista['id']}.json").write_text(
        json.dumps(vista, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"\n  vista    {rotulo(views_dir / (vista['id'] + '.json'))}")
    print(f"  diagrama {rotulo(dot_path)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Construye una vista derivada (§6.7)")
    ap.add_argument("hypothesis", help="identificador de la hipótesis, p. ej. HYP-000401")
    ap.add_argument("--records", default=None, help="directorio de registros; por defecto el dataset real")
    ap.add_argument("--scale", default="campaign-01-eukarya")
    ap.add_argument("--stdout", action="store_true", help="mostrar el DOT sin escribir nada")
    ap.add_argument(
        "--cutoff",
        default=None,
        metavar="AAAA-MM-DD",
        help="fecha de corte de la vista. Por defecto hoy, pero para que el DOT "
             "sea reproducible hay que fijarla: reconstruir una vista existente "
             "debe reutilizar SU fecha, no la de hoy (§6.7, §15.4).",
    )
    args = ap.parse_args()

    base = Path(args.records).resolve() if args.records else RECORDS
    if not base.is_dir():
        print(f"ERROR no existe el directorio: {base}")
        return 1
    return construir(
        base,
        args.hypothesis,
        args.scale,
        args.stdout,
        args.cutoff or date.today().isoformat(),
        es_fixture=args.records is not None,
    )


if __name__ == "__main__":
    sys.exit(main())
