"""Familia «hipótesis y topología» de §19.2.

Las exigencias de la guía, hechas asertos:

    1. afirmaciones incompatibles no seleccionadas
       en el mismo escenario                          §15.2, §14.5
    2. requisitos satisfechos                         §15.2
    3. topología coherente                            §15.3, E.10
    4. ausencia de ciclos en el subgrafo de
       ascendencia de cada hipótesis                  §11.3, §19.2
    5. ninguna vista mezcla topologías incompatibles  §17 paso 9, §15.4
    6. fuentes y contraevidencias vinculadas          §15.1

La sexta es la que más dice del proyecto: E.9 exige `counterevidence_ids` en el
registro precisamente porque una hipótesis que sólo guarda lo que la favorece no
es una hipótesis, es una conclusión disfrazada. Aquí eso se traduce en avisos
sobre hipótesis sin oposición registrada, y en errores cuando la evidencia
enlazada como favorable resulta cuestionar lo que la hipótesis incluye.

Sobre las vistas: §16.2 las sitúa en knowledge/views/, fuera del libro mayor que
carga validate.py. Esta familia las busca por prefijo dentro de lo que reciba, de
modo que funciona hoy sobre fixtures y funcionará sobre el repositorio cuando el
cargador incorpore ese directorio. Si hay hipótesis y no llega ninguna vista, lo
dice en vez de callar: no comprobado no es correcto.
"""

from __future__ import annotations

from collections import defaultdict

NAME = "hypotheses"
PHASE = None

CLAIM = "CLAIM-"
HYP = "HYP-"
PHYVIEW = "PHYVIEW-"
TAXVIEW = "TAXVIEW-"

# §14.5. `incompatible_con` y `rechaza_afirmacion` son restricciones duras entre
# afirmaciones: seleccionarlas juntas construye un escenario contradictorio.
_HARD_CONFLICT = {"incompatible_with", "rejects_claim"}
# `alternativa_a` es, según §14.5, relación entre hipótesis. Entre afirmaciones
# se admite, pero seleccionar las dos ramas de una alternativa merece revisión.
_SOFT_CONFLICT = {"alternative_to"}

# §14.1. La ascendencia canónica es `desciende_de`. Los predicados modales no se
# degradan nunca a ascendencia definitiva, así que forman un grafo aparte.
_ANCESTRY = "descends_from"
_MODAL_ANCESTRY = {"possible_ancestor_of", "possible_sampled_ancestor_of"}

# §15.3. Formatos que no pueden expresar reticulación sin pérdida.
_TREE_FORMATS = {"newick", "clade_list"}


# --- utilidades -------------------------------------------------------------

def _index(data: dict[str, list[dict]]) -> dict[str, dict]:
    idx: dict[str, dict] = {}
    for recs in data.values():
        for rec in recs:
            if isinstance(rec, dict) and isinstance(rec.get("id"), str):
                idx.setdefault(rec["id"], rec)
    return idx


def _by_prefix(data: dict[str, list[dict]], *prefixes: str) -> list[dict]:
    out = []
    for recs in data.values():
        for rec in recs:
            if isinstance(rec, dict) and isinstance(rec.get("id"), str) and rec["id"].startswith(prefixes):
                out.append(rec)
    return out


def _ids(rec: dict, field: str) -> list[str]:
    val = rec.get(field)
    return [v for v in val if isinstance(v, str)] if isinstance(val, list) else []


def _object_entity(claim: dict) -> str | None:
    obj = claim.get("object")
    if isinstance(obj, dict) and isinstance(obj.get("entity_id"), str):
        return obj["entity_id"]
    return None


def _conflict_pairs(claims: list[dict], predicates: set[str]) -> list[tuple[str, str, str]]:
    """Pares de afirmaciones en conflicto, con la afirmación que lo declara."""
    pairs = []
    for c in claims:
        if c.get("predicate") not in predicates:
            continue
        subj, obj = c.get("subject_id"), _object_entity(c)
        if isinstance(subj, str) and subj.startswith(CLAIM) and obj and obj.startswith(CLAIM):
            pairs.append((subj, obj, c.get("id", "(sin id)")))
    return pairs


def _cycles(edges: dict[str, set[str]]) -> list[list[str]]:
    """Ciclos del grafo dirigido, en recorrido en profundidad con pila explícita."""
    found: list[list[str]] = []
    color: dict[str, int] = {}  # 0 en curso, 1 cerrado
    for root in list(edges):
        if color.get(root):
            continue
        stack = [(root, iter(sorted(edges.get(root, ()))))]
        path = [root]
        color[root] = 0
        while stack:
            node, it = stack[-1]
            advanced = False
            for nxt in it:
                if color.get(nxt) == 0:
                    found.append(path[path.index(nxt):] + [nxt])
                elif nxt not in color:
                    color[nxt] = 0
                    path.append(nxt)
                    stack.append((nxt, iter(sorted(edges.get(nxt, ())))))
                    advanced = True
                    break
            if not advanced:
                color[node] = 1
                stack.pop()
                path.pop()
    return found


def _ancestry_edges(claim_ids: list[str], index: dict[str, dict], predicates) -> dict[str, set[str]]:
    """Aristas descendiente → ancestro a partir de las afirmaciones dadas."""
    edges: dict[str, set[str]] = defaultdict(set)
    for cid in claim_ids:
        c = index.get(cid)
        if not isinstance(c, dict):
            continue
        pred, subj, obj = c.get("predicate"), c.get("subject_id"), _object_entity(c)
        if not isinstance(subj, str) or obj is None:
            continue
        if pred == _ANCESTRY and _ANCESTRY in predicates:
            edges[subj].add(obj)
        elif pred in _MODAL_ANCESTRY and pred in predicates:
            edges[obj].add(subj)  # «posible ancestro de X» apunta de X hacia él
    return edges


# --- requisitos y exclusiones (§15.2) ---------------------------------------

def _check_requirements(hyps: list[dict], index: dict[str, dict], rep) -> None:
    """Los requisitos de la hipótesis se cumplen dentro de la propia hipótesis."""
    for h in hyps:
        hid = h.get("id", "(sin id)")
        included = set(_ids(h, "included_claim_ids"))
        required = _ids(h, "required_claim_ids")
        excluded = set(_ids(h, "excluded_claim_ids"))

        for rid in required:
            if rid not in included:
                rep.error(
                    f"hipótesis: {hid} declara {rid} como requisito pero no lo incluye. "
                    "§15.2: sin él la hipótesis no se sostiene"
                )
            if rid in excluded:
                rep.error(f"hipótesis: {hid} declara {rid} a la vez requisito y excluido (§15.2)")
            target = index.get(rid)
            if isinstance(target, dict) and target.get("record_status") not in (None, "active"):
                rep.warn(
                    f"hipótesis: {hid} se apoya en el requisito {rid}, cuyo registro está en "
                    f"{target.get('record_status')!r}. §19.2 exige requisitos satisfechos, no sólo presentes"
                )

        for cid in sorted(included & excluded):
            rep.error(
                f"hipótesis: {hid} incluye y excluye {cid} a la vez. Excluir no borra (§9.2), "
                "pero tampoco permite incluir"
            )

        for cid in sorted(included):
            target = index.get(cid)
            if isinstance(target, dict) and target.get("record_status") in ("deprecated", "superseded"):
                rep.warn(
                    f"hipótesis: {hid} incluye {cid}, en estado {target.get('record_status')!r}. "
                    "El registro se conserva (§10.6), pero seleccionarlo exige justificación"
                )


def _check_incompatible_selection(
    hyps: list[dict], views: list[dict], claims: list[dict], rep
) -> None:
    """Nada de escoger las dos ramas de una incompatibilidad (§15.2, §14.5)."""
    hard = _conflict_pairs(claims, _HARD_CONFLICT)
    soft = _conflict_pairs(claims, _SOFT_CONFLICT)

    def scan(container: dict, field: str, kind: str) -> None:
        selected = set(_ids(container, field))
        cid = container.get("id", "(sin id)")
        for a, b, decl in hard:
            if a in selected and b in selected:
                rep.error(
                    f"hipótesis: {kind} {cid} selecciona {a} y {b}, declaradas incompatibles "
                    f"por {decl}. Un escenario no sostiene las dos (§15.2)"
                )
        for a, b, decl in soft:
            if a in selected and b in selected:
                rep.warn(
                    f"hipótesis: {kind} {cid} selecciona {a} y {b}, que {decl} presenta como "
                    "alternativas. Las alternativas se enlazan, no se dibujan como ciertas a la vez (§14.5)"
                )

    for h in hyps:
        scan(h, "included_claim_ids", "la hipótesis")
    for v in views:
        scan(v, "selected_claim_ids", "la vista")


# --- topología (§15.3, §11.3) -----------------------------------------------

def _check_topology(hyps: list[dict], views: list[dict], index: dict[str, dict], rep) -> None:
    """Coherencia de la topología que las afirmaciones seleccionadas describen."""
    for owner, field, kind in (
        [(h, "included_claim_ids", "la hipótesis") for h in hyps]
        + [(v, "selected_claim_ids", "la vista") for v in views]
    ):
        oid = owner.get("id", "(sin id)")
        selected = _ids(owner, field)

        edges = _ancestry_edges(selected, index, {_ANCESTRY})
        strict = _cycles(edges)
        for cycle in strict:
            rep.error(
                f"hipótesis: {kind} {oid} contiene un ciclo de ascendencia: "
                f"{' → '.join(cycle)}. §11.3 y §19.2 lo prohíben dentro de una hipótesis"
            )

        # Los ciclos que sólo aparecen al tomar los predicados modales como
        # ascendencia se comparan por conjunto de nodos: el recorrido puede
        # devolver la misma rotación empezando por otro nodo.
        already = {frozenset(c) for c in strict}
        modal = _ancestry_edges(selected, index, {_ANCESTRY} | _MODAL_ANCESTRY)
        modal_cycles = [c for c in _cycles(modal) if frozenset(c) not in already]
        if modal_cycles:
            rep.warn(
                f"hipótesis: {kind} {oid} cierra un ciclo si se toman los predicados modales como "
                f"ascendencia: {' → '.join(modal_cycles[0])}. No son ascendencia definitiva (§14.1), "
                "pero el conjunto elegido no describe una topología posible"
            )

        multi = {node: parents for node, parents in edges.items() if len(parents) > 1}
        if multi and kind == "la vista":
            _check_reticulation_declared(owner, oid, multi, rep)


def _check_reticulation_declared(view: dict, oid: str, multi: dict[str, set[str]], rep) -> None:
    """Una red no se aplana a árbol sin declararlo (E.10, §15.3)."""
    topo = view.get("topology") if isinstance(view.get("topology"), dict) else {}
    fmt = topo.get("format")
    if topo.get("reticulation") is True or (fmt is not None and fmt not in _TREE_FORMATS):
        return
    node, parents = sorted(multi.items())[0]
    detail = f"{node} recibe ascendencia de {sorted(parents)}"
    if _ids(view, "simplifications"):
        rep.warn(
            f"hipótesis: la vista {oid} usa un formato de árbol ({fmt!r}) y sus afirmaciones "
            f"describen reticulación ({detail}). Declara simplificaciones: comprueba que cubran este caso"
        )
    else:
        rep.error(
            f"hipótesis: la vista {oid} aplana reticulación a un formato de árbol ({fmt!r}) sin "
            f"declararlo en 'simplifications': {detail} (§15.3, E.10)"
        )


def _check_scope_coherence(claims: list[dict], hyps: list[dict], rep) -> None:
    """Si una afirmación se declara dentro de una hipótesis, la hipótesis lo sabe."""
    known = {h.get("id"): (set(_ids(h, "included_claim_ids")), set(_ids(h, "excluded_claim_ids"))) for h in hyps}
    for c in claims:
        scope = c.get("scope") if isinstance(c.get("scope"), dict) else {}
        for hid in scope.get("hypothesis_ids") or []:
            if hid not in known:
                continue
            included, excluded = known[hid]
            cid = c.get("id", "(sin id)")
            if cid not in included and cid not in excluded:
                rep.warn(
                    f"hipótesis: {cid} limita su alcance a {hid}, que no la incluye ni la excluye. "
                    "El alcance de §9.3 y el conjunto de §15.1 deben decir lo mismo"
                )


# --- vistas y mezcla de topologías (§17 paso 9) -----------------------------

def _check_view_mixing(views: list[dict], hyps: list[dict], index: dict[str, dict], rep) -> None:
    """Dos hipótesis incompatibles pueden coexistir; en un mismo árbol, no."""
    hyp_by_id = {h.get("id"): h for h in hyps}
    groups: dict[str, set[str]] = defaultdict(set)
    for h in hyps:
        for gid in _ids(h, "conflict_group_ids"):
            groups[gid].add(h.get("id"))

    for v in views:
        vid = v.get("id", "(sin id)")
        used = _ids(v, "hypothesis_ids")
        selected = set(_ids(v, "selected_claim_ids"))
        excluded_here = set(_ids(v, "excluded_claim_ids"))

        for cid in sorted(selected & excluded_here):
            rep.error(f"hipótesis: la vista {vid} selecciona y excluye {cid} a la vez")

        for a in used:
            for b in used:
                if a >= b:
                    continue
                ha = hyp_by_id.get(a)
                if ha and b in _ids(ha, "alternative_hypothesis_ids"):
                    rep.error(
                        f"hipótesis: la vista {vid} materializa {a} y {b}, que se declaran "
                        "alternativas. §17 paso 9: no se mezclan topologías incompatibles"
                    )
                shared = [g for g, members in groups.items() if a in members and b in members]
                if shared:
                    rep.error(
                        f"hipótesis: la vista {vid} materializa {a} y {b}, del mismo grupo de "
                        f"conflicto {shared[0]!r}. §15.2 los define como mutuamente excluyentes"
                    )

        for hid in used:
            h = hyp_by_id.get(hid)
            if not h:
                continue
            for cid in sorted(selected & set(_ids(h, "excluded_claim_ids"))):
                rep.error(
                    f"hipótesis: la vista {vid} selecciona {cid}, que {hid} excluye por "
                    "incompatible (§15.2)"
                )
            for cid in _ids(h, "required_claim_ids"):
                if cid not in selected:
                    rep.error(
                        f"hipótesis: la vista {vid} materializa {hid} sin seleccionar su "
                        f"requisito {cid} (§15.2)"
                    )

        if used:
            for cid in sorted(selected):
                c = index.get(cid)
                scope = c.get("scope") if isinstance(c, dict) and isinstance(c.get("scope"), dict) else {}
                declared = [h for h in (scope.get("hypothesis_ids") or []) if isinstance(h, str)]
                if declared and not set(declared) & set(used):
                    rep.warn(
                        f"hipótesis: la vista {vid} selecciona {cid}, cuyo alcance se limita a "
                        f"{declared} y no a las hipótesis de la vista {used} (§9.3)"
                    )


# --- fuentes y contraevidencias (§15.1) -------------------------------------

def _check_evidence_links(hyps: list[dict], index: dict[str, dict], rep) -> None:
    """Una hipótesis carga su oposición, o no es una hipótesis."""
    for h in hyps:
        hid = h.get("id", "(sin id)")
        included = set(_ids(h, "included_claim_ids"))
        favourable = _ids(h, "supporting_evidence_ids")
        against = _ids(h, "counterevidence_ids")
        pro_sources = _ids(h, "supporting_source_ids")
        con_sources = _ids(h, "opposing_source_ids")

        if not favourable and not pro_sources:
            rep.error(
                f"hipótesis: {hid} no enlaza evidencia ni fuente favorable. §15.1 exige ambas "
                "cosas en el conjunto"
            )
        elif not pro_sources:
            rep.warn(f"hipótesis: {hid} no enlaza fuentes favorables (§15.1)")

        if not against and not con_sources:
            rep.warn(
                f"hipótesis: {hid} no registra contraevidencia ni fuentes opuestas. E.9 reserva "
                "sitio para la oposición: una hipótesis sin él es una conclusión disfrazada (§15.1)"
            )

        for eid in favourable:
            _check_evidence_direction(hid, eid, included, index, rep, favourable=True)
        for eid in against:
            _check_evidence_direction(hid, eid, included, index, rep, favourable=False)

        dims = h.get("epistemic_dimensions") if isinstance(h.get("epistemic_dimensions"), dict) else {}
        disputed = dims.get("acceptance") in ("mixed_acceptance", "minority_position")
        if disputed and not _ids(h, "alternative_hypothesis_ids"):
            rep.warn(
                f"hipótesis: {hid} declara acceptance={dims.get('acceptance')!r} y no enlaza "
                "ninguna alternativa. Si hay disputa, hay otra posición que nombrar (§14.5)"
            )

        for other in _ids(h, "alternative_hypothesis_ids"):
            target = index.get(other)
            if isinstance(target, dict) and hid not in _ids(target, "alternative_hypothesis_ids"):
                rep.warn(
                    f"hipótesis: {hid} declara alternativa a {other}, que no le devuelve el enlace. "
                    "La relación de §14.5 es simétrica"
                )


def _check_evidence_direction(
    hid: str, eid: str, included: set[str], index: dict[str, dict], rep, favourable: bool
) -> None:
    """La evidencia enlazada debe apuntar en el sentido que la hipótesis dice."""
    ev = index.get(eid)
    if not isinstance(ev, dict):
        return
    supports = set(_ids(ev, "supports_claim_ids"))
    challenges = set(_ids(ev, "challenges_claim_ids"))
    wanted, opposite = (supports, challenges) if favourable else (challenges, supports)
    rol = "favorable" if favourable else "contraria"

    if included & wanted:
        return
    if included & opposite:
        rep.error(
            f"hipótesis: {hid} enlaza {eid} como evidencia {rol}, pero {eid} "
            f"{'cuestiona' if favourable else 'respalda'} las afirmaciones que la hipótesis "
            f"incluye ({sorted(included & opposite)}). El sentido está invertido (§6.4)"
        )
    elif included:
        rep.warn(
            f"hipótesis: {hid} enlaza {eid} como evidencia {rol}, pero {eid} no se relaciona con "
            "ninguna de sus afirmaciones incluidas (§6.4)"
        )


# --- entrada ----------------------------------------------------------------

def _check_conflict_groups(hyps, data, rep) -> None:
    """Todo grupo de conflicto citado tiene que existir, y servir para algo.

    Antes eran cadenas libres y derivaron solas: dos fixtures llegaron a usar
    convenciones distintas para el mismo mecanismo. Con identificador opaco hay
    integridad referencial, y con registro propio hay un sitio donde decir en
    qué consiste el desacuerdo — saber que dos hipótesis chocan vale poco si no
    se dice en qué (ISSUE-000036).
    """
    grupos = {r["id"] for r in _by_prefix(data, "CONFLICT")}
    usados: dict[str, list[str]] = {}
    for h in hyps:
        for g in h.get("conflict_group_ids") or []:
            usados.setdefault(g, []).append(h["id"])

    for g, quienes in sorted(usados.items()):
        if g not in grupos:
            rep.error(
                f"hipótesis: {', '.join(sorted(quienes))} cita el grupo de conflicto {g}, "
                f"que no existe en conflict-groups.jsonl (§15.2)"
            )
        elif len(quienes) < 2:
            # Un grupo con un solo miembro no excluye nada: o falta la rival, o
            # el grupo sobra. Aviso, no error: puede estar a medio construir.
            rep.warn(
                f"hipótesis: el grupo de conflicto {g} sólo lo cita {quienes[0]}; "
                f"un conflicto necesita al menos dos hipótesis que se excluyan (§15.2)"
            )

    for g in sorted(grupos - set(usados)):
        rep.warn(
            f"hipótesis: el grupo de conflicto {g} está declarado y ninguna hipótesis "
            f"lo cita"
        )


def check(data: dict[str, list[dict]], rep) -> None:
    index = _index(data)
    claims = _by_prefix(data, CLAIM)
    hyps = _by_prefix(data, HYP)
    views = _by_prefix(data, PHYVIEW, TAXVIEW)

    if not hyps and not views:
        rep.info(
            "hipótesis: no hay hipótesis ni vistas todavía; la familia se ejecutó sin material "
            "que comprobar"
        )
    elif hyps and not views:
        rep.info(
            "hipótesis: no hay vistas en el conjunto cargado, así que las comprobaciones de "
            "mezcla de topologías no se han ejecutado. §16.2 sitúa las vistas en knowledge/views/"
        )

    _check_requirements(hyps, index, rep)
    _check_incompatible_selection(hyps, views, claims, rep)
    _check_topology(hyps, views, index, rep)
    _check_scope_coherence(claims, hyps, rep)
    _check_view_mixing(views, hyps, index, rep)
    _check_evidence_links(hyps, index, rep)
    _check_conflict_groups(hyps, data, rep)
