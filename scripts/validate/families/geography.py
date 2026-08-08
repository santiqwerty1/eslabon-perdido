"""Familia «geografía» de §19.2.

Las tres exigencias de la guía, hechas asertos:

    1. yacimiento y región no confundidos            §12.1
    2. ubicaciones inferidas marcadas                §12.2, §9.4
    3. coexistencia no inferida sólo por tiempo
       si la geografía es incompatible               §19.2, §14.4

La entidad geográfica de este modelo es deliberadamente delgada (E.5): un
yacimiento no guarda "está en tal región" como campo, sino como afirmación con
procedencia. Por eso casi todo lo que aquí se comprueba se lee de `claims.jsonl`
y no de `sites.jsonl` ni de `regions.jsonl`.

Criterio de severidad (§19.1): es ERROR lo que produce un dato falso —una
región metida dentro de un yacimiento, una coexistencia derivada contra la
geografía registrada—. Es WARNING lo que puede ser una laguna del corpus y no
un fallo del registro: geografía desconocida, localizador ausente. §12.3 pesa
en esta decisión, porque la paleogeografía está pospuesta y las regiones de la
primera versión son abstractas.
"""

from __future__ import annotations

from collections import defaultdict

NAME = "geography"
PHASE = None

SITE = "SITE-"
REGION = "REGION-"
OCC = "OCC-"
TIME = "TIME-"
CLAIM = "CLAIM-"

# §16.2 fija qué vive en cada fichero. El esquema comprueba que el prefijo del
# identificador concuerde con `entity_type`, pero no que el registro esté en el
# fichero que le corresponde: un yacimiento guardado en regions.jsonl pasa el
# esquema y confunde a todo lo que lea el fichero por su nombre.
_FILE_CONTRACT = {
    "sites.jsonl": (SITE, "site"),
    "regions.jsonl": (REGION, "region"),
    "occurrences.jsonl": (OCC, "occurrence"),
}

# §14.1: `miembro_de` es la afirmación canónica y `contiene` su inversa
# derivada. `occurs_in` (§9.1) sitúa algo en un lugar. Los tres sirven para
# expresar contención geográfica, y los tres tienen dirección.
_CONTAINMENT_UP = {"member_of", "occurs_in"}
_CONTAINMENT_DOWN = {"contains"}

# §14.4: `coexiste_con` es preferentemente derivada. Derivarla es exactamente
# donde aparece el error que §19.2 prohíbe.
_COEXISTENCE = {"coexists_with", "may_have_coexisted_with"}
_TEMPORAL_PREDICATES = {"temporally_overlaps_with", "dated_to"}


# --- utilidades -------------------------------------------------------------

def _index(data: dict[str, list[dict]]) -> dict[str, dict]:
    """Todos los registros por identificador, vengan del fichero que vengan."""
    idx: dict[str, dict] = {}
    for recs in data.values():
        for rec in recs:
            if isinstance(rec, dict) and isinstance(rec.get("id"), str):
                idx.setdefault(rec["id"], rec)
    return idx


def _by_prefix(data: dict[str, list[dict]], prefix: str) -> list[dict]:
    """Registros cuyo identificador lleva el prefijo dado.

    Se busca por prefijo y no por nombre de fichero para que la familia sirva
    igual sobre knowledge/records/ que sobre un fixture de tests/fixtures/.
    """
    out = []
    for recs in data.values():
        for rec in recs:
            if isinstance(rec, dict) and isinstance(rec.get("id"), str) and rec["id"].startswith(prefix):
                out.append(rec)
    return out


def _object_entity(claim: dict) -> str | None:
    """Identificador de la entidad-objeto, o None si el objeto no es entidad."""
    obj = claim.get("object")
    if isinstance(obj, dict) and isinstance(obj.get("entity_id"), str):
        return obj["entity_id"]
    return None


def _label(index: dict[str, dict], rid: str) -> str:
    rec = index.get(rid)
    lbl = rec.get("preferred_label") if isinstance(rec, dict) else None
    return f"{rid} ({lbl})" if lbl else rid


# --- 1. yacimiento y región no confundidos (§12.1) --------------------------

def _check_entity_kinds(data: dict[str, list[dict]], index: dict[str, dict], rep) -> None:
    """El tipo declarado, el prefijo y el fichero deben decir lo mismo."""
    for fname, (prefix, entity_type) in _FILE_CONTRACT.items():
        for rec in data.get(fname, []):
            rid = rec.get("id")
            if not isinstance(rid, str):
                continue
            if not rid.startswith(prefix):
                rep.error(
                    f"geografía: {rid} está en {fname}, que §16.2 reserva a {prefix}NNNNNN. "
                    "Yacimiento, región y ocurrencia no comparten fichero (§12.1)"
                )
            if rec.get("entity_type") != entity_type:
                rep.error(
                    f"geografía: {rid} está en {fname} pero declara "
                    f"entity_type={rec.get('entity_type')!r} en vez de {entity_type!r} (§12.1)"
                )

    # El mismo desajuste visto desde el prefijo, para registros que no estén en
    # el fichero canónico (fixtures, ficheros agregados).
    for prefix, entity_type in ((SITE, "site"), (REGION, "region"), (OCC, "occurrence")):
        for rec in _by_prefix(data, prefix):
            if rec.get("entity_type") != entity_type:
                rep.error(
                    f"geografía: {rec['id']} lleva prefijo {prefix} y declara "
                    f"entity_type={rec.get('entity_type')!r}: yacimiento y región son entidades "
                    "distintas, no dos etiquetas del mismo sitio (§12.1)"
                )


def _check_geographic_fields(data: dict[str, list[dict]], index: dict[str, dict], rep) -> None:
    """`site_ids` contiene yacimientos y `region_ids` regiones, nunca al revés.

    §12.1. Incluye `scope.region_ids` de las afirmaciones, que la familia
    `references` no alcanza porque sólo recorre claves de primer nivel.
    """
    expect = {"site_ids": (SITE, "site", "yacimiento"), "region_ids": (REGION, "region", "región")}

    def inspect(owner: str, field: str, values, nested: bool) -> None:
        prefix, entity_type, human = expect[field]
        if not isinstance(values, list):
            return
        for ref in values:
            if not isinstance(ref, str):
                continue
            target = index.get(ref)
            if target is None:
                if nested:
                    # references sólo mira campos `*_ids` de primer nivel.
                    rep.error(f"geografía: {owner}.scope.{field} apunta a {ref}, que no existe")
                continue
            if not ref.startswith(prefix) or target.get("entity_type") != entity_type:
                rep.error(
                    f"geografía: {owner}.{'scope.' if nested else ''}{field} incluye {ref}, que es "
                    f"{target.get('entity_type')!r} y no {human} (§12.1)"
                )

    for recs in data.values():
        for rec in recs:
            if not isinstance(rec, dict):
                continue
            owner = rec.get("id", "(sin id)")
            for field in expect:
                if field in rec:
                    inspect(owner, field, rec[field], nested=False)
            scope = rec.get("scope")
            if isinstance(scope, dict) and "region_ids" in scope:
                inspect(owner, "region_ids", scope["region_ids"], nested=True)


def _check_containment_direction(claims: list[dict], index: dict[str, dict], rep) -> None:
    """Un yacimiento está en una región; una región no está en un yacimiento.

    §12.1 más §14.1: `contiene` es la inversa derivada de `miembro_de`, así que
    una afirmación `contains` escrita a mano y sin `derivation` es una vía
    cómoda para invertir la jerarquía sin que se note.
    """
    for c in claims:
        subj, pred, obj = c.get("subject_id"), c.get("predicate"), _object_entity(c)
        cid = c.get("id", "(sin id)")
        if not isinstance(subj, str) or obj is None:
            continue
        if pred in _CONTAINMENT_UP and subj.startswith(REGION) and obj.startswith(SITE):
            rep.error(
                f"geografía: {cid} coloca la región {subj} dentro del yacimiento {obj} "
                f"con '{pred}'. La contención va del yacimiento a la región (§12.1)"
            )
        if pred in _CONTAINMENT_DOWN and subj.startswith(SITE) and obj.startswith(REGION):
            rep.error(
                f"geografía: {cid} hace que el yacimiento {subj} contenga la región {obj}. "
                "La contención va del yacimiento a la región (§12.1)"
            )
        if pred == "contains" and subj.startswith((SITE, REGION)) and obj.startswith((SITE, REGION)):
            if not c.get("derivation"):
                rep.warn(
                    f"geografía: {cid} afirma 'contains' entre entidades geográficas sin "
                    "declararse derivada. §14.1 la define como inversa derivada de 'member_of'"
                )


# --- 2. ubicaciones inferidas marcadas (§12.2) ------------------------------

def _is_geographic_claim(claim: dict) -> bool:
    obj = _object_entity(claim)
    return claim.get("predicate") == "occurs_in" or (obj is not None and obj.startswith((SITE, REGION)))


def _check_inference_marks(claims: list[dict], rep) -> None:
    """Lo inferido se marca como inferido.

    §12.2 admite ubicaciones inferidas; lo que no admite es que una inferencia
    circule con el aspecto de una observación. Las dos marcas disponibles son
    `derivation` (§9.4: regla y dependencias) y `provenance.origin = "derived"`,
    y tienen que decir lo mismo.
    """
    for c in claims:
        if not _is_geographic_claim(c):
            continue
        cid = c.get("id", "(sin id)")
        subj = c.get("subject_id") or ""
        prov = c.get("provenance") if isinstance(c.get("provenance"), dict) else {}
        origin = prov.get("origin")
        derivation = c.get("derivation")

        if derivation and origin != "derived":
            rep.error(
                f"geografía: {cid} lleva regla de derivación pero declara origin={origin!r}. "
                "Una ubicación inferida se marca como inferida (§9.4, §12.2)"
            )
        if origin == "derived" and not derivation:
            rep.error(
                f"geografía: {cid} declara origin='derived' sin regla ni dependencias. "
                "Una derivada sin regla no es reproducible (§9.4)"
            )

        # La contención administrativa (yacimiento dentro de región) no exige
        # respaldo observacional: no es una inferencia paleontológica.
        if isinstance(subj, str) and subj.startswith((SITE, REGION)):
            continue
        if not c.get("evidence_ids") and not derivation:
            rep.warn(
                f"geografía: {cid} ubica {subj or '(sin sujeto)'} sin evidencia enlazada y sin "
                "marca de inferencia: no se distingue lo observado de lo supuesto (§12.2, §4.8)"
            )


# --- 3. coexistencia y geografía (§19.2) ------------------------------------

def _region_graph(claims: list[dict]) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    """Grafo de contención: región dentro de región, yacimiento dentro de región."""
    parents: dict[str, set[str]] = defaultdict(set)
    site_regions: dict[str, set[str]] = defaultdict(set)
    for c in claims:
        subj, pred, obj = c.get("subject_id"), c.get("predicate"), _object_entity(c)
        if not isinstance(subj, str) or obj is None:
            continue
        if pred in _CONTAINMENT_UP:
            if subj.startswith(REGION) and obj.startswith(REGION):
                parents[subj].add(obj)
            elif subj.startswith(SITE) and obj.startswith(REGION):
                site_regions[subj].add(obj)
        elif pred in _CONTAINMENT_DOWN:
            if subj.startswith(REGION) and obj.startswith(REGION):
                parents[obj].add(subj)
            elif subj.startswith(REGION) and obj.startswith(SITE):
                site_regions[obj].add(subj)
    return parents, site_regions


def _ancestors(region: str, parents: dict[str, set[str]]) -> set[str]:
    """Regiones que contienen a la dada, con guarda de ciclos."""
    seen: set[str] = set()
    stack = [region]
    while stack:
        for parent in parents.get(stack.pop(), ()):
            if parent not in seen:
                seen.add(parent)
                stack.append(parent)
    return seen


def _footprints(claims: list[dict], site_regions: dict[str, set[str]]) -> dict[str, set[str]]:
    """Regiones en las que consta cada entidad, según las afirmaciones.

    Sólo `occurs_in`. Un yacimiento se resuelve a las regiones que lo contienen;
    si no consta ninguna, no aporta nada: se prefiere «geografía desconocida» a
    inventar una equivalencia entre yacimientos (§4.8). Las ocurrencias trasladan
    su geografía a la entidad a la que se asignan, un solo nivel.
    """
    foot: dict[str, set[str]] = defaultdict(set)
    for c in claims:
        if c.get("predicate") != "occurs_in":
            continue
        subj, obj = c.get("subject_id"), _object_entity(c)
        if not isinstance(subj, str) or obj is None or subj.startswith((SITE, REGION)):
            continue
        if obj.startswith(REGION):
            foot[subj].add(obj)
        elif obj.startswith(SITE):
            foot[subj] |= site_regions.get(obj, set())
    for c in claims:
        if c.get("predicate") != "assigned_to":
            continue
        subj, obj = c.get("subject_id"), _object_entity(c)
        if isinstance(subj, str) and subj.startswith(OCC) and obj is not None:
            foot[obj] |= foot.get(subj, set())
    return foot


def _compatible(fa: set[str], fb: set[str], parents: dict[str, set[str]]) -> bool:
    """Dos huellas son compatibles si comparten región o una contiene a la otra.

    Compartir un ancestro común no basta: dos regiones hermanas dentro de África
    siguen siendo dos sitios distintos. Una huella vacía es geografía
    desconocida, y lo desconocido no es incompatible (§12.2).
    """
    if not fa or not fb:
        return True
    closure_a = {r: _ancestors(r, parents) | {r} for r in fa}
    closure_b = {r: _ancestors(r, parents) | {r} for r in fb}
    for a, ca in closure_a.items():
        for b, cb in closure_b.items():
            if a in cb or b in ca:
                return True
    return False


def _derived_from_time_only(claim: dict, index: dict[str, dict]) -> bool:
    """La derivación se apoya únicamente en material temporal."""
    der = claim.get("derivation")
    if not isinstance(der, dict):
        return False
    deps = der.get("depends_on_ids") or []
    if not deps:
        return False
    for dep in deps:
        if not isinstance(dep, str):
            return False
        if dep.startswith(TIME):
            continue
        rec = index.get(dep)
        if rec is None:
            return False
        if dep.startswith(CLAIM) and (
            rec.get("claim_type") == "temporal" or rec.get("predicate") in _TEMPORAL_PREDICATES
        ):
            continue
        return False
    return True


def _check_coexistence(claims: list[dict], index: dict[str, dict], rep) -> None:
    """Coexistir es coincidir en tiempo *y* en lugar.

    §19.2: «coexistencia no inferida solo por tiempo si la geografía es
    incompatible». §14.4 añade el matiz que fija las severidades: `coexiste_con`
    es preferentemente derivada y explícita si una fuente la afirma. Derivarla
    contra la geografía registrada es un error del sistema; que una fuente la
    afirme contra ella es una discrepancia que merece issue, no un bloqueo.
    """
    parents, site_regions = _region_graph(claims)
    foot = _footprints(claims, site_regions)

    for c in claims:
        if c.get("predicate") not in _COEXISTENCE:
            continue
        cid = c.get("id", "(sin id)")
        subj, obj = c.get("subject_id"), _object_entity(c)
        if not isinstance(subj, str) or obj is None:
            continue
        prov = c.get("provenance") if isinstance(c.get("provenance"), dict) else {}
        derivation = c.get("derivation")
        derived = bool(derivation) or prov.get("origin") == "derived"
        fa, fb = foot.get(subj, set()), foot.get(obj, set())
        compatible = _compatible(fa, fb, parents)

        if derived and isinstance(derivation, dict) and not (derivation.get("depends_on_ids") or []):
            rep.warn(
                f"geografía: {cid} deriva coexistencia sin declarar dependencias, así que no "
                "puede comprobarse sobre qué se apoya (§9.4)"
            )

        if derived and _derived_from_time_only(c, index):
            if not compatible:
                rep.error(
                    f"geografía: {cid} infiere coexistencia entre {_label(index, subj)} y "
                    f"{_label(index, obj)} sólo por solapamiento temporal, y su geografía "
                    f"registrada es incompatible ({sorted(fa)} frente a {sorted(fb)}). §19.2 lo "
                    "prohíbe: coincidir en el tiempo no es coincidir en el lugar"
                )
            elif not fa or not fb:
                rep.warn(
                    f"geografía: {cid} infiere coexistencia sólo por solapamiento temporal y no "
                    f"consta geografía de {subj if not fa else obj}: la comprobación de §19.2 no "
                    "puede ejecutarse"
                )
        elif not compatible:
            rep.warn(
                f"geografía: {cid} afirma coexistencia entre {_label(index, subj)} y "
                f"{_label(index, obj)} pese a geografía incompatible ({sorted(fa)} frente a "
                f"{sorted(fb)}). Si la fuente lo sostiene, requiere issue (§14.4, §19.1)"
            )


# --- entrada ----------------------------------------------------------------

def check(data: dict[str, list[dict]], rep) -> None:
    index = _index(data)
    claims = _by_prefix(data, CLAIM)

    # El aviso no interrumpe: las comprobaciones siguen corriendo por si llega
    # material geográfico por un campo que este recuento no mira.
    if not claims and not _by_prefix(data, SITE) and not _by_prefix(data, REGION):
        rep.info(
            "geografía: no hay yacimientos, regiones ni afirmaciones todavía; la familia se "
            "ejecutó sin material que comprobar"
        )

    _check_entity_kinds(data, index, rep)
    _check_geographic_fields(data, index, rep)
    _check_containment_direction(claims, index, rep)
    _check_inference_marks(claims, rep)
    _check_coexistence(claims, index, rep)
