"""Familia «Tiempo» de §19.2.

§19.2 enumera la familia en cinco líneas. Ésta es la correspondencia exacta
entre cada línea de la guía y las comprobaciones implementadas:

| Línea de §19.2                                          | Función                |
|---------------------------------------------------------|------------------------|
| «intervalos válidos»                                     | `_check_intervals`     |
| «unidades explícitas»                                    | `_check_intervals`     |
| «observado e inferido separados»                         | `_check_determination` |
| «eventos temporalmente plausibles»                       | `_check_plausibility`  |
| «ausencia de ciclos de ascendencia dentro de una hipótesis» | `_check_cycles`     |

Y con §11.3, que desarrolla las cinco en cinco exigencias concretas:

| §11.3 «que una ascendencia inferida sea temporalmente plausible»          | `_check_plausibility` |
| §11.3 «que participantes de hibridación puedan coexistir»                 | `_check_plausibility` |
| §11.3 «que una transferencia no conecte entidades separadas por intervalos imposibles» | `_check_plausibility` |
| §11.3 «que una innovación no se presente como anterior a la evidencia citada sin marcar inferencia» | `_check_innovation` |
| §11.3 «que no haya ciclos en el subgrafo de ascendencia de una hipótesis»  | `_check_cycles`       |

Dos reglas de la guía gobiernan la severidad y son la parte fácil de
equivocar:

- **§11.3, párrafo final.** «No debe asumir que el primer fósil conocido es el
  origen real de un linaje. Una aparente inversión entre rangos observados
  genera una advertencia, no necesariamente un error.» Por eso, cuando el
  conflicto se apoya sólo en rangos *observados* la severidad baja a WARNING;
  cuando lo sostiene un rango inferido o modelado —que pretende ser la duración
  biológica, no el registro fósil— es ERROR.
- **§6.9.** «La restricción de aciclicidad se aplica a subgrafos concretos,
  especialmente a la ascendencia vertical dentro de una hipótesis.» La
  aciclicidad se comprueba **por hipótesis**, nunca sobre la unión de todas.
  Un ciclo que sólo aparece al mezclar hipótesis alternativas no es un error:
  es lo que se espera de dos topologías rivales, y se anota como INFO.

Otras decisiones documentadas:

- Los predicados reticulados (`contributes_ancestry_to`, `introgression_from`,
  `receives_gene_flow_from`, `endosymbiosis_with`…) quedan **fuera** del grafo
  de aciclicidad. §6.9 dice que no debe imponerse una semántica de dirección
  única, y un flujo génico recíproco entre dos poblaciones es un hecho
  frecuente, no una paradoja.
- `chronological_continuation_of` también queda fuera: §14.1 lo define como
  «afirmación de continuidad, **no ascendencia automática**».
- Los predicados modales cierran ciclos con WARNING, no con ERROR: §14.1 exige
  que `possible_ancestor_of` no se degrade nunca a ascendencia definitiva, así
  que un ciclo que necesita una arista modal para cerrarse no afirma una
  paradoja, sólo un conjunto de posibilidades que no pueden ser todas ciertas.

La familia no importa nada de `validate.py` ni de `jsonschema`: repite algunas
comprobaciones estructurales baratas porque en esta máquina la familia `schema`
puede quedarse sin ejecutar (ISSUE-000029).
"""

from __future__ import annotations

import re

NAME = "time"
PHASE = None  # ejecutable: sólo usa tipos ya implementados

TIME_ID_RE = re.compile(r"^TIME-[0-9]{6}$")

# §11.4. Unidades convertibles a años para *comparar*. La conversión es interna
# y nunca se escribe: §11.4 exige conservar el valor original sin redondear.
# 'generations' y 'geological_interval' no se convierten: la primera depende del
# modelo poblacional y la segunda no es numérica.
UNIT_TO_YEARS = {
    "years": 1.0,
    "thousand_years": 1e3,
    "million_years": 1e6,
    "calibrated_years": 1.0,
}
UNITS = set(UNIT_TO_YEARS) | {"generations", "geological_interval"}

# Orígenes de cuenta con escala «hacia atrás»: sólo entre ellos tiene sentido
# comparar magnitudes. 'calendar' cuenta al revés y 'relative_to_event' no tiene
# origen común, así que no entran en las comparaciones de plausibilidad.
AGO_REFS = {"before_present", "before_2000_ce", "not_stated"}

TEMPORAL_TYPES = {
    "occurrence_date",
    "observed_taxon_range",
    "inferred_lineage_range",
    "divergence_estimate",
    "event_date",
    "trait_evidence_date",
    "publication_date",
    "classification_validity_period",
}
DEEP_TIME_TYPES = {
    "occurrence_date",
    "observed_taxon_range",
    "inferred_lineage_range",
    "divergence_estimate",
    "event_date",
    "trait_evidence_date",
}
DETERMINATIONS = {"observed", "inferred", "modelled", "reported_without_basis", "unknown"}
INFERRED_DETERMINATIONS = {"inferred", "modelled"}

# Tipos de evento que exigen que sus participantes hayan podido coexistir.
# §11.3 nombra expresamente la hibridación y la transferencia; el resto son los
# tipos de §13.3 cuya definición implica contacto entre entidades vivas.
COEXISTENCE_EVENTS = {
    "hybridization": "hibridación",
    "introgression": "introgresión",
    "gene_flow": "flujo génico",
    "hybrid_origin": "origen híbrido",
    "horizontal_transfer": "transferencia horizontal",
    "vector_mediated_transfer": "transferencia mediada por vector",
    "viral_integration": "integración viral",
    "endosymbiosis": "endosimbiosis",
    "organelle_capture": "captura de orgánulo",
    "population_absorption": "absorción poblacional",
    "partial_replacement": "reemplazo parcial",
    "competition": "competencia",
    "predation": "depredación",
    "host_pathogen_relationship": "relación hospedador-patógeno",
    "coevolution": "coevolución",
    "cultural_transmission": "transmisión cultural",
    "intergroup_learning": "aprendizaje entre grupos",
    "technological_replacement": "reemplazo tecnológico",
}

INNOVATION_EVENTS = {"innovation", "trait_acquisition"}

# Ascendencia vertical definitiva. Cerrar un ciclo con estas aristas afirma que
# una entidad desciende de sí misma.
ANCESTRY_STRICT = {"descends_from"}
# Ascendencia modal o posicional (§14.1). Cierra ciclos con WARNING.
ANCESTRY_MODAL = {"possible_ancestor_of", "possible_sampled_ancestor_of", "stem_lineage_of"}

# Predicados que aportan una envolvente temporal a una entidad.
ENVELOPE_TYPES = {"observed_taxon_range", "inferred_lineage_range", "occurrence_date"}


def _temporal_index(data: dict[str, list[dict]]) -> dict[str, dict]:
    """Recoge las expresiones temporales estén en el fichero que estén.

    §16.2 no asigna fichero propio a `TemporalExpression`: las expresiones
    `TIME-` se referencian desde afirmaciones, eventos y observaciones. Se
    indexan por identificador sobre todo el libro mayor para que la familia
    siga funcionando cuando §16.2 les dé fichero.
    """
    out: dict[str, dict] = {}
    for recs in data.values():
        for rec in recs:
            rid = rec.get("id")
            if isinstance(rid, str) and TIME_ID_RE.match(rid) and rid not in out:
                out[rid] = rec
    return out


def _span(trec: dict) -> tuple[float | None, float | None] | None:
    """Devuelve (más reciente, más antiguo) en años antes del presente.

    `None` en un extremo significa intervalo abierto por ese lado, nunca cero
    (temporal-expression.json lo dice expresamente). Devuelve `None` entero
    cuando el intervalo no es comparable numéricamente.
    """
    iv = trec.get("interval")
    if not isinstance(iv, dict):
        return None
    factor = UNIT_TO_YEARS.get(iv.get("unit"))
    if factor is None:
        return None
    if (iv.get("reference_point") or "not_stated") not in AGO_REFS:
        return None
    viejo = iv.get("oldest_bound")
    joven = iv.get("youngest_bound")
    viejo = float(viejo) * factor if isinstance(viejo, (int, float)) else None
    joven = float(joven) * factor if isinstance(joven, (int, float)) else None
    if viejo is None and joven is None:
        return None
    return (joven, viejo)


def _overlaps(a: tuple, b: tuple) -> bool:
    """¿Se solapan dos envolventes (joven, viejo) en años antes del presente?"""
    a_joven, a_viejo = a
    b_joven, b_viejo = b
    if a_viejo is not None and b_joven is not None and a_viejo < b_joven:
        return False
    if b_viejo is not None and a_joven is not None and b_viejo < a_joven:
        return False
    return True


def _strictly_younger(a: tuple, b: tuple) -> bool:
    """¿Está `a` entera por delante en el tiempo (es decir, más reciente) que `b`?"""
    _a_joven, a_viejo = a
    b_joven, _b_viejo = b
    return a_viejo is not None and b_joven is not None and a_viejo < b_joven


def _observed_only(trecs: list[dict]) -> bool:
    """¿Todo el material que sostiene el conflicto es observado?

    Es la condición de §11.3 para rebajar el error a advertencia.
    """
    return all(
        t.get("determination") == "observed"
        and t.get("temporal_type") in {"observed_taxon_range", "occurrence_date"}
        for t in trecs
    )


# --- «intervalos válidos» y «unidades explícitas» ----------------------------

def _check_intervals(times: dict[str, dict], rep) -> None:
    """§19.2 Tiempo, líneas 1 y 2, sostenidas en §11.2 y §11.4."""
    for tid, t in sorted(times.items()):
        ttype = t.get("temporal_type")
        if ttype not in TEMPORAL_TYPES:
            rep.error(f"tiempo: {tid} declara temporal_type {ttype!r}, fuera de §11.1")

        if ttype == "publication_date" and not t.get("calendar_date"):
            rep.error(f"tiempo: {tid} es una fecha de publicación sin calendar_date (§11.1)")

        iv = t.get("interval")
        if not isinstance(iv, dict):
            if ttype in DEEP_TIME_TYPES:
                rep.error(
                    f"tiempo: {tid} es de tipo {ttype!r} y no lleva intervalo; una "
                    f"fecha de calendario no expresa tiempo profundo (§11.1)"
                )
            elif not t.get("calendar_date") and ttype != "publication_date":
                # La fecha de publicación ya se informó arriba con su propio mensaje.
                rep.error(f"tiempo: {tid} no lleva ni intervalo ni calendar_date (§11.2)")
            continue

        unidad = iv.get("unit")
        if not unidad:
            rep.error(
                f"tiempo: el intervalo de {tid} no declara unidad; sin unidad "
                f"explícita no es interpretable (§11.2, §11.4)"
            )
            continue
        if unidad not in UNITS:
            rep.error(f"tiempo: el intervalo de {tid} usa la unidad {unidad!r}, fuera de §11.4")
            continue

        viejo = iv.get("oldest_bound")
        joven = iv.get("youngest_bound")
        ref = iv.get("reference_point") or "not_stated"

        if viejo is None and joven is None:
            if unidad != "geological_interval":
                rep.warn(
                    f"tiempo: el intervalo de {tid} no tiene ningún límite; "
                    f"un extremo abierto es información, dos no son un intervalo (§11.2)"
                )
        elif isinstance(viejo, (int, float)) and isinstance(joven, (int, float)):
            if ref == "calendar":
                # La escala de calendario cuenta hacia delante: el límite más
                # antiguo es el número menor.
                if viejo > joven:
                    rep.error(
                        f"tiempo: {tid} cuenta en calendario y su límite más antiguo "
                        f"({viejo}) es posterior al más reciente ({joven}) (§11.2)"
                    )
            elif viejo < joven:
                rep.error(
                    f"tiempo: {tid} tiene el límite más antiguo ({viejo} {unidad}) por "
                    f"debajo del más reciente ({joven} {unidad}): el intervalo está "
                    f"invertido (§11.2)"
                )

        if ref in AGO_REFS:
            for etiqueta, valor in (("oldest_bound", viejo), ("youngest_bound", joven)):
                if isinstance(valor, (int, float)) and valor < 0:
                    rep.error(
                        f"tiempo: {tid}.{etiqueta} vale {valor} contando hacia atrás "
                        f"desde {ref}: una antigüedad negativa no es una fecha (§11.2)"
                    )

        if unidad == "geological_interval":
            if not iv.get("geological_interval"):
                rep.error(
                    f"tiempo: {tid} usa la unidad 'geological_interval' y no nombra el "
                    f"intervalo cronoestratigráfico (§11.2)"
                )
            if isinstance(viejo, (int, float)) or isinstance(joven, (int, float)):
                rep.warn(
                    f"tiempo: {tid} mezcla unidad 'geological_interval' con límites "
                    f"numéricos; declarar la unidad numérica y guardar el nombre "
                    f"geológico aparte (§11.4)"
                )
        elif ref == "not_stated" and "reference_point" not in iv:
            rep.info(
                f"tiempo: {tid} no declara reference_point; se asume una cuenta hacia "
                f"atrás para comparar, y esa suposición no está en el dato"
            )

        unc = t.get("uncertainty")
        if not isinstance(unc, dict) or not unc.get("kind"):
            rep.error(
                f"tiempo: {tid} no declara incertidumbre; la ausencia de dato no es "
                f"precisión (§11.2)"
            )
        else:
            kind = unc.get("kind")
            if kind in {"symmetric", "asymmetric"} and not any(
                isinstance(unc.get(k), (int, float)) for k in ("plus_minus", "lower", "upper")
            ):
                rep.warn(
                    f"tiempo: {tid} declara incertidumbre {kind!r} sin ninguna magnitud"
                )
            if kind in {"credible_interval", "confidence_interval"} and unc.get("level") is None:
                rep.warn(f"tiempo: {tid} declara un {kind!r} sin nivel (§11.2)")

        cal = t.get("calibration")
        if not isinstance(cal, dict) or not cal.get("system"):
            rep.error(
                f"tiempo: {tid} no declara calibración o sistema cronológico; una fecha "
                f"calibrada y otra sin calibrar no se comparan igual (§11.2)"
            )


# --- «observado e inferido separados» ----------------------------------------

def _check_determination(data: dict[str, list[dict]], times: dict[str, dict], rep) -> None:
    """§19.2 Tiempo, línea 3, sostenida en §11.1, §11.2 y §11.3.

    §11.1 avisa de que los ocho tipos no son intercambiables: «un rango
    observado no es una duración inferida». §11.3 prohíbe presentar una
    inferencia como observación sin marcarla.
    """
    for tid, t in sorted(times.items()):
        det = t.get("determination")
        ttype = t.get("temporal_type")

        if det is None:
            rep.error(
                f"tiempo: {tid} no declara determination: no puede distinguirse lo "
                f"datado de lo estimado (§11.2)"
            )
            continue
        if det not in DETERMINATIONS:
            rep.error(f"tiempo: {tid} declara determination {det!r}, fuera de §11.2")
            continue

        if ttype == "observed_taxon_range" and det in INFERRED_DETERMINATIONS:
            rep.error(
                f"tiempo: {tid} es un 'observed_taxon_range' con determination {det!r}; "
                f"un rango observado no es una duración inferida (§11.1). El tipo "
                f"correcto sería 'inferred_lineage_range'"
            )
        if ttype in {"inferred_lineage_range", "divergence_estimate"} and det == "observed":
            rep.error(
                f"tiempo: {tid} es un {ttype!r} presentado como observado; una "
                f"estimación no se presenta como observación (§11.3)"
            )
        if t.get("method_type") == "molecular_clock" and det == "observed":
            rep.error(
                f"tiempo: {tid} data por reloj molecular y se declara observado; el "
                f"reloj molecular modela, no observa (§11.3)"
            )
        if det == "reported_without_basis":
            rep.warn(
                f"tiempo: {tid} se incorporó sin base declarada "
                f"('reported_without_basis'); §19.1 exige issue o justificación"
            )

        cal = t.get("calibration")
        if isinstance(cal, dict) and cal.get("system") == "molecular_clock" and det == "observed":
            rep.error(
                f"tiempo: {tid} declara calibración por reloj molecular y determinación "
                f"observada (§11.3)"
            )

    # Una inferencia filogenética no se presenta como observación directa
    # (§11.3, y la propia descripción de observation_basis en E.11).
    for obs in data.get("trait-observations.jsonl", []):
        if obs.get("observation_basis") not in {"phylogenetic_inference", "reconstruction"}:
            continue
        for tid in obs.get("temporal_expression_ids") or []:
            t = times.get(tid)
            if t is not None and t.get("determination") == "observed":
                rep.error(
                    f"tiempo: {obs.get('id')} se obtuvo por "
                    f"{obs.get('observation_basis')!r} y fecha con {tid}, marcado como "
                    f"observado; la inferencia no se presenta como observación (§11.3)"
                )


# --- envolventes temporales por entidad --------------------------------------

def _envelopes(data: dict[str, list[dict]], times: dict[str, dict]) -> dict[str, list[dict]]:
    """Expresiones temporales que acotan la existencia de cada entidad.

    Salen de las afirmaciones temporales con procedencia, no de campos planos:
    entity.json es deliberadamente delgado y no guarda fechas (Apéndice E.5).
    """
    out: dict[str, list[dict]] = {}
    for claim in data.get("claims.jsonl", []):
        if claim.get("record_status") != "active":
            continue
        obj = claim.get("object")
        if not isinstance(obj, dict):
            continue
        tid = obj.get("temporal_expression_id")
        sujeto = claim.get("subject_id")
        if not isinstance(tid, str) or not isinstance(sujeto, str):
            continue
        t = times.get(tid)
        if t is None or t.get("temporal_type") not in ENVELOPE_TYPES:
            continue
        if _span(t) is not None:
            out.setdefault(sujeto, []).append(t)
    return out


def _compare(rep, etiqueta: str, a_id: str, a_times: list[dict], b_id: str, b_times: list[dict],
             contexto: str) -> None:
    """Comprueba que dos conjuntos de envolventes puedan solaparse.

    Severidad según §11.3: si todo el material es observado, ADVERTENCIA —el
    primer fósil conocido no es el origen del linaje—; si interviene un rango
    inferido o modelado, ERROR.
    """
    a_spans = [(t, _span(t)) for t in a_times]
    b_spans = [(t, _span(t)) for t in b_times]
    a_spans = [(t, s) for t, s in a_spans if s is not None]
    b_spans = [(t, s) for t, s in b_spans if s is not None]
    if not a_spans or not b_spans:
        return
    # Basta con que UNA pareja de dataciones se solape: §13.1 admite dataciones
    # alternativas conviviendo sin promediarse.
    if any(_overlaps(sa, sb) for _ta, sa in a_spans for _tb, sb in b_spans):
        return
    implicados = [t for t, _s in a_spans] + [t for t, _s in b_spans]
    mensaje = (
        f"tiempo: {contexto}: las envolventes de {a_id} y {b_id} no se solapan en "
        f"ningún par de dataciones ({etiqueta})"
    )
    if _observed_only(implicados):
        rep.warn(
            mensaje
            + "; se apoya sólo en rangos observados, así que es advertencia y no "
            "error (§11.3): el primer fósil conocido no es el origen del linaje"
        )
    else:
        rep.error(
            mensaje
            + "; el conflicto lo sostiene un rango inferido o modelado, que pretende "
            "ser la duración biológica (§11.3)"
        )


# --- «eventos temporalmente plausibles» --------------------------------------

def _check_plausibility(data: dict[str, list[dict]], times: dict[str, dict], rep) -> None:
    """§19.2 Tiempo, línea 4, y las tres primeras exigencias de §11.3."""
    envolventes = _envelopes(data, times)

    for ev in data.get("events.jsonl", []):
        if ev.get("record_status") != "active":
            continue
        etiqueta = COEXISTENCE_EVENTS.get(str(ev.get("event_type")))
        if etiqueta is None:
            continue
        eid = ev.get("id")
        participantes = [
            p.get("entity_id")
            for p in ev.get("participants") or []
            if isinstance(p, dict) and isinstance(p.get("entity_id"), str)
        ]

        for i, a in enumerate(participantes):
            for b in participantes[i + 1:]:
                if a == b:
                    continue
                _compare(
                    rep, etiqueta, a, envolventes.get(a, []), b, envolventes.get(b, []),
                    f"{eid} exige que sus participantes pudieran coexistir",
                )

        # La fecha del propio evento tiene que caber en la existencia de cada
        # participante.
        fechas = [times[tid] for tid in ev.get("temporal_expression_ids") or [] if tid in times]
        if fechas:
            for p in participantes:
                _compare(
                    rep, etiqueta, str(eid), fechas, p, envolventes.get(p, []),
                    f"{eid} está fechado fuera de la existencia de {p}",
                )

    # §11.3: «que una ascendencia inferida sea temporalmente plausible».
    for claim in data.get("claims.jsonl", []):
        if claim.get("record_status") != "active":
            continue
        pred = claim.get("predicate")
        obj = claim.get("object")
        objeto = obj.get("entity_id") if isinstance(obj, dict) else None
        sujeto = claim.get("subject_id")
        if not isinstance(sujeto, str) or not isinstance(objeto, str):
            continue
        if pred == "descends_from":
            ancestro, descendiente = objeto, sujeto
        elif pred in {"possible_ancestor_of", "possible_sampled_ancestor_of"}:
            ancestro, descendiente = sujeto, objeto
        else:
            continue

        a_spans = [(t, _span(t)) for t in envolventes.get(ancestro, [])]
        d_spans = [(t, _span(t)) for t in envolventes.get(descendiente, [])]
        a_spans = [(t, s) for t, s in a_spans if s is not None]
        d_spans = [(t, s) for t, s in d_spans if s is not None]
        if not a_spans or not d_spans:
            continue
        # Implausible sólo si TODAS las dataciones del ancestro quedan por
        # delante en el tiempo de TODAS las del descendiente.
        if not all(_strictly_younger(sa, sd) for _ta, sa in a_spans for _td, sd in d_spans):
            continue
        implicados = [t for t, _s in a_spans] + [t for t, _s in d_spans]
        mensaje = (
            f"tiempo: {claim.get('id')} sitúa a {ancestro} como ancestro de "
            f"{descendiente}, pero {ancestro} es entero posterior a {descendiente}"
        )
        if _observed_only(implicados):
            rep.warn(mensaje + "; inversión entre rangos observados: advertencia (§11.3)")
        else:
            rep.error(mensaje + " según un rango inferido o modelado (§11.3)")


# --- «una innovación no anterior a la evidencia citada» ----------------------

def _check_innovation(data: dict[str, list[dict]], times: dict[str, dict], rep) -> None:
    """§11.3, cuarta exigencia.

    Un evento de innovación o de adquisición de rasgo fechado por encima de
    toda la evidencia de ese rasgo puede ser correcto —la evidencia más antigua
    es un mínimo, no el origen—, pero entonces la fecha es una inferencia y
    tiene que ir marcada como tal.
    """
    fechas_de_rasgo: dict[str, list[dict]] = {}
    for obs in data.get("trait-observations.jsonl", []):
        trait = obs.get("trait_id")
        if not isinstance(trait, str):
            continue
        for tid in obs.get("temporal_expression_ids") or []:
            t = times.get(tid)
            if t is not None and _span(t) is not None:
                fechas_de_rasgo.setdefault(trait, []).append(t)

    for ev in data.get("events.jsonl", []):
        if ev.get("event_type") not in INNOVATION_EVENTS:
            continue
        if ev.get("record_status") != "active":
            continue
        rasgos = [
            p.get("entity_id")
            for p in ev.get("participants") or []
            if isinstance(p, dict) and str(p.get("entity_id", "")).startswith("TRAIT-")
        ]
        # La datación del propio evento no es evidencia del rasgo: si se contara,
        # el evento se justificaría a sí mismo.
        propias = set(ev.get("temporal_expression_ids") or [])
        evidencia = [
            t for r in rasgos for t in fechas_de_rasgo.get(str(r), [])
            if t.get("id") not in propias
        ]
        if not evidencia:
            continue
        mas_antigua = max(
            (s[1] for s in (_span(t) for t in evidencia) if s and s[1] is not None),
            default=None,
        )
        if mas_antigua is None:
            continue
        for tid in ev.get("temporal_expression_ids") or []:
            t = times.get(tid)
            span = _span(t) if t else None
            if not span or span[1] is None or span[1] <= mas_antigua:
                continue
            if t.get("determination") == "observed":
                rep.error(
                    f"tiempo: {ev.get('id')} sitúa la innovación en {tid} por encima de "
                    f"toda la evidencia del rasgo y la declara observada; si el origen "
                    f"se antedata respecto de la evidencia citada, es inferencia y debe "
                    f"marcarse (§11.3)"
                )
            else:
                rep.info(
                    f"tiempo: {ev.get('id')} antedata la innovación respecto de la "
                    f"evidencia del rasgo, marcada como "
                    f"{t.get('determination')!r}: correcto según §11.3"
                )


# --- «ausencia de ciclos de ascendencia dentro de una hipótesis» -------------

def _find_cycle(edges: dict[str, set[str]]) -> list[str] | None:
    """Primer ciclo dirigido, como lista de nodos cerrada sobre sí misma."""
    color: dict[str, int] = {}
    pila: list[str] = []

    def visita(n: str) -> list[str] | None:
        color[n] = 1
        pila.append(n)
        for m in sorted(edges.get(n, ())):
            if color.get(m, 0) == 0:
                ciclo = visita(m)
                if ciclo:
                    return ciclo
            elif color.get(m) == 1:
                return pila[pila.index(m):] + [m]
        color[n] = 2
        pila.pop()
        return None

    for nodo in sorted(edges):
        if color.get(nodo, 0) == 0:
            ciclo = visita(nodo)
            if ciclo:
                return ciclo
    return None


def _edges(claims: list[dict], predicados: set[str]) -> dict[str, set[str]]:
    """Aristas ancestro → descendiente para el conjunto de predicados dado."""
    out: dict[str, set[str]] = {}
    for c in claims:
        pred = c.get("predicate")
        if pred not in predicados:
            continue
        obj = c.get("object")
        objeto = obj.get("entity_id") if isinstance(obj, dict) else None
        sujeto = c.get("subject_id")
        if not isinstance(sujeto, str) or not isinstance(objeto, str):
            continue
        if pred == "descends_from":
            origen, destino = objeto, sujeto
        else:
            origen, destino = sujeto, objeto
        out.setdefault(origen, set()).add(destino)
    return out


def _subgraphs(data: dict[str, list[dict]]) -> dict[str, list[dict]]:
    """Reparte las afirmaciones activas en un subgrafo por hipótesis (§6.9).

    Una afirmación pertenece a una hipótesis si la nombra en su `scope` o si la
    hipótesis la incluye o la requiere; queda fuera si la hipótesis la excluye.
    Las afirmaciones sin hipótesis forman su propio subgrafo: se afirman sin
    contexto, así que un ciclo entre ellas sí es incondicional.
    """
    activos = [
        c for c in data.get("claims.jsonl", [])
        if c.get("record_status") == "active" and isinstance(c.get("id"), str)
    ]
    por_id = {c["id"]: c for c in activos}

    grupos: dict[str, list[dict]] = {}
    reclamadas: set[str] = set()
    for h in data.get("hypotheses.jsonl", []):
        hid = h.get("id")
        if not isinstance(hid, str) or h.get("record_status") != "active":
            continue
        excluidas = set(h.get("excluded_claim_ids") or [])
        ids = set(h.get("included_claim_ids") or []) | set(h.get("required_claim_ids") or [])
        for c in activos:
            alcance = c.get("scope") or {}
            if hid in (alcance.get("hypothesis_ids") or []):
                ids.add(c["id"])
        ids = {i for i in ids if i in por_id and i not in excluidas}
        reclamadas |= ids
        grupos[hid] = [por_id[i] for i in sorted(ids)]

    sueltas = [
        c for c in activos
        if not ((c.get("scope") or {}).get("hypothesis_ids")) and c["id"] not in reclamadas
    ]
    if sueltas:
        grupos["(sin hipótesis)"] = sueltas
    return grupos


def _check_cycles(data: dict[str, list[dict]], rep) -> None:
    """§19.2 Tiempo, línea 5, y §11.3 última exigencia, bajo la regla de §6.9.

    La aciclicidad es POR HIPÓTESIS. Comprobarla sobre la unión de todas
    marcaría como error precisamente lo que el modelo existe para representar:
    dos topologías rivales que ordenan los mismos nodos al revés.
    """
    activos = [c for c in data.get("claims.jsonl", []) if c.get("record_status") == "active"]

    for c in activos:
        if c.get("predicate") not in (ANCESTRY_STRICT | ANCESTRY_MODAL):
            continue
        obj = c.get("object")
        objeto = obj.get("entity_id") if isinstance(obj, dict) else None
        if objeto is not None and objeto == c.get("subject_id"):
            rep.error(
                f"tiempo: {c.get('id')} hace que {objeto} descienda de sí mismo "
                f"({c.get('predicate')})"
            )

    grupos = _subgraphs(data)
    con_ciclo_estricto: set[str] = set()

    for etiqueta, claims in sorted(grupos.items()):
        estricto = _edges(claims, ANCESTRY_STRICT)
        ciclo = _find_cycle(estricto)
        if ciclo:
            con_ciclo_estricto.add(etiqueta)
            rep.error(
                f"tiempo: ciclo de ascendencia dentro de {etiqueta}: "
                + " → ".join(ciclo)
                + " (§6.9, §11.3)"
            )
            continue
        combinado = _edges(claims, ANCESTRY_STRICT | ANCESTRY_MODAL)
        ciclo = _find_cycle(combinado)
        if ciclo:
            rep.warn(
                f"tiempo: ciclo de ascendencia dentro de {etiqueta} que sólo se cierra "
                f"con predicados modales: "
                + " → ".join(ciclo)
                + "; §14.1 no los degrada a ascendencia definitiva, pero no pueden ser "
                "todos ciertos"
            )

    if grupos:
        rep.info(
            f"tiempo: aciclicidad de ascendencia comprobada en {len(grupos)} subgrafos "
            f"por separado (§6.9), no sobre el grafo completo"
        )

    if not con_ciclo_estricto:
        global_ = _edges(activos, ANCESTRY_STRICT)
        ciclo = _find_cycle(global_)
        if ciclo:
            rep.info(
                "tiempo: la unión de todas las hipótesis contiene el ciclo "
                + " → ".join(ciclo)
                + ", pero ninguna hipótesis lo contiene por separado; §6.9 lo permite: "
                "la restricción se aplica al subgrafo, no al grafo entero"
            )


def check(data: dict[str, list[dict]], rep) -> None:
    times = _temporal_index(data)

    _check_intervals(times, rep)
    _check_determination(data, times, rep)
    _check_plausibility(data, times, rep)
    _check_innovation(data, times, rep)
    _check_cycles(data, rep)

    incomparables = sorted(
        tid for tid, t in times.items()
        if isinstance(t.get("interval"), dict) and _span(t) is None
    )
    if incomparables:
        rep.info(
            f"tiempo: {len(incomparables)} expresiones no entran en las comprobaciones "
            f"de plausibilidad por unidad no numérica u origen de cuenta no comparable "
            f"({', '.join(incomparables[:5])}{'…' if len(incomparables) > 5 else ''})"
        )
    if not times:
        rep.info(
            "tiempo: no hay expresiones temporales todavía; §16.2 no asigna fichero "
            "propio a TemporalExpression y se buscaron por prefijo TIME- en todo el "
            "libro mayor"
        )
