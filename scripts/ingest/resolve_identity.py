#!/usr/bin/env python3
"""Resolución de identidad asistida (§17 paso 5).

El paso 5 decide si dos menciones son la misma entidad. Es juicio humano
(§27.12) y la regla es conservadora: **no se fusionan entidades por parecido
nominal**. Con 1.335 etiquetas eso son horas de trabajo, y el peligro real no es
que el revisor tarde: es que se canse y empiece a aceptar sugerencias sin
mirarlas. Una herramienta que propone fusiones plausibles a granel es peor que
no tener herramienta, porque convierte el cansancio en datos.

Así que esta no propone. Hace tres cosas distintas:

1. **Separa lo que no es decisión.** Una etiqueta que aparece una sola vez y no
   se parece a ninguna otra es una entidad y ya está. Sacarla de la lista es lo
   que hace tratable el resto.
2. **Ordena por riesgo, de más a menos.** Lo primero que se mira es lo que más
   cuesta equivocarse, mientras queda atención. Lo que se mira cansado es la
   confirmación en bloque de cadenas que sólo difieren en mayúsculas.
3. **Da contexto suficiente para decidir**, y sólo automatiza el caso en que no
   hay nada que decidir: cadenas idénticas tras normalizar espacios, mayúsculas
   y acentos — y aun ésas las confirma una persona.

**Lo que nunca hace.** Fusionar por parecido. «Choanozoa» y «Choanozoa sensu
stricto» son dos circunscripciones distintas (§7.3) y una herramienta que las
una rompe el modelo de identidad entero. Los calificadores de circunscripción
suben el riesgo de un par, no lo bajan.

Toda etiqueta que quede sin resolver produce un `Issue`, nunca un dato silencioso
(§4.7, F.3): la ambigüedad bloquea el registro afectado, no la sección entera.

    resolve_identity.py propose DOCUMENTO.md [--out DIR] [--corpus DIR]
    resolve_identity.py apply --review revision.md --map identity-map.json

Los identificadores `TMP-` de la salida son provisionales y de esta herramienta.
Los identificadores opacos de §16.3 los asigna el delta, no esto.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from parse_research import parse  # noqa: E402


# --------------------------------------------------------------------------
# Normalización
# --------------------------------------------------------------------------

# Cadenas que el prompt exige escribir literalmente para declarar un hueco o un
# campo que no aplica. Son marcadores, no cosas nombradas: si entraran en el
# inventario, «n/a» sería la entidad con más afirmaciones del corpus.
MARCADORES = {
    "n/a", "na", "-", "--", "—", "ninguno", "ninguna", "sin localizar",
    "no consta en la fuente", "no aplica", "desconocido", "desconocida",
    "sin cifra publicada localizada",
    "sin sinapomorfia morfologica publicada localizada",
    "no localizado en esta sesion", "no buscado",
    "la literatura declara que no se sabe", "sin fuente", "varios", "varias",
}

# Claves locales del propio documento (§17: `C-001`, `S01`, `E01`, `H01`).
# Aparecen como sujeto y objeto en las filas de `incompatible_con` y
# `cuestionado_por`, que relacionan afirmaciones entre sí. Una afirmación no es
# una entidad.
REF_LOCAL = re.compile(r"^(?:C-\d{1,4}|[SEHF]-?\d{2,4})$", re.IGNORECASE)

# Calificadores de circunscripción. Los quitamos SÓLO para detectar que dos
# etiquetas comparten núcleo, que es motivo para mirar el par con lupa. Nunca
# para igualarlas: la diferencia entre `sensu stricto` y `sensu lato` es
# exactamente la información que §7.3 obliga a conservar.
CALIFICADORES = [
    r"sensu\s+stricto", r"sensu\s+lato", r"sensu\s+latissimo", r"sensu\s+amplo",
    r"sensu\s+[a-z][a-z.'\-]+",
    r"s\.\s*s\.?", r"s\.\s*l\.?", r"ss\.", r"sl\.",
    r"en\s+sentido\s+(?:estricto|amplio|restringido)",
    r"auct\.?", r"emend\.?(?:\s+[a-z][a-z.'\-]+)?",
    r"pro\s+parte", r"ex\s+parte", r"partim",
    r"nom\.\s*(?:illeg|nud|dub|cons|rej)\.?",
    r"uso\s+historico", r"circunscripcion\s+historica",
]
CALIF_FINAL = re.compile(
    r"[\s,;:]*[(\[]?\s*(?:" + "|".join(CALIFICADORES) + r")\s*[)\]]?[\s.,;]*$"
)

# Aristas hijo → padre, para saber si dos ubicaciones están anidadas.
PRED_ASCENDENTES = {"miembro_de", "desciende_de", "grupo_corona_de", "linaje_troncal_de"}

VIGENCIA_NO_ACTUAL = {"historical", "superseded", "rejected"}
VIGENCIA_ES = {"historical": "históricas", "superseded": "superadas",
               "rejected": "rechazadas", "current": "vigentes"}

# Ficheros de entidad de §16.3, para el cotejo opcional contra lo ya ingerido.
FICHEROS_CORPUS = [
    "clades.jsonl", "lineages.jsonl", "populations.jsonl", "specimens.jsonl",
    "sites.jsonl", "regions.jsonl", "traits.jsonl", "taxon-concepts.jsonl",
    "taxonomic-names.jsonl",
]


def clave(texto: str) -> str:
    """Forma de comparación: espacios, mayúsculas, acentos y énfasis Markdown.

    El énfasis entra porque el documento escribe los nombres específicos en
    cursiva (`*Giardia*`) y los asteriscos son marcado, no nombre. Es la única
    licencia sobre la lista de §17, y el informe enseña siempre las cadenas
    originales para que la confirmación en bloque signifique algo.
    """
    t = unicodedata.normalize("NFKD", texto)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.replace("’", "'").replace("‘", "'").replace("–", "-").replace("—", "-")
    t = re.sub(r"[*_`]+", "", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip().casefold()


def nucleo(k: str) -> tuple[str, str | None]:
    """Devuelve (núcleo, calificador retirado) sobre una clave ya normalizada."""
    resto, quitados = k, []
    while True:
        m = CALIF_FINAL.search(resto)
        if not m or not resto[: m.start()].strip():
            break
        quitados.append(m.group(0).strip(" ,;:()[]"))
        resto = resto[: m.start()].strip(" ,;:.")
    return resto, (" + ".join(reversed(quitados)) if quitados else None)


def distancia(a: str, b: str, tope: int) -> int:
    """Levenshtein con corte: devuelve tope+1 en cuanto se sabe que se pasa."""
    if abs(len(a) - len(b)) > tope:
        return tope + 1
    if a == b:
        return 0
    anterior = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        actual = [i]
        for j, cb in enumerate(b, 1):
            actual.append(min(anterior[j] + 1, actual[j - 1] + 1,
                              anterior[j - 1] + (ca != cb)))
        if min(actual) > tope:
            return tope + 1
        anterior = actual
    return anterior[-1]


def contenida(corta: str, larga: str, texto_largo: str) -> bool:
    """¿Está `corta` dentro de `larga` de una forma que signifique algo?

    Por palabras siempre: «linaje hospedador arqueano» dentro de «linaje
    hospedador arqueano no identificado» es justo el caso que §14 del encargo
    teme, tres redacciones de una sola cosa.

    Pegada, sólo si lo que sobra empieza por mayúscula —«FIX-Alfa» dentro de
    «FIX-AlfaHistorico»—, que es un compuesto y no una forma de nomenclatura.
    Sin esa condición, «Theria» estaría dentro de Eutheria, Metatheria,
    Cladotheria y Laurasiatheria, que son ocho preguntas cuya respuesta se sabe
    de antemano: un clado no es su clado padre.
    """
    if corta == larga or len(corta) > len(larga):
        return False
    if f" {corta} " in f" {larga} ":
        return True
    if len(corta) >= 5 and larga.startswith(corta):
        return texto_largo[len(corta):len(corta) + 1].isupper()
    return False


BINOMIAL = re.compile(r"[a-z][a-z-]+$")


def rango_inferior(corto: str, largo: str) -> bool:
    """¿Es `largo` el mismo nombre más un epíteto — género→especie, especie→subespecie?

    *Australopithecus* y *Australopithecus afarensis* comparten cadena y no son
    la misma entidad ni por asomo: un género no es una de sus especies. Es
    estructura de la nomenclatura binomial, no juicio, y en un documento con
    cientos de nombres específicos este patrón por sí solo llenaría la revisión
    de preguntas cuya respuesta ya se sabe.

    No se aplica a «Choanozoa» / «Choanozoa sensu stricto»: ahí el añadido es un
    calificador de circunscripción, y esos pares van al bloque de riesgo 2.
    """
    tc, tl = corto.split(), largo.split()
    if len(tc) > 2 or len(tl) <= len(tc) or not corto[:1].isupper():
        return False
    if [t.casefold() for t in tl[:len(tc)]] != [t.casefold() for t in tc]:
        return False
    return all(BINOMIAL.fullmatch(t) for t in tl[len(tc):])


CIFRAS = re.compile(r"\d+")


def difieren_solo_en_cifras(a: str, b: str) -> bool:
    """¿Son el mismo texto con distinta numeración?

    `Denisova 3` y `Denisova 4`. `KNM-ER 1470` y `KNM-ER 1472`. Su distancia de
    edición es 1 y por forma son casi la misma cadena, así que el bloqueo los
    junta y el criterio de vecindad los presenta. Pero una numeración distinta
    **es** lo que distingue un ejemplar de otro: la cifra no es ruido alrededor
    del nombre, es el nombre. Que dos etiquetas sólo difieran ahí es la señal
    más limpia que hay de que son dos cosas, no un indicio de que sean una.

    Es el mismo razonamiento que `rango_inferior` aplica a la nomenclatura
    binomial: preguntas cuya respuesta se sabe de antemano, y que en un corpus
    con series numeradas se cuentan por cientos. Cada una gasta la atención que
    hace falta arriba, en la sección donde equivocarse cuesta caro.

    El riesgo de callar está medido: si la numeración fuera una errata, la
    consecuencia es una entidad de más, que se corrige fusionando después. La de
    preguntar es que alguien conteste «sí» cansado a la pregunta 400 y funda dos
    ejemplares, que no se corrige sin volver al documento.
    """
    if a == b:
        return False
    if not CIFRAS.search(a) or not CIFRAS.search(b):
        return False
    return CIFRAS.sub("#", a) == CIFRAS.sub("#", b)


def prefijo_comun(a: str, b: str) -> int:
    n = 0
    for x, y in zip(a, b):
        if x != y:
            break
        n += 1
    return n


def sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


# --------------------------------------------------------------------------
# Inventario de etiquetas
# --------------------------------------------------------------------------

@dataclass
class Etiqueta:
    texto: str
    clave: str
    nucleo: str
    calificador: str | None
    origenes: set[str] = field(default_factory=set)
    sujeto_en: list[str] = field(default_factory=list)
    objeto_en: list[str] = field(default_factory=list)
    predicados: dict[str, set[str]] = field(default_factory=dict)
    fuentes: set[str] = field(default_factory=set)
    vigencias: set[str] = field(default_factory=set)
    filas: list[dict] = field(default_factory=list)
    tipos: set[str] = field(default_factory=set)
    marcas: set[str] = field(default_factory=set)
    sinonimos: set[str] = field(default_factory=set)
    id_corpus: str | None = None

    @property
    def apariciones(self) -> int:
        return len(self.sujeto_en) + len(self.objeto_en)


def descartable(texto: str) -> str | None:
    """Motivo por el que una celda no nombra una entidad, o None."""
    k = clave(texto)
    if not k:
        return "celda vacía"
    if k in MARCADORES:
        return "marcador de hueco o de campo que no aplica"
    if REF_LOCAL.match(texto.strip()):
        return "clave local del documento (una afirmación o una fuente, no una entidad)"
    if not re.search(r"[a-z]", k):
        return "sin letras: es una cifra o un símbolo"
    return None


def partir_sinonimos(celda: str) -> list[str]:
    if not celda or clave(celda) in MARCADORES:
        return []
    trozos = re.split(r"\s*[;,/]\s*|\s+\|\s+", celda)
    return [t.strip() for t in trozos if t.strip() and clave(t) not in MARCADORES]


# Clase gramatical cerrada: palabras que en español encabezan una nota y no un
# nombre. No es una lista de palabras prohibidas sino una categoría entera —
# preposiciones, conjunciones, artículos, adverbios de modalidad y cópulas—, y
# ninguna etiqueta del corredor empieza por una.
INICIO_DE_NOTA = {
    "a", "ademas", "ante", "antes", "aqui", "asi", "aunque", "cf", "como",
    "con", "cuando", "de", "del", "desde", "donde", "durante", "e", "el",
    "ella", "ellos", "en", "entre", "era", "es", "esa", "ese", "esta", "estan",
    "este", "esto", "fue", "hasta", "hoy", "ibid", "idem", "igual", "la", "las",
    "lo", "los", "mientras", "no", "nota", "o", "para", "pero", "por",
    "porque", "posiblemente", "probablemente", "quiza", "quizas", "salvo",
    "segun", "si", "sin", "sobre", "solamente", "solo", "son", "su", "sus",
    "tambien", "tras", "u", "un", "una", "vease", "ver", "y", "ya",
}

# «Choanozoa sensu stricto» son tres, «Choanozoa en su uso histórico» cuatro.
# Cinco deja margen de sobra para un nombre con calificador; a partir de ahí es
# una frase.
MAX_PALABRAS_SINONIMO = 5


def nota_y_no_nombre(frag: str) -> str | None:
    """Motivo por el que un trozo de la columna de sinónimos no es un nombre, o None.

    La columna se llama «sinónimos y grafías alternativas» y el prompt espera
    ahí nombres. Una investigación redactada por otro sistema mete además notas
    —«circunscripción rival de la fila homónima, según S399»—, y al partir la
    celda por comas cada trozo de esa nota entra al inventario como si alguien
    hubiera nombrado algo. Son entidades que no nombró nadie: contenido
    científico inventado por la puerta de atrás, que es justo lo que §5.1
    prohíbe. Y arrastran cola, porque después se parecen entre sí y generan
    decisiones sobre cosas que no existen.

    Tampoco se tiran en silencio: van a la lista de celdas descartadas, que el
    informe enseña. Descartar callando es inventar al revés.
    """
    palabras = clave(frag).split()
    if not palabras:
        return None                      # de eso ya se ocupa descartable()
    if len(palabras) > MAX_PALABRAS_SINONIMO:
        return (f"nota en la columna de sinónimos, no un nombre: {len(palabras)} "
                "palabras")
    if palabras[0] in INICIO_DE_NOTA:
        return (f"nota en la columna de sinónimos: empieza por «{palabras[0]}», "
                "que no encabeza un nombre")
    return None


def inventario(datos: dict, corpus: Path | None) -> tuple[dict[str, Etiqueta], list[tuple[str, str]]]:
    """Reúne toda etiqueta distinta con lo que se sabe de ella en el documento."""
    etiquetas: dict[str, Etiqueta] = {}
    excluidas: list[tuple[str, str]] = []
    vistas_excluidas: set[str] = set()

    def excluir(texto: str, motivo: str) -> None:
        if texto not in vistas_excluidas:
            vistas_excluidas.add(texto)
            excluidas.append((texto, motivo))

    def obtener(texto: str, origen: str) -> Etiqueta | None:
        motivo = descartable(texto)
        if motivo:
            excluir(texto, motivo)
            return None
        e = etiquetas.get(texto)
        if e is None:
            k = clave(texto)
            nuc, cal = nucleo(k)
            e = Etiqueta(texto=texto, clave=k, nucleo=nuc, calificador=cal)
            etiquetas[texto] = e
        e.origenes.add(origen)
        return e

    for c in datos["claims"]:
        vig = (c.get("epistemic_dimensions") or {}).get("historical_status") or "current"
        fuente = (c.get("source_ref") or "").split()[0] if c.get("source_ref") else ""
        pred = (c.get("predicate") or "").strip()
        suj = obtener(c.get("subject_label", ""), "subject")
        obj = obtener(c.get("object_label", ""), "object")
        if suj is not None:
            suj.sujeto_en.append(c["local_id"])
            suj.vigencias.add(vig)
            if fuente:
                suj.fuentes.add(fuente)
            if pred and obj is not None:
                suj.predicados.setdefault(pred, set()).add(obj.texto)
        if obj is not None:
            obj.objeto_en.append(c["local_id"])
            obj.vigencias.add(vig)
            if fuente:
                obj.fuentes.add(fuente)

    # Apéndice B: una fila por cosa nombrada, y una fila por circunscripción
    # cuando el nombre tiene rivales. Dos filas con la misma etiqueta preferida
    # son, por construcción del prompt, dos conceptos.
    for fila in datos["entities"]:
        campos = {clave(k): v for k, v in fila.items() if isinstance(k, str)}
        texto = (campos.get("etiqueta preferida") or "").strip()
        e = obtener(texto, "appendix")
        if e is None:
            continue
        e.filas.append(fila)
        tipo = (campos.get("tipo") or "").strip()
        if tipo and clave(tipo) not in MARCADORES:
            e.tipos.add(tipo)
        marcas = (campos.get("marcas") or "").strip()
        if marcas and clave(marcas) not in MARCADORES:
            e.marcas.update(m for m in re.split(r"\s+", marcas) if m)
        for sin in partir_sinonimos(campos.get("sinonimos y grafias alternativas", "")):
            motivo_nota = nota_y_no_nombre(sin)
            if motivo_nota:
                excluir(sin, motivo_nota)
                continue
            e.sinonimos.add(sin)
            s = obtener(sin, "synonym")
            if s is not None:
                s.sinonimos.add(texto)

    # Cotejo opcional contra lo ya ingerido: §17 paso 5 admite «referencia una
    # entidad existente», y eso sólo puede verse mirando el corpus.
    if corpus is not None:
        for nombre in FICHEROS_CORPUS:
            path = corpus / nombre
            if not path.exists():
                continue
            for linea in path.read_text(encoding="utf-8").splitlines():
                if not linea.strip():
                    continue
                try:
                    rec = json.loads(linea)
                except json.JSONDecodeError:
                    continue
                if rec.get("record_status") not in (None, "active"):
                    continue
                etiqueta = rec.get("preferred_label") or rec.get("label") or rec.get("name")
                if not etiqueta:
                    continue
                e = obtener(str(etiqueta), "corpus")
                if e is not None and rec.get("id"):
                    e.id_corpus = rec["id"]

    return etiquetas, excluidas


def ancestros(etiquetas: dict[str, Etiqueta]) -> dict[str, set[str]]:
    """Clausura de las aristas hijo → padre, para saber si dos ubicaciones anidan.

    Que una etiqueta sea miembro de dos grupos distintos es lo normal cuando uno
    contiene al otro. Sólo delata dos circunscripciones cuando no se alcanzan
    entre sí, y eso hay que calcularlo, no suponerlo.
    """
    memo: dict[str, set[str]] = {}

    def subir(texto: str, pila: set[str]) -> set[str]:
        if texto in memo:
            return memo[texto]
        if texto in pila:
            return set()
        pila.add(texto)
        acc: set[str] = set()
        e = etiquetas.get(texto)
        if e:
            for pred in PRED_ASCENDENTES:
                for padre in e.predicados.get(pred, set()):
                    acc.add(padre)
                    acc |= subir(padre, pila)
        pila.discard(texto)
        memo[texto] = acc
        return acc

    for texto in etiquetas:
        subir(texto, set())
    return memo


# --------------------------------------------------------------------------
# Decisiones
# --------------------------------------------------------------------------

# El orden del informe. Se revisa de arriba abajo, y arriba está lo que más
# cuesta equivocarse.
RIESGO_HOMONIMO = 4
RIESGO_CALIFICADOR = 3
RIESGO_VECINA = 2
RIESGO_IDENTICA = 1

MOTIVOS = {
    "synonym_declared": "el apéndice B declara una sinónimo de la otra",
    "containment": "una está contenida en la otra",
    "edit_distance": "distancia de edición pequeña",
    "shared_root": "misma raíz",
}
# Dentro del bloque de vecinas, de más informativo a menos.
PESO_MOTIVO = {"synonym_declared": 4, "containment": 3, "edit_distance": 2, "shared_root": 1}


@dataclass
class Decision:
    id: str
    kind: str            # block_identical | merge_group | merge_pair | homonym
    riesgo: int
    subrango: int
    etiquetas: list[str]
    motivos: list[str]
    requerida: bool = True
    cubierta_por: str | None = None
    propuesta: str | None = None   # 'same' sólo en las idénticas
    peso: int = 0                  # afirmaciones afectadas: ordena dentro del bloque


def grupos_identicos(etiquetas: dict[str, Etiqueta]) -> list[list[str]]:
    por_clave: dict[str, list[str]] = {}
    for texto, e in etiquetas.items():
        por_clave.setdefault(e.clave, []).append(texto)
    return [sorted(v) for v in por_clave.values() if len(v) > 1]


def claves_bloqueo(e: Etiqueta, tope: int) -> set[tuple[str, str]]:
    """Reduce la comparación de todos contra todos a bloques manejables.

    Comparar 1.335 etiquetas por pares son 890.000 comparaciones, y la mayoría
    entre cadenas que no se parecen en nada. Cada etiqueta genera unas claves y
    sólo se comparan las que comparten alguna.

    La clave `d` es un **vecindario de borrado**: todas las cadenas que salen de
    quitar `tope` caracteres. Dos etiquetas a distancia de edición `tope` o menos
    comparten siempre una, y sin ella una errata en mitad de una palabra corta
    —«Breopsis» y «Breolsis»— se escapaba del bloqueo y no llegaba a compararse.
    """
    compacta = e.clave.replace(" ", "")
    llaves = {("n", e.nucleo)}
    for tok in e.clave.split():
        if len(tok) >= 3:
            llaves.add(("t", tok))
    if len(compacta) >= 5:
        # Para la contención pegada, donde lo que sobra puede ser largo.
        llaves.add(("p", compacta[:5]))
    if len(compacta) >= 4:
        nivel = {compacta}
        for _ in range(max(1, tope)):
            nivel = {s[:i] + s[i + 1:] for s in nivel for i in range(len(s))}
            llaves |= {("d", s) for s in nivel}
    elif compacta:
        llaves.add(("w", compacta))
    return llaves


def pares_candidatos(etiquetas: dict[str, Etiqueta], tope_edicion: int,
                     raiz: int) -> tuple[dict[tuple[str, str], set[str]], dict[str, int]]:
    """Pares que merecen mirada humana, con el motivo por el que la merecen.

    Devuelve también el recuento de los pares que se apartaron por regla, para
    que el informe pueda decir cuántas preguntas se ahorró y por qué. Un filtro
    que no se declara es un filtro en el que no se puede confiar.
    """
    bloques: dict[tuple[str, str], list[str]] = {}
    for texto, e in etiquetas.items():
        for k in claves_bloqueo(e, tope_edicion):
            bloques.setdefault(k, []).append(texto)

    candidatos: set[tuple[str, str]] = set()
    for miembros in bloques.values():
        if len(miembros) < 2:
            continue
        miembros = sorted(miembros)
        for i in range(len(miembros)):
            for j in range(i + 1, len(miembros)):
                candidatos.add((miembros[i], miembros[j]))

    # Un sinónimo declarado en el apéndice B puede no parecerse en nada a su
    # pareja —Choanozoa y Apoikozoa no comparten una letra útil—, así que ningún
    # bloqueo por forma los junta. Se añaden a mano: son pocos y son exactos.
    por_clave = {e.clave: t for t, e in etiquetas.items()}
    for texto, e in etiquetas.items():
        for s in e.sinonimos:
            otro = por_clave.get(clave(s))
            if otro and otro != texto:
                candidatos.add(tuple(sorted((texto, otro))))  # type: ignore[arg-type]

    pares: dict[tuple[str, str], set[str]] = {}
    suprimidos: dict[str, int] = {"rango": 0, "numeracion": 0}
    for a, b in candidatos:
        ea, eb = etiquetas[a], etiquetas[b]
        if ea.clave == eb.clave:
            continue  # eso es el bloque de idénticas, no un par
        motivos: set[str] = set()

        if ea.nucleo == eb.nucleo and (ea.calificador or eb.calificador):
            motivos.add("qualifier")

        if b in ea.sinonimos or a in eb.sinonimos or (
            any(clave(s) == eb.clave for s in ea.sinonimos)
            or any(clave(s) == ea.clave for s in eb.sinonimos)
        ):
            motivos.add("synonym_declared")

        if contenida(ea.clave, eb.clave, eb.texto) or contenida(eb.clave, ea.clave, ea.texto):
            motivos.add("containment")

        if distancia(ea.clave, eb.clave, tope_edicion) <= tope_edicion:
            motivos.add("edit_distance")

        if raiz and " " not in ea.clave and " " not in eb.clave:
            comun = prefijo_comun(ea.clave, eb.clave)
            if comun >= raiz and comun < max(len(ea.clave), len(eb.clave)):
                motivos.add("shared_root")

        # Sólo por estar uno dentro del otro, y siendo el largo el corto más un
        # epíteto, no hay nada que preguntar. Si además hay otro motivo, sí.
        if motivos == {"containment"} and not (ea.calificador or eb.calificador):
            corto, largo = sorted((ea.texto, eb.texto), key=len)
            if rango_inferior(corto, largo):
                suprimidos["rango"] += 1
                continue

        # Lo mismo con la numeración, y por la misma razón. Sólo cuando el
        # parecido de forma es el único motivo: si el apéndice B los declara
        # sinónimos, o si uno lleva calificador de circunscripción, la cifra deja
        # de ser la única diferencia y la pregunta vuelve a tener sentido.
        if motivos <= {"edit_distance", "shared_root"} and difieren_solo_en_cifras(
                ea.clave, eb.clave):
            suprimidos["numeracion"] += 1
            continue

        if motivos:
            pares[(a, b)] = motivos
    return pares, suprimidos


def senales_homonimo(e: Etiqueta, en_sinonimia: set[str],
                     arriba: dict[str, set[str]]) -> tuple[list[str], list[str]]:
    """Indicios de que una sola etiqueta esté nombrando más de una cosa.

    Separados en dos clases a propósito. Los **fuertes** son incompatibles con
    una sola circunscripción: dos filas en el apéndice B, dos grupos hermanos,
    ser miembro y hermano del mismo nodo. Los de **apoyo** son frecuentes y no
    prueban nada por sí solos — en este corredor casi todo lleva `⚠`—, así que
    hacen falta dos para levantar una decisión. Sin esa distinción, la sección
    de riesgo máximo se llenaría de nodos discutidos y dejaría de leerse.
    """
    fuertes: list[str] = []
    apoyo: list[str] = []

    if len(e.filas) > 1:
        fuertes.append(f"el apéndice B le dedica {len(e.filas)} filas: por el propio "
                       "formato del encargo, eso son circunscripciones rivales")
    # `≈` es fuerte por decisión del propio encargo: «Toda marca `≈` obliga a
    # esas filas», una por circunscripción. La marca declara que la equivalencia
    # depende de la definición, que es la definición misma de dos conceptos.
    if "≈" in e.marcas:
        fuertes.append("marcada «≈»: su equivalencia con otro nombre depende de la "
                       "definición adoptada, y el encargo obliga a una fila por "
                       "circunscripción")
    if len(e.tipos) > 1:
        fuertes.append("el apéndice B le da varios tipos: " + ", ".join(sorted(e.tipos)))

    hermanos = e.predicados.get("grupo_hermano_de", set())
    if len(hermanos) > 1:
        fuertes.append(f"se le atribuyen {len(hermanos)} grupos hermanos distintos: "
                       + ", ".join(f"«{h}»" for h in sorted(hermanos)))
    coronas = e.predicados.get("grupo_corona_de", set())
    if len(coronas) > 1:
        fuertes.append("se le atribuyen varios grupos corona: "
                       + ", ".join(f"«{c}»" for c in sorted(coronas)))

    miembro = e.predicados.get("miembro_de", set())
    solapan = miembro & hermanos
    if solapan:
        fuertes.append("es a la vez miembro y grupo hermano de "
                       + ", ".join(f"«{x}»" for x in sorted(solapan))
                       + ": eso no se sostiene con una sola circunscripción")

    if len(miembro) > 1 and len(e.fuentes) > 1:
        ordenados = sorted(miembro)
        sueltos = [
            (x, y) for i, x in enumerate(ordenados) for y in ordenados[i + 1:]
            if y not in arriba.get(x, set()) and x not in arriba.get(y, set())
        ]
        if sueltos:
            x, y = sueltos[0]
            fuertes.append(f"se la ubica en «{x}» y en «{y}», que no se contienen entre sí "
                           f"según el propio documento, y con {len(e.fuentes)} fuentes distintas")

    if "⚠" in e.marcas:
        apoyo.append("marcada «⚠»: posición, contenido o validez discutidos")
    # `[H]` no es homonimia. El encargo la define como «nodo cuya composición
    # depende de la hipótesis adoptada»: un solo nodo cuyo contenido se discute,
    # que es exactamente lo que la capa de hipótesis existe para representar. Un
    # homónimo es otra cosa —un nombre con dos circunscripciones— y confundirlos
    # llenaría la sección de riesgo máximo de nodos discutidos, que en este
    # corredor son casi todos. Cuenta como apoyo, no como prueba.
    if "[H]" in e.marcas:
        apoyo.append("marcada «[H]»: su composición depende de la hipótesis adoptada; "
                     "eso es contenido discutido de un nodo, no necesariamente dos nodos")
    if e.texto in en_sinonimia:
        apoyo.append("participa en una propuesta de sinonimia: hay historia nomenclatural detrás")
    if e.vigencias & VIGENCIA_NO_ACTUAL and "current" in e.vigencias:
        apoyo.append("tiene afirmaciones vigentes y afirmaciones "
                     + "/".join(VIGENCIA_ES[v] for v in sorted(e.vigencias & VIGENCIA_NO_ACTUAL))
                     + ": el nombre se usa hoy y se usó antes, quizá con otro contenido")

    return fuertes, apoyo


def construir_decisiones(etiquetas: dict[str, Etiqueta], tope_edicion: int,
                         raiz: int) -> tuple[list[Decision], list[str], dict[str, int]]:
    arriba = ancestros(etiquetas)
    decisiones: list[Decision] = []

    en_sinonimia: set[str] = set()
    for e in etiquetas.values():
        objetos = e.predicados.get("sinonimo_propuesto_de", set())
        if objetos:
            en_sinonimia.add(e.texto)
            en_sinonimia |= objetos

    for texto, e in sorted(etiquetas.items()):
        fuertes, apoyo = senales_homonimo(e, en_sinonimia, arriba)
        if fuertes or len(apoyo) >= 2:
            decisiones.append(Decision(
                id="", kind="homonym", riesgo=RIESGO_HOMONIMO,
                subrango=2 * len(fuertes) + len(apoyo),
                etiquetas=[texto], motivos=fuertes + apoyo, peso=e.apariciones))

    pares, suprimidos = pares_candidatos(etiquetas, tope_edicion, raiz)
    for (a, b), motivos in pares.items():
        calificador = "qualifier" in motivos
        otros = sorted(motivos - {"qualifier"}, key=lambda m: -PESO_MOTIVO.get(m, 0))
        texto_motivos = []
        if calificador:
            ca = etiquetas[a].calificador or "sin calificador"
            cb = etiquetas[b].calificador or "sin calificador"
            texto_motivos.append(f"mismo núcleo «{etiquetas[a].nucleo}», calificador "
                                 f"distinto: {ca} / {cb}")
        for m in otros:
            if m == "edit_distance":
                d = distancia(etiquetas[a].clave, etiquetas[b].clave, 9)
                texto_motivos.append(f"{MOTIVOS[m]} ({d})")
            elif m == "shared_root":
                n = prefijo_comun(etiquetas[a].clave, etiquetas[b].clave)
                texto_motivos.append(f"{MOTIVOS[m]}: comparten «{etiquetas[a].clave[:n]}»")
            else:
                texto_motivos.append(MOTIVOS[m])
        decisiones.append(Decision(
            id="", kind="merge_pair",
            riesgo=RIESGO_CALIFICADOR if calificador else RIESGO_VECINA,
            subrango=9 if calificador else max((PESO_MOTIVO.get(m, 0) for m in otros), default=0),
            etiquetas=[a, b], motivos=texto_motivos,
            peso=etiquetas[a].apariciones + etiquetas[b].apariciones))

    identicos = grupos_identicos(etiquetas)
    bloque_id = None
    if identicos:
        bloque = Decision(
            id="", kind="block_identical", riesgo=RIESGO_IDENTICA, subrango=9,
            etiquetas=[], motivos=[
                f"{len(identicos)} grupos de cadenas que sólo difieren en espacios, "
                "mayúsculas, acentos o cursivas"],
            peso=sum(sum(etiquetas[t].apariciones for t in g) for g in identicos))
        decisiones.append(bloque)
        bloque_id = bloque

    decisiones.sort(key=lambda d: (-d.riesgo, -d.subrango, -d.peso, d.etiquetas))
    ancho = max(4, len(str(len(decisiones) + len(identicos))))
    for i, d in enumerate(decisiones, 1):
        d.id = f"D-{i:0{ancho}d}"

    # Los grupos idénticos van colgados del bloque: se proponen resueltos y no
    # cuentan como decisión aparte, pero se pueden desmarcar uno a uno.
    n = len(decisiones)
    for g in sorted(identicos, key=lambda g: -sum(etiquetas[t].apariciones for t in g)):
        n += 1
        decisiones.append(Decision(
            id=f"D-{n:0{ancho}d}", kind="merge_group", riesgo=RIESGO_IDENTICA,
            subrango=0, etiquetas=g,
            motivos=["idénticas tras normalizar"], requerida=False,
            cubierta_por=bloque_id.id if bloque_id else None, propuesta="same",
            peso=sum(etiquetas[t].apariciones for t in g)))

    implicadas = {t for d in decisiones for t in d.etiquetas}
    unicas = sorted(t for t in etiquetas if t not in implicadas)
    return decisiones, unicas, suprimidos


# --------------------------------------------------------------------------
# Informe de revisión
# --------------------------------------------------------------------------

def token_revision(doc_hash: str, decisiones: list[Decision]) -> str:
    """Ata el fichero de revisión al mapa que resuelve.

    Sin esto, marcar una revisión y aplicarla contra otro mapa produciría
    fusiones que nadie autorizó, en silencio y con aspecto de trabajo hecho.
    """
    h = hashlib.sha256(doc_hash.encode("utf-8"))
    for d in decisiones:
        h.update(f"|{d.id}:{d.kind}:{'~'.join(d.etiquetas)}".encode("utf-8"))
    return h.hexdigest()[:16]


def _contexto(texto: str, etiquetas: dict[str, Etiqueta], por_id: dict,
              limite: int) -> list[str]:
    e = etiquetas[texto]
    lineas = []
    cabeza = []
    if e.id_corpus:
        cabeza.append(f"ya en el corpus como `{e.id_corpus}`")
    if e.tipos:
        cabeza.append("tipo: " + ", ".join(sorted(e.tipos)))
    if e.marcas:
        cabeza.append("marcas: " + " ".join(sorted(e.marcas)))
    if e.sinonimos:
        cabeza.append("sinónimos declarados: " + ", ".join(f"«{s}»" for s in sorted(e.sinonimos)))
    if e.fuentes:
        cabeza.append("fuentes: " + ", ".join(sorted(e.fuentes)))
    cabeza.append("1 aparición" if e.apariciones == 1 else f"{e.apariciones} apariciones")
    lineas.append(f"  - «{texto}» — " + " · ".join(cabeza))
    for cid in (e.sujeto_en + e.objeto_en)[:limite]:
        c = por_id.get(cid)
        if not c:
            continue
        obj = c.get("object_label") or "n/a"
        fuente = c.get("source_ref") or "sin fuente"
        lineas.append(f"      `{cid}` {c.get('subject_label')} · "
                      f"{c.get('predicate')} · {obj}  ({fuente})")
    resto = e.apariciones - min(limite, e.apariciones)
    if resto > 0:
        lineas.append(f"      … y {resto} fila{'s' if resto != 1 else ''} más")
    return lineas


def informe(documento: Path, doc_hash: str, datos: dict, etiquetas: dict[str, Etiqueta],
            decisiones: list[Decision], unicas: list[str],
            excluidas: list[tuple[str, str]], limite: int,
            hallazgos_parse: int, suprimidos: dict[str, int]) -> tuple[str, dict]:
    por_id = {c["local_id"]: c for c in datos["claims"]}
    token = token_revision(doc_hash, decisiones)

    requeridas = [d for d in decisiones if d.requerida]
    por_clase = {
        "homonym": [d for d in decisiones if d.kind == "homonym"],
        "qualifier": [d for d in decisiones if d.kind == "merge_pair" and d.riesgo == RIESGO_CALIFICADOR],
        "neighbour": [d for d in decisiones if d.kind == "merge_pair" and d.riesgo == RIESGO_VECINA],
        "identical_groups": [d for d in decisiones if d.kind == "merge_group"],
    }
    n_identicas = sum(len(d.etiquetas) for d in por_clase["identical_groups"])

    L: list[str] = []
    L.append(f"# Revisión de identidad · {documento.name}")
    L.append("")
    L.append(f"<!-- review-token: {token} -->")
    L.append(f"<!-- document-hash: {doc_hash} -->")
    L.append("")
    L.append(f"Generado el {date.today().isoformat()} por `scripts/ingest/resolve_identity.py`. "
             "Resuelve el **paso 5 de §17**, que es juicio humano (§27.12).")
    L.append("")
    L.append("> **Este fichero es trabajo humano en cuanto lo marcas.** Si lo dejaste en "
             "`generated/`, sácalo de ahí: `make clean-generated` lo borra.")
    L.append("")

    L.append("## Cómo se marca")
    L.append("")
    L.append("Cada línea que empieza por `- [ ] D-` es una decisión. Escribe dentro del corchete:")
    L.append("")
    L.append("| marca | significado |")
    L.append("|---|---|")
    L.append("| `s` o `x` | **sí** a la pregunta de esa sección |")
    L.append("| `n` | **no** |")
    L.append("| `?` | no lo sé con este material |")
    L.append("| vacío | sin revisar |")
    L.append("")
    L.append("`?` y vacío significan lo mismo para el corpus: **la etiqueta queda sin resolver "
             "y abre un `Issue`** (§4.7, F.3). No se pierde nada y no se inventa nada; se "
             "bloquean los registros afectados, no la sección entera.")
    L.append("")
    L.append("Puedes añadir una nota al final de la línea después de ` ;; `. Se guarda en el "
             "`Issue` o en el mapa.")
    L.append("")
    L.append("No cambies los identificadores `D-` ni el `review-token` de arriba: `apply` los "
             "usa para comprobar que esta revisión corresponde a este documento.")
    L.append("")

    L.append("## El tamaño del trabajo, antes de empezar")
    L.append("")
    L.append("| | |")
    L.append("|---|---:|")
    L.append(f"| afirmaciones en el documento | {len(datos['claims'])} |")
    L.append(f"| etiquetas distintas | {len(etiquetas)} |")
    L.append(f"| celdas descartadas por no nombrar nada | {len(excluidas)} |")
    L.append(f"| **decisiones que quedan para ti** | **{len(requeridas)}** |")
    L.append(f"| etiquetas sin ambigüedad: una entidad cada una | {len(unicas)} |")
    L.append(f"| fusiones propuestas automáticamente | {n_identicas - len(por_clase['identical_groups'])} |")
    L.append("")
    L.append("Reparto de las decisiones. Las secciones van de más riesgo a menos, que es el "
             "orden en que conviene gastar la atención:")
    L.append("")
    L.append("| sección | qué se decide | decisiones |")
    L.append("|---|---|---:|")
    L.append(f"| 1 · riesgo máximo | una etiqueta que quizá nombra dos cosas | {len(por_clase['homonym'])} |")
    L.append(f"| 2 | pares que difieren en un calificador de circunscripción | {len(por_clase['qualifier'])} |")
    L.append(f"| 3 | pares parecidos por otro motivo | {len(por_clase['neighbour'])} |")
    L.append(f"| 4 · riesgo mínimo | confirmación en bloque de {len(por_clase['identical_groups'])} grupos idénticos | "
             f"{1 if por_clase['identical_groups'] else 0} |")
    L.append("")
    if suprimidos.get("rango") or suprimidos.get("numeracion"):
        L.append("No se te preguntan estos pares, y conviene que sepas cuáles:")
        L.append("")
        if suprimidos.get("numeracion"):
            L.append(f"- **{suprimidos['numeracion']}** pares que sólo difieren en la "
                     "**numeración** — `Denisova 3` frente a `Denisova 4`. La cifra no es "
                     "ruido alrededor del nombre: es lo que distingue un ejemplar del "
                     "siguiente. Entran como entidades distintas.")
        if suprimidos.get("rango"):
            L.append(f"- **{suprimidos['rango']}** pares en que uno es el otro más un "
                     "**epíteto** — un género y una de sus especies. Un género no es su "
                     "especie. Entran como entidades distintas.")
        L.append("")
        L.append("En los dos casos el filtro se equivoca hacia el mismo lado: si acertara al "
                 "revés serían dos entidades donde había una, y eso se corrige fusionando "
                 "más tarde. Lo que no se corrige es fundir dos ejemplares.")
        L.append("")
    if hallazgos_parse:
        L.append(f"> El documento trae {hallazgos_parse} errores de conformidad de formato "
                 "(`parse_research.py`). No impiden resolver identidad, pero conviene "
                 "arreglarlos antes de generar el delta.")
        L.append("")
    L.append("---")
    L.append("")

    # --- 1. homónimos ------------------------------------------------------
    L.append("## 1 · Una etiqueta, ¿dos cosas? — riesgo máximo")
    L.append("")
    L.append("Aquí no hay nada que fusionar: la cadena ya es la misma. El error posible es el "
             "contrario, **no separar**. Un nombre usado con dos circunscripciones son dos "
             "conceptos taxonómicos (§7.3), y si entran como uno, todo lo que se cuelgue de "
             "él hereda la confusión.")
    L.append("")
    L.append("**`s`** = sí, esconde más de una entidad · **`n`** = no, es una sola.")
    L.append("")
    L.append("Un `s` **no resuelve** la etiqueta: dice que hace falta escindirla en conceptos "
             "con su fuente cada uno, y eso es una operación con datos que no cabe en una "
             "marca. Deja `Issue` con la escisión propuesta.")
    L.append("")
    if not por_clase["homonym"]:
        L.append("*Ninguna etiqueta da señales de homonimia.*")
        L.append("")
    for d in por_clase["homonym"]:
        L.append(f"- [ ] {d.id} · ¿homónimo? · «{d.etiquetas[0]}»")
        for m in d.motivos:
            L.append(f"      · {m}")
        L.extend(_contexto(d.etiquetas[0], etiquetas, por_id, limite))
        L.append("")

    # --- 2. calificadores --------------------------------------------------
    L.append("## 2 · Mismo núcleo, distinto calificador de circunscripción")
    L.append("")
    L.append("Estos pares **nunca** se proponen fusionados. `sensu stricto` frente a `sensu "
             "lato` no es una variante de grafía: es la diferencia de contenido que el nombre "
             "existe para marcar. Choanozoa *sensu stricto* y Choanozoa en su uso histórico "
             "son dos filas del apéndice B por exigencia del encargo, no una con nota.")
    L.append("")
    L.append("**`s`** = son la misma entidad · **`n`** = son distintas (lo normal aquí).")
    L.append("")
    if not por_clase["qualifier"]:
        L.append("*Ningún par difiere sólo en un calificador.*")
        L.append("")
    for d in por_clase["qualifier"]:
        L.append(f"- [ ] {d.id} · ¿misma entidad? · «{d.etiquetas[0]}» ↔ «{d.etiquetas[1]}»")
        for m in d.motivos:
            L.append(f"      · {m}")
        for t in d.etiquetas:
            L.extend(_contexto(t, etiquetas, por_id, limite))
        L.append("")

    # --- 3. vecinas --------------------------------------------------------
    L.append("## 3 · Parecidas por otro motivo")
    L.append("")
    L.append("Tampoco se proponen fusionadas. Un sinónimo declarado en el apéndice B es una "
             "afirmación de la investigación sobre nomenclatura, y sigue sin ser una "
             "identidad: dos nombres pueden ser sinónimos nomenclaturales y designar "
             "circunscripciones distintas según el autor.")
    L.append("")
    L.append("**`s`** = son la misma entidad · **`n`** = son distintas.")
    L.append("")
    L.append("Los pares se deciden **de dos en dos, sin cadena**: que A sea B y B sea C no lo "
             "decide la herramienta. Si tus respuestas lo implican, `apply` te lo dice.")
    L.append("")
    if not por_clase["neighbour"]:
        L.append("*Ningún par parecido.*")
        L.append("")
    for d in por_clase["neighbour"]:
        L.append(f"- [ ] {d.id} · ¿misma entidad? · «{d.etiquetas[0]}» ↔ «{d.etiquetas[1]}»")
        for m in d.motivos:
            L.append(f"      · {m}")
        for t in d.etiquetas:
            L.extend(_contexto(t, etiquetas, por_id, limite))
        L.append("")

    # --- 4. idénticas ------------------------------------------------------
    L.append("## 4 · Idénticas tras normalizar — confirmación en bloque")
    L.append("")
    L.append("Estas cadenas sólo difieren en espacios, mayúsculas, acentos o cursivas de "
             "Markdown. Es el único caso en que la herramienta propone fusión, y aun así "
             "hace falta que alguien lo confirme: si el bloque queda sin marcar, **todos** "
             "los grupos quedan sin resolver y abren `Issue`.")
    L.append("")
    if por_clase["identical_groups"]:
        bloque = next(d for d in decisiones if d.kind == "block_identical")
        L.append(f"- [ ] {bloque.id} · **confirmo los {len(por_clase['identical_groups'])} "
                 "grupos de abajo, salvo los que marque `n`**")
        L.append("")
        L.append("Las líneas de abajo se dejan como están para aceptar la propuesta. Si "
                 "alguna no cuadra —dos cosas distintas que se escriben igual—, márcala `n`. "
                 "Sin la confirmación de arriba **no se fusiona ninguna**, por mucho que se "
                 "queden sin marcar.")
        L.append("")
        for d in por_clase["identical_groups"]:
            variantes = " ↔ ".join(f"«{t}»" for t in d.etiquetas)
            L.append(f"- [ ] {d.id} · {variantes}")
        L.append("")
    else:
        L.append("*Ninguna etiqueta se repite con otra grafía.*")
        L.append("")

    # --- 5. sin ambigüedad -------------------------------------------------
    L.append("## 5 · Sin ambigüedad — no requieren decisión")
    L.append("")
    L.append(f"{len(unicas)} etiquetas no se parecen a ninguna otra ni dan señales de "
             "homonimia. Cada una entra como una entidad, que es la opción conservadora: "
             "crear de más se corrige fusionando después, y fusionar de menos no se corrige "
             "sin volver al documento.")
    L.append("")
    L.append("<details><summary>verlas</summary>")
    L.append("")
    for t in unicas:
        e = etiquetas[t]
        marca = f" · ya en el corpus como `{e.id_corpus}`" if e.id_corpus else ""
        n_ap = "1 aparición" if e.apariciones == 1 else f"{e.apariciones} apariciones"
        L.append(f"- «{t}» — {n_ap}{marca}")
    L.append("")
    L.append("</details>")
    L.append("")

    # --- 6. descartadas ----------------------------------------------------
    if excluidas:
        L.append("## 6 · Celdas descartadas")
        L.append("")
        L.append("No nombran nada: marcadores de hueco del propio encargo y claves locales "
                 "del documento. Se listan porque descartar en silencio es como inventar en "
                 "silencio, sólo que al revés.")
        L.append("")
        L.append("<details><summary>verlas</summary>")
        L.append("")
        for texto, motivo in sorted(excluidas):
            L.append(f"- `{texto}` — {motivo}")
        L.append("")
        L.append("</details>")
        L.append("")

    L.append("---")
    L.append("")
    L.append("Cuando termines:")
    L.append("")
    L.append("```bash")
    L.append(".venv/bin/python scripts/ingest/resolve_identity.py apply \\")
    L.append("    --review  RUTA/identity-review.md \\")
    L.append("    --map     RUTA/identity-map.json")
    L.append("```")
    L.append("")

    resumen = {
        "labels": len(etiquetas),
        "claims": len(datos["claims"]),
        "decisions_total": len(decisiones),
        "decisions_required": len(requeridas),
        "homonym": len(por_clase["homonym"]),
        "qualifier_pairs": len(por_clase["qualifier"]),
        "neighbour_pairs": len(por_clase["neighbour"]),
        "identical_groups": len(por_clase["identical_groups"]),
        "identical_labels": n_identicas,
        "unique": len(unicas),
        "excluded_cells": len(excluidas),
        "suppressed_numbering": suprimidos.get("numeracion", 0),
        "suppressed_rank": suprimidos.get("rango", 0),
        "review_token": token,
    }
    return "\n".join(L) + "\n", resumen


def mapa_propuesto(documento: Path, doc_hash: str, etiquetas: dict[str, Etiqueta],
                   decisiones: list[Decision], unicas: list[str], resumen: dict) -> dict:
    """Mapa etiqueta → identificador provisional.

    Provisional de verdad: `TMP-` no es ninguno de los prefijos de §16.3 y no
    puede acabar en `knowledge/records/` por accidente. Sólo las etiquetas que
    ya existen en el corpus llevan identificador real, porque ahí la identidad
    ya estaba decidida.
    """
    ids: dict[str, str] = {}
    n = 0
    entidades: dict[str, dict] = {}

    def asignar(textos: list[str], estado: str, decision: str | None) -> None:
        nonlocal n
        existente = next((etiquetas[t].id_corpus for t in textos if etiquetas[t].id_corpus), None)
        if existente:
            eid = existente
        else:
            n += 1
            eid = f"TMP-{n:06d}"
        entidades[eid] = {
            "labels": textos,
            "status": estado,
            "decision_id": decision,
            "in_corpus": bool(existente),
            "claims": sorted({c for t in textos
                              for c in etiquetas[t].sujeto_en + etiquetas[t].objeto_en}),
        }
        for t in textos:
            ids[t] = eid

    for t in unicas:
        asignar([t], "unique", None)

    for d in decisiones:
        if d.kind == "merge_group":
            asignar(d.etiquetas, "proposed_pending_confirmation", d.cubierta_por or d.id)

    # Todo lo demás queda sin resolver hasta que alguien decida: cada etiqueta,
    # por ahora, su propia entidad provisional y su decisión pendiente.
    for d in decisiones:
        if d.kind in ("merge_pair", "homonym"):
            for t in d.etiquetas:
                if t not in ids:
                    asignar([t], "pending_decision", d.id)
                else:
                    entidades[ids[t]].setdefault("also_in_decisions", []).append(d.id)

    return {
        "generated_at": date.today().isoformat(),
        "generated_by": "scripts/ingest/resolve_identity.py",
        "document": str(documento),
        "document_hash": doc_hash,
        "step": "§17 paso 5 · resolución de identidad",
        "id_note": "TMP-###### es provisional y de esta herramienta. Los identificadores "
                   "opacos de §16.3 los asigna el delta.",
        "summary": resumen,
        "decisions": [
            {"id": d.id, "kind": d.kind, "risk": d.riesgo, "required": d.requerida,
             "covered_by": d.cubierta_por, "proposal": d.propuesta,
             "labels": d.etiquetas, "reasons": d.motivos}
            for d in decisiones
        ],
        "labels": {t: {"provisional_id": ids.get(t), "key": e.clave,
                       "occurrences": e.apariciones,
                       "corpus_id": e.id_corpus}
                   for t, e in sorted(etiquetas.items())},
        "provisional_entities": entidades,
    }


# --------------------------------------------------------------------------
# Vuelta: leer la revisión marcada
# --------------------------------------------------------------------------

LINEA_DECISION = re.compile(r"^\s*[-*]\s*\[(.?)\]\s*(D-\d+)\b(.*)$")
MARCAS_SI = {"s", "x", "✓", "v"}
MARCAS_NO = {"n"}
MARCAS_DUDA = {"?"}


def leer_revision(path: Path) -> tuple[dict[str, tuple[str, str]], str | None, list[str]]:
    """Devuelve {D-xxxx: (marca, nota)}, el token y los avisos de lectura."""
    texto = path.read_text(encoding="utf-8")
    m = re.search(r"review-token:\s*([0-9a-f]{8,})", texto)
    token = m.group(1) if m else None
    marcas: dict[str, tuple[str, str]] = {}
    avisos: list[str] = []
    for n, linea in enumerate(texto.splitlines(), 1):
        mm = LINEA_DECISION.match(linea)
        if not mm:
            continue
        bruto, did, cola = mm.group(1).strip().lower(), mm.group(2), mm.group(3)
        nota = cola.split(";;", 1)[1].strip() if ";;" in cola else ""
        if not bruto:
            marca = "pending"
        elif bruto in MARCAS_SI:
            marca = "yes"
        elif bruto in MARCAS_NO:
            marca = "no"
        elif bruto in MARCAS_DUDA:
            marca = "unknown"
        else:
            avisos.append(f"línea {n}: marca «{bruto}» no reconocida en {did}; "
                          "se trata como sin revisar")
            marca = "pending"
        if did in marcas and marcas[did][0] != marca:
            avisos.append(f"línea {n}: {did} aparece dos veces con marcas distintas; "
                          "manda la última")
        marcas[did] = (marca, nota)
    return marcas, token, avisos


class Union:
    def __init__(self) -> None:
        self.padre: dict[str, str] = {}

    def buscar(self, x: str) -> str:
        self.padre.setdefault(x, x)
        while self.padre[x] != x:
            self.padre[x] = self.padre[self.padre[x]]
            x = self.padre[x]
        return x

    def unir(self, a: str, b: str) -> None:
        ra, rb = self.buscar(a), self.buscar(b)
        if ra != rb:
            self.padre[rb] = ra


def issue(clave_local: str, tipo: str, titulo: str, descripcion: str,
          severidad: str, etiquetas: list[str], filas: list[str],
          propuesta: str | None) -> dict:
    """Borrador de `Issue` (E.12).

    `id` va a `null` a propósito: §16.3 dice que los identificadores opacos los
    asigna el pipeline, y `affects.claim_ids` sólo admite `CLAIM-######`, que
    todavía no existe. Las claves locales del documento viajan en
    `evidence_locators`, que es texto libre y es donde se pueden comprobar.
    """
    return {
        "id": None,
        "local_key": clave_local,
        "issue_type": tipo,
        "title": titulo,
        "description": descripcion,
        "severity": severidad,
        "raised_in": None,
        "affects": {"record_ids": [], "claim_ids": [], "mention_ids": []},
        "evidence_locators": [f"etiqueta: {t}" for t in etiquetas]
                             + [f"fila: {f}" for f in filas],
        "proposed_resolution": propuesta,
        "blocks": "los registros que usan estas etiquetas; no la sección (F.3)",
        "related_issue_ids": [],
        "resolution": {"status": "open", "resolved_in": None, "decision_id": None},
        "record_status": "active",
    }


def aplicar(revision: Path, mapa_path: Path, salida: Path) -> int:
    mapa = json.loads(mapa_path.read_text(encoding="utf-8"))
    marcas, token, avisos = leer_revision(revision)

    esperado = mapa.get("summary", {}).get("review_token")
    if token is None:
        print("ERROR   la revisión no lleva `review-token`. ¿Se editó la cabecera?")
        return 1
    if esperado and token != esperado:
        print(f"ERROR   la revisión no corresponde a este mapa\n"
              f"        token en la revisión: {token}\n"
              f"        token del mapa:       {esperado}\n"
              "        Aplicar marcas de otro documento produciría fusiones que nadie "
              "autorizó. Vuelve a generar la propuesta.")
        return 1

    decisiones = {d["id"]: d for d in mapa["decisions"]}
    sobrantes = sorted(set(marcas) - set(decisiones))
    if sobrantes:
        avisos.append("la revisión marca decisiones que no están en el mapa: "
                      + ", ".join(sobrantes[:5]))

    bloque = next((d for d in mapa["decisions"] if d["kind"] == "block_identical"), None)
    bloque_ok = bloque is not None and marcas.get(bloque["id"], ("pending", ""))[0] == "yes"
    if bloque is not None and not bloque_ok and any(
            marcas.get(d["id"], ("pending", ""))[0] == "yes"
            for d in mapa["decisions"] if d["kind"] == "merge_group"):
        avisos.append(f"hay grupos idénticos marcados «s», pero la confirmación en bloque "
                      f"{bloque['id']} sigue vacía: sin ella no se fusiona ninguno")

    union = Union()
    uniones: list[tuple[str, str]] = []      # las aristas, por si hay que deshacerlas
    confirmados: list[dict] = []
    negados: list[tuple[str, str]] = []
    pendientes: list[dict] = []
    homonimos: list[dict] = []
    notas: dict[str, str] = {}

    for d in mapa["decisions"]:
        marca, nota = marcas.get(d["id"], ("pending", ""))
        if nota:
            notas[d["id"]] = nota

        if d["kind"] == "block_identical":
            continue

        if d["kind"] == "merge_group":
            # Propuesta automática: sólo vale si alguien confirmó el bloque. Un
            # `s` suelto en una línea de grupo no basta, porque esas líneas las
            # escribió la herramienta y no distinguiría su propia propuesta de
            # una confirmación humana.
            if marca == "no":
                negados.extend((d["labels"][i], d["labels"][j])
                               for i in range(len(d["labels"]))
                               for j in range(i + 1, len(d["labels"])))
            elif bloque_ok:
                for t in d["labels"][1:]:
                    union.unir(d["labels"][0], t)
                    uniones.append((d["labels"][0], t))
                confirmados.append(d)
            else:
                pendientes.append(d)
            continue

        if d["kind"] == "homonym":
            if marca == "no":
                confirmados.append(d)
            else:
                homonimos.append({**d, "mark": marca})
            continue

        # merge_pair
        if marca == "yes":
            union.unir(d["labels"][0], d["labels"][1])
            uniones.append((d["labels"][0], d["labels"][1]))
            confirmados.append(d)
        elif marca == "no":
            negados.append((d["labels"][0], d["labels"][1]))
        else:
            pendientes.append(d)

    # Contradicción: dos etiquetas separadas a mano que la cadena de otras
    # respuestas vuelve a juntar. No se resuelve sola y no la elige la
    # herramienta. Se deshace **el grupo entero** en el que aparece: dejar la
    # fusión en pie con una nota al lado sería registrar una identidad que
    # nadie autorizó, que es exactamente lo que §17 prohíbe.
    contradicciones = [(a, b) for a, b in negados if union.buscar(a) == union.buscar(b)]
    disueltas: set[str] = set()
    if contradicciones:
        tocados = {union.buscar(a) for a, _ in contradicciones}
        disueltas = {t for t in mapa["labels"] if union.buscar(t) in tocados}
        rehecho = Union()
        for a, b in uniones:
            if union.buscar(a) not in tocados:
                rehecho.unir(a, b)
        union = rehecho

    todas = list(mapa["labels"].keys())
    grupos: dict[str, list[str]] = {}
    for t in todas:
        grupos.setdefault(union.buscar(t), []).append(t)

    # Fusiones que nadie miró de frente: A=B y B=C preguntados, A=C no. Un grupo
    # idéntico sí se enseñó entero, así que todas sus parejas cuentan como vistas.
    pares_preguntados: set[tuple[str, str]] = set()
    for d in mapa["decisions"]:
        if d["kind"] not in ("merge_pair", "merge_group"):
            continue
        ls = sorted(d["labels"])
        pares_preguntados.update((ls[i], ls[j])
                                 for i in range(len(ls)) for j in range(i + 1, len(ls)))
    implicitas = []
    for miembros in grupos.values():
        if len(miembros) < 3:
            continue
        ms = sorted(miembros)
        for i in range(len(ms)):
            for j in range(i + 1, len(ms)):
                if (ms[i], ms[j]) not in pares_preguntados:
                    implicitas.append((ms[i], ms[j]))

    label_pendiente: dict[str, list[str]] = {}
    for d in pendientes + homonimos:
        for t in d["labels"]:
            label_pendiente.setdefault(t, []).append(d["id"])
    for t in disueltas:
        label_pendiente.setdefault(t, []).append("contradicción")

    # --- issues -----------------------------------------------------------
    issues: list[dict] = []
    origen = {t: info for t, info in mapa["labels"].items()}
    entidades_prev = mapa.get("provisional_entities", {})
    filas_de: dict[str, list[str]] = {}
    for info in entidades_prev.values():
        for t in info["labels"]:
            filas_de[t] = info.get("claims", [])

    for d in pendientes:
        n = len(issues) + 1
        etiquetas = d["labels"]
        filas = sorted({f for t in etiquetas for f in filas_de.get(t, [])})
        titulo = ("Identidad sin resolver entre "
                  + " y ".join(f"«{t}»" for t in etiquetas))
        cuerpo = ("El paso 5 de §17 no se decidió para este par. Motivos por los que se "
                  "presentó: " + "; ".join(d["reasons"]) + ". "
                  "No se fusiona: §17 prohíbe hacerlo por parecido nominal.")
        if notas.get(d["id"]):
            cuerpo += f" Nota del revisor: {notas[d['id']]}"
        issues.append(issue(f"IDENT-{n:04d}", "unresolved_identity", titulo, cuerpo,
                            "warning", etiquetas, filas,
                            "decidir en la revisión de identidad, o dejar dos entidades"))

    for d in homonimos:
        n = len(issues) + 1
        t = d["labels"][0]
        confirmado = d.get("mark") == "yes"
        titulo = (f"«{t}» nombra más de una cosa" if confirmado
                  else f"Posible homónimo conceptual: «{t}»")
        cuerpo = ("; ".join(d["reasons"]) + ". ")
        cuerpo += ("El revisor confirma que la etiqueta esconde más de una entidad: hay que "
                   "escindirla en conceptos taxonómicos con su fuente cada uno (§7.3), y eso "
                   "no cabe en una marca de revisión."
                   if confirmado else
                   "Sin decidir. Mientras tanto la etiqueta no se resuelve.")
        if notas.get(d["id"]):
            cuerpo += f" Nota del revisor: {notas[d['id']]}"
        issues.append(issue(f"IDENT-{n:04d}", "unresolved_identity", titulo, cuerpo,
                            "error" if confirmado else "warning",
                            [t], filas_de.get(t, []),
                            "crear un TaxonConcept por circunscripción, cada uno con su fuente"
                            if confirmado else "decidir si es una entidad o varias"))

    for a, b in contradicciones:
        n = len(issues) + 1
        issues.append(issue(
            f"IDENT-{n:04d}", "conflicting_claims",
            f"Respuestas incompatibles sobre «{a}» y «{b}»",
            "La revisión las separa explícitamente, pero la cadena de las demás respuestas "
            "las vuelve a unir. Una de las dos respuestas está mal y la herramienta no elige "
            "cuál: se deshacen todas las fusiones del grupo y sus etiquetas quedan sin "
            "resolver.",
            "error", [a, b],
            sorted(set(filas_de.get(a, []) + filas_de.get(b, []))),
            "revisar las decisiones que encadenan estas dos etiquetas"))

    # --- mapa definitivo ---------------------------------------------------
    entidades: dict[str, dict] = {}
    ids: dict[str, str] = {}
    n = 0
    for raiz, miembros in sorted(grupos.items()):
        miembros = sorted(miembros)
        existente = next((origen[t].get("corpus_id") for t in miembros
                          if origen[t].get("corpus_id")), None)
        if existente:
            eid = existente
        else:
            n += 1
            eid = f"TMP-{n:06d}"
        bloqueadas = sorted({d for t in miembros for d in label_pendiente.get(t, [])})
        entidades[eid] = {
            "labels": miembros,
            "status": "unresolved" if bloqueadas else "resolved",
            "blocked_by": bloqueadas,
            "in_corpus": bool(existente),
            "claims": sorted({f for t in miembros for f in filas_de.get(t, [])}),
        }
        for t in miembros:
            ids[t] = eid

    resueltas = sum(len(e["labels"]) for e in entidades.values() if e["status"] == "resolved")
    definitivo = {
        "generated_at": date.today().isoformat(),
        "generated_by": "scripts/ingest/resolve_identity.py apply",
        "document": mapa.get("document"),
        "document_hash": mapa.get("document_hash"),
        "review": str(revision),
        "review_token": token,
        "id_note": mapa.get("id_note"),
        "summary": {
            "labels": len(todas),
            "entities": len(entidades),
            "labels_resolved": resueltas,
            "labels_unresolved": len(todas) - resueltas,
            "decisions_total": len(mapa["decisions"]),
            "decisions_answered": sum(1 for d in mapa["decisions"]
                                      if d["required"] and marcas.get(d["id"], ("pending", ""))[0]
                                      in ("yes", "no")),
            "decisions_required": sum(1 for d in mapa["decisions"] if d["required"]),
            "decisions_pending": len(pendientes) + len(homonimos),
            "issues": len(issues),
            "contradictions": len(contradicciones),
            "implicit_merges": len(implicitas),
        },
        "labels": ids,
        "entities": entidades,
        "reviewer_notes": notas,
    }

    salida.mkdir(parents=True, exist_ok=True)
    (salida / "identity-map-final.json").write_text(
        json.dumps(definitivo, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (salida / "identity-issues.json").write_text(
        json.dumps({
            "note": "Borradores de Issue (E.12). `id` es null a propósito: lo asigna el "
                    "delta. Ninguna etiqueta sin resolver queda en silencio (§4.7, F.3).",
            "issues": issues,
        }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    s = definitivo["summary"]
    print(f"revisión  {revision}")
    print(f"  decisiones contestadas   {s['decisions_answered']} de {s['decisions_required']}")
    print(f"  etiquetas resueltas      {s['labels_resolved']} de {s['labels']}")
    print(f"  entidades provisionales  {s['entities']}")
    print(f"  issues abiertos          {s['issues']}")
    for a in avisos:
        print(f"AVISO   {a}")
    if implicitas:
        print(f"AVISO   {len(implicitas)} fusiones se siguen de tus respuestas sin que se te "
              "preguntaran una por una:")
        for a, b in implicitas[:5]:
            print(f"          «{a}» = «{b}»")
    for a, b in contradicciones:
        print(f"ERROR   «{a}» y «{b}» se marcaron distintas y las demás respuestas las unen")
    if disueltas:
        print(f"        se deshacen las fusiones de {len(disueltas)} etiquetas implicadas; "
              "revisa esas decisiones y vuelve a aplicar")
    print(f"\n  mapa    {salida / 'identity-map-final.json'}")
    print(f"  issues  {salida / 'identity-issues.json'}")
    n_sin = s["labels_unresolved"]
    if n_sin:
        print(f"\n  Queda{'' if n_sin == 1 else 'n'} {n_sin} "
              f"etiqueta{'' if n_sin == 1 else 's'} sin resolver. §28.1 no da la sección por "
              "terminada mientras la cobertura no sea completa; eso es correcto.")
    return 1 if contradicciones else 0


# --------------------------------------------------------------------------
# Propuesta
# --------------------------------------------------------------------------

def proponer(documento: Path, salida: Path, corpus: Path | None, tope_edicion: int,
             raiz: int, limite: int) -> int:
    bruto = documento.read_bytes()
    doc_hash = sha256(bruto)
    datos, h = parse(documento)

    etiquetas, excluidas = inventario(datos, corpus)
    decisiones, unicas, suprimidos = construir_decisiones(etiquetas, tope_edicion, raiz)
    texto, resumen = informe(documento, doc_hash, datos, etiquetas, decisiones,
                             unicas, excluidas, limite, len(h.errores), suprimidos)
    mapa = mapa_propuesto(documento, doc_hash, etiquetas, decisiones, unicas, resumen)

    salida.mkdir(parents=True, exist_ok=True)
    (salida / "identity-review.md").write_text(texto, encoding="utf-8")
    (salida / "identity-map.json").write_text(
        json.dumps(mapa, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"{documento.name}")
    print(f"  afirmaciones            {resumen['claims']}")
    print(f"  etiquetas distintas     {resumen['labels']}")
    print(f"  celdas descartadas      {resumen['excluded_cells']}")
    print()
    print(f"  DECISIONES HUMANAS      {resumen['decisions_required']}")
    print(f"    homónimos posibles      {resumen['homonym']}")
    print(f"    pares con calificador   {resumen['qualifier_pairs']}")
    print(f"    pares parecidos         {resumen['neighbour_pairs']}")
    print(f"    confirmación en bloque  {1 if resumen['identical_groups'] else 0}"
          f"  ({resumen['identical_groups']} grupos, "
          f"{resumen['identical_labels']} etiquetas)")
    print()
    print(f"  sin ambigüedad          {resumen['unique']}  "
          f"({resumen['unique'] * 100 // max(resumen['labels'], 1)} % del total)")
    if resumen["suppressed_numbering"] or resumen["suppressed_rank"]:
        print(f"  no se preguntan         {resumen['suppressed_numbering']} pares que sólo "
              f"difieren en la numeración, {resumen['suppressed_rank']} de género/especie")
    if h.errores:
        print(f"\n  AVISO  el documento trae {len(h.errores)} errores de conformidad "
              "(`parse_research.py`); no impiden resolver identidad")
    print()
    print(f"  revisión  {salida / 'identity-review.md'}")
    print(f"  mapa      {salida / 'identity-map.json'}")
    print()
    print("  Nada se ha fusionado. Marca la revisión y después:")
    print(f"    resolve_identity.py apply --review {salida / 'identity-review.md'} "
          f"--map {salida / 'identity-map.json'}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Resolución de identidad asistida (§17 paso 5)")
    sub = ap.add_subparsers(dest="command", required=True)

    p = sub.add_parser("propose", help="agrupar por riesgo y emitir la revisión")
    p.add_argument("document")
    p.add_argument("--out", default=None, metavar="DIR",
                   help="por defecto generated/identity/<documento>/")
    p.add_argument("--corpus", default=None, metavar="DIR",
                   help="cotejar contra entidades ya ingeridas (knowledge/records)")
    p.add_argument("--edit-threshold", type=int, default=1, metavar="N",
                   help="distancia de edición máxima para presentar un par (por defecto 1; "
                        "2 triplica los pares y casi todo lo que añade son taxones distintos)")
    p.add_argument("--root-prefix", type=int, default=0, metavar="N",
                   help="pasada extra: pares que comparten N caracteres iniciales. "
                        "Desactivada por defecto, ver la cabecera del script")
    p.add_argument("--context", type=int, default=4, metavar="N",
                   help="filas del registro que se muestran por etiqueta")

    a = sub.add_parser("apply", help="leer la revisión marcada y fijar el mapa")
    a.add_argument("--review", required=True)
    a.add_argument("--map", required=True, dest="mapa")
    a.add_argument("--out", default=None, metavar="DIR",
                   help="por defecto, junto a la revisión")

    args = ap.parse_args()

    if args.command == "propose":
        doc = Path(args.document)
        if not doc.exists():
            print(f"ERROR no existe: {doc}")
            return 1
        salida = Path(args.out) if args.out else ROOT / "generated" / "identity" / doc.stem
        corpus = Path(args.corpus) if args.corpus else None
        if corpus is not None and not corpus.is_dir():
            print(f"ERROR no es un directorio: {corpus}")
            return 1
        return proponer(doc, salida, corpus, args.edit_threshold,
                        args.root_prefix, args.context)

    revision, mapa = Path(args.review), Path(args.mapa)
    for p_ in (revision, mapa):
        if not p_.exists():
            print(f"ERROR no existe: {p_}")
            return 1
    salida = Path(args.out) if args.out else revision.parent
    return aplicar(revision, mapa, salida)


if __name__ == "__main__":
    sys.exit(main())
