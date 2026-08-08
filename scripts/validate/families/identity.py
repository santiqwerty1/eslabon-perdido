"""Familia «Identidad» de §19.2.

§19.2 enumera la familia en cuatro líneas. Ésta es la correspondencia exacta
entre cada línea de la guía y las comprobaciones implementadas:

| Línea de §19.2                               | Función              |
|----------------------------------------------|----------------------|
| «alias no duplicados de manera ambigua»       | `_check_aliases`     |
| «homónimos taxonómicos no fusionados»         | `_check_homonyms`    |
| «nombre y concepto taxonómico diferenciados»  | `_check_name_concept`|
| «espécimen y taxón diferenciados»             | `_check_specimen`    |

Se añade además, por encargo explícito, la línea que §19.2 coloca bajo
«Integridad referencial» porque su materia es la identidad:

| «las fusiones conservan redirecciones»        | `_check_merges`      |

Apoyos normativos usados: §7.1 (distinciones obligatorias), §7.2 (un nombre no
contiene circunscripción), §7.3 (el concepto es el uso de un nombre *según una
fuente*), §7.7 (un espécimen no se convierte en taxón), §7.9 (rasgo frente a
observación), §14.1 y §14.5 (tratamiento de cada predicado), §16.4 (nada se
fusiona sin operación registrada y reversible) y §10.6 (`record_status`).

Nota de degradación: la familia no importa nada de `validate.py` ni de
`jsonschema`. Repite a propósito dos comprobaciones estructurales baratas
—prefijo contra `entity_type`, y campos de circunscripción en un `NAME-`—
porque en esta máquina la familia `schema` puede quedarse sin ejecutar
(ISSUE-000029) y son justo las que confunden nombre, concepto y entidad.
"""

from __future__ import annotations

import re

NAME = "identity"
PHASE = None  # ejecutable: sólo usa tipos ya implementados

ID_RE = re.compile(
    r"\b(SEC|PASSAGE|MENTION|SRC|NAME|TAXCONCEPT|CLADE|LINEAGE|POP|SPECIMEN|SITE|"
    r"REGION|OCC|TRAIT|TRAITOBS|GENE|ALLELE|EVENT|CLAIM|EVID|DATASET|ANALYSIS|"
    r"RESULT|HYP|TAXVIEW|PHYVIEW|CAMP|CHAPTER|MECH|GAME|ISSUE|TERM|TIME)-[0-9]{6}\b"
)

# Los ocho ficheros que comparten entity.json (§16.2, Apéndice E.5).
ENTITY_FILES = (
    "clades.jsonl",
    "lineages.jsonl",
    "populations.jsonl",
    "specimens.jsonl",
    "sites.jsonl",
    "regions.jsonl",
    "occurrences.jsonl",
    "traits.jsonl",
)

# entity_type -> prefijo obligatorio de §16.3.
TYPE_PREFIX = {
    "biological_lineage": "LINEAGE",
    "clade": "CLADE",
    "population": "POP",
    "specimen": "SPECIMEN",
    "site": "SITE",
    "region": "REGION",
    "occurrence": "OCC",
    "trait": "TRAIT",
}

# Identidades taxonómicas: lo que un espécimen NO es (§7.7).
TAXONOMIC_PREFIXES = ("TAXCONCEPT", "CLADE", "LINEAGE", "NAME")

# Predicados que tratan al sujeto o al objeto como taxón o linaje. Excluidos a
# propósito los modales `possible_ancestor_of` y `possible_sampled_ancestor_of`:
# §14.1 los define como afirmación modal, y un espécimen sí puede ser ancestro
# muestreado posible. `member_of` tampoco entra: un espécimen puede ser miembro
# de una población sin dejar de ser un objeto físico.
TAXON_ONLY_PREDICATES = {
    "descends_from",
    "diverges_from",
    "sister_group_of",
    "stem_lineage_of",
    "crown_group_of",
    "contains",
}

# Predicados que sitúan una entidad dentro de una taxonomía: su objeto debe ser
# un concepto, nunca un nombre suelto (§7.2, §7.3, §14.5 `clasificado_como_por`).
CONCEPT_TARGET_PREDICATES = {
    "assigned_to",
    "classified_as_by",
    "historically_classified_as",
}

# §7.9 y trait-observation.json: el portador declarado y el identificador del
# portador tienen que ser la misma cosa.
BEARER_PREFIX = {
    "specimen": ("SPECIMEN",),
    "population": ("POP",),
    "taxon_concept": ("TAXCONCEPT",),
    "clade": ("CLADE",),
    "biological_lineage": ("LINEAGE",),
    "analysis": ("ANALYSIS",),
}


def _norm(text: str) -> str:
    """Normaliza una grafía para comparar: espacios colapsados y sin caja."""
    return " ".join(str(text or "").split()).casefold()


def _prefix(rid: object) -> str:
    return str(rid).split("-", 1)[0] if isinstance(rid, str) and "-" in rid else ""


def _index(data: dict[str, list[dict]]) -> dict[str, tuple[dict, str]]:
    """Mapa identificador -> (registro, fichero) sobre todo el libro mayor."""
    out: dict[str, tuple[dict, str]] = {}
    for fname, recs in data.items():
        for rec in recs:
            rid = rec.get("id")
            if isinstance(rid, str) and rid not in out:
                out[rid] = (rec, fname)
    return out


def _entities(data: dict[str, list[dict]]):
    for fname in ENTITY_FILES:
        for rec in data.get(fname, []):
            yield fname, rec


def _entity_object_id(claim: dict) -> str | None:
    obj = claim.get("object")
    if isinstance(obj, dict):
        val = obj.get("entity_id")
        if isinstance(val, str):
            return val
    return None


# --- «alias no duplicados de manera ambigua» ---------------------------------

def _check_aliases(data: dict[str, list[dict]], rep, index) -> None:
    """§19.2 Identidad, línea 1.

    Un alias afirma «esto designa la misma entidad». Es ambiguo cuando dos
    entidades activas se lo disputan, cuando una entidad se declara alias de sí
    misma, o cuando el alias apunta a otra entidad que sigue activa: eso último
    es una fusión de hecho sin la operación `MERGE_CONFIRMED_IDENTITIES` que
    exige §16.4. Un alias que apunta a un registro ya `merged` no es un error:
    es exactamente la redirección que comprueba `_check_merges`.
    """
    claimed: dict[str, list[str]] = {}

    for fname, rec in _entities(data):
        rid = rec.get("id")
        aliases = rec.get("alias_ids") or []
        if not isinstance(aliases, list):
            continue

        if isinstance(rid, str) and rid in aliases:
            rep.error(f"identidad: {rid} se declara alias de sí misma ({fname})")

        vistos = [a for a in aliases if isinstance(a, str)]
        if len(set(vistos)) != len(vistos):
            rep.warn(f"identidad: {rid} repite un alias en alias_ids ({fname})")

        if rec.get("record_status") != "active":
            # Un registro fusionado conserva sus alias como historia; no los
            # reclama para sí (§0.1: nunca se borra, pero tampoco compite).
            continue

        for alias in set(vistos):
            claimed.setdefault(alias, []).append(str(rid))

            if alias == rid:
                continue  # ya se informó como autorreferencia
            destino = index.get(alias)
            if destino is None:
                continue  # la existencia la comprueba la familia `references`
            drec, dfile = destino
            if dfile in ENTITY_FILES and drec.get("record_status") == "active":
                rep.error(
                    f"identidad: {rid} declara alias a {alias}, que es otra entidad "
                    f"activa: es una fusión de hecho sin MERGE_CONFIRMED_IDENTITIES "
                    f"(§16.4)"
                )

    for alias, duenos in sorted(claimed.items()):
        unicos = sorted(set(duenos))
        if len(unicos) > 1:
            rep.error(
                f"identidad: el alias {alias} es ambiguo, lo reclaman "
                f"{', '.join(unicos)} (§19.2)"
            )

    # Etiquetas idénticas dentro del mismo tipo de entidad. No es un error —dos
    # registros pueden documentar cosas distintas con el mismo rótulo— pero sí
    # es la ambigüedad que §19.2 pide señalar; §19.1 exige entonces issue.
    por_etiqueta: dict[tuple[str, str], list[str]] = {}
    for _fname, rec in _entities(data):
        if rec.get("record_status") != "active":
            continue
        clave = (str(rec.get("entity_type")), _norm(rec.get("preferred_label", "")))
        if clave[1]:
            por_etiqueta.setdefault(clave, []).append(str(rec.get("id")))
    for (etype, etiqueta), ids in sorted(por_etiqueta.items()):
        if len(ids) > 1:
            rep.warn(
                f"identidad: {len(ids)} entidades activas de tipo {etype} comparten "
                f"la etiqueta {etiqueta!r} ({', '.join(sorted(ids))}); el "
                f"identificador es opaco (§16.3), así que la etiqueta no basta "
                f"para distinguirlas"
            )


# --- «homónimos taxonómicos no fusionados» -----------------------------------

def _check_homonyms(data: dict[str, list[dict]], rep, index) -> None:
    """§19.2 Identidad, línea 2, sostenida en §7.2 y §7.3.

    Un mismo nombre puede haber servido a conceptos distintos. Fusionar dos
    registros que comparten grafía pero difieren en autoría destruye esa
    historia y es justo lo que §4.9 y §7.2 prohíben. La comprobación no es
    «no puede haber grafías repetidas» —eso sería lo contrario de lo que pide
    la guía— sino «una grafía repetida no puede haber terminado fusionada».
    """
    nombres = data.get("taxonomic-names.jsonl", [])
    por_grafia: dict[str, list[dict]] = {}
    for n in nombres:
        grafia = _norm(n.get("canonical_spelling", ""))
        if grafia:
            por_grafia.setdefault(grafia, []).append(n)

    for grafia, grupo in sorted(por_grafia.items()):
        if len(grupo) < 2:
            continue
        ids = sorted(str(n.get("id")) for n in grupo)
        fusionados = [n for n in grupo if n.get("record_status") == "merged"]
        autorias = {n.get("authorship") for n in grupo if n.get("authorship")}
        rangos = {n.get("rank_when_established") for n in grupo}
        distintos = len(autorias) > 1 or len(rangos) > 1

        if fusionados and distintos:
            rep.error(
                f"identidad: la grafía {grafia!r} tiene registros con autoría o "
                f"rango distintos y alguno quedó fusionado ({ids}): son homónimos "
                f"y §19.2 prohíbe fusionarlos"
            )
        elif fusionados:
            rep.warn(
                f"identidad: la grafía {grafia!r} tiene un registro fusionado "
                f"({ids}) y no consta autoría que los distinga; confirmar que no "
                f"eran homónimos antes de dar la fusión por buena (§7.2)"
            )
        elif distintos:
            rep.info(
                f"identidad: la grafía {grafia!r} corresponde a {len(grupo)} "
                f"nombres separados con autoría o rango distintos ({ids}): "
                f"homonimia conservada, que es lo correcto"
            )
        else:
            rep.warn(
                f"identidad: {len(grupo)} nombres comparten la grafía {grafia!r} "
                f"sin autoría ni rango que los distinga ({ids}); no puede decidirse "
                f"si son homónimos o duplicados"
            )

    conceptos = data.get("taxon-concepts.jsonl", [])

    # Dos conceptos del mismo nombre según fuentes distintas son homónimos
    # conceptuales legítimos (§7.3). Fusionarlos borra una circunscripción.
    por_nombre: dict[str, list[dict]] = {}
    for c in conceptos:
        nid = c.get("name_id")
        if isinstance(nid, str):
            por_nombre.setdefault(nid, []).append(c)
    for nid, grupo in sorted(por_nombre.items()):
        if len(grupo) < 2:
            continue
        fuentes = {c.get("according_to_source_id") for c in grupo}
        if len(fuentes) < 2:
            continue
        ids = sorted(str(c.get("id")) for c in grupo)
        fusionados = [c for c in grupo if c.get("record_status") == "merged"]
        if fusionados:
            rep.error(
                f"identidad: {ids} usan el nombre {nid} según fuentes distintas y "
                f"alguno quedó fusionado: son conceptos homónimos, no duplicados "
                f"(§7.3)"
            )
        else:
            rep.info(
                f"identidad: el nombre {nid} sostiene {len(grupo)} conceptos según "
                f"fuentes distintas ({ids}); conservados por separado"
            )

    # Homonimia o incompatibilidad declarada expresamente entre conceptos.
    for c in conceptos:
        cid = str(c.get("id"))
        for rel in c.get("relation_to_other_concepts") or []:
            if not isinstance(rel, dict):
                continue
            if rel.get("relation") not in {"conceptual_homonym", "incompatible"}:
                continue
            otro_id = rel.get("other_concept_id")
            pareja = [(cid, c)]
            destino = index.get(otro_id) if isinstance(otro_id, str) else None
            if destino is not None:
                pareja.append((str(otro_id), destino[0]))
            for rid, rec in pareja:
                if rec.get("record_status") == "merged":
                    rep.error(
                        f"identidad: {rid} está declarado "
                        f"{rel.get('relation')} con {otro_id if rid == cid else cid} "
                        f"y su registro figura como fusionado (§19.2: los homónimos "
                        f"no se fusionan)"
                    )


# --- «nombre y concepto taxonómico diferenciados» ----------------------------

def _check_name_concept(data: dict[str, list[dict]], rep, index) -> None:
    """§19.2 Identidad, línea 3, sostenida en §7.2 y §7.3.

    Lo que convierte un nombre en concepto es la fuente que lo circunscribe:
    por eso `according_to_source_id` es obligatorio y por eso un `NAME-` no
    puede llevar circunscripción. Un `assigned_to` que apunta a un nombre en
    vez de a un concepto asigna la entidad a una etiqueta sin contenido.
    """
    for c in data.get("taxon-concepts.jsonl", []):
        cid = c.get("id")

        nid = c.get("name_id")
        if not nid:
            rep.error(f"identidad: {cid} no declara name_id: sin nombre no hay concepto (§7.3)")
        elif _prefix(nid) != "NAME":
            rep.error(
                f"identidad: {cid}.name_id apunta a {nid}, que no es un nombre "
                f"taxonómico (§7.2)"
            )
        elif nid not in index:
            rep.error(f"identidad: {cid}.name_id apunta a {nid}, que no existe")

        sid = c.get("according_to_source_id")
        if not sid:
            rep.error(
                f"identidad: {cid} no declara according_to_source_id; sin fuente "
                f"sólo hay un nombre, no un concepto (§7.3)"
            )
        elif _prefix(sid) != "SRC":
            rep.error(
                f"identidad: {cid}.according_to_source_id apunta a {sid}, que no es "
                f"una fuente"
            )
        elif sid not in index:
            rep.error(f"identidad: {cid}.according_to_source_id apunta a {sid}, que no existe")

    # Un nombre no circunscribe (§7.2). El esquema lo impide con
    # additionalProperties, pero la familia `schema` puede no haberse ejecutado.
    prohibidos = (
        "circumscription",
        "included_entity_ids",
        "excluded_entity_ids",
        "rank_assignment",
        "according_to_source_id",
        "parent_concept_id",
    )
    for n in data.get("taxonomic-names.jsonl", []):
        for campo in prohibidos:
            if campo in n:
                rep.error(
                    f"identidad: el nombre {n.get('id')} lleva {campo!r}; la "
                    f"circunscripción pertenece al TaxonConcept, no al nombre (§7.2)"
                )

    for claim in data.get("claims.jsonl", []):
        if claim.get("predicate") not in CONCEPT_TARGET_PREDICATES:
            continue
        objetivo = _entity_object_id(claim)
        if objetivo and _prefix(objetivo) == "NAME":
            rep.error(
                f"identidad: {claim.get('id')} usa {claim.get('predicate')} contra "
                f"{objetivo}, que es un nombre y no un concepto: un nombre no tiene "
                f"circunscripción (§7.2, §14.5)"
            )


# --- «espécimen y taxón diferenciados» ---------------------------------------

def _check_specimen(data: dict[str, list[dict]], rep, index) -> None:
    """§19.2 Identidad, línea 4, sostenida en §7.7 y §7.9.

    Un espécimen es un objeto físico. No se convierte automáticamente en taxón,
    especie, población ni ancestro. Se comprueban las tres vías por las que la
    confusión entra en los datos: el alias, el predicado y el portador de una
    observación de rasgo.
    """
    for fname, rec in _entities(data):
        rid = rec.get("id")
        etype = rec.get("entity_type")

        esperado = TYPE_PREFIX.get(str(etype))
        if esperado and _prefix(rid) != esperado:
            rep.error(
                f"identidad: {rid} declara entity_type {etype!r} pero su prefijo no "
                f"es {esperado}- (§16.3)"
            )

        aliases = [a for a in (rec.get("alias_ids") or []) if isinstance(a, str)]
        if etype == "specimen":
            for a in aliases:
                if _prefix(a) in TAXONOMIC_PREFIXES:
                    rep.error(
                        f"identidad: el espécimen {rid} declara alias a {a}: un "
                        f"espécimen no es un taxón ni un linaje (§7.7). La relación "
                        f"correcta es una afirmación 'assigned_to' con procedencia"
                    )
        elif etype in {"clade", "biological_lineage", "population"}:
            for a in aliases:
                if _prefix(a) == "SPECIMEN":
                    rep.error(
                        f"identidad: {rid} ({etype}) declara alias al espécimen {a}: "
                        f"el material que documenta un grupo no es el grupo (§7.7)"
                    )

    for claim in data.get("claims.jsonl", []):
        if claim.get("predicate") not in TAXON_ONLY_PREDICATES:
            continue
        extremos = (("sujeto", claim.get("subject_id")), ("objeto", _entity_object_id(claim)))
        for papel, extremo in extremos:
            if isinstance(extremo, str) and _prefix(extremo) == "SPECIMEN":
                rep.error(
                    f"identidad: {claim.get('id')} usa {claim.get('predicate')} con "
                    f"el espécimen {extremo} como {papel}; ese predicado trata a sus "
                    f"extremos como taxones o linajes (§7.7, §14.1). Para un "
                    f"espécimen existen los predicados modales "
                    f"'possible_ancestor_of' y 'possible_sampled_ancestor_of'"
                )

    for obs in data.get("trait-observations.jsonl", []):
        btype = obs.get("bearer_type")
        bid = obs.get("bearer_id")
        esperados = BEARER_PREFIX.get(str(btype))
        if esperados and isinstance(bid, str) and _prefix(bid) not in esperados:
            rep.error(
                f"identidad: {obs.get('id')} declara bearer_type {btype!r} con "
                f"portador {bid}; observar un rasgo en un espécimen no es "
                f"observarlo en un taxón (§7.9)"
            )


# --- «las fusiones conservan redirecciones» ----------------------------------

def _redirect_target(rec: dict, entrantes: dict[str, list[str]], index) -> str | None:
    """Destino de una fusión.

    Se admiten dos canales, porque sólo `entity.json` tiene `alias_ids`:
    el registro superviviente que reclama al fusionado como alias, o una nota
    del propio registro que cite el identificador de destino (§16.4 exige
    operación registrada y reversible, no un campo concreto).
    """
    rid = str(rec.get("id"))
    reclamantes = entrantes.get(rid) or []
    if reclamantes:
        return reclamantes[0]
    citados = [
        m.group(0)
        for nota in rec.get("notes") or []
        for m in ID_RE.finditer(str(nota))
        if m.group(0) != rid
    ]
    for candidato in citados:
        if candidato in index:
            return candidato
    # Se devuelve igualmente el primer destino citado aunque no exista: así el
    # informe distingue «no hay redirección» de «la redirección está rota».
    return citados[0] if citados else None


def _check_merges(data: dict[str, list[dict]], rep, index) -> None:
    """§19.2 Integridad referencial, línea 3.

    Un registro `merged` sin redirección es información perdida: quien tenga el
    identificador viejo no puede llegar al nuevo, y §0.1 y §16.4 prohíben que
    fusionar equivalga a borrar. Se comprueba además que la cadena de
    redirecciones termine: una fusión circular no lleva a ningún sitio.
    """
    entrantes: dict[str, list[str]] = {}
    for _fname, rec in _entities(data):
        if rec.get("record_status") != "active":
            continue
        for alias in rec.get("alias_ids") or []:
            if isinstance(alias, str):
                entrantes.setdefault(alias, []).append(str(rec.get("id")))

    destinos: dict[str, str] = {}
    fusionados: list[tuple[str, dict, str]] = []
    for fname, recs in sorted(data.items()):
        for rec in recs:
            if rec.get("record_status") != "merged":
                continue
            rid = str(rec.get("id"))
            fusionados.append((rid, rec, fname))
            destino = _redirect_target(rec, entrantes, index)
            if destino is None:
                rep.error(
                    f"identidad: {rid} ({fname}) está marcado 'merged' y no conserva "
                    f"redirección: ningún registro activo lo reclama como alias ni "
                    f"sus notas citan destino (§19.2, §16.4)"
                )
                continue
            if destino not in index:
                rep.error(
                    f"identidad: {rid} redirige a {destino}, que no existe (§19.2)"
                )
                continue
            destinos[rid] = destino

    ciclos_vistos: set[frozenset[str]] = set()
    for rid, _rec, _fname in fusionados:
        destino = destinos.get(rid)
        visitados = [rid]
        while destino is not None:
            if destino in visitados:
                huella = frozenset(visitados[visitados.index(destino):])
                if huella not in ciclos_vistos:
                    ciclos_vistos.add(huella)
                    rep.error(
                        "identidad: cadena de fusiones circular: "
                        + " → ".join(visitados + [destino])
                    )
                break
            visitados.append(destino)
            destino = destinos.get(destino)
        else:
            final = visitados[-1]
            if final != rid:
                estado = index.get(final, ({}, ""))[0].get("record_status")
                if estado not in {"active", None}:
                    rep.warn(
                        f"identidad: la fusión de {rid} termina en {final}, cuyo "
                        f"record_status es {estado!r}: la redirección no lleva a un "
                        f"registro vigente"
                    )


def check(data: dict[str, list[dict]], rep) -> None:
    index = _index(data)
    _check_aliases(data, rep, index)
    _check_homonyms(data, rep, index)
    _check_name_concept(data, rep, index)
    _check_specimen(data, rep, index)
    _check_merges(data, rep, index)

    conceptos = len(data.get("taxon-concepts.jsonl", []))
    nombres = len(data.get("taxonomic-names.jsonl", []))
    entidades = sum(len(data.get(f, [])) for f in ENTITY_FILES)
    if not (conceptos or nombres or entidades):
        rep.info(
            "identidad: no hay nombres, conceptos ni entidades todavía; la familia "
            "se ejecutó sin material que comprobar"
        )
