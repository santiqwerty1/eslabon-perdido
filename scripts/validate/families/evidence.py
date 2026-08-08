"""Familia «evidencia» de §19.2.

Las exigencias de la guía, hechas asertos:

    1. soporte cuantitativo con tipo y fuente        §10.7, §6.4
    2. no hay porcentajes inventados                 §4.1
    3. la evidencia respalda la afirmación indicada  §6.4, §19.2
    4. fuente general y localizador específico       §6.4, E.7

La segunda es §4.1 convertida en código. La regla que aplica esta familia es
literal: un número que expresa confianza sólo entra si viene con tipo de medida,
método y fuente. Bootstrap, probabilidad posterior, intervalo o margen de error
sí; «confianza 0,85» no, venga de donde venga. Un `measure_type` vago con la
cadena completa detrás se avisa en lugar de rechazarse, porque puede ser el
vocabulario de la fuente y no una invención del ingestor: eso se resuelve
leyendo la fuente, y §19.1 ya obliga a que todo WARNING lleve issue.

La tercera comprueba la simetría del enlace en los dos sentidos. Que una
afirmación cite una evidencia que no la respalda —o peor, que la cuestiona— no
lo detecta ningún esquema: los dos registros son válidos por separado.
"""

from __future__ import annotations

NAME = "evidence"
PHASE = None

CLAIM = "CLAIM-"
EVID = "EVID-"
RESULT = "RESULT-"
EVENT = "EVENT-"

# Vocabulario de medidas explícitas: la enumeración de `Result.support` (E.11)
# más las dos formas que §4.1 nombra en prosa. Fuera de esta lista no hay
# rechazo automático, pero sí exigencia de método y fuente.
_RECOGNISED_MEASURES = {
    "bootstrap",
    "posterior_probability",
    "jackknife",
    "bremer",
    "p_value",
    "confidence_interval",
    "credible_interval",
    "margin_of_error",
    "standard_error",
}

# Palabras que designan una confianza sin decir cómo se midió. Son exactamente
# las que §4.1 prohíbe usar como porcentaje arbitrario.
_VAGUE_TOKENS = (
    "confidence", "confianza", "certainty", "certeza", "seguridad",
    "reliability", "fiabilidad", "score", "puntuacion", "likelihood",
    "verosimilitud", "probability", "probabilidad", "percent", "porcentaje",
    "strength", "fuerza",
)

_MOLECULAR = {"molecular", "genomic", "mitochondrial", "chromosomal", "paleoproteomic"}


# --- utilidades -------------------------------------------------------------

def _index(data: dict[str, list[dict]]) -> dict[str, dict]:
    idx: dict[str, dict] = {}
    for recs in data.values():
        for rec in recs:
            if isinstance(rec, dict) and isinstance(rec.get("id"), str):
                idx.setdefault(rec["id"], rec)
    return idx


def _by_prefix(data: dict[str, list[dict]], prefix: str) -> list[dict]:
    out = []
    for recs in data.values():
        for rec in recs:
            if isinstance(rec, dict) and isinstance(rec.get("id"), str) and rec["id"].startswith(prefix):
                out.append(rec)
    return out


def _ids(rec: dict, field: str) -> list[str]:
    val = rec.get(field)
    return [v for v in val if isinstance(v, str)] if isinstance(val, list) else []


def _norm(text) -> str:
    """Normaliza un tipo de medida: minúsculas, sin acentos, con guiones bajos."""
    if not isinstance(text, str):
        return ""
    out = text.strip().lower().replace("-", "_").replace(" ", "_")
    for accented, plain in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ñ", "n")):
        out = out.replace(accented, plain)
    return out


def _is_vague(measure_type) -> bool:
    norm = _norm(measure_type)
    if norm in _RECOGNISED_MEASURES:
        return False
    return any(token in norm for token in _VAGUE_TOKENS)


def _carries_number(value) -> bool:
    """Un valor numérico, o una cadena que arrastra cifras («87 %», «0,9»)."""
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return True
    return isinstance(value, str) and any(ch.isdigit() for ch in value)


def _blank(value) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


# --- 1 y 2. soporte cuantitativo y porcentajes inventados (§10.7, §4.1) -----

def _check_quantitative_support(claims: list[dict], rep) -> None:
    """Cada medida guarda tipo, método, escala, fuente y a qué se aplica."""
    for c in claims:
        cid = c.get("id", "(sin id)")
        support = c.get("quantitative_support")
        if not isinstance(support, list):
            support = []
        for n, item in enumerate(support, 1):
            if not isinstance(item, dict):
                continue
            where = f"{cid}.quantitative_support[{n}]"
            measure = item.get("measure_type")
            value = item.get("value")
            has_source = not _blank(item.get("source_id"))
            has_method = not _blank(item.get("method"))
            numeric = _carries_number(value)

            if _blank(measure):
                rep.error(f"evidencia: {where} guarda un valor sin tipo de medida (§10.7)")
            if numeric and not has_source:
                rep.error(
                    f"evidencia: {where} guarda el valor {value!r} sin fuente. §4.1: los valores "
                    "cuantitativos sólo se almacenan cuando una fuente los proporciona"
                )
            if numeric and not has_method:
                rep.error(
                    f"evidencia: {where} guarda el valor {value!r} sin método. Sin método no se "
                    "sabe qué mide (§10.7)"
                )
            if numeric and _is_vague(measure):
                if has_source and has_method:
                    rep.warn(
                        f"evidencia: {where} usa measure_type={measure!r}, que nombra una confianza "
                        "sin decir cómo se midió. Lleva método y fuente, así que se avisa en vez de "
                        "rechazarse: comprueba contra la fuente si es bootstrap, probabilidad "
                        "posterior, intervalo o margen de error (§4.1)"
                    )
                else:
                    rep.error(
                        f"evidencia: {where} guarda {measure!r}={value!r} sin la cadena completa de "
                        "tipo, método y fuente. §4.1 prohíbe los porcentajes arbitrarios de confianza"
                    )
            elif not numeric and not _blank(value) and not has_source:
                rep.warn(f"evidencia: {where} guarda un valor sin fuente (§10.7)")

            missing = [
                name
                for name, present in (
                    ("escala", not _blank(item.get("scale"))),
                    ("nodo o relación al que aplica", not _blank(item.get("applies_to"))),
                    ("condiciones del análisis", not _blank(item.get("analysis_conditions"))),
                )
                if not present
            ]
            if numeric and missing:
                rep.warn(f"evidencia: {where} no registra {', '.join(missing)} (§10.7)")
            if has_source and _blank(item.get("locator")):
                rep.warn(
                    f"evidencia: {where} cita la fuente sin localizador específico "
                    "(página, figura, tabla o material suplementario) (§6.4, §19.2)"
                )


def _check_quantitative_claims(claims: list[dict], rep) -> None:
    """Una afirmación cuantitativa sin medida detrás es un número inventado."""
    for c in claims:
        if c.get("claim_type") != "quantitative":
            continue
        cid = c.get("id", "(sin id)")
        obj = c.get("object") if isinstance(c.get("object"), dict) else {}
        if not _carries_number(obj.get("value")):
            continue
        support = c.get("quantitative_support")
        if not (isinstance(support, list) and support):
            rep.error(
                f"evidencia: {cid} afirma el valor {obj.get('value')!r} sin soporte cuantitativo "
                "que declare tipo de medida, método y fuente (§4.1, §10.7)"
            )
        if _blank(obj.get("unit")) and _blank(obj.get("scale")):
            rep.warn(
                f"evidencia: {cid} guarda un valor sin unidad ni escala: no se distingue 0–1 de "
                "0–100 ni una unidad de otra (§10.7, §11.4)"
            )


def _check_results(results: list[dict], index: dict[str, dict], rep) -> None:
    """El soporte estadístico de un resultado también necesita fuente (§6.4)."""
    for r in results:
        rid = r.get("id", "(sin id)")
        own = _ids(r, "source_ids")
        analysis = index.get(r.get("analysis_id")) if isinstance(r.get("analysis_id"), str) else None
        inherited = _ids(analysis, "source_ids") if isinstance(analysis, dict) else []
        sourced = bool(own or inherited)

        support = r.get("support") if isinstance(r.get("support"), dict) else None
        if support is not None:
            measure = support.get("measure_type")
            if not sourced:
                rep.error(
                    f"evidencia: {rid} guarda soporte {measure!r}={support.get('value')!r} y ni el "
                    "resultado ni su análisis citan fuente (§4.1, §6.4)"
                )
            if _carries_number(support.get("value")) and _blank(support.get("scale")):
                rep.warn(
                    f"evidencia: {rid} guarda soporte {measure!r} sin escala. §10.7 prohíbe "
                    "convertir medidas distintas a una escala común ficticia, y sin escala no se sabe cuál es"
                )
            if _norm(measure) == "other" and _blank(r.get("description")):
                rep.warn(
                    f"evidencia: {rid} usa measure_type='other' sin describir qué mide (§10.7)"
                )

        if _carries_number(r.get("value")) and not sourced:
            rep.error(
                f"evidencia: {rid} guarda el valor {r.get('value')!r} y ni el resultado ni su "
                "análisis citan fuente (§4.1)"
            )


def _check_event_proportions(events: list[dict], index: dict[str, dict], rep) -> None:
    """Una proporción de mezcla es un número: necesita de dónde sale (§4.1, §13.1)."""
    for e in events:
        eid = e.get("id", "(sin id)")
        participants = e.get("participants")
        if not isinstance(participants, list):
            continue
        quantified = [
            p for p in participants
            if isinstance(p, dict) and p.get("proportion") is not None
        ]
        if not quantified:
            continue
        backed = bool(_ids(e, "evidence_ids"))
        if not backed:
            for cid in _ids(e, "claim_ids"):
                claim = index.get(cid)
                if isinstance(claim, dict) and claim.get("quantitative_support"):
                    backed = True
                    break
        if not backed:
            entities = [p.get("entity_id") for p in quantified]
            rep.error(
                f"evidencia: {eid} cuantifica la participación de {entities} sin evidencia "
                "enlazada ni afirmación con soporte cuantitativo. §13.1 admite proporciones de la "
                "fuente; §4.1 no admite proporciones sin fuente"
            )


# --- 3. la evidencia respalda lo que dice respaldar (§6.4) ------------------

def _check_evidence_direction(evidence: list[dict], claims: list[dict], index: dict[str, dict], rep) -> None:
    """El enlace afirmación ↔ evidencia dice lo mismo leído en los dos sentidos."""
    for ev in evidence:
        eid = ev.get("id", "(sin id)")
        supports = set(_ids(ev, "supports_claim_ids"))
        challenges = set(_ids(ev, "challenges_claim_ids"))

        for cid in sorted(supports & challenges):
            rep.error(
                f"evidencia: {eid} respalda y cuestiona {cid} a la vez. Los dos sentidos son "
                "simétricos (E.7), no simultáneos"
            )
        if not supports and not challenges:
            rep.warn(
                f"evidencia: {eid} no respalda ni cuestiona ninguna afirmación. §6.4 exige "
                "afirmaciones respaldadas o cuestionadas: una evidencia suelta no es trazable"
            )

        for cid in sorted(supports):
            claim = index.get(cid)
            if isinstance(claim, dict) and eid not in _ids(claim, "evidence_ids") + _ids(claim, "counterevidence_ids"):
                rep.warn(
                    f"evidencia: {eid} respalda {cid}, que no la enlaza. El enlace unidireccional "
                    "hace que el mismo grafo diga cosas distintas según por dónde se recorra (§6.4)"
                )
        for cid in sorted(challenges):
            claim = index.get(cid)
            if isinstance(claim, dict) and eid not in _ids(claim, "counterevidence_ids") + _ids(claim, "evidence_ids"):
                rep.warn(
                    f"evidencia: {eid} cuestiona {cid}, que no la enlaza. La contraevidencia viaja "
                    "con la afirmación (E.6), no en un apéndice aparte"
                )

    for c in claims:
        cid = c.get("id", "(sin id)")
        for eid in _ids(c, "evidence_ids"):
            ev = index.get(eid)
            if not isinstance(ev, dict):
                continue
            if cid in _ids(ev, "supports_claim_ids"):
                continue
            if cid in _ids(ev, "challenges_claim_ids"):
                rep.error(
                    f"evidencia: {cid} se apoya en {eid}, que la cuestiona. El sentido está "
                    "invertido (§6.4, §19.2)"
                )
            else:
                rep.error(
                    f"evidencia: {cid} se apoya en {eid}, que no respalda esa afirmación: "
                    f"{eid} respalda {_ids(ev, 'supports_claim_ids') or 'nada'} (§19.2)"
                )
        for eid in _ids(c, "counterevidence_ids"):
            ev = index.get(eid)
            if not isinstance(ev, dict):
                continue
            if cid in _ids(ev, "challenges_claim_ids"):
                continue
            if cid in _ids(ev, "supports_claim_ids"):
                rep.error(
                    f"evidencia: {cid} registra {eid} como contraevidencia, pero {eid} la respalda. "
                    "El sentido está invertido (§6.4)"
                )
            else:
                rep.error(
                    f"evidencia: {cid} registra {eid} como contraevidencia, y {eid} no cuestiona "
                    "esa afirmación (§19.2)"
                )


# --- 4. fuente general y localizador específico (§6.4, E.7) ----------------

def _check_source_and_locator(evidence: list[dict], index: dict[str, dict], rep) -> None:
    for ev in evidence:
        eid = ev.get("id", "(sin id)")
        source_id = ev.get("source_id")

        if _blank(source_id):
            if _ids(ev, "issue_ids"):
                rep.warn(
                    f"evidencia: {eid} no tiene fuente resuelta; queda pendiente por su cuestión "
                    "'missing_source' (E.7, E.12)"
                )
            else:
                rep.error(
                    f"evidencia: {eid} no tiene fuente ni cuestión pendiente que lo justifique. "
                    "E.7 admite source_id nulo sólo con un 'missing_source' registrado"
                )
        else:
            source = index.get(source_id)
            section_provided = isinstance(source, dict) and source.get("source_type") == "section_provided"
            if section_provided:
                if not _ids(ev, "passage_ids"):
                    rep.warn(
                        f"evidencia: {eid} procede de la sección y no enlaza pasaje. El pasaje es "
                        "su localizador (§17 paso 2, §4.5)"
                    )
            elif _blank(ev.get("locator")):
                rep.warn(
                    f"evidencia: {eid} cita {source_id} sin localizador específico: página, figura, "
                    "tabla o material suplementario (§6.4, §19.2)"
                )

        if ev.get("evidence_type") == "statistical" and not _ids(ev, "result_ids"):
            rep.warn(
                f"evidencia: {eid} es estadística y no enlaza resultado. §6.4 fija la cadena "
                "fuente → conjunto de datos → análisis → resultado → afirmación"
            )
        if ev.get("evidence_type") in _MOLECULAR and not (_ids(ev, "dataset_ids") or _ids(ev, "analysis_ids")):
            rep.info(
                f"evidencia: {eid} es {ev.get('evidence_type')!r} y no enlaza conjunto de datos ni "
                "análisis (§6.4)"
            )
        if not _ids(ev, "limitations"):
            rep.info(
                f"evidencia: {eid} no registra limitaciones. §6.4 pide anotar lo que la evidencia "
                "no permite concluir, aunque la fuente sea entusiasta"
            )


# --- fuerza de evidencia declarada (§10.3, §4.1) ---------------------------

def _check_strength_declarations(data: dict[str, list[dict]], rep) -> None:
    """Declarar fuerza de evidencia obliga a decir por qué, y a tener evidencia."""
    for recs in data.values():
        for rec in recs:
            if not isinstance(rec, dict):
                continue
            dims = rec.get("epistemic_dimensions")
            if not isinstance(dims, dict):
                continue
            rid = rec.get("id", "(sin id)")
            strength = dims.get("evidence_strength")
            if strength in ("high", "medium", "low") and _blank(dims.get("evidence_strength_reason")):
                rep.error(
                    f"evidencia: {rid} declara evidence_strength={strength!r} sin razón. §10.3 la "
                    "exige: sin ella el eje es una etiqueta sin contenido"
                )
            if strength == "high" and rid.startswith(CLAIM) and not _ids(rec, "evidence_ids"):
                rep.warn(
                    f"evidencia: {rid} declara fuerza de evidencia alta y no enlaza ninguna "
                    "evidencia (§10.3, §4.1)"
                )


# --- entrada ----------------------------------------------------------------

def check(data: dict[str, list[dict]], rep) -> None:
    index = _index(data)
    claims = _by_prefix(data, CLAIM)
    evidence = _by_prefix(data, EVID)
    results = _by_prefix(data, RESULT)
    events = _by_prefix(data, EVENT)

    if not (claims or evidence or results or events):
        rep.info(
            "evidencia: no hay evidencia, afirmaciones, resultados ni eventos todavía; la familia "
            "se ejecutó sin material que comprobar"
        )

    _check_quantitative_support(claims, rep)
    _check_quantitative_claims(claims, rep)
    _check_results(results, index, rep)
    _check_event_proportions(events, index, rep)
    _check_evidence_direction(evidence, claims, index, rep)
    _check_source_and_locator(evidence, index, rep)
    _check_strength_declarations(data, rep)
