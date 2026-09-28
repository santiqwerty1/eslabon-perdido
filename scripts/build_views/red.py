#!/usr/bin/env python3
"""La red por hipótesis: una vista filogenética por hipótesis (§6.7, §15.3, §17 paso 9, §20.3).

Cada vista toma el **tronco común** —las afirmaciones de topología sin alcance
de hipótesis— y las de **una** hipótesis, y deja fuera las de sus rivales: dos
hipótesis del mismo grupo de conflicto no se dibujan en un mismo árbol. Los
conflictos que la vista no decide quedan sin resolver, en politomía. Además de
una vista por hipótesis hay una del tronco solo, sin ninguna.

**Qué es topología.** `member_of` cuelga un nodo de otro; `sister_group_of`
junta dos hermanos; `stem_lineage_of` pone un linaje en el tronco de un clado;
`diverges_from` no coloca nada y sólo se comprueba. Una afirmación queda fuera,
con su motivo, si:

- es derivada (§9.4): la vista la recalcula;
- su alcance es otra hipótesis: rival de la vista o de un conflicto que la
  vista no decide;
- la hipótesis de la vista la excluye;
- es del tronco e histórica: el tronco toma lo vigente;
- cuelga algo de un concepto taxonómico: eso es clasificación según una fuente
  (§4.3), no topología.

**Cómo se arma el árbol.**

1. Contención: cada nodo cuelga del padre más interno de los que le dan sus
   `member_of`. Una población (LECA) no es una rama: se anota en su nodo.
2. Ancla: la especificación dice qué grupo de conflicto decide la primera
   divergencia de qué clado. En él, la afirmación hermana de la hipótesis es
   esa bipartición. Si un lado es un complemento declarado («el resto de
   Eukaryota»), recibe todo lo demás, y si el otro lado estaba en lo hondo del
   tronco el árbol se re-enraíza: los clados del camino dejan de serlo. Sin
   complemento, lo que no tiene lado declarado queda en la raíz, marcado.
3. Composiciones: la especificación da los miembros de los clados compuestos
   que el libro mayor deja sin ellos. Es un hallazgo, y la vista lo dice.
4. Hermanos: dos hermanos bajo un mismo padre con más hijos forman un nodo sin
   nombre; uno sin ubicar se pone junto a su hermano; dos sin ubicar quedan
   fuera del árbol principal, juntos.
5. Tronco: `stem_lineage_of` inserta un nodo de tronco sobre el clado.
6. Verificación: cada afirmación seleccionada se comprueba contra el árbol
   final. La que no se cumple sale de la selección con su motivo. Así se ve qué
   afirmaciones del tronco contradice una raíz aunque la hipótesis no lo diga.

**Qué escribe.** Los registros PHYVIEW en
`knowledge/views/phylogenetic-views.jsonl`, con identificador estable por
conjunto de hipótesis y versión que sólo sube si cambia el contenido; y la
página de pequeños múltiplos en `generated/views/red.html`. La fecha de corte
es la del corpus congelado, así que dos ejecuciones sobre los mismos registros
dan los mismos bytes.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECORDS = ROOT / "knowledge" / "records"
VISTAS = ROOT / "knowledge" / "views" / "phylogenetic-views.jsonl"
ESPEC = ROOT / "knowledge" / "view-specs" / "red.json"
SALIDA = ROOT / "generated" / "views"
PLANTILLA = Path(__file__).with_name("red.plantilla.html")

sys.path.insert(0, str(Path(__file__).parent))
from cronologia import Registros, cita_corta, leer  # noqa: E402

# Lo que la vista dibuja.
TOPOLOGIA = {"member_of", "sister_group_of", "stem_lineage_of", "diverges_from"}
# Estructurales que la vista todavía no dibuja: salen con su motivo.
NO_DIBUJADOS = {"contains", "descends_from", "crown_group_of", "possible_ancestor_of",
                "possible_sampled_ancestor_of", "chronological_continuation_of"}
RETICULADOS = {"hybridizes_with", "receives_gene_flow_from", "introgression_from",
               "contributes_ancestry_to", "transfers_gene_to", "integrates_viral_material_from",
               "endosymbiosis_with", "originates_hybrid_lineage_with"}
DE_RED = TOPOLOGIA | NO_DIBUJADOS | RETICULADOS

# Motivos de exclusión, en el orden en que la página los presenta.
MOTIVOS = {
    "rival": "de una hipótesis rival del mismo grupo de conflicto",
    "otra_hipotesis": "de una hipótesis de otro conflicto, que esta vista no decide",
    "excluida": "la hipótesis de la vista la excluye",
    "contradicha": "no se cumple en el árbol de esta vista",
    "no_dibujable": "une nodos que quedan en árboles distintos",
    "clasificacion": "cuelga algo de un concepto taxonómico: es clasificación según una fuente (§4.3)",
    "historica": "es histórica, y el tronco sólo toma lo vigente",
    "derivada": "es derivada: la vista la recalcula (§9.4)",
    "no_dibujado": "esta vista todavía no dibuja su predicado",
}
TIPOS = {"CLADE": "clado", "TAXCONCEPT": "concepto", "LINEAGE": "linaje", "POP": "población"}


def hipotesis_corta(h: dict) -> str | None:
    """El código del corredor («H24»), que la conversión deja en la descripción."""
    m = re.search(r"\((H\d+) del corredor\)", h.get("description") or "")
    return m.group(1) if m else None


# --- el árbol --------------------------------------------------------------------------

class Arbol:
    """Un bosque de nodos con nombre (identificadores) y sin él (`~n`)."""

    def __init__(self) -> None:
        self.padre: dict[str, str] = {}
        self.hijos: dict[str, list[str]] = defaultdict(list)
        self.tipo: dict[str, str] = {}
        self.marcas: dict[str, set[str]] = defaultdict(set)
        self.anotaciones: dict[str, list[str]] = defaultdict(list)
        self.origen: dict[str, str] = {}
        self.nodos: set[str] = set()
        self.n = 0

    def implicito(self, tipo: str = "implicito") -> str:
        self.n += 1
        k = f"~{self.n}"
        self.tipo[k] = tipo
        self.nodos.add(k)
        return k

    def poner(self, hijo: str, padre: str, origen: str | None = None) -> None:
        viejo = self.padre.get(hijo)
        if viejo is not None:
            self.hijos[viejo].remove(hijo)
        self.padre[hijo] = padre
        self.hijos[padre].append(hijo)
        self.nodos.update((hijo, padre))
        if origen:
            self.origen[hijo] = origen

    def soltar(self, n: str) -> None:
        viejo = self.padre.pop(n, None)
        if viejo is not None:
            self.hijos[viejo].remove(n)

    def quitar(self, n: str) -> None:
        """Saca un nodo que ya no tiene hijos (un clado roto por un re-enraizado)."""
        assert not self.hijos.get(n), n
        self.soltar(n)
        self.nodos.discard(n)
        self.hijos.pop(n, None)

    def renombrar(self, viejo: str, nuevo: str) -> None:
        """Da nombre a un nodo implícito: la composición declarada lo identifica."""
        padre = self.padre.pop(viejo, None)
        if padre is not None:
            i = self.hijos[padre].index(viejo)
            self.hijos[padre][i] = nuevo
            self.padre[nuevo] = padre
        for h in self.hijos.pop(viejo, []):
            self.padre[h] = nuevo
            self.hijos[nuevo].append(h)
        self.nodos.discard(viejo)
        self.nodos.add(nuevo)
        self.marcas[nuevo] |= self.marcas.pop(viejo, set())

    def ancestros(self, n: str) -> list[str]:
        out = []
        while n in self.padre:
            n = self.padre[n]
            out.append(n)
        return out

    def cima(self, n: str) -> str:
        a = self.ancestros(n)
        return a[-1] if a else n

    def es_ancestro(self, a: str, n: str) -> bool:
        return a in self.ancestros(n)

    def agrupar(self, a: str, b: str, origen: str) -> bool:
        """a y b son hermanos bajo el mismo padre: si hay más hijos, un nodo sin nombre los junta."""
        p = self.padre[a]
        otros = [h for h in self.hijos[p] if h not in (a, b) and "sin_lado" not in self.marcas[h]]
        if not otros:
            return False
        i = self.implicito()
        self.poner(i, p, origen)
        self.poner(a, i)
        self.poner(b, i)
        return True

    def subir_troncos(self, n: str) -> str:
        while n in self.padre and self.tipo.get(self.padre[n]) == "tronco":
            n = self.padre[n]
        return n


# --- selección --------------------------------------------------------------------------

class Libro:
    """Los registros que la red necesita."""

    def __init__(self, base: Path, raiz: Path):
        self.r = Registros(base, raiz / "knowledge" / "corpus" / "passages")
        self.grupos = {g["id"]: g for g in leer(base / "conflict-groups.jsonl")
                       if g.get("record_status", "active") == "active"}
        self.grupos_de: dict[str, list[str]] = {
            h: list(x.get("conflict_group_ids") or []) for h, x in self.r.hypotheses.items()}
        self.miembros: dict[str, set[str]] = defaultdict(set)
        for h, gs in self.grupos_de.items():
            for g in gs:
                self.miembros[g].add(h)

    def etiqueta(self, n: str) -> str:
        return self.r.etiqueta(n)

    def rivales(self, hyps: list[str]) -> set[str]:
        return {o for h in hyps for g in self.grupos_de.get(h, []) for o in self.miembros[g]} - set(hyps)


def objeto(c: dict) -> str | None:
    return (c.get("object") or {}).get("entity_id")


def seleccionar(libro: Libro, hyps: list[str]) -> tuple[list[dict], dict[str, tuple[str, str]]]:
    """Las candidatas de la vista y las excluidas de entrada, con su motivo."""
    rivales = libro.rivales(hyps)
    excluye = {c for h in hyps for c in (libro.r.hypotheses[h].get("excluded_claim_ids") or [])}
    candidatas, fuera = [], {}
    for cid in sorted(libro.r.claims):
        c = libro.r.claims[cid]
        pred = c["predicate"]
        if pred not in DE_RED:
            continue
        alcance = set((c.get("scope") or {}).get("hypothesis_ids") or [])
        dims = c.get("epistemic_dimensions") or {}
        if c.get("derivation"):
            fuera[cid] = ("derivada", "")
        elif alcance and not alcance & set(hyps):
            quien = ", ".join(sorted(alcance))
            fuera[cid] = ("rival", quien) if alcance & rivales else ("otra_hipotesis", quien)
        elif cid in excluye:
            fuera[cid] = ("excluida", ", ".join(h for h in hyps if cid in
                                               (libro.r.hypotheses[h].get("excluded_claim_ids") or [])))
        elif not alcance and dims.get("historical_status") in ("historical", "superseded", "rejected"):
            fuera[cid] = ("historica", dims.get("historical_status"))
        elif pred == "member_of" and (objeto(c) or "").startswith("TAXCONCEPT-"):
            fuera[cid] = ("clasificacion", libro.etiqueta(objeto(c)))
        elif pred not in TOPOLOGIA:
            fuera[cid] = ("no_dibujado", pred)
        else:
            candidatas.append(c)
    return candidatas, fuera


# --- construcción ------------------------------------------------------------------------

def anclas_de(espec: dict, libro: Libro, hyps: list[str], candidatas: list[dict]) -> list[dict]:
    """Las bipartiticiones que decide la vista: una por hipótesis de un grupo anclado."""
    out = []
    for h in hyps:
        for g in libro.grupos_de.get(h, []):
            ancla = espec.get("anclas", {}).get(g)
            if not ancla:
                continue
            propias = [c for c in candidatas if c["predicate"] == "sister_group_of"
                       and h in ((c.get("scope") or {}).get("hypothesis_ids") or [])]
            out.append({"grupo": g, "hipotesis": h, "nodo": ancla["nodo"], "motivo": ancla["motivo"],
                        "claims": propias})
    return out


def construir_vista(libro: Libro, espec: dict, hyps: list[str]) -> dict:
    candidatas, fuera = seleccionar(libro, hyps)
    raiz = espec["raiz"]
    comps = espec.get("complementos", {})
    composiciones = espec.get("composiciones", {})
    arbol = Arbol()
    hallazgos: list[str] = []
    usadas: dict[str, str] = {}  # lecturas de la especificación que la vista usó

    anclas = anclas_de(espec, libro, hyps, candidatas)
    de_raiz: dict[str, dict] = {}
    sin_raiz: list[str] = []
    for a in anclas:
        if len(a["claims"]) != 1:
            sin_raiz.append(a["grupo"])
            hallazgos.append(
                f"{a['hipotesis']} no trae afirmación hermana en {a['grupo']}: sus afirmaciones no enraízan, y la "
                f"primera divergencia de {libro.etiqueta(a['nodo'])} queda sin resolver." if not a["claims"] else
                f"{a['hipotesis']} tiene {len(a['claims'])} afirmaciones hermanas en {a['grupo']}: la vista no sabe "
                f"cuál es la primera divergencia de {libro.etiqueta(a['nodo'])} y la deja sin resolver.")
            continue
        de_raiz[a["claims"][0]["id"]] = a

    # Una raíz con complemento puede re-enraizar el tronco. Las afirmaciones del
    # tronco que la hipótesis excluye por eso siguen diciendo cómo es el árbol sin
    # raíz: sirven de andamio para re-enraizarlo, pero no se seleccionan.
    andamio: list[dict] = []
    if any(x in comps for cid in de_raiz for x in (de_raiz[cid]["claims"][0]["subject_id"],
                                                   objeto(de_raiz[cid]["claims"][0]))):
        for cid in sorted(fuera):
            c = libro.r.claims[cid]
            if (fuera[cid][0] == "excluida" and c["predicate"] in TOPOLOGIA and not c.get("derivation")
                    and not (c.get("scope") or {}).get("hypothesis_ids")
                    and not (c["predicate"] == "member_of" and (objeto(c) or "").startswith("TAXCONCEPT-"))):
                andamio.append(c)
    construccion = candidatas + andamio

    todas = {c["id"]: c for c in construccion}
    for c in construccion:
        arbol.nodos.add(c["subject_id"])
        if objeto(c):
            arbol.nodos.add(objeto(c))

    # 1 · contención ----------------------------------------------------------------------
    padres: dict[str, dict[str, str]] = defaultdict(dict)
    for c in construccion:
        if c["predicate"] == "member_of" and objeto(c):
            padres[c["subject_id"]][objeto(c)] = c["id"]
    # Un lado de la raíz sin padre cuelga del nodo anclado; el complemento se coloca después.
    lados: dict[str, tuple[str, str]] = {}
    for cid, a in de_raiz.items():
        c = todas[cid]
        for lado in (c["subject_id"], objeto(c)):
            if lado not in comps and not padres.get(lado):
                padres[lado][a["nodo"]] = cid
            if lado not in comps and a["nodo"] in padres.get(lado, {}):
                lados[lado] = (a["nodo"], cid)

    def arriba(n: str, visto: frozenset = frozenset()) -> set[str]:
        out: set[str] = set()
        for p in padres.get(n, {}):
            if p in visto:
                continue
            out.add(p)
            out |= arriba(p, visto | {n})
        return out

    def internos_de(ps: dict[str, str]) -> list[str]:
        return [p for p in sorted(ps) if all(q == p or q in arriba(p) for q in ps)]

    # Dos padres que no se contienen, uno de ellos un lado de la raíz y el otro un
    # clado del tronco bajo el nodo anclado: dos clados que comparten un miembro
    # están anidados, y en una raíz partida en dos lados, el del tronco cae dentro
    # del lado que contiene a su miembro.
    cambio = True
    while cambio:
        cambio = False
        for hijo in sorted(padres):
            ps = padres[hijo]
            if internos_de(ps):
                continue
            suyos = [p for p in ps if p in lados]
            if len(suyos) != 1:
                continue
            nodo, cid = lados[suyos[0]]
            otros = [p for p in ps if p not in lados and p != nodo]
            if otros and all(nodo in arriba(p) for p in otros):
                for p in otros:
                    padres[p][suyos[0]] = cid
                cambio = True

    for hijo in sorted(padres):
        ps = padres[hijo]
        internos = internos_de(ps)
        if internos:
            elegido = internos[0]
        else:
            # Dos padres que no se contienen: manda la hipótesis de la vista.
            propios = [p for p in sorted(ps) if set(hyps) & set(
                (todas.get(ps[p], {}).get("scope") or {}).get("hypothesis_ids") or [])]
            elegido = (propios or sorted(ps))[0]
        if hijo.startswith("POP-"):
            arbol.anotaciones[elegido].append(hijo)
            arbol.nodos.discard(hijo)
        else:
            arbol.poner(hijo, elegido, ps[elegido])

    # 2 · composiciones y hermanos, hasta que no cambie nada -----------------------------
    hermanas = sorted((c for c in construccion if c["predicate"] == "sister_group_of" and c["id"] not in de_raiz),
                      key=lambda c: c["id"])
    pendientes = {k for k in composiciones if k in arbol.nodos} | {k for k in comps if k in arbol.nodos}

    def colocado(n: str) -> bool:
        return n in arbol.padre or bool(arbol.hijos.get(n))

    cambio = True
    while cambio:
        cambio = False
        for k in sorted(composiciones):
            if k not in arbol.nodos or colocado(k):
                continue
            miembros = composiciones[k]["miembros"]
            puestos = [m for m in miembros if m in arbol.padre]
            ps = {arbol.padre[m] for m in puestos}
            if len(ps) != 1:
                continue
            p = ps.pop()
            for m in miembros:
                if m not in arbol.padre:
                    arbol.poner(m, p, f"composición de {k}")
            resto = [h for h in arbol.hijos[p] if h not in miembros]
            if not resto and arbol.tipo.get(p) == "implicito":
                arbol.renombrar(p, k)
            else:
                arbol.poner(k, p, f"composición de {k}")
                for m in miembros:
                    arbol.poner(m, k)
            arbol.marcas[k].add("composicion")
            usadas[k] = composiciones[k]["motivo"]
            cambio = True
        for c in hermanas:
            a, b = c["subject_id"], objeto(c)
            if not b or a == b:
                continue
            if any(x in pendientes and not colocado(x) for x in (a, b)):
                continue
            pa, pb = arbol.padre.get(a), arbol.padre.get(b)
            if pa is not None and pa == pb:
                cambio |= arbol.agrupar(a, b, c["id"])
            elif pa is not None and pb is None and arbol.cima(pa) != b:
                arbol.poner(b, pa, c["id"])
                arbol.agrupar(a, b, c["id"])
                cambio = True
            elif pb is not None and pa is None and arbol.cima(pb) != a:
                arbol.poner(a, pb, c["id"])
                arbol.agrupar(a, b, c["id"])
                cambio = True
            elif pa is None and pb is None:
                i = arbol.implicito()
                arbol.poner(a, i, c["id"])
                arbol.poner(b, i, c["id"])
                cambio = True

    # 3 · linajes troncales -----------------------------------------------------------------
    for c in sorted((c for c in construccion if c["predicate"] == "stem_lineage_of"), key=lambda c: c["id"]):
        linaje, clado = c["subject_id"], objeto(c)
        if not clado or linaje in arbol.padre:
            continue
        t = arbol.implicito("tronco")
        p = arbol.padre.get(clado)
        if p is not None:
            arbol.poner(t, p, c["id"])
        arbol.poner(clado, t)
        arbol.poner(linaje, t, c["id"])

    # 4 · la raíz de la hipótesis -------------------------------------------------------------
    rotos: list[str] = []
    for cid, a in sorted(de_raiz.items()):
        c, n = todas[cid], a["nodo"]
        lados = [c["subject_id"], objeto(c)]
        comp = next((x for x in lados if x in comps and comps[x]["dentro_de"] == n
                     and comps[x]["de"] in lados), None)
        if comp:
            usadas[comp] = comps[comp]["motivo"]
            otro = comps[comp]["de"]
            arbol.marcas[comp].add("complemento")
            if arbol.padre.get(otro) not in (None, n) and arbol.es_ancestro(n, otro):
                rotos += reenraizar(arbol, n, otro, comp, cid)
            else:
                if arbol.padre.get(otro) != n:
                    arbol.poner(otro, n, cid)
                arbol.poner(comp, n, cid)
                for h in list(arbol.hijos[n]):
                    if h not in (otro, comp):
                        arbol.poner(h, comp)
        else:
            for lado in lados:
                if arbol.padre.get(lado) != n:
                    if lado not in arbol.padre and arbol.cima(n) != lado:
                        arbol.poner(lado, n, cid)
            if all(arbol.padre.get(x) == n for x in lados):
                for h in arbol.hijos[n]:
                    if h not in lados:
                        arbol.marcas[h].add("sin_lado")

    # 5 · verificación --------------------------------------------------------------------------
    principal = arbol.cima(raiz) if raiz in arbol.nodos else raiz
    seleccionadas = []
    for c in candidatas:
        ok, motivo, detalle = cumple(arbol, libro, c, set(rotos))
        if ok:
            seleccionadas.append(c["id"])
            # La rama que pone una afirmación de la hipótesis se dibuja como tal (§20.2).
            if set(hyps) & set((c.get("scope") or {}).get("hypothesis_ids") or []):
                for x in (c["subject_id"], objeto(c)) if c["predicate"] == "sister_group_of" else (c["subject_id"],):
                    if x in arbol.nodos:
                        arbol.marcas[arbol.subir_troncos(x)].add("hipotesis")
        else:
            fuera[c["id"]] = (motivo, detalle)
    for c in andamio:
        if cumple(arbol, libro, c, set(rotos))[0]:
            hallazgos.append(f"{', '.join(hyps)} excluye {c['id']}, y el árbol re-enraizado la cumple: la exclusión "
                             "no se debe a su raíz.")
    return {
        "hipotesis": hyps, "arbol": arbol, "principal": principal, "seleccionadas": sorted(seleccionadas),
        "fuera": fuera, "rotos": rotos, "usadas": usadas, "hallazgos": hallazgos, "sin_raiz": sin_raiz,
        "anclas": [{"grupo": a["grupo"], "nodo": a["nodo"], "motivo": a["motivo"],
                    "claim": a["claims"][0]["id"] if len(a["claims"]) == 1 else None} for a in anclas],
    }


def reenraizar(arbol: Arbol, n: str, a: str, b: str, origen: str) -> list[str]:
    """Pone la raíz de n entre a (en lo hondo) y su complemento b. Devuelve los clados rotos."""
    camino = list(reversed([x for x in arbol.ancestros(a) if x == n or arbol.es_ancestro(n, x)]))
    # camino = [n, P1, ..., Pk], Pk padre de a
    actual = None
    for nivel in range(len(camino) - 1, 0, -1):
        p = camino[nivel]
        siguiente = a if nivel == len(camino) - 1 else camino[nivel + 1]
        grupo = [h for h in arbol.hijos[p] if h != siguiente] + ([actual] if actual else [])
        if len(grupo) == 1:
            actual = grupo[0]
        else:
            i = arbol.implicito()
            arbol.marcas[i].add("reenraizado")
            for h in grupo:
                arbol.poner(h, i)
            actual = i
    arbol.soltar(a)
    grupo0 = [h for h in arbol.hijos[n] if h != camino[1]] + ([actual] if actual else [])
    arbol.poner(b, n, origen)
    for h in grupo0:
        arbol.poner(h, b)
    arbol.poner(a, n, origen)
    # Del más hondo al más alto: cada clado del camino se queda sin hijos al quitar el de debajo.
    rotos = []
    for p in reversed(camino[1:]):
        arbol.quitar(p)
        if not p.startswith("~"):
            rotos.append(p)
    return sorted(rotos)


def cumple(arbol: Arbol, libro: Libro, c: dict, rotos: set[str]) -> tuple[bool, str, str]:
    """¿Se cumple la afirmación en el árbol? Si no, por qué."""
    pred, s, o = c["predicate"], c["subject_id"], objeto(c)
    et = libro.etiqueta

    def ausente(x: str) -> str | None:
        if x in rotos:
            return f"{et(x)} deja de ser un clado con esta raíz"
        if x not in arbol.nodos and not any(x in v for v in arbol.anotaciones.values()):
            return f"{et(x)} no está en el árbol"
        return None

    for x in (s, o):
        if x and (m := ausente(x)):
            return False, "contradicha", m
    if pred == "member_of":
        if s.startswith("POP-"):
            donde = next((k for k, v in arbol.anotaciones.items() if s in v), None)
            if donde == o or (donde and arbol.es_ancestro(o, donde)):
                return True, "", ""
            return False, "contradicha", f"{et(s)} se anota en {et(donde) if donde else 'ningún nodo'}"
        if arbol.es_ancestro(o, s):
            return True, "", ""
        p = arbol.padre.get(s)
        return False, "contradicha", f"{et(s)} cuelga de {et(p) if p and not p.startswith('~') else 'otro nodo'}"
    if pred == "sister_group_of":
        a, b = arbol.subir_troncos(s), arbol.subir_troncos(o)
        pa, pb = arbol.padre.get(a), arbol.padre.get(b)
        if pa is not None and pa == pb:
            hijos = {h for h in arbol.hijos[pa] if "sin_lado" not in arbol.marcas[h]}
            if hijos == {a, b}:
                return True, "", ""
            return False, "contradicha", f"{et(s)} y {et(o)} comparten padre con otros nodos"
        if arbol.cima(a) != arbol.cima(b):
            return False, "no_dibujable", f"{et(s)} y {et(o)} quedan en árboles distintos"
        return False, "contradicha", f"{et(s)} y {et(o)} no son hermanos en este árbol"
    if pred == "stem_lineage_of":
        p = arbol.padre.get(s)
        if p is not None and arbol.tipo.get(p) == "tronco" and arbol.padre.get(o) == p:
            return True, "", ""
        return False, "contradicha", f"{et(s)} no está en el tronco de {et(o)}"
    if pred == "diverges_from":
        if arbol.cima(s) != arbol.cima(o):
            return False, "no_dibujable", f"{et(s)} y {et(o)} quedan en árboles distintos"
        if arbol.es_ancestro(s, o) or arbol.es_ancestro(o, s):
            return False, "contradicha", f"uno de los dos contiene al otro"
        return True, "", ""
    return False, "no_dibujado", pred


# --- salida -----------------------------------------------------------------------------

def orden_hijos(libro: Libro, arbol: Arbol, n: str) -> list[str]:
    def clave(h: str) -> tuple:
        return (0 if arbol.hijos.get(h) else 1, primera_hoja(h).lower(), h)

    def primera_hoja(h: str) -> str:
        if h.startswith("~"):
            hs = sorted(primera_hoja(x) for x in arbol.hijos.get(h, [])) or [h]
            return hs[0]
        return libro.etiqueta(h)
    return sorted(arbol.hijos.get(n, []), key=clave)


def newick(libro: Libro, arbol: Arbol, n: str) -> str:
    rotulo = "" if n.startswith("~") else n
    hijos = orden_hijos(libro, arbol, n)
    if not hijos:
        return rotulo
    return "(" + ",".join(newick(libro, arbol, h) for h in hijos) + ")" + rotulo


def nodo_json(libro: Libro, arbol: Arbol, n: str) -> dict:
    tipo = arbol.tipo.get(n) or TIPOS.get(n.split("-")[0], "otro")
    return {
        "id": None if n.startswith("~") else n,
        "etiqueta": None if n.startswith("~") else libro.r.etiqueta(n, larga=True),
        "corta": None if n.startswith("~") else libro.etiqueta(n),
        "tipo": tipo,
        "marcas": sorted(arbol.marcas.get(n, ())),
        "anotaciones": [{"id": p, "etiqueta": libro.etiqueta(p)} for p in sorted(arbol.anotaciones.get(n, []))],
        "origen": arbol.origen.get(n),
        "hijos": [nodo_json(libro, arbol, h) for h in orden_hijos(libro, arbol, n)],
    }


def parentesis(libro: Libro, arbol: Arbol, n: str) -> str:
    """Un árbol suelto, legible: «(Corallochytrea (Corallochytrium), Syssomonas)»."""
    rotulo = "" if n.startswith("~") else f"{libro.etiqueta(n)} ({n})"
    hijos = orden_hijos(libro, arbol, n)
    if not hijos:
        return rotulo
    dentro = ", ".join(parentesis(libro, arbol, h) for h in hijos)
    return f"{rotulo} [{dentro}]" if rotulo else f"[{dentro}]"


def registro(libro: Libro, espec: dict, v: dict, previo: dict | None, ident: str, corte: str,
             revision: str) -> dict:
    """El PHYVIEW de una vista (E.10)."""
    arbol, hyps, fuera = v["arbol"], v["hipotesis"], v["fuera"]
    et = libro.etiqueta
    if hyps:
        h = libro.r.hypotheses[hyps[0]]
        corto = hipotesis_corta(h)
        nombre = f"Red de {corto + ' · ' if corto else ''}{h['name']}"
    else:
        nombre = "Tronco común de la red"

    criterios = [
        (f"Materializa {', '.join(hyps)} sobre el tronco común: las afirmaciones de topología sin alcance de "
         "hipótesis." if hyps else
         "Sólo el tronco común: las afirmaciones de topología sin alcance de hipótesis. Ningún conflicto se decide."),
        "Topología es member_of (cuelga un nodo de su padre más interno), sister_group_of (junta dos hermanos), "
        "stem_lineage_of (pone un linaje en el tronco de un clado) y diverges_from (sólo se comprueba).",
        "Cada afirmación seleccionada se cumple en el árbol dibujado; la que no, se excluye con su motivo.",
        "Excluir no es borrar: las excluidas siguen en el libro mayor, y las de las hipótesis rivales se "
        "materializan en su propia vista (§20.3).",
    ]
    for a in v["anclas"]:
        criterios.append(f"{a['grupo']} decide la primera divergencia de {et(a['nodo'])} ({a['nodo']}): "
                         f"{a['motivo']}")
    for k in sorted(v["usadas"]):
        lectura = "complemento" if k in espec.get("complementos", {}) else "composición"
        criterios.append(f"Lectura de la especificación ({lectura}) de {et(k)} ({k}): {v['usadas'][k]}")
    por_motivo: dict[str, list[str]] = defaultdict(list)
    for cid, (motivo, _) in fuera.items():
        por_motivo[motivo].append(cid)
    for motivo in MOTIVOS:
        if por_motivo.get(motivo):
            criterios.append(f"Excluidas porque {MOTIVOS[motivo]}: {', '.join(sorted(por_motivo[motivo]))}.")

    simplificaciones = []
    sin_resolver = sorted({g for h in libro.r.hypotheses for g in libro.grupos_de.get(h, [])
                           if libro.grupos.get(g, {}).get("scope") == "topology"}
                          - {g for h in hyps for g in libro.grupos_de.get(h, [])} | set(v["sin_raiz"]))
    if sin_resolver:
        simplificaciones.append(
            "Conflictos que la vista no decide y deja en politomía: "
            + "; ".join(f"{g} ({libro.grupos[g]['name']})" for g in sin_resolver) + ".")
    sin_lado = sorted(n for n in arbol.nodos if "sin_lado" in arbol.marcas.get(n, ()))
    if sin_lado:
        simplificaciones.append("Sin lado declarado en la raíz de la hipótesis, en politomía: "
                                + ", ".join(f"{et(n)} ({n})" for n in sin_lado) + ".")
    cimas = sorted({arbol.cima(n) for n in arbol.nodos} - {v["principal"]})
    fuera_arbol = [parentesis(libro, arbol, c) for c in cimas]
    if fuera_arbol:
        simplificaciones.append("Fuera del árbol principal, porque ninguna afirmación seleccionada los enlaza con "
                                f"{et(espec['raiz'])}: " + "; ".join(fuera_arbol) + ".")
    if any(arbol.anotaciones.values()):
        simplificaciones.append("Las poblaciones no son ramas: se anotan en el nodo del que son miembro ("
                                + ", ".join(f"{et(p)} en {et(k)}" for k, ps in sorted(arbol.anotaciones.items())
                                            for p in ps) + ").")
    if hyps:
        otras = [c for h in hyps for c in (libro.r.hypotheses[h].get("included_claim_ids") or [])
                 if c in libro.r.claims and libro.r.claims[c]["predicate"] not in DE_RED]
        if otras:
            simplificaciones.append(f"{len(otras)} afirmaciones de la hipótesis no son de topología y no se "
                                    f"dibujan: {', '.join(sorted(otras))}.")
    simplificaciones.append("Los fósiles asignados a un clado (assigned_to) y las fechas no se dibujan: están en "
                            "«Relojes y rocas».")
    simplificaciones.append("Newick no expresa reticulación; esta vista no selecciona ninguna afirmación reticulada.")

    notas = ["Vista editorial fechada, no verdad absoluta (§15.4)."]
    if v["rotos"]:
        notas.append("Con esta raíz dejan de ser clados: "
                     + ", ".join(f"{et(x)} ({x})" for x in v["rotos"]) + ".")
    if hyps:
        propias = set(c for h in hyps for c in (libro.r.hypotheses[h].get("excluded_claim_ids") or []))
        contradichas = sorted(c for c, (m, _) in fuera.items()
                              if m == "contradicha" and c not in propias
                              and not (libro.r.claims[c].get("scope") or {}).get("hypothesis_ids"))
        if contradichas and v["rotos"]:
            notas.append(f"La raíz de {', '.join(hyps)} contradice {len(contradichas)} afirmaciones del tronco que "
                         f"la hipótesis no declara en excluded_claim_ids: {', '.join(contradichas)}.")
    notas += v["hallazgos"]

    contenido = {
        "name": nombre,
        "cutoff_date": corte,
        "hypothesis_ids": list(hyps),
        "selected_claim_ids": v["seleccionadas"],
        "excluded_claim_ids": sorted(fuera),
        "event_ids": [],
        "editorial_criteria": criterios,
        "simplifications": simplificaciones,
        "topology": {"format": "newick", "content": newick(libro, arbol, v["principal"]) + ";",
                     "content_path": None, "content_hash": None, "reticulation": False},
        "scale": espec.get("escala"),
        "generated_artifacts": [{"artifact_type": "report", "path": "generated/views/red.html",
                                 "content_hash": None}],
        "issue_ids": [],
        "notes": notas,
        "record_status": "active",
    }
    if previo and all(previo.get(k) == x for k, x in contenido.items()):
        return previo
    version = "1.0.0"
    if previo:
        mayor, menor, _ = (int(x) for x in previo["view_version"].split("."))
        version = f"{mayor}.{menor + 1}.0"
    return {"id": ident, **contenido, "view_version": version, "built_from_dataset_revision": revision}


def construir(base: Path = RECORDS, raiz: Path = ROOT, espec_path: Path | None = None,
              vistas_path: Path | None = None) -> dict:
    espec = json.loads((espec_path or raiz / ESPEC.relative_to(ROOT)).read_text(encoding="utf-8"))
    vistas_path = vistas_path or raiz / VISTAS.relative_to(ROOT)
    manifiesto_path = raiz / "knowledge" / "corpus" / "manifests" / "dataset.json"
    manifiesto = json.loads(manifiesto_path.read_text(encoding="utf-8"))
    congelada = manifiesto.get("corpus_freeze") or {}
    corpus = json.loads((raiz / congelada["path"]).read_text(encoding="utf-8")) if congelada.get("path") else {}
    corte = corpus.get("cutoff") or "1970-01-01"
    revision = manifiesto.get("dataset_revision") or "REV-000000"

    libro = Libro(base, raiz)
    previos = leer(vistas_path)
    por_hyps = {tuple(sorted(p.get("hypothesis_ids") or [])): p for p in previos}
    siguiente = max([int(p["id"].split("-")[1]) for p in previos] or [0]) + 1

    registros, vistas = [], []
    pedidas = set()
    for pedida in espec["vistas"]:
        hyps = list(pedida["hipotesis"])
        clave = tuple(sorted(hyps))
        pedidas.add(clave)
        for h in hyps:
            if h not in libro.r.hypotheses:
                raise SystemExit(f"la especificación pide una vista de {h}, que no está activa")
        previo = por_hyps.get(clave)
        if previo:
            ident = previo["id"]
        else:
            ident = f"PHYVIEW-{siguiente:06d}"
            siguiente += 1
        v = construir_vista(libro, espec, hyps)
        rec = registro(libro, espec, v, previo, ident, corte, revision)
        registros.append(rec)
        vistas.append((rec, v))
    # Una vista que la especificación ya no pide no se borra: se retira (§9.2).
    for p in previos:
        if tuple(sorted(p.get("hypothesis_ids") or [])) not in pedidas:
            registros.append({**p, "record_status": "deprecated"} if p.get("record_status") == "active" else p)
    registros.sort(key=lambda r: r["id"])

    return {"registros": registros, "vistas": vistas, "libro": libro, "espec": espec,
            "meta": {"revision": revision, "snapshot": manifiesto.get("snapshot_id"), "corte": corte,
                     "corpus": {"version": corpus.get("version") or congelada.get("version"),
                                "commit": (congelada.get("commit") or "")[:7],
                                "decision": congelada.get("decision")}}}


def jsonl(registros: list[dict]) -> str:
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in registros)


# --- la página ------------------------------------------------------------------------

TITULOS = {
    "rival": "De hipótesis rivales",
    "otra_hipotesis": "De conflictos que esta vista no decide",
    "excluida": "Excluidas por la hipótesis",
    "contradicha": "Contradichas por este árbol",
    "no_dibujable": "Sin dibujo posible",
    "clasificacion": "Clasificación, no topología",
    "historica": "Históricas",
    "derivada": "Derivadas",
    "no_dibujado": "Predicados que la vista no dibuja",
}


def foco_de(libro: Libro, espec: dict, grupo: str, tronco: dict | None) -> str:
    """El nodo en disputa: el anclado, o el ancestro común de lo que tocan las hipótesis en el tronco."""
    for g, ancla in (espec.get("anclas") or {}).items():
        if g == grupo:
            return ancla["nodo"]
    raiz = espec["raiz"]
    if not tronco:
        return raiz
    arbol, principal = tronco["arbol"], tronco["principal"]
    tocados = set()
    for h in sorted(libro.miembros.get(grupo, ())):
        for cid in libro.r.hypotheses[h].get("included_claim_ids") or []:
            c = libro.r.claims.get(cid)
            if c and c["predicate"] in DE_RED:
                tocados |= {x for x in (c["subject_id"], objeto(c)) if x}
    puestos = sorted(x for x in tocados if x in arbol.nodos and arbol.cima(x) == principal)
    if not puestos:
        return raiz
    comunes = None
    for x in puestos:
        linea = [x] + arbol.ancestros(x)
        comunes = linea if comunes is None else [y for y in linea if y in comunes]
    foco = comunes[0] if comunes else raiz
    # Si el común es uno de los tocados, se sube uno: la relación en disputa tiene que verse.
    if foco in tocados and foco in arbol.padre:
        foco = arbol.padre[foco]
    while foco.startswith("~") and foco in arbol.padre:
        foco = arbol.padre[foco]
    return foco


def datos_pagina(d: dict) -> dict:
    libro, espec = d["libro"], d["espec"]
    et = libro.etiqueta
    tronco = next((v for _, v in d["vistas"] if not v["hipotesis"]), None)
    vistas = []
    for rec, v in d["vistas"]:
        arbol = v["arbol"]
        excluidas = []
        for motivo in MOTIVOS:
            filas = [{"id": cid, "texto": libro.r.resumen(libro.r.claims[cid]), "detalle": det}
                     for cid, (m, det) in sorted(v["fuera"].items()) if m == motivo]
            if filas:
                excluidas.append({"motivo": motivo, "titulo": TITULOS[motivo], "por_que": MOTIVOS[motivo],
                                  "afirmaciones": filas})
        h = libro.r.hypotheses[v["hipotesis"][0]] if v["hipotesis"] else None
        cimas = sorted({arbol.cima(n) for n in arbol.nodos} - {v["principal"]})
        vistas.append({
            "id": rec["id"], "version": rec["view_version"], "revision": rec["built_from_dataset_revision"],
            "nombre": rec["name"], "corto": hipotesis_corta(h) if h else None,
            "titulo": h["name"] if h else "Tronco común",
            "hipotesis": v["hipotesis"],
            "descripcion": (re.sub(r"\s*\(H\d+ del corredor\)$", "", h.get("description") or "") if h else
                            "Lo que ninguna hipótesis disputa: las afirmaciones de topología sin alcance de hipótesis."),
            "grupos": [g for x in v["hipotesis"] for g in libro.grupos_de.get(x, [])],
            "arbol": nodo_json(libro, arbol, v["principal"]),
            "sueltos": [nodo_json(libro, arbol, c) for c in cimas],
            "rotos": [{"id": x, "etiqueta": et(x)} for x in v["rotos"]],
            "sin_lado": [{"id": n, "etiqueta": et(n)} for n in sorted(arbol.nodos)
                         if "sin_lado" in arbol.marcas.get(n, ())],
            "sin_raiz": v["sin_raiz"],
            "seleccionadas": len(rec["selected_claim_ids"]),
            "excluidas": excluidas,
            "criterios": rec["editorial_criteria"],
            "simplificaciones": rec["simplifications"],
            "notas": rec["notes"][1:],
            "newick": rec["topology"]["content"],
        })
    grupos = []
    for g in sorted(libro.grupos):
        if libro.grupos[g].get("scope") != "topology":
            continue
        ids = [x["id"] for x in vistas if g in x["grupos"]]
        if not ids:
            continue
        grupos.append({"id": g, "nombre": libro.grupos[g]["name"], "descripcion": libro.grupos[g]["description"],
                       "foco": foco_de(libro, espec, g, tronco), "vistas": ids})
    total = sum(1 for c in libro.r.claims.values() if c["predicate"] in DE_RED)
    return {"vista": {"nombre": espec.get("nombre"), "decision": espec.get("decision"), **d["meta"],
                      "afirmaciones_de_red": total},
            "raiz": espec["raiz"], "grupos": grupos, "vistas": vistas,
            "tronco": next((x["id"] for x in vistas if not x["hipotesis"]), None)}


def pagina(datos: dict, documento: bool = True) -> str:
    """La plantilla con los datos dentro. Sin `documento`, el fragmento para el visor de artefactos."""
    plantilla = PLANTILLA.read_text(encoding="utf-8")
    cabeza, _, cuerpo = plantilla.partition("<!--CUERPO-->")
    carga = json.dumps(datos, ensure_ascii=False, sort_keys=True).replace("</", "<\\/")
    v = datos["vista"]
    sustituciones = {
        "__DATOS__": carga,
        "__META__": html.escape(f"{v['revision']} · {v['snapshot']} · corpus {v['corpus']['version']} "
                                f"({v['corpus']['commit']}), corte {v['corte']} · {v['decision']}"),
        "__CUENTA__": html.escape(f"{len(datos['vistas'])} vistas sobre {v['afirmaciones_de_red']} afirmaciones de "
                                  f"topología y {len(datos['grupos'])} conflictos."),
    }
    for clave, valor in sustituciones.items():
        cabeza, cuerpo = cabeza.replace(clave, valor), cuerpo.replace(clave, valor)
    if not documento:
        return cabeza.strip() + "\n" + cuerpo.strip() + "\n"
    return ('<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + cabeza.strip() + "\n</head>\n<body>\n" + cuerpo.strip() + "\n</body>\n</html>\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="La red por hipótesis: una vista filogenética por hipótesis")
    ap.add_argument("--records", default=None, help="directorio de registros; por defecto el dataset real")
    ap.add_argument("--salida", default=None, help=f"carpeta de la página; por defecto {SALIDA.relative_to(ROOT)}")
    ap.add_argument("--vistas", default=None, help=f"fichero de vistas; por defecto {VISTAS.relative_to(ROOT)}")
    ap.add_argument("--fragmento", default=None, metavar="RUTA",
                    help="escribe además la página sin envoltorio, para publicarla como artefacto")
    args = ap.parse_args()

    base = Path(args.records).resolve() if args.records else RECORDS
    if not base.is_dir():
        print(f"ERROR no existe el directorio: {base}")
        return 1
    vistas_path = Path(args.vistas).resolve() if args.vistas else VISTAS
    d = construir(base, vistas_path=vistas_path)
    vistas_path.parent.mkdir(parents=True, exist_ok=True)
    vistas_path.write_text(jsonl(d["registros"]), encoding="utf-8")
    datos = datos_pagina(d)
    salida = Path(args.salida).resolve() if args.salida else SALIDA
    salida.mkdir(parents=True, exist_ok=True)
    (salida / "red.json").write_text(json.dumps(datos, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                                     encoding="utf-8")
    (salida / "red.html").write_text(pagina(datos), encoding="utf-8")
    if args.fragmento:
        Path(args.fragmento).write_text(pagina(datos, documento=False), encoding="utf-8")

    print(f"La red por hipótesis · {len(d['vistas'])} vistas")
    for rec, v in d["vistas"]:
        print(f"  {rec['id']} v{rec['view_version']} · {rec['name']} · seleccionadas "
              f"{len(rec['selected_claim_ids'])}, excluidas {len(rec['excluded_claim_ids'])}"
              + (f", rotos {len(v['rotos'])}" if v["rotos"] else ""))
    for ruta in (vistas_path, salida / "red.html", salida / "red.json"):
        try:
            print(f"  {ruta.relative_to(ROOT)}")
        except ValueError:
            print(f"  {ruta}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
