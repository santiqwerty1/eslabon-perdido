#!/usr/bin/env python3
"""Relojes y rocas: la vista temporal de lo convertido (§6.7, §20).

Pone en un mismo eje, en millones de años, lo que dicen los relojes
moleculares y lo que registran las rocas. Es una vista derivada: no escribe en
`knowledge/`, lee los registros activos y deja la página en
`generated/views/`.

**Qué va en el eje.** Cada afirmación `dated_to` es una marca. Su datación
decide el carril: la que modela un método (`determination: modelled`) es un
reloj; la observada o inferida del registro es una roca. Las dataciones de un
mismo evento conviven sin promediarse (ISSUE-000040).

**Qué no va.** Toda afirmación activa queda en uno de cuatro sitios, y la
página dice cuál:

- en el eje, como marca;
- en «por qué no coinciden», si habla de un método o de lo que condiciona una
  fecha;
- en la ficha de una marca, si habla de la entidad que la marca data;
- fuera, con su motivo.

Una vista que no dice lo que dejó fuera miente por omisión (§6.7). Las
hipótesis rivales sobre un fósil se leen en su ficha, lado a lado; nunca se
dibujan juntas en el eje como si fueran verdad a la vez (§20.3).

**Cómo se codifica.** La forma dice qué es (barra de reloj, rombo de fósil,
círculo de biomarcador, corchete de roca datada) y el relleno dice la fuerza
de la evidencia: lleno, rayado, hueco o con borde discontinuo. El color nunca
porta significado (§20.2, §20.6); el de la escala de tiempo es el de la carta
estratigráfica internacional, que sólo acompaña a su rótulo.

La salida es reproducible: la fecha de corte es la del corpus congelado, no la
de hoy, y dos ejecuciones sobre los mismos registros dan los mismos bytes.
"""

from __future__ import annotations

import argparse
import html
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECORDS = ROOT / "knowledge" / "records"
SALIDA = ROOT / "generated" / "views"
PLANTILLA = Path(__file__).with_name("cronologia.plantilla.html")

# Carta cronoestratigráfica internacional (ICS v2023/09): límites en Ma y el
# color oficial de cada unidad. Sitúa las dataciones que el corpus da como
# intervalo con nombre («Mesoproterozoico») y dibuja la escala del eje.
ICS_FUENTE = "Carta cronoestratigráfica internacional, ICS v2023/09"
ERAS = [
    ("Arcaico", 4031, 2500, "#F0047F"),
    ("Paleoproterozoico", 2500, 1600, "#F74370"),
    ("Mesoproterozoico", 1600, 1000, "#FDB462"),
    ("Neoproterozoico", 1000, 538.8, "#FEB342"),
    ("Paleozoico", 538.8, 251.902, "#99C08D"),
]
PERIODOS = [
    ("Sideriano", 2500, 2300, "#F74F7C"),
    ("Riásico", 2300, 2050, "#F75B89"),
    ("Orosírico", 2050, 1800, "#F76898"),
    ("Estatérico", 1800, 1600, "#F875A7"),
    ("Calímico", 1600, 1400, "#FDC07A"),
    ("Ectásico", 1400, 1200, "#F3CC8A"),
    ("Esténico", 1200, 1000, "#FED99A"),
    ("Tónico", 1000, 720, "#FEBF4E"),
    ("Criogénico", 720, 635, "#FECC5C"),
    ("Ediacárico", 635, 538.8, "#FED96A"),
    ("Cámbrico", 538.8, 485.4, "#7FA056"),
]
INTERVALOS = {n.lower(): (a, b) for n, a, b, _ in ERAS + PERIODOS}

# Predicados que explican por qué relojes y rocas no coinciden: hablan de
# métodos, de sus supuestos y de lo que calibra o limita una fecha.
METODO = {"limits", "depends_on", "provides_bound", "assumes", "calibrates",
          "incompatible_with", "may_bias"}
# Los que dibujarían un árbol (los mismos que build_views.py).
ESTRUCTURALES = {"member_of", "descends_from", "sister_group_of", "contains",
                 "stem_lineage_of", "crown_group_of"}

VERBOS = {
    "dated_to": "se data en",
    "shows_evidence_of": "muestra indicios de",
    "assigned_to": "se asigna a",
    "classified_as_by": "se clasifica como",
    "limits": "limita",
    "depends_on": "depende de",
    "provides_bound": "aporta",
    "assumes": "supone",
    "calibrates": "calibra",
    "incompatible_with": "es incompatible con",
    "may_bias": "puede sesgar",
    "biomarker_of": "es biomarcador de",
    "preys_on": "depreda a",
    "stem_lineage_of": "es linaje troncal de",
    "occurs_in": "se encuentra en",
    "member_of": "es miembro de",
    "sister_group_of": "es grupo hermano de",
}

FAMILIAS = {
    "claims": "claims.jsonl", "evidence": "evidence.jsonl", "sources": "sources.jsonl",
    "hypotheses": "hypotheses.jsonl", "issues": "issues.jsonl", "time": "temporal-expressions.jsonl",
    "results": "results.jsonl", "analyses": "analyses.jsonl", "occurrences": "occurrences.jsonl",
    "names": "taxonomic-names.jsonl", "concepts": "taxon-concepts.jsonl",
}
ENTIDADES = ("events.jsonl", "clades.jsonl", "lineages.jsonl", "populations.jsonl",
             "specimens.jsonl", "sites.jsonl", "molecules.jsonl", "methods.jsonl",
             "traits.jsonl", "regions.jsonl", "occurrences.jsonl", "taxon-concepts.jsonl")


def leer(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def activos(path: Path) -> dict[str, dict]:
    return {r["id"]: r for r in leer(path) if r.get("record_status", "active") == "active"}


def cita_corta(src: dict | None) -> str:
    """«Douzery et al. 2004» a partir de la ficha de una fuente."""
    if not src:
        return "fuente sin ficha"
    autores = src.get("authors") or []
    primero = (autores[0] if autores else src.get("citation_key") or "?").split(",")[0].strip()
    if len(autores) > 2 or (autores and "et al" in autores[0]):
        nombre = f"{primero} et al."
    elif len(autores) == 2:
        nombre = f"{primero} y {autores[1].split(',')[0].strip()}"
    else:
        nombre = primero
    return f"{nombre} {src.get('year') or 's. f.'}".strip()


class Registros:
    """Los registros activos que la vista necesita, con sus etiquetas."""

    def __init__(self, base: Path, pasajes: Path):
        f = {k: activos(base / v) for k, v in FAMILIAS.items()}
        self.claims, self.evidence, self.sources = f["claims"], f["evidence"], f["sources"]
        self.hypotheses, self.issues, self.time = f["hypotheses"], f["issues"], f["time"]
        self.results, self.analyses, self.occurrences = f["results"], f["analyses"], f["occurrences"]
        self.names, self.concepts = f["names"], f["concepts"]
        self.entidades: dict[str, dict] = {}
        for nombre in ENTIDADES:
            self.entidades.update(activos(base / nombre))
        self.pasajes: dict[str, dict] = {}
        for p in sorted(pasajes.glob("*.json")) if pasajes.is_dir() else []:
            for x in json.loads(p.read_text(encoding="utf-8")):
                self.pasajes[x["id"]] = x

    def etiqueta(self, rid: str | None, larga: bool = False) -> str:
        if not rid:
            return "—"
        e = self.entidades.get(rid)
        if e is None:
            return rid
        if rid.startswith("TAXCONCEPT-"):
            nombre = (self.names.get(e.get("name_id") or "") or {}).get("canonical_spelling") or rid
            if larga and e.get("according_to_source_id"):
                return f"{nombre} sensu {cita_corta(self.sources.get(e['according_to_source_id']))}"
            return nombre
        if rid.startswith("OCC-"):
            return self.etiqueta(e.get("entity_id"), larga)
        return e.get("preferred_label") or e.get("label") or e.get("name") or rid

    def objeto(self, c: dict) -> str:
        o = c.get("object") or {}
        if o.get("entity_id"):
            return self.etiqueta(o["entity_id"])
        if o.get("temporal_expression_id"):
            t = self.time.get(o["temporal_expression_id"]) or {}
            return (t.get("interval") or {}).get("original_expression") or o["temporal_expression_id"]
        if o.get("category"):
            return f"«{o['category']}»"
        if "value" in o:
            return f"{o['value']} {o.get('unit') or ''}".strip()
        return "—"

    def resumen(self, c: dict) -> str:
        verbo = VERBOS.get(c["predicate"], c["predicate"])
        texto = f"{self.etiqueta(c['subject_id'])} {verbo} {self.objeto(c)}"
        return texto[:1].upper() + texto[1:]


def intervalo(t: dict) -> dict:
    """Normaliza una datación: desde (más antiguo) y hasta (más joven), en Ma.

    `forma` dice cómo se dibuja: `intervalo`, `punto`, `minimo` (más antiguo
    que `hasta`, sin límite viejo), `desde` (de `desde` hasta hoy) o
    `geologico` (un intervalo con nombre situado con la carta ICS).
    """
    iv = t.get("interval") or {}
    viejo, joven = iv.get("oldest_bound"), iv.get("youngest_bound")
    if iv.get("unit") == "geological_interval":
        nombre = (iv.get("geological_interval") or iv.get("original_expression") or "").strip()
        limites = INTERVALOS.get(nombre.lower())
        if limites is None:
            return {"forma": "sin_situar", "nombre": nombre}
        return {"forma": "geologico", "desde": limites[0], "hasta": limites[1], "nombre": nombre}
    escala = {"million_years": 1, "thousand_years": 1e-3, "years": 1e-6}.get(iv.get("unit"))
    if escala is None or (viejo is None and joven is None):
        return {"forma": "sin_situar", "nombre": iv.get("original_expression") or ""}
    viejo = viejo * escala if viejo is not None else None
    joven = joven * escala if joven is not None else None
    if viejo is None:
        return {"forma": "minimo", "desde": None, "hasta": joven}
    if joven is None:
        return {"forma": "desde", "desde": viejo, "hasta": None}
    if viejo == joven:
        return {"forma": "punto", "desde": viejo, "hasta": joven}
    return {"forma": "intervalo", "desde": viejo, "hasta": joven}


def clase_de(r: Registros, c: dict, t: dict) -> tuple[str, str]:
    """(carril, clase) de una marca: reloj o roca, y qué tipo de roca."""
    if t.get("determination") == "modelled":
        return "reloj", "reloj"
    sujeto = c["subject_id"]
    if sujeto.startswith("OCC-"):
        ent = (r.occurrences.get(sujeto) or {}).get("entity_id") or ""
        return "roca", ("biomarcador" if ent.startswith("MOL-") else "fosil")
    if sujeto.startswith("SITE-"):
        return "roca", "unidad"
    return "roca", "registro"


def construir(base: Path = RECORDS, raiz: Path = ROOT) -> dict:
    """Los datos de la vista: marcas, fichas y la cuenta de lo que queda fuera."""
    r = Registros(base, raiz / "knowledge" / "corpus" / "passages")
    manifiesto = json.loads((raiz / "knowledge" / "corpus" / "manifests" / "dataset.json")
                            .read_text(encoding="utf-8"))
    congelada = manifiesto.get("corpus_freeze") or {}
    corpus = {}
    if congelada.get("path") and (raiz / congelada["path"]).exists():
        corpus = json.loads((raiz / congelada["path"]).read_text(encoding="utf-8"))

    # --- marcas ---------------------------------------------------------------
    marcas: list[dict] = []
    sin_situar: list[str] = []
    for c in sorted(r.claims.values(), key=lambda x: x["id"]):
        if c["predicate"] != "dated_to":
            continue
        t = r.time.get((c.get("object") or {}).get("temporal_expression_id") or "")
        if t is None:
            sin_situar.append(c["id"])
            continue
        iv = intervalo(t)
        if iv["forma"] == "sin_situar":
            sin_situar.append(c["id"])
            continue
        carril, clase = clase_de(r, c, t)
        dims = c.get("epistemic_dimensions") or {}
        fuentes = (c.get("provenance") or {}).get("source_ids") or []
        sujeto = c["subject_id"]
        entidad = (r.occurrences.get(sujeto) or {}).get("entity_id") if sujeto.startswith("OCC-") else sujeto
        marcas.append({
            "claim": c["id"], "time": t["id"], "carril": carril, "clase": clase,
            "sujeto": sujeto, "entidad": entidad,
            "etiqueta": r.etiqueta(sujeto),
            "cursiva": bool(entidad and entidad.startswith("TAXCONCEPT-")),
            "cita": cita_corta(r.sources.get(fuentes[0])) if fuentes else "sin fuente",
            "n_fuentes": len(fuentes),
            "original": (t.get("interval") or {}).get("original_expression") or "",
            "fuerza": dims.get("evidence_strength") or "unknown",
            "no_resuelta": dims.get("resolution") in ("unresolved", "insufficient_information"),
            "superada": dims.get("historical_status") in ("superseded", "rejected", "historical"),
            **iv,
        })

    marcadas = {m["claim"] for m in marcas}
    # Una afirmación va a la ficha de una marca si su sujeto es lo que la marca
    # data o algo con lo que eso se relaciona directamente (el linaje del que un
    # biomarcador es indicio), o si su objeto es un fósil, un biomarcador o una
    # roca que la marca data (quien perforó unos microfósiles). Un clado o un
    # evento como objeto no basta: por Eukaryota se llegaría a todo.
    directas: dict[str, set[str]] = {}
    for m in marcas:
        for e in {m["sujeto"], m["entidad"]} - {None}:
            directas.setdefault(e, set()).add(m["claim"])
    vecinas = {e: set(v) for e, v in directas.items()}
    for c in r.claims.values():
        obj = (c.get("object") or {}).get("entity_id")
        if obj and c["subject_id"] in directas:
            vecinas.setdefault(obj, set()).update(directas[c["subject_id"]])
    con_marca = {e: sorted(v) for e, v in directas.items()}

    # --- el reparto de cada afirmación activa ---------------------------------
    metodo, en_ficha, fuera = [], {}, []
    for c in sorted(r.claims.values(), key=lambda x: x["id"]):
        if c["id"] in marcadas:
            continue
        if c["id"] in sin_situar:
            fuera.append((c["id"], "Su datación no se puede situar en el eje."))
            continue
        if c["predicate"] in METODO:
            metodo.append(c["id"])
            continue
        obj = (c.get("object") or {}).get("entity_id")
        por_objeto = directas.get(obj, set()) if obj and not obj.startswith(("CLADE-", "EVENT-")) else set()
        destinos = sorted(vecinas.get(c["subject_id"], set()) | por_objeto)
        if destinos:
            en_ficha[c["id"]] = destinos
        else:
            fuera.append((c["id"], "Habla de algo que no tiene fecha en las secciones convertidas."))

    # --- eventos de los relojes, con su dispersión ------------------------------
    eventos: dict[str, dict] = {}
    for m in marcas:
        if m["carril"] != "reloj":
            continue
        ev = eventos.setdefault(m["sujeto"], {"id": m["sujeto"], "etiqueta": m["etiqueta"], "claims": []})
        ev["claims"].append(m["claim"])
    for ev in eventos.values():
        cotas = [x for m in marcas if m["claim"] in ev["claims"] for x in (m["desde"], m["hasta"]) if x is not None]
        ev["rango"] = [max(cotas), min(cotas)] if cotas else None
        ev["issues"] = sorted(i for i, x in r.issues.items()
                              if ev["id"] in (x.get("affects") or {}).get("record_ids", []))

    fichas = {cid: ficha(r, cid, con_marca, en_ficha) for cid in sorted(r.claims)}

    # Las hipótesis, con lo que dicen de sus rivales y si alguna de sus
    # afirmaciones llega al eje, directamente o por la ficha de una marca.
    hipotesis = []
    for h in sorted(r.hypotheses):
        x = r.hypotheses[h]
        incluidas = x.get("included_claim_ids") or []
        llegan = sorted({m for c in incluidas for m in ([c] if c in marcadas else en_ficha.get(c, []))})
        hipotesis.append({"id": h, "nombre": x.get("name"), "claims": incluidas,
                          "alternativas": x.get("alternative_hypothesis_ids") or [],
                          "grupos": x.get("conflict_group_ids") or [], "marcas": llegan})
    estructurales = sorted(c["id"] for c in r.claims.values() if c["predicate"] in ESTRUCTURALES)
    secciones = sorted({s for c in r.claims.values() for s in (c.get("provenance") or {}).get("section_ids", [])})

    datos = {
        "vista": {
            "nombre": "Relojes y rocas",
            "fecha_de_corte": corpus.get("cutoff"),
            "corpus": {"version": corpus.get("version") or congelada.get("version"),
                       "commit": (congelada.get("commit") or "")[:7],
                       "congelado": corpus.get("frozen_on"), "decision": congelada.get("decision")},
            "revision": manifiesto.get("dataset_revision"),
            "snapshot": manifiesto.get("snapshot_id"),
            "secciones": secciones,
            "cuenta": {"activas": len(r.claims), "en_el_eje": len(marcas), "de_metodo": len(metodo),
                       "en_fichas": len(en_ficha), "fuera": len(fuera), "estructurales": len(estructurales)},
            "criterios": [
                "Cada afirmación dated_to activa es una marca; nada se promedia ni se funde.",
                "Carril por la datación: la modelada por un método es un reloj; la observada o inferida "
                "del registro, una roca.",
                "Las hipótesis rivales sobre un fósil se leen en su ficha, lado a lado, y no se dibujan "
                "en el eje (§20.3).",
                "El relleno de una marca dice la fuerza de la evidencia de su afirmación; la forma, qué es. "
                "El color no porta significado (§20.6).",
            ],
            "simplificaciones": [
                f"Las dataciones con intervalo geológico con nombre se sitúan con los límites de la {ICS_FUENTE}.",
                "El eje se recorta a las unidades de la carta que contienen las fechas numéricas; lo que "
                "sigue más allá se marca con una flecha.",
                "Una fecha aproximada sin intervalo («aproximadamente 1.6 Ga») se dibuja como un punto.",
            ],
            "sin_topologia": (
                f"De {len(r.claims)} afirmaciones activas, {len(estructurales)} "
                f"{'es estructural' if len(estructurales) == 1 else 'son estructurales'}: "
                "la vista no puede dibujar un árbol."
            ),
        },
        "escala": {"eras": ERAS, "periodos": PERIODOS, "fuente": ICS_FUENTE},
        "marcas": marcas,
        "eventos": sorted(eventos.values(), key=lambda e: (-(e["rango"] or [0])[0], e["id"])),
        "metodo": metodo,
        "en_fichas": sorted(en_ficha),
        "hipotesis": hipotesis,
        "fuera": [{"claim": cid, "motivo": motivo} for cid, motivo in fuera],
        "fichas": fichas,
    }
    return datos


def ficha(r: Registros, cid: str, con_marca: dict[str, list[str]], en_ficha: dict[str, list[str]]) -> dict:
    """Todo lo que lleva de una afirmación a su evidencia, su fuente y su pasaje."""
    c = r.claims[cid]
    prov = c.get("provenance") or {}

    def evid(eid: str) -> dict:
        e = r.evidence.get(eid) or {}
        resultados = [{"id": x, "descripcion": (r.results.get(x) or {}).get("description"),
                       "valor": " ".join(str(v) for v in ((r.results.get(x) or {}).get("value"),
                                                          (r.results.get(x) or {}).get("unit")) if v)}
                      for x in e.get("result_ids") or []]
        return {"id": eid, "tipo": e.get("evidence_type"), "descripcion": e.get("description"),
                "localizador": e.get("locator"), "fuente": e.get("source_id"),
                "cita": cita_corta(r.sources.get(e.get("source_id") or "")), "resultados": resultados}

    evid_ids = c.get("evidence_ids") or []
    contra_ids = c.get("counterevidence_ids") or []
    fuentes = sorted(set(prov.get("source_ids") or [])
                     | {(r.evidence.get(e) or {}).get("source_id") for e in evid_ids + contra_ids} - {None})

    sujeto = c["subject_id"]
    entidad = (r.occurrences.get(sujeto) or {}).get("entity_id") if sujeto.startswith("OCC-") else sujeto
    implicadas = {sujeto, entidad, (c.get("object") or {}).get("entity_id")} - {None}
    # Lo que también se afirma de la entidad que esta marca data.
    relacionadas = sorted(x for x, destinos in en_ficha.items() if cid in destinos)
    relacionadas += sorted(x for x in r.claims if x != cid and x not in relacionadas
                           and r.claims[x]["predicate"] in METODO
                           and {r.claims[x]["subject_id"], (r.claims[x].get("object") or {}).get("entity_id")}
                           & ({entidad} - {None}))
    ids_hipotesis = sorted(h for h, x in r.hypotheses.items()
                           if cid in (x.get("included_claim_ids") or [])
                           or any(r.claims.get(y, {}).get("subject_id") in implicadas
                                  for y in x.get("included_claim_ids") or []))
    hipotesis = []
    for h in ids_hipotesis:
        x = r.hypotheses[h]
        hipotesis.append({
            "id": h, "nombre": x.get("name"), "descripcion": x.get("description"),
            "supuestos": x.get("assumptions") or [],
            "a_favor": [cita_corta(r.sources.get(s)) for s in x.get("supporting_source_ids") or []],
            "en_contra": [cita_corta(r.sources.get(s)) for s in x.get("opposing_source_ids") or []],
            "alternativas": x.get("alternative_hypothesis_ids") or [],
            "fuerza": (x.get("epistemic_dimensions") or {}).get("evidence_strength"),
            "notas": x.get("notes") or [],
        })
    issues = sorted(i for i, x in r.issues.items()
                    if cid in (x.get("affects") or {}).get("claim_ids", [])
                    or implicadas & set((x.get("affects") or {}).get("record_ids", [])))

    t = r.time.get((c.get("object") or {}).get("temporal_expression_id") or "")
    datacion = None
    if t:
        iv = t.get("interval") or {}
        datacion = {"id": t["id"], "tipo": t.get("temporal_type"), "original": iv.get("original_expression"),
                    "metodo": t.get("method"), "tipo_de_metodo": t.get("method_type"),
                    "calibracion": (t.get("calibration") or {}).get("system"),
                    "determinacion": t.get("determination"),
                    "incertidumbre": (t.get("uncertainty") or {}).get("description"),
                    "notas": t.get("notes") or [], **intervalo(t)}

    return {
        "id": cid, "resumen": r.resumen(c), "predicado": c["predicate"],
        "sujeto": {"id": sujeto, "etiqueta": r.etiqueta(sujeto, larga=True)},
        "objeto": r.objeto(c), "notas": c.get("notes") or [],
        "dimensiones": c.get("epistemic_dimensions") or {},
        "datacion": datacion,
        "evidencia": [evid(e) for e in evid_ids],
        "contraevidencia": [evid(e) for e in contra_ids],
        "fuentes": [{"id": s, "clave": (r.sources.get(s) or {}).get("citation_key"),
                     "cita": cita_corta(r.sources.get(s)),
                     "titulo": (r.sources.get(s) or {}).get("title"),
                     "revista": (r.sources.get(s) or {}).get("container"),
                     "doi": (r.sources.get(s) or {}).get("doi"),
                     "verificacion": (r.sources.get(s) or {}).get("verification_status")}
                    for s in fuentes],
        "pasajes": [{"id": p, "seccion": (r.pasajes.get(p) or {}).get("section_id"),
                     "texto": (r.pasajes.get(p) or {}).get("text")}
                    for p in prov.get("passage_ids") or []],
        "hipotesis": hipotesis,
        "relacionadas": [{"id": x, "resumen": r.resumen(r.claims[x])} for x in relacionadas],
        "cuestiones": [{"id": i, "titulo": r.issues[i].get("title"),
                        "descripcion": r.issues[i].get("description")} for i in issues],
        "marcas": con_marca.get(sujeto, []) if c["predicate"] != "dated_to" else [cid],
    }


# --- la página -----------------------------------------------------------------

ANCHO, IZQ, DER = 1000, 262, 972
FILA, CABECERA = 24, 20


def svg(datos: dict) -> str:
    """El eje en SVG, con una marca por afirmación. Estático: se lee sin script."""
    marcas = datos["marcas"]
    numericas = [x for m in marcas if m["forma"] != "geologico" for x in (m["desde"], m["hasta"]) if x is not None]
    bordes = sorted({b for _, a, b, _ in ERAS + PERIODOS} | {a for _, a, _, _ in ERAS + PERIODOS})
    viejo = min((b for b in bordes if b >= max(numericas)), default=max(numericas))
    joven = max((b for b in bordes if b <= min(numericas)), default=min(numericas))

    def x(ma: float) -> float:
        return round(IZQ + (viejo - ma) / (viejo - joven) * (DER - IZQ), 1)

    def recorte(ma: float | None, por_defecto: float) -> float:
        return por_defecto if ma is None else max(joven, min(viejo, ma))

    esc = html.escape
    filas: list[str] = []
    y = 0

    # Escala: eras y periodos con su color ICS, recortados al eje.
    escala = ['<g class="escala" aria-hidden="true">']
    for fila, unidades, alto in ((0, ERAS, 18), (18, PERIODOS, 16)):
        for nombre, a, b, color in unidades:
            if b >= viejo or a <= joven:
                continue
            xa, xb = x(min(a, viejo)), x(max(b, joven))
            escala.append(f'<rect x="{xa}" y="{fila}" width="{round(xb - xa, 1)}" height="{alto}" '
                          f'fill="{color}" class="ics"/>')
            if xb - xa > len(nombre) * 5.6 + 8:
                escala.append(f'<text x="{round((xa + xb) / 2, 1)}" y="{fila + alto - 5}" '
                              f'class="ics-rotulo" text-anchor="middle">{esc(nombre)}</text>')
    marcas_ma = [m for m in range(int(math.ceil(joven / 100) * 100), int(viejo) + 1, 100)]
    for ma in marcas_ma:
        escala.append(f'<line x1="{x(ma)}" x2="{x(ma)}" y1="36" y2="42" class="tic"/>')
        if ma % 250 == 0 or ma == marcas_ma[-1] or ma == marcas_ma[0]:
            escala.append(f'<text x="{x(ma)}" y="54" class="tic-rotulo" text-anchor="middle">{ma}</text>')
    escala.append(f'<text x="{IZQ - 26}" y="54" class="tic-rotulo" text-anchor="end">Ma</text>')
    escala.append("</g>")
    y = 64

    def cabecera(texto: str, detalle: str = "") -> None:
        nonlocal y
        y += 10
        filas.append(f'<text x="0" y="{y + 14}" class="carril">{esc(texto.upper())}</text>')
        if detalle:
            filas.append(f'<text x="{DER}" y="{y + 14}" class="carril-detalle" text-anchor="end">{esc(detalle)}</text>')
        y += CABECERA + 6

    def grupo(texto: str, detalle: str = "") -> None:
        nonlocal y
        extra = f'<tspan class="grupo-detalle" dx="10">{esc(detalle)}</tspan>' if detalle else ""
        filas.append(f'<text x="0" y="{y + 15}" class="grupo">{esc(texto[:1].upper() + texto[1:])}{extra}</text>')
        y += CABECERA

    def marca(m: dict, rotulo: str) -> None:
        nonlocal y
        cy = y + FILA / 2
        relleno = {"high": "alta", "medium": "media", "low": "baja"}.get(m["fuerza"], "desconocida")
        etiqueta = f'{m["etiqueta"]} · {m["original"]} · evidencia {relleno}'
        g = [f'<g class="marca {m["clase"]} fuerza-{relleno}" data-claim="{m["claim"]}" tabindex="0" '
             f'role="button" aria-label="{esc(etiqueta)}">',
             f'<rect class="fondo-fila" x="0" y="{y}" width="{DER}" height="{FILA}"/>']
        estilo = ' font-style="italic"' if m["cursiva"] and rotulo == m["etiqueta"] else ""
        g.append(f'<text x="0" y="{cy + 4}" class="rotulo"{estilo}>{esc(recortar(rotulo, 40))}</text>')
        xa = x(recorte(m["desde"], viejo))
        xb = x(recorte(m["hasta"], joven))
        flecha_izq = m["forma"] == "minimo" or (m["desde"] is not None and m["desde"] > viejo)
        flecha_der = m["forma"] == "desde" or (m["hasta"] is not None and m["hasta"] < joven)
        if m["forma"] == "minimo":
            xa = max(IZQ, xb - 46)
        if m["forma"] == "punto":
            forma = "circle" if m["clase"] == "biomarcador" else "rombo"
            if forma == "circle":
                g.append(f'<circle class="figura" cx="{xa}" cy="{cy}" r="5.5"/>')
            else:
                g.append(f'<path class="figura" d="M{xa} {cy - 6.5}L{xa + 6.5} {cy}L{xa} {cy + 6.5}'
                         f'L{xa - 6.5} {cy}Z"/>')
            fin = xa + 10
        elif m["clase"] == "unidad":
            g.append(f'<path class="figura corchete" d="M{xa} {cy - 6}V{cy + 6}M{xa} {cy}H{xb}'
                     f'M{xb} {cy - 6}V{cy + 6}"/>')
            fin = xb + 6
        else:
            radio = 4 if m["clase"] == "biomarcador" else 1.5
            g.append(f'<rect class="figura" x="{xa}" y="{cy - 4.5}" width="{max(round(xb - xa, 1), 2)}" '
                     f'height="9" rx="{radio}"/>')
            fin = xb + 6
        if flecha_izq:
            g.append(f'<path class="flecha" d="M{xa - 2} {cy}l7 -5v10z"/>')
        if flecha_der:
            g.append(f'<path class="flecha" d="M{xb + 2} {cy}l-7 -5v10z"/>')
            fin = xb + 8
        texto = m["original"] if m["forma"] != "geologico" else f'{m["nombre"]} ({fmt(m["desde"])}–{fmt(m["hasta"])} Ma)'
        if m["no_resuelta"]:
            texto += " ?"
        if fin + len(texto) * 6.2 > DER + 20:
            g.append(f'<text x="{xa - 10}" y="{cy + 4}" class="valor" text-anchor="end">{esc(texto)}</text>')
        else:
            g.append(f'<text x="{fin}" y="{cy + 4}" class="valor">{esc(texto)}</text>')
        g.append("</g>")
        filas.append("".join(g))
        y += FILA

    por_claim = {m["claim"]: m for m in marcas}
    relojes = [m for m in marcas if m["carril"] == "reloj"]
    cabecera("Relojes moleculares", f"{len(relojes)} estimaciones · ninguna se promedia")
    for ev in datos["eventos"]:
        rango = ev["rango"]
        grupo(ev["etiqueta"],
              f"{len(ev['claims'])} {'estimación' if len(ev['claims']) == 1 else 'estimaciones'}"
              + (f" · {fmt(rango[1])}–{fmt(rango[0])} Ma" if rango and len(ev["claims"]) > 1 else ""))
        for cid in sorted(ev["claims"], key=lambda c: orden(por_claim[c])):
            m = por_claim[cid]
            marca(m, m["cita"] + (f" +{m['n_fuentes'] - 1}" if m["n_fuentes"] > 1 else ""))

    rocas = [m for m in marcas if m["carril"] == "roca"]
    cabecera("Rocas", f"{len(rocas)} dataciones del registro")
    for clase, titulo in (("fosil", "Fósiles"), ("biomarcador", "Biomarcadores"),
                          ("unidad", "Unidades datadas"), ("registro", "Registro de un clado")):
        del_grupo = sorted((m for m in rocas if m["clase"] == clase), key=orden)
        if not del_grupo:
            continue
        grupo(titulo)
        for m in del_grupo:
            marca(m, m["etiqueta"])

    alto = y + 8
    rejilla = "".join(f'<line x1="{x(ma)}" x2="{x(ma)}" y1="64" y2="{alto}" class="rejilla"/>'
                      for ma in marcas_ma)
    return (f'<svg class="eje" viewBox="0 0 {ANCHO} {alto}" role="group" '
            f'aria-label="Dataciones en millones de años, de {fmt(viejo)} a {fmt(joven)} Ma" '
            f'data-viejo="{viejo}" data-joven="{joven}">'
            + PATRONES + rejilla + "".join(escala) + "".join(filas) + "</svg>")


PATRONES = (
    '<defs><pattern id="rayado" width="5" height="5" patternUnits="userSpaceOnUse" '
    'patternTransform="rotate(45)"><rect width="5" height="5" class="rayado-fondo"/>'
    '<line x1="0" y1="0" x2="0" y2="5" class="rayado-linea"/></pattern></defs>'
)


def orden(m: dict) -> tuple:
    viejo = m["desde"] if m["desde"] is not None else m["hasta"]
    return (-(viejo or 0), m["claim"])


def fmt(ma: float | None) -> str:
    if ma is None:
        return "?"
    return str(int(ma)) if float(ma).is_integer() else f"{ma:g}"


def recortar(texto: str, n: int) -> str:
    return texto if len(texto) <= n else texto[: n - 1].rstrip() + "…"


def pagina(datos: dict, documento: bool = True) -> str:
    """La página: la plantilla con el eje y los datos dentro.

    Con `documento`, un HTML completo; sin él, el fragmento que el visor de
    artefactos envuelve por su cuenta.
    """
    plantilla = PLANTILLA.read_text(encoding="utf-8")
    cabeza, _, cuerpo = plantilla.partition("<!--CUERPO-->")
    carga = json.dumps(datos, ensure_ascii=False, sort_keys=True).replace("</", "<\\/")
    v = datos["vista"]
    cuenta = v["cuenta"]
    sustituciones = {
        "__EJE__": svg(datos),
        "__DATOS__": carga,
        "__SECCIONES__": " y ".join(v["secciones"]),
        "__META__": html.escape(
            f"{v['revision']} · {v['snapshot']} · corpus {v['corpus']['version']} ({v['corpus']['commit']}), "
            f"corte {v['fecha_de_corte']}"),
        "__CUENTA__": (f"{cuenta['activas']} afirmaciones activas: {cuenta['en_el_eje']} en el eje, "
                       f"{cuenta['de_metodo']} de método, {cuenta['en_fichas']} en las fichas y "
                       f"{cuenta['fuera']} fuera."),
        "__SIN_TOPOLOGIA__": html.escape(v["sin_topologia"]),
        "__ICS__": html.escape(datos["escala"]["fuente"]),
    }
    for clave, valor in sustituciones.items():
        cabeza, cuerpo = cabeza.replace(clave, valor), cuerpo.replace(clave, valor)
    if not documento:
        return cabeza.strip() + "\n" + cuerpo.strip() + "\n"
    return ('<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + cabeza.strip() + "\n</head>\n<body>\n" + cuerpo.strip() + "\n</body>\n</html>\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="Relojes y rocas: la vista temporal de lo convertido")
    ap.add_argument("--records", default=None, help="directorio de registros; por defecto el dataset real")
    ap.add_argument("--salida", default=None, help=f"carpeta de salida; por defecto {SALIDA.relative_to(ROOT)}")
    ap.add_argument("--fragmento", default=None, metavar="RUTA",
                    help="escribe además la página sin envoltorio, para publicarla como artefacto")
    args = ap.parse_args()

    base = Path(args.records).resolve() if args.records else RECORDS
    if not base.is_dir():
        print(f"ERROR no existe el directorio: {base}")
        return 1
    datos = construir(base)
    salida = Path(args.salida).resolve() if args.salida else SALIDA
    salida.mkdir(parents=True, exist_ok=True)
    (salida / "cronologia.json").write_text(
        json.dumps(datos, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (salida / "cronologia.html").write_text(pagina(datos), encoding="utf-8")
    if args.fragmento:
        Path(args.fragmento).write_text(pagina(datos, documento=False), encoding="utf-8")

    c = datos["vista"]["cuenta"]
    print(f"Relojes y rocas · {c['activas']} afirmaciones activas")
    print(f"  en el eje {c['en_el_eje']} · de método {c['de_metodo']} · en fichas {c['en_fichas']} · fuera {c['fuera']}")
    print(f"  {datos['vista']['sin_topologia']}")
    for nombre in ("cronologia.html", "cronologia.json"):
        try:
            print(f"  {(salida / nombre).relative_to(ROOT)}")
        except ValueError:
            print(f"  {salida / nombre}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
