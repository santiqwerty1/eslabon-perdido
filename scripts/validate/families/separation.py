#!/usr/bin/env python3
"""Familia «Separación de capas» de §19.2.

Es §4.4 convertido en hecho comprobable. La jugabilidad puede seleccionar,
resumir, agrupar y ocultar complejidad; no puede alterar una relación
científica, convertir una hipótesis en hecho ni borrar una controversia. Y §6.8
lo dice del lado del almacenamiento: la proyección de juego referencia
entidades, afirmaciones, eventos y vistas, pero mantiene sus propios datos, que
**no se almacenan dentro de cada nodo científico**.

De ahí las cuatro comprobaciones:

1. el núcleo científico no contiene costos, bonificaciones ni condiciones de
   victoria;
2. la proyección de juego no reescribe afirmaciones científicas;
3. las vistas generadas identifican sus simplificaciones;
4. **la dirección de las referencias** — que es lo que hace la separación
   verificable en vez de declarativa. Una proyección puede apuntar al núcleo:
   ése es su enlace de vuelta al Atlas. El núcleo no puede apuntar a una
   proyección, porque entonces borrar el módulo de campaña rompería datos
   científicos y la prueba de §27.10 dejaría de sostenerse.

Las capas se deciden por el prefijo del identificador, no por la carpeta: un
registro `GAME-` dentro de `knowledge/records/` es una violación aunque el
fichero se llame como toque, y un `CLAIM-` dentro de `game/` también.

Las rutas son constantes de módulo para que las pruebas las reapunten a
`tests/fixtures/` sin tocar el repositorio real.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

NAME = "separation"
PHASE = None

ROOT = Path(__file__).resolve().parents[3]
SCIENCE_DIRS = (
    ROOT / "knowledge" / "views",
    ROOT / "knowledge" / "classifications",
)
PROJECTION_DIRS = (ROOT / "game" / "projections",)
GAME_DIRS = (ROOT / "game" / "campaigns", ROOT / "game" / "mechanics", ROOT / "game" / "core")

ANY_ID_RE = re.compile(r"\b([A-Z]+)-[0-9]{6}\b")

GAME_PREFIXES = {"GAME", "MECH", "CAMP", "CHAPTER"}
PROJECTION_PREFIX = "GAME"
VIEW_PREFIXES = {"TAXVIEW", "PHYVIEW"}
SCIENCE_PREFIXES = {
    "SEC", "PASSAGE", "MENTION", "SRC", "NAME", "TAXCONCEPT", "CLADE", "LINEAGE",
    "POP", "SPECIMEN", "SITE", "REGION", "OCC", "TRAIT", "TRAITOBS", "GENE",
    "ALLELE", "EVENT", "CLAIM", "EVID", "DATASET", "ANALYSIS", "RESULT", "HYP",
    "TAXVIEW", "PHYVIEW", "TIME",
}

# Vocabulario de mecánica. Se comparan piezas de la clave en snake_case, no
# subcadenas: 'rank_system' y 'support' son ciencia legítima y no deben caer.
MECHANIC_TOKENS = {
    "cost", "costs", "upkeep", "price", "budget",
    "bonus", "bonuses", "malus", "buff", "debuff", "penalty", "penalties",
    "reward", "rewards", "loot", "xp", "points", "score", "scoring",
    "victory", "defeat", "win", "lose", "loss", "gameover",
    "unlock", "unlocks", "unlockable", "achievement", "achievements",
    "quest", "objective", "objectives", "difficulty", "balance", "balancing",
    "hp", "mana", "stamina", "energy", "perk", "perks", "tier", "tech",
    "game", "gameplay", "player", "playable", "mechanic", "mechanics",
}
# Claves compuestas que no se parten bien en tokens.
MECHANIC_KEY_RE = re.compile(
    r"(victory_condition|win_condition|lose_condition|game_over|"
    r"condicion_de_victoria|bonificacion|coste|costo|recompensa|puntuacion)"
)

# Campos del núcleo científico. Dentro de la capa 8 significan que la
# proyección ha dejado de referenciar y ha empezado a reescribir.
SCIENCE_ONLY_KEYS = {
    "predicate", "subject_id", "claim_type", "epistemic_dimensions",
    "quantitative_support", "evidence_ids", "counterevidence_ids", "derivation",
    "claim_text", "claim_override", "claim_overrides", "overrides",
    "restated_claim", "rewritten_claim", "corrected_claim",
    "selected_claim_ids", "excluded_claim_ids", "editorial_criteria",
}
# Claves demasiado genéricas para prohibirlas por el nombre: sólo delatan una
# reescritura cuando llevan dentro el registro entero. `content_budget.claims`
# con un número es un presupuesto de contenido, no una afirmación copiada.
SCIENCE_SHAPED_KEYS = {"claims", "object", "claim", "hypotheses", "evidence"}

# §10.1. Lo que no es consenso amplio no se proyecta como hecho sin decirlo.
NON_CONSENSUS = {"mixed_acceptance", "minority_position", "not_assessed"}


# --- carga y clasificación ---------------------------------------------------

def _load_file(path: Path, rep) -> list[dict]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        rep.error(f"separación: {path.name} no se puede leer — {exc}")
        return []
    records: list[dict] = []
    if path.suffix == ".jsonl":
        for n, line in enumerate(text.splitlines(), 1):
            if line.strip():
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    rep.error(f"separación: {path.name}:{n}: JSON inválido — {exc.msg}")
        return records
    try:
        doc = json.loads(text)
    except json.JSONDecodeError as exc:
        rep.error(f"separación: {path.name}: JSON inválido — {exc.msg}")
        return []
    if isinstance(doc, list):
        return [d for d in doc if isinstance(d, dict)]
    return [doc] if isinstance(doc, dict) else []


def _load_dirs(dirs, rep) -> list[tuple[str, dict]]:
    out = []
    for directory in dirs:
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*")):
            if path.is_file() and path.suffix in (".json", ".jsonl"):
                label = str(path.relative_to(ROOT)) if ROOT in path.parents else path.name
                out.extend((label, rec) for rec in _load_file(path, rep))
    return out


def _prefix(rec: dict) -> str | None:
    rid = rec.get("id")
    if isinstance(rid, str) and "-" in rid:
        found = ANY_ID_RE.fullmatch(rid)
        if found:
            return found.group(1)
    return None


def _walk(node, path: str = "", key: str = ""):
    """Emite (ruta, clave, valor) de cada campo, a cualquier hondura.

    Los elementos de una lista se emiten con la clave de su lista: un
    identificador escondido en `alias_ids[0]` tiene que verse igual que uno
    escrito en un campo suelto.
    """
    if isinstance(node, dict):
        for k, value in node.items():
            here = f"{path}.{k}" if path else k
            yield here, k, value
            yield from _walk(value, here, k)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            here = f"{path}[{i}]"
            yield here, key, item
            yield from _walk(item, here, key)


def _strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for value in node.values():
            yield from _strings(value)
    elif isinstance(node, list):
        for item in node:
            yield from _strings(item)


def _tokens(key: str) -> set[str]:
    return {t for t in re.split(r"[^a-z0-9]+", key.lower()) if t}


def _looks_like_record(value) -> bool:
    """¿El valor es un registro completo y no un recuento o una referencia?"""
    if isinstance(value, dict):
        return bool(set(value) & (SCIENCE_ONLY_KEYS | {"id", "provenance", "scope"}))
    if isinstance(value, list):
        return any(isinstance(item, dict) for item in value)
    return False


# --- 1. el núcleo científico no contiene mecánica ----------------------------

def _check_core_free_of_mechanics(science, rep) -> None:
    for where, rec in science:
        if _prefix(rec) in GAME_PREFIXES:
            continue  # ya se señala como registro de capa 8 fuera de sitio
        rid = rec.get("id", "?")
        for path, key, _ in _walk(rec):
            if path.endswith("]"):
                continue  # la clave de la lista ya se ha juzgado una vez
            low = key.lower()
            hit = sorted(_tokens(low) & MECHANIC_TOKENS)
            if not hit and MECHANIC_KEY_RE.search(low.replace("-", "_")):
                hit = [low]
            if hit:
                rep.error(
                    f"separación: {where}:{rid}.{path} es vocabulario de mecánica "
                    f"({', '.join(hit)}) dentro del núcleo científico; §6.8 guarda "
                    "costos, efectos y condiciones en la proyección de juego, no en "
                    "el nodo científico"
                )


# --- 2 y 4. dirección de las referencias -------------------------------------

def _check_direction(science, rep) -> None:
    for where, rec in science:
        rid = rec.get("id", "?")
        own = _prefix(rec)
        if own in GAME_PREFIXES:
            rep.error(
                f"separación: {where} almacena {rid}, un registro de la capa 8, junto "
                "al núcleo científico; §6.8 le da almacenamiento propio en game/"
            )
            continue
        for path, key, value in _walk(rec):
            if not isinstance(value, str):
                continue
            found = ANY_ID_RE.fullmatch(value)
            if not found:
                continue
            prefix = found.group(1)
            if prefix == PROJECTION_PREFIX:
                rep.error(
                    f"separación: {where}:{rid}.{path} apunta a {value}, una "
                    "GameProjection: la referencia sólo va en el sentido contrario "
                    "(§6.8). Si el núcleo depende del juego, borrar el módulo de "
                    "campaña rompe datos científicos (§27.10)"
                )
            elif prefix == "MECH":
                rep.error(
                    f"separación: {where}:{rid}.{path} apunta a la mecánica {value}; "
                    "un cambio de balance no puede tocar una afirmación (§27.10)"
                )
            elif prefix in GAME_PREFIXES:
                rep.warn(
                    f"separación: {where}:{rid}.{path} apunta a {value}, de la capa 8; "
                    "el alcance de campaña se declara en la proyección, no en el registro"
                )
        # Un identificador de capa 8 citado dentro de un texto no es una
        # referencia estructural, pero conviene verlo antes de que lo sea.
        for text in _strings(rec):
            if ANY_ID_RE.fullmatch(text):
                continue
            for found in ANY_ID_RE.finditer(text):
                if found.group(1) in GAME_PREFIXES:
                    rep.warn(
                        f"separación: {where}:{rid} menciona {found.group(0)} dentro de "
                        "un texto libre; compruébese que es documentación y no una "
                        "dependencia del núcleo hacia el juego (§4.4)"
                    )


# --- 2. la proyección no reescribe la ciencia --------------------------------

def _check_projection_does_not_rewrite(game, rep) -> None:
    for where, rec in game:
        rid = rec.get("id", "?")
        own = _prefix(rec)
        if own in SCIENCE_PREFIXES:
            rep.error(
                f"separación: {where} almacena {rid}, un registro científico, dentro "
                "de la capa de juego; la proyección referencia por identificador, no "
                "guarda su propia copia (§6.8)"
            )
            continue
        for path, key, value in _walk(rec):
            low = key.lower()
            if not path.endswith("]") and (
                low in SCIENCE_ONLY_KEYS
                or (low in SCIENCE_SHAPED_KEYS and _looks_like_record(value))
            ):
                rep.error(
                    f"separación: {where}:{rid}.{path} es un campo del núcleo "
                    f"científico ('{key}') dentro de la capa de juego: la proyección "
                    "está reescribiendo la afirmación en vez de referenciarla (§4.4)"
                )
            if isinstance(value, dict):
                nested = value.get("id")
                if isinstance(nested, str):
                    found = ANY_ID_RE.fullmatch(nested)
                    if found and found.group(1) in SCIENCE_PREFIXES:
                        rep.error(
                            f"separación: {where}:{rid}.{path} incrusta una copia del "
                            f"registro científico {nested}; referénciese por "
                            "identificador (§6.8)"
                        )


# --- 2 bis. la proyección declara lo que simplifica --------------------------

def _check_projection_declares(projections, science_index, rep) -> None:
    for where, rec in projections:
        prefix = _prefix(rec)
        if prefix != PROJECTION_PREFIX:
            if prefix is None:
                rep.warn(
                    f"separación: {where} no lleva identificador GAME-; una proyección "
                    "sin identidad no se puede contrastar con el núcleo (§16.3)"
                )
            continue
        rid = rec.get("id", "?")
        refs = rec.get("scientific_reference_ids")
        refs = [r for r in refs if isinstance(r, str)] if isinstance(refs, list) else []
        if not refs:
            rep.warn(
                f"separación: {where}:{rid} no declara scientific_reference_ids; una "
                "proyección sin anclaje al Atlas no se puede contrastar con el núcleo"
            )
        justification = rec.get("justification")
        if not isinstance(justification, str) or not justification.strip():
            rep.error(
                f"separación: {where}:{rid} no registra justificación de diseño; §6.8 "
                "y §18.4 exigen decir por qué la simplificación sigue siendo "
                "científicamente aceptable"
            )
        declared = [
            s for key in ("simplifications", "scientific_constraints")
            for s in (rec.get(key) or [])
            if isinstance(s, str) and s.strip()
        ]
        disputed = sorted(
            ref for ref in refs
            if ref.startswith("HYP-") or science_index.get(ref) in NON_CONSENSUS
        )
        if disputed and not declared:
            rep.error(
                f"separación: {where}:{rid} proyecta {', '.join(disputed[:3])}, que no "
                "es consenso amplio, sin declarar simplificaciones ni restricciones "
                "científicas: así es como se acaba por convertir una hipótesis en "
                "hecho, que es lo que §4.4 prohíbe (§18.4)"
            )
        elif not declared:
            rep.warn(
                f"separación: {where}:{rid} no declara simplificación ni restricción "
                "alguna; §18.4 pide registrar qué se omite, qué se agrupa y qué "
                "incertidumbre se muestra"
            )


# --- 3. las vistas identifican sus simplificaciones --------------------------

def _check_views_declare_simplifications(views, rep) -> None:
    for where, rec in views:
        rid = rec.get("id", "?")
        simplifications = rec.get("simplifications")
        excluded = rec.get("excluded_claim_ids") or rec.get("excluded_entity_ids") or []
        artifacts = rec.get("generated_artifacts") or []

        if simplifications is None:
            rep.error(
                f"separación: la vista {where}:{rid} no tiene campo 'simplifications'; "
                "§19.2 exige que una vista generada identifique lo que simplifica"
            )
            continue
        if not isinstance(simplifications, list):
            rep.error(
                f"separación: la vista {where}:{rid}.simplifications no es una lista"
            )
            continue
        vacias = [i for i, s in enumerate(simplifications)
                  if not isinstance(s, str) or not s.strip()]
        for i in vacias:
            rep.error(
                f"separación: la vista {where}:{rid}.simplifications[{i}] está vacía; "
                "declarar una simplificación sin decir cuál no identifica nada"
            )
        if not simplifications:
            if artifacts:
                # Un artefacto materializado se mira sin abrir el registro: lo que
                # el dibujo deja fuera no se lee en ninguna parte (§20.1).
                rep.error(
                    f"separación: la vista {where}:{rid} materializa "
                    f"{len(artifacts)} artefactos sin declarar una sola "
                    "simplificación; quien mire el diagrama no tiene forma de saber "
                    "qué se quedó fuera (§15.4, §19.2)"
                )
            elif excluded:
                rep.warn(
                    f"separación: la vista {where}:{rid} excluye {len(excluded)} "
                    "afirmaciones sin declarar una sola simplificación; "
                    "excluded_claim_ids dice cuáles, pero no qué cuesta dejarlas "
                    "fuera (§15.4)"
                )
            else:
                rep.info(
                    f"separación: la vista {where}:{rid} declara no simplificar nada; "
                    "compruébese a mano si es cierto"
                )
        if not (rec.get("editorial_criteria") or []):
            rep.error(
                f"separación: la vista {where}:{rid} no declara criterios editoriales "
                "(§15.4); sin ellos aparenta ser la clasificación verdadera"
            )


# --- entrada -----------------------------------------------------------------

def check(data: dict[str, list[dict]], rep) -> None:
    science: list[tuple[str, dict]] = [
        (fname, rec) for fname, recs in data.items()
        for rec in recs if isinstance(rec, dict)
    ]
    # Vistas y proyecciones viven fuera de records/ (§16.2 y §6.8). En el dataset
    # real estan donde dice la guia; un fixture las trae junto a sus registros.
    # Sin esto, un caso de prueba que ejercita la separacion de capas no tendria
    # proyeccion que comprobar y pasaria en verde sin comprobar nada.
    base = getattr(rep, "records_dir", None)
    if base is not None:
        base = Path(base)
        science_dirs = (base / "views", base / "classifications")
        projection_dirs = (base / "projections",)
        game_dirs = (base / "game", base / "mechanics")
    else:
        science_dirs, projection_dirs, game_dirs = SCIENCE_DIRS, PROJECTION_DIRS, GAME_DIRS

    science += _load_dirs(science_dirs, rep)
    projections = _load_dirs(projection_dirs, rep)
    game = projections + _load_dirs(game_dirs, rep)

    # Los registros de capa 8 que aparezcan dentro de `data` (por ejemplo un
    # fixture que los mezcla) se juzgan como capa 8, no como núcleo.
    misplaced = [(w, r) for w, r in science if _prefix(r) == PROJECTION_PREFIX]
    projections += misplaced
    game += misplaced

    views = [(w, r) for w, r in science if _prefix(r) in VIEW_PREFIXES]

    # Índice de aceptación para saber qué proyecta la capa 8 (§10.1).
    science_index: dict[str, str] = {}
    for _, rec in science:
        rid = rec.get("id")
        dims = rec.get("epistemic_dimensions")
        if isinstance(rid, str) and isinstance(dims, dict):
            acceptance = dims.get("acceptance")
            if isinstance(acceptance, str):
                science_index[rid] = acceptance

    _check_core_free_of_mechanics(science, rep)
    _check_direction(science, rep)
    _check_projection_does_not_rewrite(game, rep)
    _check_projection_declares(projections, science_index, rep)
    _check_views_declare_simplifications(views, rep)

    if not projections:
        rep.info(
            "separación: no hay ninguna GameProjection todavía; la comprobación de "
            "reescritura se ejecutará cuando exista la capa 8 (§6.8, fase mínima 8)"
        )
    if not views:
        rep.info(
            "separación: no hay vistas construidas todavía; la comprobación de "
            "simplificaciones declaradas se ejecutará cuando existan (§6.7)"
        )
