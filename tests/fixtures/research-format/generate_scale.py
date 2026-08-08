#!/usr/bin/env python3
"""Generador determinista de un documento de investigación sintético **a escala real**.

Por qué existe
--------------
`SEC-SAMPLE.md` prueba que el formato se reconoce; con seis filas no prueba nada
sobre el coste. La investigación de la Campaña 1 llega con del orden de 8.330
líneas, 1.593 afirmaciones y 425 fuentes, y conviene saber **antes** de que llegue
si `scripts/ingest/parse_research.py` la lee en un segundo o en un minuto, cuánta
memoria pide y qué comprobación se degrada a esa escala. Este script fabrica un
documento del mismo formato y de las mismas dimensiones para poder medirlo.

Qué NO es
---------
**Corpus.** Ni una etiqueta, ni una cifra, ni una fuente de las que salen de aquí
corresponde a nada real: todas las etiquetas llevan el prefijo `FIX-`, los DOI
apuntan a `10.0000/` y los repositorios a dominios `.invalid`, que por RFC 2606
no resuelven. §5.1 prohíbe inventar contenido científico; la salida de este
generador no es contenido científico ni puede confundirse con él, y por eso no
vive en `knowledge/` sino en `generated/`, que está en `.gitignore`.

Determinismo
------------
Misma semilla y mismos parámetros ⇒ mismo fichero byte a byte. Para conseguirlo:

- el generador aleatorio es **propio** (splitmix64, unas líneas más abajo).
  `random` no garantiza la misma secuencia entre versiones de Python, y aquí
  «determinista» significa que dos ejecuciones se pueden comparar con `diff`;
- no se lee el reloj: la fecha de corte y la de consulta son parámetros;
- los repartos se calculan con aritmética entera y desempate por nombre, no con
  coma flotante ni con orden de conjunto;
- se itera siempre sobre listas, nunca sobre `set`.

Los casos difíciles que trae a propósito
----------------------------------------
El documento real no será una repetición de filas iguales, así que éste tampoco:

1. **Etiquetas casi idénticas que no son la misma entidad** — `FIX-Alfa-0001`
   frente a `FIX-Alfa-0001 sensu stricto`, dos filas del apéndice B y una fila
   del registro con predicado `no_sinonimo_de*` que lo dice expresamente. Es la
   trampa del paso 5 de §17: la resolución de identidad por parecido nominal.
2. **Homónimo conceptual** — la misma etiqueta preferida en dos filas de B, con
   dos circunscripciones y dos fuentes distintas. Un nombre, dos contenidos.
3. **Filas de síntesis que citan otras filas** — `sintesis(C-0012, C-0031)`, y
   **siempre hacia atrás**: ninguna síntesis depende de una fila posterior.
4. **Afirmaciones negativas conviviendo con la positiva** — `carece_de_rasgo*`
   sobre el mismo sujeto y objeto que una fila `posee_rasgo` anterior, sin que
   ninguna de las dos borre a la otra (§9.2).
5. **Fuentes de calidad desigual** — preprints sin revisar, síntesis secundarias,
   trabajos corregidos, y fuentes sin DOI: unas con URL resoluble y otras con el
   literal `DOI no verificado` que pide el prompt.

Uso
---
    .venv/bin/python tests/fixtures/research-format/generate_scale.py
    .venv/bin/python tests/fixtures/research-format/generate_scale.py --afirmaciones 200 --lineas 1200
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]

# --- dimensiones declaradas por la investigación real ------------------------
# Son los valores por defecto. Crecen: si el documento llega más grande, se
# cambian aquí o por línea de comandos y se vuelve a medir.
DIM_LINEAS = 8330
DIM_AFIRMACIONES = 1593
DIM_FUENTES = 425
DIM_ENTIDADES = 1335
DIM_EVENTOS = 99
DIM_HIPOTESIS = 77
DIM_FECHAS = 249
DIM_MAGNITUDES = 384
DIM_BUSQUEDAS = 76


# ============================================================================
# Aleatoriedad reproducible
# ============================================================================

class Aleatorio:
    """splitmix64. Corto, sin estado global y con la misma salida en cualquier
    versión de Python, que es justo lo que `random` no promete."""

    MASCARA = (1 << 64) - 1

    def __init__(self, semilla: int) -> None:
        self.estado = (semilla ^ 0x9E3779B97F4A7C15) & self.MASCARA

    def siguiente(self) -> int:
        self.estado = (self.estado + 0x9E3779B97F4A7C15) & self.MASCARA
        z = self.estado
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & self.MASCARA
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & self.MASCARA
        return (z ^ (z >> 31)) & self.MASCARA

    def entero(self, n: int) -> int:
        """Entero en [0, n). El sesgo del módulo es despreciable con n pequeño
        frente a 2**64 y, sobre todo, es siempre el mismo."""
        return self.siguiente() % n if n > 0 else 0

    def rango(self, a: int, b: int) -> int:
        """Entero en [a, b], ambos incluidos."""
        return a + self.entero(b - a + 1)

    def elige(self, secuencia: list):
        return secuencia[self.entero(len(secuencia))]


# ============================================================================
# Utilidades de tabla y reparto
# ============================================================================

def celda(valor) -> str:
    """Una celda no puede contener ni tubería ni salto de línea: una sola de
    cualquiera de las dos rompe la tabla y el parser la lee desalineada."""
    return str(valor).replace("|", "/").replace("\n", " ").strip()


def fila(celdas: list) -> str:
    return "| " + " | ".join(celda(c) for c in celdas) + " |"


def tabla(cabecera: list[str], filas: list[list]) -> list[str]:
    lineas = [fila(cabecera), "|" + "---|" * len(cabecera)]
    lineas.extend(fila(f) for f in filas)
    return lineas


def reparto_por_pesos(total: int, pesos: list[tuple[str, int]]) -> dict[str, int]:
    """Reparto de mayor resto en aritmética entera, con desempate por nombre.

    En coma flotante el desempate dependería de la plataforma; aquí no depende
    de nada."""
    suma = sum(p for _, p in pesos)
    cuentas: dict[str, int] = {}
    asignado = 0
    restos: list[tuple[int, str]] = []
    for nombre, peso in pesos:
        num = total * peso
        base = num // suma
        cuentas[nombre] = base
        asignado += base
        restos.append((num % suma, nombre))
    restos.sort(key=lambda t: (-t[0], t[1]))
    for i in range(total - asignado):
        cuentas[restos[i % len(restos)][1]] += 1
    return cuentas


def intercalar(cuentas: dict[str, int]) -> list[str]:
    """Reparte las etiquetas por todo el recorrido en vez de agruparlas.

    Importa para el realismo: un documento real no tiene las 90 síntesis
    seguidas al final. Y importa para la corrección, porque una síntesis sólo
    puede citar filas anteriores y agruparlas al principio lo impediría."""
    total = sum(cuentas.values())
    nombres = list(cuentas)
    hecho = {n: 0 for n in nombres}
    salida: list[str] = []
    for i in range(1, total + 1):
        mejor, mejor_clave = None, None
        for n in nombres:
            # deuda = cuánto le falta a esta etiqueta respecto de su cuota en i
            deuda = cuentas[n] * i - hecho[n] * total
            clave = (-deuda, n)
            if mejor_clave is None or clave < mejor_clave:
                mejor_clave, mejor = clave, n
        salida.append(mejor)
        hecho[mejor] += 1
    return salida


def decimal(entero_en_decimas: int) -> str:
    """1234 → «123,4». En español la coma decimal, y sin coma flotante."""
    return f"{entero_en_decimas // 10},{entero_en_decimas % 10}"


# ============================================================================
# Vocabularios sintéticos
# ============================================================================

GRIEGAS = ["Alfa", "Beta", "Gamma", "Delta", "Épsilon", "Zeta", "Eta", "Theta",
           "Iota", "Kappa", "Lambda", "My", "Ny", "Xi", "Ómicron", "Pi", "Rho",
           "Sigma", "Tau", "Ípsilon", "Fi", "Ji", "Psi", "Omega"]

APELLIDOS = ["Sintética", "Molde", "Prueba", "Ficticia", "Maqueta", "Patrón",
             "Esquema", "Plantilla", "Simulacro", "Andamio", "Boceto", "Réplica",
             "Calco", "Vaciado", "Troquel", "Bosquejo"]

INICIALES = list("ABCDEFGHIJKLMNPRSTVZ")

TIPOS_FUENTE = ["investigación primaria", "revisión", "base de datos taxonómica",
                "preprint", "capítulo o libro", "tesis", "divulgación o blog", "otro"]

NOTAS_CALIDAD = [
    "n/a",
    "síntesis secundaria sin datos propios",
    "única fuente que sostiene una afirmación de este documento",
    "trabajo corregido por sus autores (corrigendum)",
    "sin DOI: se cita por URL resoluble",
    "acceso sólo al resumen",
    "recurso no revisado por pares",
]

ACEPTACION = ["consenso amplio", "aceptación mayoritaria", "aceptación mixta",
              "posición minoritaria", "no evaluado"]
FUERZA = ["alta", "media", "baja", "desconocida"]
RESOLUCION = ["resuelta", "parcialmente resuelta", "sin resolver",
              "información insuficiente"]
VIGENCIA = ["vigente", "histórica", "superada", "rechazada"]

MOTIVOS = [
    "replicado en tres análisis sintéticos independientes",
    "un solo conjunto de datos, sin réplica",
    "inferido de un único carácter",
    "topología sensible al modelo de heterogeneidad composicional",
    "medido en un organismo sintético y extrapolado",
    "el soporte cae al eliminar los sitios más rápidos",
    "coincide en concatenación y en coalescencia de árboles génicos",
    "la fuente lo presenta como compatible, no como demostrado",
    "depende de una calibración única",
    "muestreo taxonómico escaso en la rama larga",
    "no se ha puesto a prueba desde su publicación",
    "reconstrucción de estado ancestral con un solo método",
]

LOCALIZADORES = ["§{a}.{b}", "fig. {n}", "tabla {n}", "supl. fig. S{n}", "p. {n}",
                 "§{a}.{b}.{c}", "sin localizar"]

TIPOS_EVENTO = ["endosimbiosis", "transferencia horizontal",
                "transferencia génica endosimbiótica", "divergencia", "radiación",
                "extinción", "adquisición de rasgo", "pérdida de rasgo",
                "reducción genómica", "depredación", "competencia",
                "relación huésped-patógeno", "asociación no heredable"]

PAPELES = ["hospedador", "endosimbionte", "simbionte extracelular", "donante",
           "receptor", "población parental", "linaje resultante", "depredador",
           "presa", "huésped", "parásito", "competidor"]

DESENLACES = ["transitoria", "dependencia", "integración heredable", "degradación",
              "pérdida", "no determinado"]

TIPOS_FECHA = ["edad de ocurrencia", "rango observado", "rango inferido de linaje",
               "estimación de divergencia", "intervalo de evento",
               "evidencia de rasgo", "publicación"]

METODOS_FECHA = [
    "reloj relajado log-normal con dos calibraciones sintéticas",
    "reloj estricto, calibración mínima única",
    "reloj autocorrelado, datación de evidencia total",
    "datación radiométrica sintética sobre el nivel FIX",
    "acotación estratigráfica entre dos niveles FIX",
    "datación por nodos con prior uniforme",
]

UNIDADES_MAGNITUD = ["µm", "pg", "kbp", "Mbp", "células · mL⁻¹", "pmol · h⁻¹",
                     "% atm actual", "µmol · L⁻¹", "°C", "generaciones",
                     "mutaciones · sitio⁻¹ · generación⁻¹", "kJ · mol⁻¹"]

PROXIES = ["microscopía sintética", "recuento sobre cultivo FIX",
           "proxy geoquímico sintético", "ensayo de aclaramiento FIX",
           "modelo de balance de masas sintético", "secuenciación de cobertura FIX",
           "calorimetría sintética"]

TIPOS_ENTIDAD = {
    "clado": "clado sin rango",
    "nombre": "nombre taxonómico",
    "concepto": "concepto taxonómico",
    "linaje": "linaje",
    "poblacion": "población reconstruida",
    "rasgo": "rasgo",
    "gen": "gen",
    "organulo": "orgánulo",
    "metodo": "método",
    "ambiental": "magnitud ambiental",
    "termino": "término histórico",
    "fosil": "nombre taxonómico",
}

MARCAS_CLADO = ["n/a", "⚠", "[F]", "[H]", "⚠ [F]", "n/a", "[F]"]

# Secciones del documento. El peso decide cuántas filas del registro caen en cada
# una: §18 del prompt exige que las secciones 5–13 (ecología, mecanismos y
# magnitudes) pesen al menos tanto como la eucariogénesis y la nomenclatura.
SECCIONES = [
    (1, "Alcance sintético del corredor", 3),
    (2, "El punto de partida sintético", 6),
    (3, "Eucariogénesis sintética", 8),
    (4, "Raíz y forma del grupo sintético", 6),
    (5, "Registro material sintético", 9),
    (6, "Tiempo: relojes sintéticos y su desacuerdo", 7),
    (7, "Ambiente sintético", 8),
    (8, "Ecología y trofismo sintéticos", 10),
    (9, "Asociación: catálogo sintético de desenlaces", 10),
    (10, "Rasgos con costo", 7),
    (11, "Sexo, meiosis y ciclo vital sintéticos", 6),
    (12, "Multicelularidad sintética", 7),
    (13, "Escalas, tasas y recuentos sintéticos", 6),
    (14, "Nombres y nomenclatura sintéticos", 9),
    (15, "Lo que no se sabe, y cómo lo sabemos", 6),
    (16, "Material sintético sin encaje", 2),
]

SUBSECCIONES = [
    "Lo que se observa",
    "Lo que se infiere y con qué método",
    "Dónde discrepan las fuentes",
    "Qué quedaría por comprobar",
]

# Plantillas de prosa. Todas llevan localizador de fuente porque la regla de
# densidad del prompt lo exige en cualquier oración con cifra, fecha, relación de
# parentesco o atribución: el recuento de control declara cero `[SIN FUENTE]`.
PROSA = [
    "El nodo {A} se recupera con {n} genes y {m} posiciones bajo un modelo sitio-heterogéneo, y el soporte transcrito es {sop} ([{f}]).",
    "La posición de {A} cambia al recodificar los aminoácidos con el esquema sintético SR4: el soporte baja de {n} a {m} ([{f}]).",
    "{A} y {B} aparecen como grupos hermanos en concatenación y no en coalescencia de árboles génicos, y los autores lo atribuyen al muestreo ([{f}]).",
    "La atribución de {A} descansa en un solo carácter, y la propia fuente la presenta como compatible con la hipótesis, no como demostrada ([{f}]).",
    "El intervalo publicado para {A} es de {n} a {m} Ma, con la incertidumbre tal como la da la fuente y sin conversión de unidad ([{f}]).",
    "No hay valor publicado para el coste de {A}: la celda correspondiente del apéndice F lleva el marcador y no una estimación ([{f}]).",
    "{A} conserva {n} genes en el orgánulo sintético frente a los {m} de sus parientes de vida libre, según el recuento de la fuente ([{f}]).",
    "La marca interpretada como depredación sobre {A} mide {dec} µm, y la fuente discute dos alternativas: alteración posterior y artefacto de preparación ([{f}]).",
    "La asociación entre {A} y {B} se describe con transmisión mixta, y la fuente no ordena los dos episodios entre sí ([{f}]).",
    "El repertorio de {A} incluye {n} familias del conjunto sintético, y faltan {m} de las que sí están en {B} ([{f}]).",
    "La hipótesis {H} predice un orden de adquisición distinto del de su rival, y la observación que las separaría está descrita en el apéndice E ([{f}]).",
    "{A} vive en el ambiente sintético FIX-{amb} y la reconstrucción del ambiente ancestral del nodo es explícitamente provisional ([{f}]).",
    "La fila {C} registra la relación en su forma expresa; esta frase sólo la comenta y no añade evidencia ([{f}]).",
    "Dos trabajos dan valores incompatibles para la misma magnitud de {A}, {n} y {m} en la misma unidad original, y aquí se conservan los dos sin promediar ([{f}]).",
    "La circunscripción de {A} varía según el autor, de modo que el apéndice B trae una fila por circunscripción y no una fila con nota ([{f}]).",
    "El término histórico asociado a {A} sigue apareciendo en la literatura antigua, y por eso se conserva etiquetado como histórico en lugar de borrarse ([{f}]).",
    "La respuesta descrita en {A} es reversible al retirar la señal y se manifiesta en {n} horas, de modo que no exige cambio genético fijado ([{f}]).",
    "El recuento de orígenes independientes para el proceso sintético asociado a {A} va de {n} a {m} según quién lo haga y con qué criterio ([{f}]).",
    "Ninguna fuente recuperada en esta sesión da densidades celulares para el intervalo de {A}; el hueco queda etiquetado en la sección 15 ([{f}]).",
    "El soporte de {A} es {sop} en el análisis principal y no se recupera al eliminar el taxón de rama larga {B} ([{f}]).",
]

# Los rasgos del apéndice de costes. Varias filas llevan a propósito el marcador
# literal que el prompt exige cuando no hay cifra publicada: el documento real
# traerá muchas, y eso es un resultado correcto y no un fallo.
RASGOS_COSTE = [
    ("compartimento sintético FIX-C1", "aislamiento de dos procesos", "membrana interna", True),
    ("sistema de membranas FIX-C2", "tráfico dirigido", "compartimento FIX-C1", False),
    ("citoesqueleto FIX-C3", "cambio de forma controlado", "n/a", True),
    ("ingestión de partículas FIX-C4", "acceso a presa mayor", "citoesqueleto FIX-C3", True),
    ("orgánulo oxidativo FIX-C5", "rendimiento energético mayor", "asociación estable", True),
    ("apéndice móvil FIX-C6", "desplazamiento dirigido", "citoesqueleto FIX-C3", False),
    ("adhesión FIX-C7", "permanencia en agregado", "n/a", False),
    ("señalización FIX-C8", "respuesta a señal externa", "adhesión FIX-C7", True),
    ("división cerrada FIX-C9", "reparto de copias", "citoesqueleto FIX-C3", False),
    ("división abierta FIX-C10", "reparto de copias", "citoesqueleto FIX-C3", False),
    ("peroxisoma sintético FIX-C11", "manejo de especies reactivas", "orgánulo FIX-C5", False),
    ("ciclo sexual FIX-C12", "recombinación", "división FIX-C9", True),
    ("pared FIX-C13", "resistencia mecánica", "n/a", False),
    ("latencia FIX-C14", "persistencia sin recurso", "pared FIX-C13", True),
]

TIPOLOGIA_ASOCIACION = [
    "contacto sin consecuencia",
    "depredación o consumo",
    "parasitismo",
    "asociación transitoria facultativa",
    "asociación estable no heredable",
    "endosimbiosis con transmisión vertical",
    "dependencia mutua obligada",
    "integración con transferencia de genes al genoma del hospedador",
    "reducción extrema u orgánulo derivado",
    "degradación o pérdida de la asociación",
    "ruptura con recuperación de vida libre",
]

ETIQUETAS_HUECO = ["LA LITERATURA DECLARA QUE NO SE SABE",
                   "NO LOCALIZADO EN ESTA SESIÓN",
                   "NO BUSCADO"]

# Reparto de arquetipos de fila. Los «creadores» introducen una entidad nueva;
# los «no creadores» hablan de lo ya introducido o del propio registro.
PESOS_CREADORES = [
    ("pertenencia", 37), ("rasgo", 21), ("termino", 9), ("hermandad", 10),
    ("nombre", 6), ("linaje", 5), ("poblacion", 3), ("fosil", 3),
    ("metodo", 2), ("ambiental", 2),
]
PESOS_NO_CREADORES = [
    ("sintesis", 35), ("cuestionamiento", 17), ("negativa", 16), ("edad", 12),
    ("valor", 10), ("evento", 5), ("hipotesis", 3), ("historico", 2),
]

# Las primeras filas tienen que introducir clados sin depender de nada anterior:
# una síntesis en la fila 2 no tendría qué citar.
ARRANQUE = 12


# ============================================================================
# Generación de datos
# ============================================================================

class Config:
    def __init__(self, args: argparse.Namespace) -> None:
        self.salida = Path(args.salida)
        self.semilla = args.semilla
        self.lineas = args.lineas
        self.afirmaciones = args.afirmaciones
        self.fuentes = args.fuentes
        self.entidades = args.entidades
        self.eventos = args.eventos
        self.hipotesis = args.hipotesis
        self.fechas = args.fechas
        self.magnitudes = args.magnitudes
        self.busquedas = args.busquedas_negativas
        self.gemelos = args.gemelos
        self.homonimos = args.homonimos
        self.corte = args.corte
        self.ancho_c = max(3, len(str(self.afirmaciones)))
        self.ancho_s = max(2, len(str(self.fuentes)))
        self.ancho_e = max(2, len(str(self.eventos)))
        self.ancho_h = max(2, len(str(self.hipotesis)))

    def c(self, n: int) -> str:
        return f"C-{n:0{self.ancho_c}d}"

    def s(self, n: int) -> str:
        return f"S{n:0{self.ancho_s}d}"

    def e(self, n: int) -> str:
        return f"E{n:0{self.ancho_e}d}"

    def h(self, n: int) -> str:
        return f"H{n:0{self.ancho_h}d}"


def generar_fuentes(cfg: Config, rnd: Aleatorio) -> list[dict]:
    """Apéndice A. Calidad desigual a propósito, y tres formas de referencia:
    DOI resoluble, URL resoluble sin DOI, y el literal `DOI no verificado`."""
    fuentes = []
    for i in range(1, cfg.fuentes + 1):
        n_autores = rnd.rango(1, 3)
        autores = "; ".join(
            f"{rnd.elige(APELLIDOS)}, {rnd.elige(INICIALES)}." for _ in range(n_autores))
        tipo = TIPOS_FUENTE[(i * 3) % len(TIPOS_FUENTE)]
        familia = GRIEGAS[i % len(GRIEGAS)]
        forma = i % 7
        if forma == 3:
            # sin DOI, pero con URL que sí se recuperó
            doi = f"https://repositorio.invalid/fix/{i:04d}"
            nota = "sin DOI: se cita por URL resoluble"
        elif forma == 5:
            # el caso que el prompt pide escribir literalmente
            doi = f"DOI no verificado — https://repositorio.invalid/fix/{i:04d}"
            nota = "sin DOI verificado en esta sesión"
        else:
            doi = f"https://doi.org/10.0000/fix.{i:04d}"
            nota = NOTAS_CALIDAD[(i * 5) % len(NOTAS_CALIDAD)]
        if tipo == "preprint":
            nota = "preprint sin revisión por pares"
        fuentes.append({
            "clave": cfg.s(i),
            "autores": autores,
            "año": str(2004 + (i * 7) % 22),
            "título": f"Estudio sintético {i:04d} sobre la familia FIX-{familia}",
            "publicación": f"Repositorio Ficticio {1 + i % 19}",
            "doi": doi,
            "tipo": tipo,
            "notas": nota,
            "consulta": cfg.corte,
        })
    return fuentes


def localizador(rnd: Aleatorio) -> str:
    plantilla = rnd.elige(LOCALIZADORES)
    return plantilla.format(a=rnd.rango(1, 18), b=rnd.rango(1, 9),
                            c=rnd.rango(1, 6), n=rnd.rango(1, 40))


def generar_registro(cfg: Config, rnd: Aleatorio,
                     fuentes: list[dict]) -> tuple[list[dict], list[dict]]:
    """Recorre las filas del registro y va creando entidades por el camino.

    El orden importa: una entidad existe porque una fila la introduce, y sólo
    después puede ser objeto de otra fila. Así el apéndice B puede declarar en
    qué fila aparece cada entidad por primera vez sin inventárselo."""
    n = cfg.afirmaciones
    e_total = cfg.entidades
    if e_total > n:
        raise SystemExit("cada fila introduce como mucho una entidad: "
                         f"--entidades ({e_total}) no puede superar "
                         f"--afirmaciones ({n})")

    creadores = max(0, e_total - cfg.gemelos - cfg.homonimos)
    no_creadores = n - e_total
    cuentas = reparto_por_pesos(creadores, PESOS_CREADORES)
    cuentas.update({"distincion": cfg.gemelos, "circunscripcion": cfg.homonimos})
    cuentas.update(reparto_por_pesos(no_creadores, PESOS_NO_CREADORES))
    if cuentas.get("pertenencia", 0) < ARRANQUE:
        # Quien manda aquí NO es --afirmaciones: las filas de arranque salen del
        # reparto de las entidades creadoras, así que subir --afirmaciones no
        # mueve esta cuenta ni un poco. Decirlo, porque el consejo equivocado
        # cuesta varios intentos.
        raise SystemExit(
            f"sólo salen {cuentas.get('pertenencia', 0)} filas de arranque y hacen "
            f"falta {ARRANQUE}: las primeras filas tienen que introducir clados sin "
            f"depender de nada anterior.\n"
            f"  Lo decide --entidades ({e_total}) menos --gemelos ({cfg.gemelos}) y "
            f"--homonimos ({cfg.homonimos}), no --afirmaciones ({n}).\n"
            f"  Sube --entidades, o baja --gemelos y --homonimos.")
    cuentas["pertenencia"] -= ARRANQUE
    etiquetas = ["pertenencia"] * ARRANQUE + intercalar(cuentas)

    afirmaciones: list[dict] = []
    entidades: list[dict] = []
    por_tipo: dict[str, list[str]] = {k: [] for k in TIPOS_ENTIDAD}
    positivas_rasgo: list[dict] = []      # filas `posee_rasgo`, para negarlas luego
    contador_entidad = 0

    def nueva(clase: str, fila_id: str, base: str = "", sinonimos: str = "",
              marcas: str = "") -> str:
        nonlocal contador_entidad
        contador_entidad += 1
        i = contador_entidad
        if clase == "gemelo":
            etiqueta = f"{base} sensu stricto"
            tipo, marca = "concepto taxonómico", "≈ ⚠"
        elif clase == "homonimo":
            etiqueta = base
            tipo, marca = "concepto taxonómico", "≈ ⚠"
        elif clase == "clado":
            etiqueta = f"FIX-{GRIEGAS[i % len(GRIEGAS)]}-{i:04d}"
            tipo, marca = TIPOS_ENTIDAD[clase], MARCAS_CLADO[i % len(MARCAS_CLADO)]
        elif clase == "nombre":
            etiqueta = f"FIX-{GRIEGAS[i % len(GRIEGAS)]}ella-{i:04d}"
            tipo, marca = TIPOS_ENTIDAD[clase], "≈"
        elif clase == "fosil":
            etiqueta = f"FIX-fosil-{i:04d}"
            tipo, marca = TIPOS_ENTIDAD[clase], "†"
        else:
            etiqueta = f"FIX-{clase}-{i:04d}"
            tipo, marca = TIPOS_ENTIDAD[clase], "n/a"
        entidades.append({
            "etiqueta": etiqueta,
            "tipo": tipo,
            "sinonimos": sinonimos or "n/a",
            "marcas": marcas or marca,
            "fila": fila_id,
        })
        clave_pool = "clado" if clase in ("gemelo", "homonimo") else clase
        por_tipo.setdefault(clave_pool, []).append(etiqueta)
        return etiqueta

    def existente(clase: str) -> str:
        pool = por_tipo.get(clase) or por_tipo["clado"]
        return pool[rnd.entero(len(pool))]

    bases_tomadas: set[str] = set()

    def base_libre() -> str:
        """Un clado que todavía no sea base de ningún gemelo ni de ningún homónimo.

        Con `existente` a secas dos gemelos podían caer sobre el mismo clado y
        producir dos filas del apéndice B con la misma etiqueta preferida y la
        misma nota: un duplicado exacto, que no es el caso difícil que se quería
        fabricar. `--gemelos 6` tiene que dar seis parejas distintas.

        El barrido hacia delante desde una posición sorteada mantiene el
        determinismo: no se itera sobre el conjunto, sólo se consulta."""
        pool = por_tipo["clado"]
        inicio = rnd.entero(len(pool))
        for salto in range(len(pool)):
            candidato = pool[(inicio + salto) % len(pool)]
            if candidato not in bases_tomadas:
                bases_tomadas.add(candidato)
                return candidato
        raise SystemExit(
            f"no quedan clados libres como base de gemelo u homónimo: hay "
            f"{len(pool)} y ya se han usado {len(bases_tomadas)}. "
            f"Sube --entidades o baja --gemelos y --homonimos.")

    def fuente_de(k: int) -> str:
        """Las primeras filas agotan el apéndice A una por una, para que ninguna
        fuente quede sin citar; el resto se reparte con sesgo hacia unas pocas
        muy citadas, que es lo que hace un documento real."""
        if k <= cfg.fuentes:
            idx = k
        elif rnd.entero(4) == 0:
            idx = rnd.rango(1, min(cfg.fuentes, 24))
        else:
            idx = rnd.rango(1, cfg.fuentes)
        return f"{cfg.s(idx)} {localizador(rnd)}"

    for k, etiqueta in enumerate(etiquetas, start=1):
        fila_id = cfg.c(k)
        acep = ACEPTACION[(k * 3) % len(ACEPTACION)]
        fue = FUERZA[(k * 5) % len(FUERZA)]
        res = RESOLUCION[(k * 7) % len(RESOLUCION)]
        vig = "vigente"
        motivo = MOTIVOS[(k * 11) % len(MOTIVOS)]
        atribucion = "expresa"
        fuente = fuente_de(k)

        if etiqueta == "pertenencia":
            padre = existente("clado") if por_tipo["clado"] else "n/a"
            suj = nueva("clado", fila_id)
            pred, obj = "miembro_de", padre
            if obj == "n/a":
                pred, obj = "grupo_corona_de", suj
            texto = f"{suj} pertenece a {obj}"
        elif etiqueta == "hermandad":
            hermano = existente("clado")
            suj = nueva("clado", fila_id)
            pred, obj = "grupo_hermano_de", hermano
            texto = f"{suj} es grupo hermano de {obj}"
        elif etiqueta == "linaje":
            destino = existente("clado")
            suj = nueva("linaje", fila_id)
            pred, obj = "linaje_troncal_de", destino
            texto = f"{suj} se interpreta como linaje troncal de {obj}"
        elif etiqueta == "poblacion":
            padre = existente("clado")
            suj = nueva("poblacion", fila_id)
            pred, obj = "desciende_de", padre
            texto = f"{suj} se reconstruye como población descendiente de {obj}"
        elif etiqueta == "fosil":
            destino = existente("clado")
            suj = nueva("fosil", fila_id)
            pred, obj = "linaje_troncal_de", destino
            texto = f"{suj} se asigna al grupo tronco de {obj}"
        elif etiqueta == "nombre":
            destino = existente("clado")
            suj = nueva("nombre", fila_id)
            pred, obj = "sinonimo_propuesto_de", destino
            texto = f"{suj} se ha propuesto como sinónimo de {obj}"
            vig = "histórica"
        elif etiqueta == "rasgo":
            clase = ["rasgo", "gen", "organulo"][k % 3]
            suj = existente("clado")
            obj = nueva(clase, fila_id)
            pred = "posee_rasgo"
            texto = f"{suj} posee {obj}"
            positivas_rasgo.append({"fila": fila_id, "sujeto": suj, "objeto": obj})
        elif etiqueta == "metodo":
            suj = existente("clado")
            obj = nueva("metodo", fila_id)
            pred = "respaldado_por"
            texto = f"La posición de {suj} está respaldada por {obj}"
        elif etiqueta == "ambiental":
            suj = existente("clado")
            obj = nueva("ambiental", fila_id)
            pred = "tiene_edad_estimada"
            texto = (f"{suj} tiene una edad estimada dentro de {obj}, "
                     f"de {decimal(rnd.rango(80, 240))} a {decimal(rnd.rango(240, 400))} Ma")
        elif etiqueta == "termino":
            suj = nueva("termino", fila_id)
            pred, obj = "requiere_verificacion*", "n/a"
            texto = f"El término {suj} no designa un clado y su uso corriente induce a error"
            atribucion, fuente = "glosa", "n/a"
            fue, motivo = "desconocida", "comentario del autor, sin fuente detrás"
            acep, res = "no evaluado", "información insuficiente"
        elif etiqueta == "distincion":
            base = base_libre()
            suj = nueva("gemelo", fila_id, base=base,
                        sinonimos=f"no es sinónimo de {base} pese al parecido de la etiqueta")
            pred, obj = "no_sinonimo_de*", base
            texto = (f"{suj} y {base} no designan la misma entidad: la circunscripción "
                     f"restringida excluye linajes que la amplia incluye")
            acep, fue = "aceptación mixta", "media"
            motivo = "dos fuentes con circunscripciones declaradas distintas"
            res = "parcialmente resuelta"
        elif etiqueta == "circunscripcion":
            base = base_libre()
            otra = cfg.s(rnd.rango(1, cfg.fuentes))
            suj = nueva("homonimo", fila_id, base=base,
                        sinonimos=f"circunscripción rival de la fila homónima, según {otra}")
            pred, obj = "clasificado_como_por", otra
            texto = (f"El nombre {base} se usa con una segunda circunscripción, "
                     f"que excluye parte del contenido de la primera")
            acep, res, vig = "aceptación mixta", "sin resolver", "histórica"
            fue, motivo = "media", "dos circunscripciones publicadas sin arbitraje posterior"
        elif etiqueta == "negativa":
            if positivas_rasgo:
                pos = positivas_rasgo[rnd.entero(len(positivas_rasgo))]
                suj, obj, pred = pos["sujeto"], pos["objeto"], "carece_de_rasgo*"
                texto = (f"No se ha documentado que {suj} posea {obj}; la fila "
                         f"{pos['fila']} afirma lo contrario a partir de otra fuente")
            else:
                suj, obj, pred = existente("clado"), "n/a", "sin_evidencia_publicada_de*"
                texto = f"No hay búsqueda publicada del rasgo sintético en {suj}"
            acep, res = "aceptación mixta", "sin resolver"
            fue, motivo = "baja", "ausencia de observación, no observación de ausencia"
        elif etiqueta == "cuestionamiento":
            a = rnd.rango(1, k - 1)
            b = rnd.rango(1, k - 1)
            if b == a:
                b = 1 + (a % (k - 1))
            suj, obj, pred = cfg.c(a), cfg.c(b), "cuestionado_por"
            texto = f"La fila {cfg.c(a)} queda cuestionada por la fila {cfg.c(b)}"
            acep, res = "aceptación mixta", "sin resolver"
            fue, motivo = "media", "las dos filas proceden de fuentes distintas"
        elif etiqueta == "sintesis":
            a = rnd.rango(1, k - 1)
            b = rnd.rango(1, k - 1)
            if b == a:
                b = 1 + (a % (k - 1))
            suj, obj, pred = cfg.c(a), cfg.c(b), "incompatible_con"
            texto = f"Las filas {cfg.c(a)} y {cfg.c(b)} no pueden ser ciertas a la vez"
            atribucion = f"sintesis({cfg.c(a)}, {cfg.c(b)})"
            acep, res = "no evaluado", "sin resolver"
            fue, motivo = "desconocida", "derivada de dos filas del propio registro"
        elif etiqueta == "edad":
            suj = existente("clado")
            obj = existente("ambiental") if por_tipo.get("ambiental") else "n/a"
            pred = "tiene_edad_estimada"
            texto = (f"La divergencia de {suj} se estima entre "
                     f"{decimal(rnd.rango(100, 200))} y {decimal(rnd.rango(200, 320))} Ma")
        elif etiqueta == "valor":
            suj = existente("clado")
            obj = existente("rasgo") if por_tipo.get("rasgo") else "n/a"
            pred = "tiene_valor_medido"
            texto = (f"{suj} presenta un valor medido de {decimal(rnd.rango(10, 900))} "
                     f"{rnd.elige(UNIDADES_MAGNITUD)} para {obj}")
        elif etiqueta == "evento":
            suj, obj = existente("clado"), existente("clado")
            pred = "endosimbiosis_con"
            texto = (f"{suj} mantiene una endosimbiosis con {obj}, registrada como "
                     f"evento {cfg.e(1 + rnd.entero(cfg.eventos))}")
        elif etiqueta == "hipotesis":
            suj = existente("clado")
            obj = cfg.h(1 + rnd.entero(cfg.hipotesis))
            pred = "respaldado_por"
            texto = f"La posición de {suj} está respaldada por la hipótesis {obj}"
        else:  # historico
            suj = existente("nombre") if por_tipo.get("nombre") else existente("clado")
            obj = existente("clado")
            pred = "clasificado_como_por"
            texto = f"{suj} se clasificó dentro de {obj} en la literatura anterior"
            vig, res = "histórica", "resuelta"

        afirmaciones.append({
            "id": fila_id, "texto": texto, "sujeto": suj, "predicado": pred,
            "objeto": obj, "atribucion": atribucion, "fuente": fuente,
            "aceptacion": acep, "fuerza": fue, "motivo": motivo,
            "resolucion": res, "vigencia": vig, "etiqueta": etiqueta,
        })

    if contador_entidad != e_total:
        raise SystemExit(f"reparto incoherente: {contador_entidad} entidades "
                         f"creadas frente a {e_total} pedidas")
    return afirmaciones, entidades


def generar_apendices(cfg: Config, rnd: Aleatorio, afirmaciones: list[dict],
                      entidades: list[dict], fuentes: list[dict]) -> dict:
    """Apéndices C–G. Toda clave `C-…` que se cite aquí existe en el registro:
    §4.5 lo exige y el parser lo comprueba fila a fila."""
    ids = [a["id"] for a in afirmaciones]
    clados = [e["etiqueta"] for e in entidades if e["tipo"] == "clado sin rango"]

    def ref(i: int) -> str:
        return ids[i % len(ids)]

    def dos_refs(i: int) -> str:
        return f"{ref(i)}, {ref(i * 7 + 3)}"

    def cita() -> str:
        return f"{cfg.s(rnd.rango(1, cfg.fuentes))} {localizador(rnd)}"

    eventos = []
    for i in range(1, cfg.eventos + 1):
        a, b = rnd.elige(clados), rnd.elige(clados)
        papel_a, papel_b = PAPELES[i % len(PAPELES)], PAPELES[(i * 3 + 1) % len(PAPELES)]
        eventos.append([
            cfg.e(i),
            TIPOS_EVENTO[i % len(TIPOS_EVENTO)],
            f"{a}: {papel_a} · {b}: {papel_b}",
            rnd.elige(clados) if i % 3 else "n/a",
            f"entre {decimal(rnd.rango(90, 200))} y {decimal(rnd.rango(200, 350))} Ma",
            dos_refs(i * 13),
            cita(),
            DESENLACES[i % len(DESENLACES)],
        ])

    hipotesis = []
    for i in range(1, cfg.hipotesis + 1):
        rival = cfg.h(1 + (i % cfg.hipotesis))
        hipotesis.append([
            cfg.h(i),
            f"Sostiene que el nodo {rnd.elige(clados)} se explica por el mecanismo sintético M{i:02d}",
            f"Da por bueno que {rnd.elige(clados)} estaba presente antes del episodio",
            dos_refs(i * 17),
            f"{cfg.s(rnd.rango(1, cfg.fuentes))}, {cfg.s(rnd.rango(1, cfg.fuentes))}",
            cfg.s(rnd.rango(1, cfg.fuentes)) if i % 4 else "ninguna localizada",
            (f"{rival} en el orden relativo de los dos episodios; en el resto son compatibles"
             if i % 3 else f"{rival} sólo en apariencia: responden a preguntas distintas"),
            f"Una observación de {rnd.elige(clados)} anterior al episodio la falsaría",
        ])

    fechas = []
    for i in range(1, cfg.fechas + 1):
        ant = rnd.rango(1100, 2400)
        rec = ant - rnd.rango(50, 400)
        unidad = "Ma" if i % 3 else "Ga"
        if unidad == "Ga":
            ant, rec = rnd.rango(12, 25), rnd.rango(8, 12)
        fechas.append([
            f"{rnd.elige(clados)} ({TIPOS_FECHA[i % len(TIPOS_FECHA)]})",
            decimal(ant), decimal(rec), unidad,
            f"IC 95 % {decimal(ant + 40)}–{decimal(max(rec - 40, 1))} {unidad}"
            if i % 5 else "no consta en la fuente",
            TIPOS_FECHA[i % len(TIPOS_FECHA)],
            METODOS_FECHA[i % len(METODOS_FECHA)],
            "observado" if i % 4 == 0 else "inferido",
            cita(),
            ref(i * 11),
        ])

    magnitudes = []
    for i in range(1, cfg.magnitudes + 1):
        unidad = UNIDADES_MAGNITUD[i % len(UNIDADES_MAGNITUD)]
        magnitudes.append([
            f"magnitud sintética {i:04d} de {rnd.elige(clados)}",
            decimal(rnd.rango(5, 9800)),
            unidad,
            rnd.elige(clados),
            PROXIES[i % len(PROXIES)],
            f"± {decimal(rnd.rango(2, 90))} {unidad}" if i % 3 else "no consta en la fuente",
            "observado" if i % 3 == 0 else "inferido",
            cita(),
            ref(i * 5),
        ])

    # Apéndice G: material relevante que no encaja en ninguna sección.
    no_encajado = []
    for i in range(1, 13):
        no_encajado.append([
            f"Observación sintética suelta {i:02d} sobre {rnd.elige(clados)}",
            "no pertenece a ninguna sección sin forzar el encuadre",
            f"sección {1 + (i * 3) % 15}",
            cita(),
            ref(i * 23),
        ])

    busquedas = []
    for i in range(1, cfg.busquedas + 1):
        busquedas.append([
            f"hueco sintético {i:03d}: {rnd.elige(clados)} sin dato de {rnd.elige(UNIDADES_MAGNITUD)}",
            f"\"FIX termino{i:03d}\" AND \"magnitud sintética\"",
            ETIQUETAS_HUECO[i % len(ETIQUETAS_HUECO)],
            "la fuente declara que no se sabe" if i % 3 == 0 else
            ("no se recuperó nada en esta sesión" if i % 3 == 1 else
             "fuera del alcance declarado del encargo"),
        ])

    # Rasgos con costo. `sin_cifra` cuenta las celdas con el marcador literal,
    # porque el recuento de control del apéndice H tiene que declararlo.
    costes = []
    sin_cifra = 0
    for i, (rasgo, habilita, dependencias, hay_cifra) in enumerate(RASGOS_COSTE, start=1):
        if hay_cifra:
            valor = decimal(rnd.rango(20, 4800))
            unidad = UNIDADES_MAGNITUD[i % len(UNIDADES_MAGNITUD)]
        else:
            valor = unidad = "SIN CIFRA PUBLICADA LOCALIZADA"
            sin_cifra += 2
        costes.append([
            rasgo, habilita, dependencias, valor, unidad,
            f"organismo sintético {rnd.elige(clados)}, condición de cultivo FIX-{i:02d}",
            "medida" if hay_cifra and i % 2 == 0 else "estimada por los autores",
            cita(),
            "n/a" if i % 4 else "compensación documentada en la misma fuente",
        ])

    nodos = []
    for i in range(1, 13):
        nodos.append([
            clados[i * 3 % len(clados)],
            f"{clados[(i * 3 + 1) % len(clados)]}, {clados[(i * 3 + 2) % len(clados)]}",
            clados[(i * 5) % len(clados)],
            "SIN SINAPOMORFÍA MORFOLÓGICA PUBLICADA LOCALIZADA" if i % 3 else
            f"carácter ultraestructural sintético U{i:02d} ({cita()})",
            f"inserción rara sintética I{i:02d} ({cita()})",
            "filogenómica" if i % 2 else "filogenómica y carácter raro",
            f"soporte {rnd.rango(60, 100)} / pp {decimal(rnd.rango(80, 100))}",
            f"{decimal(rnd.rango(100, 220))}–{decimal(rnd.rango(220, 360))} Ma",
            METODOS_FECHA[i % len(METODOS_FECHA)],
            dos_refs(i * 29),
        ])

    tipologia = []
    for i, tipo in enumerate(TIPOLOGIA_ASOCIACION, start=1):
        documentado = i != len(TIPOLOGIA_ASOCIACION)
        tipologia.append([
            f"{i}. {tipo}",
            f"caso sintético {rnd.elige(clados)} con {rnd.elige(clados)}" if documentado
            else "SIN CASO DOCUMENTADO LOCALIZADO",
            cita() if documentado else "n/a",
            "transmisión vertical y cuello de botella" if i % 2 else
            "disponibilidad ambiental de la función aportada",
            ref(i * 37),
        ])

    compat = []
    for i in range(1, 16):
        a, b = cfg.h(1 + (i % cfg.hipotesis)), cfg.h(1 + ((i * 5) % cfg.hipotesis))
        compat.append([
            f"{a} frente a {b}",
            ["mutuamente excluyentes", "parcialmente compatibles", "compatibles"][i % 3],
            "chocan sólo en el orden de adquisición; comparten el resto del montaje"
            if i % 3 == 1 else "responden a la misma pregunta con montajes distintos",
            f"Observar {rnd.elige(clados)} antes del episodio separaría las dos",
            ref(i * 41),
        ])

    return {"eventos": eventos, "hipotesis": hipotesis, "fechas": fechas,
            "magnitudes": magnitudes, "no_encajado": no_encajado,
            "busquedas": busquedas, "costes": costes, "sin_cifra": sin_cifra,
            "nodos": nodos, "tipologia": tipologia, "compat": compat}


def generar_datos(cfg: Config) -> dict:
    rnd = Aleatorio(cfg.semilla)
    fuentes = generar_fuentes(cfg, rnd)
    afirmaciones, entidades = generar_registro(cfg, rnd, fuentes)
    apendices = generar_apendices(cfg, rnd, afirmaciones, entidades, fuentes)

    # «Afirmaciones que dependen de una sola fuente»: se cuenta, no se estima.
    usos: dict[str, int] = {}
    for a in afirmaciones:
        clave = a["fuente"].split()[0]
        if clave != "n/a":
            usos[clave] = usos.get(clave, 0) + 1
    solitarias = sum(1 for a in afirmaciones
                     if a["fuente"] != "n/a" and usos.get(a["fuente"].split()[0], 0) == 1)

    datos = {"fuentes": fuentes, "afirmaciones": afirmaciones,
             "entidades": entidades, "solitarias": solitarias}
    datos.update(apendices)
    return datos


# ============================================================================
# Montaje del documento
# ============================================================================

def parrafo(rnd: Aleatorio, cfg: Config, clados: list[str], ids: list[str]) -> str:
    plantilla = rnd.elige(PROSA)
    return plantilla.format(
        A=rnd.elige(clados), B=rnd.elige(clados),
        n=rnd.rango(12, 980), m=rnd.rango(12, 980),
        dec=decimal(rnd.rango(3, 220)),
        sop=f"{rnd.rango(50, 100)} / pp {decimal(rnd.rango(80, 100))}",
        f=f"{cfg.s(rnd.rango(1, cfg.fuentes))} {localizador(rnd)}",
        H=cfg.h(1 + rnd.entero(cfg.hipotesis)),
        C=ids[rnd.entero(len(ids))],
        amb=rnd.rango(1, 40),
    )


def construir(cfg: Config, datos: dict, relleno: int, linea_extra: bool) -> list[str]:
    """Monta el documento. `relleno` son párrafos de prosa adicionales, dos
    líneas cada uno, con los que se ajusta la extensión total al objetivo."""
    rnd = Aleatorio(cfg.semilla ^ 0x5EED)
    L: list[str] = []
    afirmaciones = datos["afirmaciones"]
    clados = [e["etiqueta"] for e in datos["entidades"] if e["tipo"] == "clado sin rango"]
    ids = [a["id"] for a in afirmaciones]

    def blanco() -> None:
        L.append("")

    # --- cabecera ----------------------------------------------------------
    L.append("*Documento sintético generado por "
             "`tests/fixtures/research-format/generate_scale.py`. No es ciencia y no es "
             "corpus: reproduce el formato y la escala que exige "
             "`docs/campaigns/C01-PROMPT-INVESTIGACION.md` para poder medir el coste de "
             "leerlo. Ninguna etiqueta, cifra ni fuente de aquí corresponde a nada real.*")
    blanco()
    L.append("# Encargo de investigación sintético: molde a escala")
    blanco()
    L.append(f"**Fecha de corte bibliográfico: {cfg.corte}.**")
    blanco()
    L.append("**Unidad temporal por defecto:** Ma. Cuando una fuente publica en Ga se "
             "conserva la unidad original y así se declara en cada fila del apéndice D.")
    blanco()
    L.append("**Autoridades de referencia declaradas:** clasificación sintética FIX "
             "(edición 3), recursos de secuencia sintéticos FIX-Seq y FIX-Prot, y la "
             "escala temporal sintética FIX-Chrono. Cualquier desviación se declara en la "
             "fila correspondiente.")
    blanco()
    L.append("**Marcado:** todos los nodos de este documento son clados sintéticos sin "
             "rango formal salvo donde se diga lo contrario, y esto se declara una sola "
             "vez. Se marca nodo a nodo sólo lo que discrimina: `⚠` posición o contenido "
             "discutidos · `≈` equivalencia dependiente de la definición adoptada · `[F]` "
             "clado recuperado por filogenómica sin sinapomorfía morfológica publicada · "
             "`[H]` composición dependiente de la hipótesis adoptada. `†` sólo en "
             "etiquetas con registro fósil propio.")
    blanco()
    L.append("**Lista cerrada de etiquetas descriptivas.** Se usan siempre con esta "
             "redacción literal, sin abreviar ni parafrasear:")
    blanco()
    for etiqueta in ("linaje hospedador sintético no identificado",
                     "simbionte sintético ancestral no muestreado",
                     "población sintética troncal sin descendientes vivos",
                     "linaje sintético conocido sólo por genoma ensamblado"):
        L.append(f"- «{etiqueta}»")
    blanco()

    # --- secciones ---------------------------------------------------------
    pesos = [(f"s{n}", peso) for n, _, peso in SECCIONES]
    por_seccion = reparto_por_pesos(cfg.afirmaciones, pesos)
    relleno_seccion = [relleno // len(SECCIONES) + (1 if i < relleno % len(SECCIONES) else 0)
                       for i in range(len(SECCIONES))]

    cursor = 0
    for orden, (numero, titulo, _) in enumerate(SECCIONES):
        cuantas = por_seccion[f"s{numero}"]
        bloque = afirmaciones[cursor:cursor + cuantas]
        cursor += cuantas

        L.append(f"## {numero}. {titulo}")
        blanco()
        L.append(parrafo(rnd, cfg, clados, ids))
        blanco()

        extra = relleno_seccion[orden]
        for j, sub in enumerate(SUBSECCIONES, start=1):
            L.append(f"### {numero}.{j} {sub}")
            blanco()
            cuantos = 2 + extra // len(SUBSECCIONES) + (1 if j <= extra % len(SUBSECCIONES) else 0)
            for _ in range(cuantos):
                L.append(parrafo(rnd, cfg, clados, ids))
                blanco()

            # Un árbol por sección, con las marcas de §14 y sin fundir topologías.
            if j == 2 and numero % 4 == 1 and len(clados) > 8:
                base = (numero * 7) % (len(clados) - 5)
                L.append("```")
                L.append(f"{clados[base]} ⚠")
                L.append(f"├── {clados[base + 1]} [F]")
                L.append(f"│   └── {clados[base + 2]} ≈")
                L.append(f"├── {clados[base + 3]} [H]")
                L.append(f"└── {clados[base + 4]}")
                L.append("```")
                blanco()

        # Tablas propias de cada sección, en su sitio y no al final.
        if numero == 3:
            L.append("### 3.5 Matriz de compatibilidad entre hipótesis")
            blanco()
            L.extend(tabla(["par de modelos", "relación", "en qué punto choca",
                            "qué observación los distinguiría", "#"], datos["compat"]))
            blanco()
        if numero == 4:
            L.append("### 4.5 Vista de resumen por nodo")
            blanco()
            L.append("Esta tabla no contiene nada que no esté ya en el registro.")
            blanco()
            L.extend(tabla(["nodo", "qué linajes quedan dentro", "qué linaje queda fuera",
                            "sinapomorfía morfológica propuesta",
                            "carácter molecular propuesto", "tipo de evidencia",
                            "soporte cuantitativo transcrito", "edad estimada",
                            "método de la estimación", "#"], datos["nodos"]))
            blanco()
        if numero == 9:
            L.append("### 9.5 Tipología cerrada de desenlaces")
            blanco()
            L.extend(tabla(["tipo", "caso documentado", "fuente",
                            "qué mantiene la asociación en ese estado", "#"],
                           datos["tipologia"]))
            blanco()
        if numero == 10:
            L.append("### 10.5 Coste publicado por rasgo")
            blanco()
            L.extend(tabla(["rasgo", "qué habilita", "dependencias previas que exige",
                            "cifra de coste publicada", "unidad exacta",
                            "organismo, condición experimental o modelo",
                            "medida o estimada por los autores", "fuente y localizador",
                            "compensación documentada"], datos["costes"]))
            blanco()
        if numero == 15:
            L.append("### 15.5 Búsquedas negativas")
            blanco()
            L.extend(tabla(["hueco", "términos exactos buscados", "etiqueta", "motivo"],
                           datos["busquedas"]))
            blanco()

        L.append("### Registro de afirmaciones")
        blanco()
        L.extend(tabla(
            ["#", "Afirmación", "Sujeto", "Predicado", "Objeto", "Atribución",
             "Fuente", "Aceptación", "Fuerza", "Motivo", "Resolución", "Vigencia"],
            [[a["id"], a["texto"], a["sujeto"], a["predicado"], a["objeto"],
              a["atribucion"], a["fuente"], a["aceptacion"], a["fuerza"],
              a["motivo"], a["resolucion"], a["vigencia"]] for a in bloque]))
        blanco()

    # --- apéndices ---------------------------------------------------------
    L.append("## 17. Apéndices")
    blanco()
    L.append("**A. Fuentes.**")
    blanco()
    L.extend(tabla(["clave", "autores", "año", "título", "publicación o repositorio",
                    "DOI", "tipo", "notas de calidad", "fecha de consulta"],
                   [[f["clave"], f["autores"], f["año"], f["título"], f["publicación"],
                     f["doi"], f["tipo"], f["notas"], f["consulta"]]
                    for f in datos["fuentes"]]))
    blanco()

    L.append("**B. Entidades.**")
    blanco()
    L.append("Las etiquetas casi idénticas no se fusionan y los homónimos llevan una fila "
             "por circunscripción, con la fuente en la columna de sinónimos: son dos "
             "contenidos, no un contenido con nota.")
    blanco()
    L.extend(tabla(["etiqueta preferida", "tipo", "sinónimos y grafías alternativas",
                    "marcas", "#"],
                   [[e["etiqueta"], e["tipo"], e["sinonimos"], e["marcas"], e["fila"]]
                    for e in datos["entidades"]]))
    blanco()

    L.append("**C. Eventos.**")
    blanco()
    L.extend(tabla(["clave", "tipo", "participantes con su papel",
                    "entidad resultante si la hay", "intervalo temporal",
                    "# de las filas que lo sostienen",
                    "qué fuente lo describe como evento", "desenlace"],
                   datos["eventos"]))
    blanco()

    L.append("**D. Fechas.**")
    blanco()
    L.extend(tabla(["a qué se aplica", "límite más antiguo", "límite más reciente",
                    "unidad explícita", "incertidumbre tal como la da la fuente",
                    "tipo", "método y calibración", "observado o inferido",
                    "fuente con localizador", "#"], datos["fechas"]))
    blanco()

    L.append("**E. Hipótesis.**")
    blanco()
    L.extend(tabla(["clave", "qué sostiene en una frase", "supuestos que da por buenos",
                    "# de las filas que la componen", "fuentes a favor",
                    "fuentes en contra",
                    "con qué otras hipótesis es incompatible y en qué punto exacto",
                    "qué observación la falsaría"], datos["hipotesis"]))
    blanco()

    L.append("**F. Magnitudes.**")
    blanco()
    L.extend(tabla(["magnitud", "valor tal como lo publica la fuente", "unidad original",
                    "organismo, nodo o intervalo al que se aplica", "método o proxy",
                    "incertidumbre publicada", "observado o inferido",
                    "fuente con localizador", "#"], datos["magnitudes"]))
    blanco()

    L.append("**G. Material no encajado.**")
    blanco()
    L.extend(tabla(["material", "por qué no encaja", "a qué sección pertenecería",
                    "fuente con localizador", "#"], datos["no_encajado"]))
    blanco()

    L.append("**H. Recuento de control.**")
    blanco()
    L.extend(tabla(["magnitud", "valor"], [
        ["fuentes distintas", len(datos["fuentes"])],
        ["oraciones marcadas `[SIN FUENTE]`", 0],
        ["filas del registro", len(afirmaciones)],
        ["afirmaciones que dependen de una sola fuente", datos["solitarias"]],
        ["celdas con `SIN CIFRA PUBLICADA LOCALIZADA`", datos["sin_cifra"]],
    ]))
    blanco()

    # --- cierre ------------------------------------------------------------
    L.append("## 18. Cierre")
    blanco()
    L.append("Las seis preguntas del encargo, con la sección donde está el material "
             "sintético que las respondería:")
    blanco()
    preguntas = [
        "¿Qué hace estable una asociación inicialmente conflictiva? — sección 9.",
        "¿Cómo cambian los costos y beneficios con el ambiente? — secciones 7 y 10.",
        "¿Cuándo una dependencia se vuelve heredable? — sección 9 y apéndice C.",
        "¿Qué distingue divergencia, transferencia e integración? — apéndice C.",
        "¿Cómo puede la misma evidencia apoyar reconstrucciones diferentes? — sección 3 y apéndice E.",
        "¿Qué rasgos están observados y cuáles inferidos? — apéndices D y F.",
    ]
    for i, p in enumerate(preguntas, start=1):
        L.append(f"{i}. {p}")
    if linea_extra:
        L.append("7. Nota de ajuste: esta línea existe para que la extensión total "
                 "cuadre con la dimensión pedida.")
    blanco()
    return L


# ============================================================================
# Entrada
# ============================================================================

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Genera un documento de investigación sintético a escala real",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument("--salida", "-o",
                    default=str(RAIZ / "generated" / "research-scale" / "SEC-SCALE.md"),
                    help="fichero de salida; por defecto en generated/, que no se versiona")
    ap.add_argument("--semilla", type=int, default=20260807,
                    help="misma semilla y mismos parámetros, mismo fichero byte a byte")
    ap.add_argument("--lineas", type=int, default=DIM_LINEAS,
                    help="extensión total objetivo, en líneas")
    ap.add_argument("--afirmaciones", type=int, default=DIM_AFIRMACIONES,
                    help="filas del registro")
    ap.add_argument("--fuentes", type=int, default=DIM_FUENTES,
                    help="filas del apéndice A")
    ap.add_argument("--entidades", type=int, default=DIM_ENTIDADES,
                    help="filas del apéndice B; no puede superar --afirmaciones")
    ap.add_argument("--eventos", type=int, default=DIM_EVENTOS,
                    help="filas del apéndice C")
    ap.add_argument("--fechas", type=int, default=DIM_FECHAS,
                    help="filas del apéndice D")
    ap.add_argument("--hipotesis", type=int, default=DIM_HIPOTESIS,
                    help="filas del apéndice E")
    ap.add_argument("--magnitudes", type=int, default=DIM_MAGNITUDES,
                    help="filas del apéndice F")
    ap.add_argument("--busquedas-negativas", type=int, default=DIM_BUSQUEDAS,
                    help="filas de la tabla de búsquedas negativas de §15")
    ap.add_argument("--gemelos", type=int, default=6,
                    help="pares de etiquetas casi idénticas que NO son la misma entidad")
    ap.add_argument("--homonimos", type=int, default=4,
                    help="etiquetas repetidas con dos circunscripciones distintas")
    ap.add_argument("--corte", default="2026-08-07",
                    help="fecha de corte bibliográfico declarada, y fecha de consulta")
    args = ap.parse_args()

    cfg = Config(args)
    datos = generar_datos(cfg)

    # Dos pasadas: la primera mide el esqueleto, la segunda ajusta la prosa hasta
    # la extensión pedida. Cada párrafo de relleno son exactamente dos líneas.
    base = len(construir(cfg, datos, 0, False))
    relleno = max(0, (cfg.lineas - base) // 2)
    extra = (cfg.lineas - base) % 2 == 1 and cfg.lineas > base
    lineas = construir(cfg, datos, relleno, extra)

    cfg.salida.parent.mkdir(parents=True, exist_ok=True)
    with open(cfg.salida, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lineas) + "\n")

    bytes_ = cfg.salida.stat().st_size
    print(f"{cfg.salida}")
    print(f"  líneas               {len(lineas)}  (objetivo {cfg.lineas})")
    print(f"  tamaño               {bytes_ / 1024:.1f} KiB")
    print(f"  afirmaciones         {len(datos['afirmaciones'])}")
    print(f"  fuentes              {len(datos['fuentes'])}")
    print(f"  entidades            {len(datos['entidades'])}")
    print(f"  eventos              {len(datos['eventos'])}")
    print(f"  hipótesis            {len(datos['hipotesis'])}")
    print(f"  fechas               {len(datos['fechas'])}")
    print(f"  magnitudes           {len(datos['magnitudes'])}")
    print(f"  búsquedas negativas  {len(datos['busquedas'])}")
    reparto: dict[str, int] = {}
    for a in datos["afirmaciones"]:
        base_atrib = a["atribucion"].split("(")[0]
        reparto[base_atrib] = reparto.get(base_atrib, 0) + 1
    print("  atribución           " + " · ".join(
        f"{k} {v}" for k, v in sorted(reparto.items())))
    if len(lineas) > cfg.lineas:
        print(f"AVISO: las tablas por sí solas ocupan {base} líneas, más que el objetivo "
              f"de --lineas ({cfg.lineas}). La prosa no se recorta: sube --lineas o baja "
              f"las dimensiones tabulares.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
