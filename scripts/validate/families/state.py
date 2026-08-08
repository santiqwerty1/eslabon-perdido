#!/usr/bin/env python3
"""Familia «Estado» de §19.2.

Comprueba cuatro cosas:

1. **registros superados conservados** — §0.1 y §16.4: nada desaparece. Un
   registro se depreca cambiando `record_status`, nunca borrando la línea;
2. **deprecaciones con reemplazo o razón** — cerrar un registro sin decir por
   qué ni hacia dónde equivale a borrarlo con otro nombre;
3. **migraciones documentadas** — un cambio de `schema_version` o un salto en
   la cadena de revisiones exige documento en `schemas/migrations/`;
4. **dimensiones epistemológicas no mezcladas** — §10.

La cuarta es la sutil. §10 rechaza un `epistemic_status` único porque mezclaba
preguntas distintas, y separa seis ejes independientes. Dos de ellos comparten
el valor `superseded`: §10.5 describe la vigencia de la IDEA y §10.6 el ciclo
de vida del REGISTRO. Ahí es donde los ejes vuelven a fundirse en la práctica:
se marca el registro como superado porque la idea lo está y, con eso, se pierde
el registro de la idea superada, que es justo lo que §0.1 manda conservar. Una
hipótesis abandonada en 1970 sigue teniendo un registro **activo**; lo superado
es su contenido, no su ficha.

Las rutas son constantes de módulo a propósito: las pruebas las reapuntan a
`tests/fixtures/` sin tocar el dataset real.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

NAME = "state"
PHASE = None

ROOT = Path(__file__).resolve().parents[3]
SNAPSHOTS_DIR = ROOT / "knowledge" / "snapshots"
DELTAS_DIR = ROOT / "knowledge" / "deltas"
MIGRATIONS_DIR = ROOT / "schemas" / "migrations"
MANIFEST_PATH = ROOT / "knowledge" / "corpus" / "manifests" / "dataset.json"

ID_RE = re.compile(r"\b[A-Z]+-[0-9]{6}\b")
SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
REV_RE = re.compile(r"^REV-([0-9]{6})$")

# §10.6. Ciclo de vida del registro.
CLOSED_STATUSES = ("deprecated", "merged", "superseded", "archived")
NEEDS_SUCCESSOR = ("merged", "superseded")

# §10.1–§10.5. Ejes independientes y sus valores.
AXIS_VALUES = {
    "acceptance": {
        "broad_consensus", "majority_acceptance", "mixed_acceptance",
        "minority_position", "not_assessed",
    },
    "evidence_strength": {"high", "medium", "low", "unknown"},
    "resolution": {
        "resolved", "partially_resolved", "unresolved", "insufficient_information",
    },
    "historical_status": {"current", "historical", "superseded", "rejected"},
}
EPISTEMIC_ALLOWED = set(AXIS_VALUES) | {"evidence_strength_reason"}

# Un solo campo no puede responder a dos preguntas de §10 a la vez.
AXIS_TOKENS = (
    "acceptance", "evidence_strength", "resolution", "historical_status",
    "record_status", "view_role",
)

# Campos rechazados por nombre: colapsan ejes o cifran la certeza.
COLLAPSED_FIELDS = {
    "epistemic_status", "epistemic_state", "epistemic_level", "epistemic_score",
    "epistemic_summary", "epistemics", "status_epistemico", "estado_epistemico",
    "overall_status", "combined_status", "global_status", "consolidated_status",
    "overall_score", "reliability_score", "trust_score", "quality_score",
    "truth_value", "truth_score",
}

# §4.1 y §10: la certeza no se resume en un número. Se compara pieza a pieza de
# la clave en snake_case; `uncertainty` (§11.2, §12.2) declara lo que no se sabe
# y es justo lo contrario de un grado de confianza, así que queda a salvo.
CONFIDENCE_RE = re.compile(
    r"(confidence|confianza|certainty|certeza|credence|probabilit|probabilid|"
    r"likelihood|verosimilit|belief|creencia|fiabilidad)"
)
CONFIDENCE_SAFE = {"uncertainty", "uncertainties", "incertidumbre", "unknown"}

# Un reemplazo puede declararse con cualquiera de estos nombres; ninguno está
# todavía en los esquemas, así que en la práctica viaja en `notes`.
REPLACEMENT_KEYS = (
    "superseded_by", "superseded_by_id", "replaced_by", "replaced_by_id",
    "replacement_id", "merged_into", "merged_into_id", "successor_id",
)
REASON_KEYS = ("deprecation_reason", "reason", "notes")
PLACEHOLDERS = {
    "", "-", "--", "?", "n/a", "na", "tbd", "todo", "pendiente", "sin razón",
    "sin razon", "por determinar", "sin especificar", "ninguna", "none", "null",
}
MIN_REASON = 4

# Claves del delta de §17 paso 13 cuyo contenido son identificadores de
# registro. Las de vistas quedan fuera: viven en knowledge/views/.
DELTA_RECORD_KEYS = (
    "records_added", "records_updated", "records_deprecated", "claims_added",
    "events_added", "hypotheses_added", "issues_added", "issues_resolved",
)
REMOVAL_RE = re.compile(r"(removed|deleted|purged|dropped|erased|borrad|elimin)")

# Recuentos comparables con los del snapshot (véase scripts/snapshot).
ENTITY_FILES = (
    "taxonomic-names.jsonl", "taxon-concepts.jsonl", "clades.jsonl",
    "lineages.jsonl", "populations.jsonl", "specimens.jsonl", "sites.jsonl",
    "regions.jsonl", "occurrences.jsonl", "traits.jsonl",
    "trait-observations.jsonl",
)
COUNT_FILES = {
    "mentions": ("mentions.jsonl",),
    "claims": ("claims.jsonl",),
    "events": ("events.jsonl",),
    "hypotheses": ("hypotheses.jsonl",),
    "sources": ("sources.jsonl",),
    "issues": ("issues.jsonl",),
    "entities": ENTITY_FILES,
}


# --- utilidades --------------------------------------------------------------

def _walk(node, path: str = ""):
    """Emite (ruta, clave, valor) de cada campo del registro, a cualquier hondura."""
    if isinstance(node, dict):
        for key, value in node.items():
            here = f"{path}.{key}" if path else key
            yield here, key, value
            yield from _walk(value, here)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            yield from _walk(item, f"{path}[{i}]")


def _read_json(path: Path, rep) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        rep.error(f"estado: {path.name} no se puede leer — {exc}")
        return None


def _texts(rec: dict, keys) -> list[str]:
    out = []
    for key in keys:
        value = rec.get(key)
        if isinstance(value, str):
            out.append(value)
        elif isinstance(value, list):
            out.extend(v for v in value if isinstance(v, str))
    return out


# --- 1. registros superados conservados --------------------------------------

def _check_conservation(data, rep, snapshots_dir: Path, deltas_dir: Path) -> None:
    counts = {
        key: sum(len(data.get(f, [])) for f in files)
        for key, files in COUNT_FILES.items()
    }

    snaps = sorted(snapshots_dir.glob("SNAP-*.json")) if snapshots_dir.exists() else []
    if not snaps:
        rep.info(
            "estado: no hay snapshot con el que comparar; la conservación de "
            "registros no se ha comprobado por recuento (§16.6)"
        )
    else:
        snap = _read_json(snaps[-1], rep) or {}
        snap_id = snap.get("snapshot_id", snaps[-1].stem)
        for key, before in (snap.get("counts") or {}).items():
            if key not in counts or not isinstance(before, int):
                continue
            if counts[key] < before:
                rep.error(
                    f"estado: {key}: {snap_id} registraba {before} y ahora hay "
                    f"{counts[key]}; §0.1 y §16.4 no permiten que un registro "
                    "desaparezca — deprecar es cambiar record_status, no borrar la línea"
                )

    ids = {
        rec["id"]
        for recs in data.values()
        for rec in recs
        if isinstance(rec, dict) and isinstance(rec.get("id"), str)
    }
    deltas = sorted(deltas_dir.glob("*.json")) if deltas_dir.exists() else []
    if not deltas:
        rep.info(
            "estado: no hay deltas registrados; la conservación de lo que cada "
            "sección incorporó se comprobará cuando existan (§17 paso 13)"
        )
    parsed = []
    for path in deltas:
        delta = _read_json(path, rep)
        if delta is None:
            continue
        parsed.append((path, delta))
        for key, value in delta.items():
            if REMOVAL_RE.search(key.lower()) and value:
                rep.error(
                    f"estado: el delta {path.name} declara '{key}': §16.4 no "
                    "contempla ninguna operación de borrado, sólo DEPRECATE_RECORD, "
                    "SUPERSEDE_RECORD y MERGE_CONFIRMED_IDENTITIES"
                )
        for key in DELTA_RECORD_KEYS:
            for item in delta.get(key) or []:
                rid = item.get("id") if isinstance(item, dict) else item
                if not isinstance(rid, str) or not ID_RE.fullmatch(rid):
                    continue
                if rid not in ids:
                    rep.error(
                        f"estado: el delta {path.name} incorporó {rid} en '{key}' "
                        "y ese registro ya no está en el dataset (§0.1: nada desaparece)"
                    )
    return parsed


# --- 2. deprecaciones con reemplazo o razón ----------------------------------

def _successor(rec: dict) -> str | None:
    for key in REPLACEMENT_KEYS:
        value = rec.get(key)
        if isinstance(value, str) and ID_RE.fullmatch(value):
            return value
        if isinstance(value, list):
            for item in value:
                if isinstance(item, str) and ID_RE.fullmatch(item):
                    return item
    for text in _texts(rec, REASON_KEYS):
        found = ID_RE.search(text)
        if found:
            return found.group(0)
    return None


def _reason(rec: dict) -> str | None:
    for text in _texts(rec, REASON_KEYS):
        clean = text.strip()
        if len(clean) >= MIN_REASON and clean.lower() not in PLACEHOLDERS:
            return clean
    return None


def _check_deprecations(data, rep, ids: set[str]) -> None:
    for fname, recs in data.items():
        for rec in recs:
            if not isinstance(rec, dict):
                continue
            status = rec.get("record_status")
            if status not in CLOSED_STATUSES:
                continue
            rid = rec.get("id", "?")
            successor = _successor(rec)
            reason = _reason(rec)
            dims = rec.get("epistemic_dimensions")
            historical = dims.get("historical_status") if isinstance(dims, dict) else None

            if status in NEEDS_SUCCESSOR and successor is None:
                if status == "superseded" and historical == "superseded":
                    rep.error(
                        f"estado: {fname}:{rid} tiene record_status 'superseded' sin "
                        "registro que lo reemplace, y su historical_status también es "
                        "'superseded': §10.5 (vigencia de la IDEA) y §10.6 (ciclo de "
                        "vida del REGISTRO) se están usando como sinónimos. Una idea "
                        "superada se conserva en un registro activo"
                    )
                else:
                    rep.error(
                        f"estado: {fname}:{rid} tiene record_status '{status}' sin "
                        "reemplazo declarado; §19.2 exige reemplazo o razón y §16.4 "
                        "que la operación sea reversible"
                    )
            elif successor is None and reason is None:
                rep.error(
                    f"estado: {fname}:{rid} tiene record_status '{status}' sin "
                    "reemplazo ni razón escrita (§19.2, familia Estado)"
                )
            if successor is not None and successor not in ids and successor != rec.get("id"):
                rep.warn(
                    f"estado: {fname}:{rid} declara como reemplazo {successor}, que no "
                    "está en el dataset; si vive en otra capa, dilo en notes"
                )


# --- 3. migraciones documentadas ---------------------------------------------

def _check_migrations(data, rep, deltas, migrations_dir: Path,
                      snapshots_dir: Path, manifest_path: Path) -> None:
    versions: set[str] = set()
    for source in ([manifest_path] if manifest_path.exists() else []) + (
        sorted(snapshots_dir.glob("SNAP-*.json")) if snapshots_dir.exists() else []
    ):
        doc = _read_json(source, rep) or {}
        if isinstance(doc.get("schema_version"), str):
            versions.add(doc["schema_version"])
    for _, delta in deltas:
        if isinstance(delta.get("schema_version"), str):
            versions.add(delta["schema_version"])
    for recs in data.values():
        for rec in recs:
            if isinstance(rec, dict) and isinstance(rec.get("schema_version"), str):
                versions.add(rec["schema_version"])
    versions = {v for v in versions if SEMVER_RE.match(v)}

    docs = []
    if migrations_dir.exists():
        for path in sorted(migrations_dir.rglob("*")):
            if path.is_file():
                try:
                    docs.append((path.name, path.read_text(encoding="utf-8", errors="replace")))
                except OSError:
                    docs.append((path.name, ""))

    def documented(*needles: str) -> bool:
        return any(all(n in name or n in text for n in needles) for name, text in docs)

    if len(versions) <= 1:
        rep.info(
            f"estado: un único schema_version en el dataset "
            f"({sorted(versions)[0] if versions else 'sin declarar'}); no hay "
            "migración de esquema que documentar (§16.5)"
        )
    else:
        ordered = sorted(versions, key=lambda v: tuple(int(p) for p in v.split(".")))
        for old, new in zip(ordered, ordered[1:]):
            if not documented(old, new):
                rep.error(
                    f"estado: conviven schema_version {old} y {new} sin documento en "
                    f"{migrations_dir.name}/ que describa la migración (§16.5, §19.2)"
                )

    for path, delta in deltas:
        if "MIGRATE_SCHEMA" in json.dumps(delta, ensure_ascii=False) and not docs:
            rep.error(
                f"estado: el delta {path.name} registra MIGRATE_SCHEMA y "
                f"{migrations_dir.name}/ está vacío: la migración no está documentada"
            )

    chain = []
    for path, delta in deltas:
        before, after = delta.get("dataset_revision_before"), delta.get("dataset_revision_after")
        if isinstance(before, str) and isinstance(after, str):
            mb, ma = REV_RE.match(before), REV_RE.match(after)
            if mb and ma:
                chain.append((int(ma.group(1)), before, after, path.name))
    chain.sort()
    for (n_prev, _, after_prev, name_prev), (_, before, _, name) in zip(chain, chain[1:]):
        if before != after_prev:
            if documented(after_prev, before):
                rep.info(
                    f"estado: salto de revisión entre {name_prev} y {name} "
                    f"({after_prev} → {before}), documentado como migración"
                )
            else:
                rep.error(
                    f"estado: la cadena de revisiones salta de {after_prev} ({name_prev}) "
                    f"a {before} ({name}) sin migración documentada; el estado deja de "
                    "reconstruirse sin la conversación (§4.6, §16.5)"
                )


# --- 4. dimensiones epistemológicas no mezcladas -----------------------------

def _check_axes(data, rep) -> None:
    mirrored: list[str] = []
    superseded_ideas = 0

    for fname, recs in data.items():
        for rec in recs:
            if not isinstance(rec, dict):
                continue
            rid = rec.get("id", "?")
            where = f"{fname}:{rid}"

            # (c) ningún campo colapsa ejes ni cifra la certeza.
            for path, key, _ in _walk(rec):
                low = key.lower()
                if low in COLLAPSED_FIELDS:
                    rep.error(
                        f"estado: {where}.{path} resume en un solo campo lo que §10 "
                        "separa en ejes independientes; el `epistemic_status` único "
                        "está rechazado"
                    )
                    continue
                pieces = [p for p in re.split(r"[^a-z0-9]+", low) if p]
                if any(p not in CONFIDENCE_SAFE and CONFIDENCE_RE.search(p) for p in pieces):
                    rep.error(
                        f"estado: {where}.{path} cifra la certeza en un grado o "
                        "porcentaje; §10.3 pide fuerza de evidencia con razón escrita "
                        "y §10.7 medidas con su escala, su método y su fuente"
                    )
                    continue
                hits = [t for t in AXIS_TOKENS if t in low]
                if len(hits) >= 2:
                    rep.error(
                        f"estado: {where}.{path} junta los ejes {', '.join(hits)} en un "
                        "mismo campo; §10 los declara independientes"
                    )

            # Cada eje en su sitio: los de §10.1–§10.5 anidados, el de §10.6 en raíz.
            for axis, values in AXIS_VALUES.items():
                raw = rec.get(axis)
                if isinstance(raw, str) and raw in values:
                    rep.error(
                        f"estado: {where}.{axis} está en la raíz con un valor de §10; "
                        "los ejes epistemológicos van anidados bajo epistemic_dimensions"
                    )

            dims = rec.get("epistemic_dimensions")
            if not isinstance(dims, dict):
                continue
            if "record_status" in dims:
                rep.error(
                    f"estado: {where}.epistemic_dimensions.record_status: §10.6 describe "
                    "el ciclo de vida del registro y va en la raíz; dentro de las "
                    "dimensiones se confunde con historical_status (§10.5)"
                )
            for extra in sorted(set(dims) - EPISTEMIC_ALLOWED):
                rep.error(
                    f"estado: {where}.epistemic_dimensions.{extra} no es ninguno de los "
                    "ejes de §10; un eje nuevo es un cambio de contrato (§16.5)"
                )

            # (b) la fuerza de evidencia lleva razón escrita.
            strength = dims.get("evidence_strength")
            reason = dims.get("evidence_strength_reason")
            if isinstance(strength, str) and strength != "unknown":
                clean = reason.strip() if isinstance(reason, str) else ""
                if len(clean) < MIN_REASON or clean.lower() in PLACEHOLDERS:
                    rep.error(
                        f"estado: {where}: evidence_strength '{strength}' sin razón "
                        "escrita; §10.3 la exige y sin ella el eje se vuelve una nota "
                        "de opinión indistinguible de la aceptación (§10.1)"
                    )

            # (a) los dos ejes que comparten 'superseded' no son sinónimos.
            historical = dims.get("historical_status")
            if historical in ("superseded", "rejected"):
                superseded_ideas += 1
                if rec.get("record_status") == "superseded":
                    mirrored.append(where)

    if superseded_ideas >= 2 and len(mirrored) == superseded_ideas:
        rep.warn(
            "estado: las "
            f"{superseded_ideas} ideas superadas o rechazadas del dataset llevan además "
            "record_status 'superseded' sin excepción: los ejes §10.5 y §10.6 se están "
            "moviendo como uno solo. Conservar una idea superada es mantener su registro "
            f"activo ({', '.join(sorted(mirrored)[:5])})"
        )


# --- entrada -----------------------------------------------------------------

def check(data: dict[str, list[dict]], rep) -> None:
    # Conservacion y migraciones necesitan snapshots, deltas y migraciones.
    # En el dataset real viven donde dice §16.2; un fixture trae los suyos junto
    # a sus registros, y ahi es donde hay que buscarlos. Comparar un fixture
    # contra el snapshot del dataset real produciria falsos positivos, pero
    # saltarse la comprobacion la dejaria sin probar: la solucion no es omitirla,
    # es resolverla en el ambito correcto.
    base = getattr(rep, "records_dir", None)
    if base is not None:
        base = Path(base)
        snapshots_dir = base / "snapshots"
        deltas_dir = base / "deltas"
        migrations_dir = base / "migrations"
        manifest_path = base / "dataset.json"
    else:
        snapshots_dir, deltas_dir = SNAPSHOTS_DIR, DELTAS_DIR
        migrations_dir, manifest_path = MIGRATIONS_DIR, MANIFEST_PATH

    deltas = _check_conservation(data, rep, snapshots_dir, deltas_dir) or []

    ids = {
        rec["id"]
        for recs in data.values()
        for rec in recs
        if isinstance(rec, dict) and isinstance(rec.get("id"), str)
    }
    _check_deprecations(data, rep, ids)
    _check_migrations(data, rep, deltas, migrations_dir, snapshots_dir, manifest_path)
    _check_axes(data, rep)
