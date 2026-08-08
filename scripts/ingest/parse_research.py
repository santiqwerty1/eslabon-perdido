#!/usr/bin/env python3
"""Lector de la capa de registro de una investigación encargada.

`docs/campaigns/C01-PROMPT-INVESTIGACION.md` pide el documento en **dos capas**:
prosa, que se lee, y un registro de filas numeradas, que se procesa. Este script
lee la segunda.

Hace dos trabajos a la vez, y el segundo es el que más vale antes de tener el
documento:

1. **Conformidad.** Comprueba que la investigación llegó en el formato pedido:
   columnas en orden, vocabularios cerrados respetados, apéndices presentes,
   recuento de control cuadrando con lo que se cuenta de verdad. Un fallo aquí
   no es un fallo del parser: es un hallazgo sobre la investigación.
2. **Traducción.** Convierte las filas a los registros del proyecto. La capa de
   registro ya viene con sujeto, predicado, objeto, procedencia y los cuatro
   ejes epistémicos, así que la conversión es mecánica y no requiere criterio.

**Lo que NO hace.** Resolver identidad. Las etiquetas del registro son texto
—«FIX-Alfa»— y convertirlas en entidades con identificador opaco exige decidir
si dos etiquetas son la misma cosa, que es el paso 5 de §17 y es juicio humano
(§27.12). El script propone un mapa etiqueta→entidad y lo deja para revisión.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

COLUMNAS = ["#", "Afirmación", "Sujeto", "Predicado", "Objeto", "Atribución",
            "Fuente", "Aceptación", "Fuerza", "Motivo", "Resolución", "Vigencia"]

ACEPTACION = {
    "consenso amplio": "broad_consensus",
    "aceptación mayoritaria": "majority_acceptance",
    "aceptación mixta": "mixed_acceptance",
    "posición minoritaria": "minority_position",
    "no evaluado": "not_assessed",
}
FUERZA = {"alta": "high", "media": "medium", "baja": "low", "desconocida": "unknown"}
RESOLUCION = {
    "resuelta": "resolved",
    "parcialmente resuelta": "partially_resolved",
    "sin resolver": "unresolved",
    "información insuficiente": "insufficient_information",
}
VIGENCIA = {"vigente": "current", "histórica": "historical",
            "superada": "superseded", "rechazada": "rejected"}
ATRIBUCION = {"expresa", "sintesis", "síntesis", "glosa"}

# Apéndices tabulares del prompt, reconocidos por su primera columna.
# El documento real trae ocho; leer sólo tres dejaría fuera eventos, fechas,
# hipótesis y magnitudes, que son la mitad del contenido estructurado.
APENDICES = {
    "clave":              None,      # A fuentes / C eventos / E hipótesis: se afina por columnas
    "etiqueta preferida": "entities",
    "a qué se aplica":    "dates",
    "magnitud":           None,      # F magnitudes / H recuento: se afina por columnas
}

TIPO_FUENTE = {
    "investigación primaria": "primary_research",
    "revisión": "review",
    "base de datos taxonómica": "taxonomic_database",
    "preprint": "preprint",
    "capítulo o libro": "book_or_chapter",
    "tesis": "thesis",
    "divulgación o blog": "popular_or_blog",
    "otro": "other",
}


def _parse_repo(base: Path) -> tuple[dict, Hallazgos]:
    """Corpus servido como repositorio de CSV en vez de un solo Markdown.

    La investigacion migro a CSV, y eso elimina de golpe tres riesgos del
    formato anterior: una tabla no puede partirse en dos, las celdas con pipes o
    enlaces no rompen el reparto de columnas, y el troceado por secciones que
    §17 exige ya viene hecho. El contrato semantico no cambia —mismas columnas,
    mismo orden— asi que se reconstruyen las tablas y se reutiliza intacta toda
    la comprobacion de conformidad.
    """
    import csv
    import json as _json

    man = _json.loads((base / "manifest.json").read_text(encoding="utf-8"))
    trozos = [f"Fecha de corte bibliografico: {man.get('fecha_de_corte_bibliografico', '')}", ""]

    def volcar(f: Path) -> None:
        with f.open(encoding="utf-8", newline="") as fh:
            filas = list(csv.reader(fh))
        if len(filas) < 2:
            return
        cab, cuerpo = filas[0], filas[1:]
        limpia = lambda c: c.replace("|", "\\|").replace("\n", " ")
        trozos.append("| " + " | ".join(limpia(c) for c in cab) + " |")
        trozos.append("|" + "---|" * len(cab))
        for fila in cuerpo:
            fila = (fila + [""] * len(cab))[: len(cab)]
            trozos.append("| " + " | ".join(limpia(c) for c in fila) + " |")
        trozos.append("")

    afirm = sorted((base / "data" / "afirmaciones").glob("*.csv"))
    for f in afirm:
        volcar(f)
    for f in sorted((base / "data" / "apendices").glob("*.csv")):
        volcar(f)

    datos, h = _parse_texto("\n".join(trozos))
    if not afirm:
        h.error(f"no hay ficheros de afirmaciones en {base}/data/afirmaciones/")
    datos["manifest"] = man
    datos["secciones"] = [f.stem for f in afirm]

    estado = str(man.get("estado", ""))
    if "provisional" in estado or "faltan" in estado:
        h.aviso(f"el manifiesto declara el corpus incompleto: «{estado}». "
                "Ingerir ahora fijaria un estado que va a cambiar")

    cuentas = man.get("counts") or {}
    for clave, real in (("afirmaciones", len(datos["claims"])), ("fuentes", len(datos["sources"])),
                        ("entidades", len(datos["entities"])), ("eventos", len(datos["events"])),
                        ("hipotesis", len(datos["hypotheses"])), ("fechas", len(datos["dates"])),
                        ("magnitudes", len(datos["magnitudes"]))):
        d = cuentas.get(clave)
        if isinstance(d, int) and d != real:
            h.error(f"el manifiesto declara {d} en «{clave}» y se leen {real}")
    return datos, h


class Hallazgos:
    def __init__(self) -> None:
        self.errores: list[str] = []
        self.avisos: list[str] = []

    def error(self, m: str) -> None:
        self.errores.append(m)

    def aviso(self, m: str) -> None:
        self.avisos.append(m)


def tablas(texto: str) -> list[tuple[list[str], list[list[str]]]]:
    """Extrae toda tabla Markdown como (cabecera, filas)."""
    salida = []
    lineas = texto.splitlines()
    i = 0
    while i < len(lineas):
        if lineas[i].strip().startswith("|") and i + 1 < len(lineas) and re.match(
            r"^\s*\|[\s:|-]+\|\s*$", lineas[i + 1]
        ):
            cab = [c.strip() for c in lineas[i].strip().strip("|").split("|")]
            filas = []
            j = i + 2
            while j < len(lineas) and lineas[j].strip().startswith("|"):
                filas.append([c.strip() for c in lineas[j].strip().strip("|").split("|")])
                j += 1
            salida.append((cab, filas))
            i = j
        else:
            i += 1
    return salida


def es_registro(cab: list[str]) -> bool:
    return len(cab) >= 6 and cab[0] == "#" and "Afirmación" in cab


def comprobar_registro(cab: list[str], h: Hallazgos) -> None:
    if cab != COLUMNAS:
        faltan = [c for c in COLUMNAS if c not in cab]
        sobran = [c for c in cab if c not in COLUMNAS]
        if faltan:
            h.error(f"registro: faltan columnas {faltan}")
        if sobran:
            h.error(f"registro: columnas no previstas {sobran}")
        if not faltan and not sobran:
            h.error(f"registro: columnas en orden distinto del pedido\n  esperado: {COLUMNAS}\n  recibido: {cab}")


def _leer_csv(path: Path) -> tuple[list[str], list[list[str]]]:
    import csv
    with path.open(encoding="utf-8", newline="") as fh:
        filas = list(csv.reader(fh))
    return (filas[0], filas[1:]) if filas else ([], [])


def tablas_repo(base: Path, h: Hallazgos) -> list[tuple[list[str], list[list[str]]]]:
    """Lee el corpus servido como repositorio de CSV en vez de un solo Markdown.

    La investigacion migro a CSV (`0.5.0-csv-migration`) y eso resuelve de golpe
    tres riesgos que el formato Markdown traia: una tabla no puede partirse en
    dos, las celdas con pipes o enlaces no rompen el reparto de columnas, y el
    troceado por secciones que §17 exige ya viene hecho por el propio corpus.
    El contrato semantico no cambia: las columnas son las mismas y en el mismo
    orden, asi que toda la comprobacion de conformidad se reutiliza tal cual.
    """
    salida = []
    afirm = sorted((base / "data" / "afirmaciones").glob("*.csv"))
    if not afirm:
        h.error(f"no hay ficheros de afirmaciones en {base}/data/afirmaciones/")
    for f in afirm:
        cab, filas = _leer_csv(f)
        salida.append((cab, filas))
    for f in sorted((base / "data" / "apendices").glob("*.csv")):
        cab, filas = _leer_csv(f)
        salida.append((cab, filas))
    return salida


def parse(path: Path) -> tuple[dict, Hallazgos]:
    # Un directorio con manifest.json es el corpus servido como repositorio.
    if path.is_dir() and (path / "manifest.json").exists():
        return _parse_repo(path)
    return _parse_texto(path.read_text(encoding="utf-8"))


def _parse_texto(texto: str) -> tuple[dict, Hallazgos]:
    h = Hallazgos()

    corte = re.search(r"[Ff]echa de corte bibliográfico[:\s]*\**\s*([0-9]{4}-[0-9]{2}-[0-9]{2})", texto)
    if not corte:
        corte = re.search(r"[Cc]orte bibliográfico[:\s]*\**\s*([^\n*]{4,40})", texto)
    if not corte:
        h.error("no se declara fecha de corte bibliográfico; el prompt la exige al principio")

    afirmaciones: list[dict] = []
    fuentes: list[dict] = []
    entidades: list[dict] = []
    eventos: list[dict] = []
    hipotesis: list[dict] = []
    fechas: list[dict] = []
    magnitudes: list[dict] = []
    no_encajado: list[dict] = []
    control: dict[str, str] = {}
    etiquetas: set[str] = set()
    # Toda tabla que ninguna rama reclame se pierde sin dejar rastro. Contarlas
    # y decir cuáles son convierte la pérdida silenciosa en un aviso legible.
    tablas_por_clase: dict[str, int] = {}
    sin_reconocer: list[tuple[list[str], int]] = []

    def clasificada(nombre: str) -> None:
        tablas_por_clase[nombre] = tablas_por_clase.get(nombre, 0) + 1

    encontradas = tablas(texto)
    # Una tabla partida en dos —por un salto de página, un párrafo intercalado o
    # una línea en blanco— deja su segunda mitad sin cabecera ni separador, y el
    # escáner deja de verla como tabla: las filas no se pierden en una rama, se
    # pierden antes de llegar a ninguna. Contar las líneas que empiezan por «|» y
    # restar las que quedaron dentro de alguna tabla las saca a la luz sin tener
    # que adivinar dónde estaba el corte. En los tres documentos correctos que hay
    # hoy la diferencia es exactamente 0, así que no admite falso positivo barato.
    lineas_pipe = sum(1 for ln in texto.splitlines() if ln.strip().startswith("|"))
    lineas_en_tabla = sum(2 + len(filas) for _, filas in encontradas)
    if lineas_pipe > lineas_en_tabla:
        h.error(f"{lineas_pipe - lineas_en_tabla} líneas empiezan por «|» y no pertenecen "
                "a ninguna tabla: son filas huérfanas de una tabla partida en dos, y "
                "no se ha leído ninguna. Vuelve a unirla o reemite cabecera y separador")

    for cab, filas in encontradas:
        if es_registro(cab):
            clasificada("registro")
            comprobar_registro(cab, h)
            idx = {c: i for i, c in enumerate(cab)}

            def col(f: list[str], nombre: str) -> str:
                i = idx.get(nombre)
                return f[i].strip() if i is not None and i < len(f) else ""

            for f in filas:
                num = col(f, "#")
                # Una fila con menos celdas que la cabecera no es una fila corta:
                # es una fila cuyos últimos ejes epistémicos se rellenan solos con
                # el valor por defecto. Sin este aviso la pérdida es invisible.
                if len(f) < len(cab):
                    h.error(f"{num or '(sin #)'}: la fila trae {len(f)} celdas y la cabecera "
                            f"{len(cab)}; las columnas {cab[len(f):]} se darían por vacías")
                atrib = col(f, "Atribución").lower()
                base = atrib.split("(")[0].strip()
                if base not in ATRIBUCION:
                    h.error(f"{num}: atribución {atrib!r} fuera del vocabulario {sorted(ATRIBUCION)}")
                if base.startswith("sintesis") or base.startswith("síntesis"):
                    if "(" not in atrib:
                        h.error(f"{num}: atribución 'sintesis' sin las filas de origen entre paréntesis")
                acep, fue = col(f, "Aceptación").lower(), col(f, "Fuerza").lower()
                res, vig = col(f, "Resolución").lower(), col(f, "Vigencia").lower()
                for valor, mapa, etiqueta in ((acep, ACEPTACION, "Aceptación"), (fue, FUERZA, "Fuerza"),
                                              (res, RESOLUCION, "Resolución"), (vig, VIGENCIA, "Vigencia")):
                    if valor and valor not in mapa:
                        h.error(f"{num}: {etiqueta} {valor!r} fuera del vocabulario cerrado")
                if fue and fue != "desconocida" and not col(f, "Motivo"):
                    h.error(f"{num}: fuerza {fue!r} sin motivo escrito; §10.3 lo exige")
                if base == "expresa" and not col(f, "Fuente"):
                    h.error(f"{num}: atribución 'expresa' sin fuente")
                for campo in ("Sujeto", "Objeto"):
                    v = col(f, campo)
                    if v and v not in ("n/a", "-"):
                        etiquetas.add(v)
                afirmaciones.append({
                    "local_id": num,
                    "text": col(f, "Afirmación"),
                    "subject_label": col(f, "Sujeto"),
                    "predicate": col(f, "Predicado"),
                    "object_label": col(f, "Objeto"),
                    "attribution": base,
                    "attribution_refs": re.findall(r"C-\d+", col(f, "Atribución")),
                    "source_ref": col(f, "Fuente"),
                    "epistemic_dimensions": {
                        "acceptance": ACEPTACION.get(acep, "not_assessed"),
                        "evidence_strength": FUERZA.get(fue, "unknown"),
                        "evidence_strength_reason": col(f, "Motivo") or None,
                        "resolution": RESOLUCION.get(res, "unresolved"),
                        "historical_status": VIGENCIA.get(vig, "current"),
                    },
                })
        elif cab and cab[0].lower() == "clave" and "tipo" in [c.lower() for c in cab] and any(
                c.lower().startswith("autor") for c in cab):
            clasificada("A fuentes")
            for f in filas:
                d = dict(zip(cab, f))
                tipo = d.get("tipo", "").lower()
                if tipo and tipo not in TIPO_FUENTE:
                    h.aviso(f"fuente {d.get('clave')}: tipo {tipo!r} fuera de la lista cerrada")
                doi = d.get("DOI", "")
                if doi and doi != "n/a" and not doi.startswith("http") and "no verificado" not in doi:
                    h.aviso(f"fuente {d.get('clave')}: DOI {doi!r} no es una URL resoluble")
                fuentes.append({"key": d.get("clave"), "authors": d.get("autores"),
                                "year": d.get("año"), "title": d.get("título"),
                                "container": d.get("publicación o repositorio"),
                                "doi": doi, "source_type": TIPO_FUENTE.get(tipo, "other"),
                                "quality_notes": d.get("notas de calidad"),
                                "consulted_at": d.get("fecha de consulta")})
        elif cab and cab[0].lower().startswith("etiqueta"):
            clasificada("B entidades")
            for f in filas:
                entidades.append(dict(zip(cab, f)))
        elif cab and cab[0].lower() == "clave" and any("participante" in c.lower() for c in cab):
            clasificada("C eventos")
            for f in filas:
                d = dict(zip(cab, f))
                eventos.append(d)
                papeles = d.get("participantes con su papel", "") or d.get("participantes", "")
                # El papel puede ir entre parentesis —«Eukaryota (linaje
                # resultante)»— o tras dos puntos o guion. El prompt no fijo el
                # separador, asi que se admiten los tres: lo que importa es que
                # el papel ESTE, no como se escriba (§13.2).
                if papeles and not re.search(r"[(\[:\u2014-]", papeles):
                    h.error(f"evento {d.get('clave')}: participantes sin papel declarado. "
                            "«A y B participaron» no dice quién entró en quién (§13.2)")
        elif cab and cab[0].lower() == "clave" and any("sostiene" in c.lower() for c in cab):
            clasificada("E hipótesis")
            for f in filas:
                hipotesis.append(dict(zip(cab, f)))
        elif cab and cab[0].lower().startswith("a qué se aplica"):
            clasificada("D fechas")
            for f in filas:
                d = dict(zip(cab, f))
                fechas.append(d)
                unidad = (d.get("unidad explícita") or d.get("unidad") or "").strip()
                if not unidad or unidad in ("n/a", "-"):
                    h.error(f"fecha «{f[0][:40]}»: sin unidad explícita. Entre 1,5 y 2,5 "
                            "la ambigüedad Ma/Ga es real y un intervalo sin unidad no sirve")
                obs = (d.get("observado o inferido") or "").strip().lower()
                if obs and obs not in ("observado", "inferido"):
                    h.error(f"fecha «{f[0][:40]}»: «{obs}» no es ni observado ni inferido (§11)")
        elif cab and cab[0].lower() == "magnitud" and len(cab) > 3:
            clasificada("F magnitudes")
            for f in filas:
                d = dict(zip(cab, f))
                magnitudes.append(d)
                if not (d.get("unidad original") or "").strip():
                    h.error(f"magnitud «{f[0][:40]}»: sin unidad original. §10.7 prohíbe "
                            "convertir medidas distintas a una escala común")
        elif cab and cab[0].lower() in ("magnitud", "control"):
            # El apéndice H se titula «magnitud|valor» en el molde Markdown y
            # «control|valor» en el corpus servido como CSV. Es el mismo apéndice.
            clasificada("H recuento")
            for f in filas:
                if len(f) >= 2:
                    control[f[0]] = f[1]
        elif cab and cab[0].lower() == "material":
            # Apéndice G, material no encajado. No se lee como dato, pero cuenta
            # para saber cuánto quedó fuera de la estructura.
            clasificada("G material no encajado")
            for f in filas:
                no_encajado.append(dict(zip(cab, f)))
        else:
            sin_reconocer.append((cab, len(filas)))

    if not afirmaciones:
        h.error("no se encontró ninguna tabla de registro de afirmaciones")
    if not fuentes:
        h.error("no se encontró el apéndice A de fuentes")

    # Una tabla que ninguna rama reclama no produce error: produce silencio, que
    # es peor. Basta con que una cabecera diga «actores» donde el prompt dice
    # «participantes» para que un apéndice entero desaparezca. Estas dos listas
    # no juzgan el contenido, sólo hacen visible lo que el lector NO leyó.
    for cab, n in sin_reconocer:
        h.aviso(f"tabla no reconocida ({n} filas), no se ha leído nada de ella: "
                f"{cab}")
    # Cada apéndice es una tabla. Cero significa que se perdió o cambió de nombre;
    # más de una, que el documento llegó por partes o que otra se coló en su sitio.
    for nombre in ("A fuentes", "B entidades", "C eventos", "D fechas",
                   "E hipótesis", "F magnitudes", "H recuento"):
        n = tablas_por_clase.get(nombre, 0)
        if n == 0:
            h.aviso(f"apéndice {nombre}: ninguna tabla lo reconoce; o falta o su "
                    "primera columna no se llama como pide §17")
        elif n > 1:
            h.aviso(f"apéndice {nombre}: {n} tablas distintas encajan aquí; "
                    "si el documento llegó por partes, sus filas están duplicadas")

    # El recuento de control es un autoinforme: comprobarlo es barato y detecta
    # que el documento se generó por partes o se truncó.
    if control:
        pares = [("filas del registro", len(afirmaciones)), ("fuentes distintas", len(fuentes))]
        for etiqueta, real in pares:
            declarado = next((v for k, v in control.items()
                              if etiqueta in k.lower()
                              or (etiqueta == "filas del registro" and "filas del registro" in k.lower())
                              or (etiqueta == "fuentes distintas" and "fuentes distintas" in k.lower())), None)
            if declarado and declarado.strip().isdigit() and int(declarado) != real:
                h.error(f"recuento de control: declara {declarado} en «{etiqueta}» y se cuentan {real}")
    else:
        h.aviso("no se encontró el apéndice H de recuento de control")

    claves = {f["key"] for f in fuentes}
    # El conjunto se calcula UNA vez. Reconstruirlo dentro del bucle hacía el
    # coste cuadrático en el número de afirmaciones: irrelevante a 1.593 filas
    # (33 ms), pero el documento sigue creciendo y el arreglo es una línea.
    locales_ref = {a["local_id"] for a in afirmaciones}
    # El `#` es la clave con la que los ocho apéndices apuntan al registro y con
    # la que aguas abajo se indexa por diccionario. Repetido, una de las dos filas
    # desaparece sin ruido; hoy sólo se notaba de rebote y con otro mensaje.
    if len(locales_ref) != len(afirmaciones):
        cuenta = Counter(a["local_id"] for a in afirmaciones)
        repetidos = sorted(k for k, n in cuenta.items() if n > 1)
        h.error(f"el registro repite {len(repetidos)} identificadores locales; "
                f"§16 pide que el `#` sea correlativo y no se reinicie por sección. "
                f"Primeros: {repetidos[:8]}")
    for a in afirmaciones:
        # El campo puede traer varias claves y localizadores: «S412; S395 fig. 2».
        # Se comprueban TODAS las claves, no solo la primera, y sin la puntuacion
        # pegada. `BN-` son busquedas negativas, no fuentes: una afirmacion puede
        # citarlas legitimamente para decir que se busco y no se encontro.
        # Las claves del apendice A son S01..S479: SIEMPRE dos o tres digitos.
        # Un `S` seguido de un solo digito no es ni puede ser una clave; es
        # material suplementario del propio trabajo citado —«suppl. figs. S2-S3»,
        # «S1 Data»—, que es notacion estandar en literatura cientifica.
        #
        # Distinguirlos por el ancho es exacto, no heuristico. La version
        # anterior degradaba a aviso cualquier clave desconocida que viniera
        # tras una valida, y eso habria tapado una referencia colgante de
        # verdad: exactamente el fallo que §4.5 existe para impedir.
        for ref in re.findall(r"\bS\d{2,}\b", a["source_ref"] or ""):
            if ref not in claves:
                h.error(f"{a['local_id']}: cita la fuente {ref}, que no está en el apéndice A")
        if a["attribution"].startswith("sintesis") or a["attribution"].startswith("síntesis"):
            for r in a["attribution_refs"]:
                if r not in locales_ref:
                    h.error(f"{a['local_id']}: su síntesis cita {r}, que no existe en el registro")

    # Toda clave que un apéndice cite debe existir en el registro (§4.5).
    locales = locales_ref
    # `entidades` faltaba: sus 1.335 filas citan el registro por su columna `#`
    # (§17 B) y ninguna se comprobaba.
    for coleccion, nombre in ((eventos, "evento"), (hipotesis, "hipótesis"),
                              (fechas, "fecha"), (magnitudes, "magnitud"),
                              (entidades, "entidad")):
        for d in coleccion:
            for celda in d.values():
                if not isinstance(celda, str):
                    continue
                for ref in re.findall(r"\bC-\d+\b", celda):
                    if ref not in locales:
                        h.error(f"{nombre} cita {ref}, que no existe en el registro de afirmaciones")

    return {
        "cutoff": corte.group(1).strip() if corte else None,
        "claims": afirmaciones,
        "sources": fuentes,
        "entities": entidades,
        "events": eventos,
        "hypotheses": hipotesis,
        "dates": fechas,
        "magnitudes": magnitudes,
        "unfiled": no_encajado,
        "labels": sorted(etiquetas),
        "control": control,
    }, h


def main() -> int:
    ap = argparse.ArgumentParser(description="Lee la capa de registro de una investigación")
    ap.add_argument("documento")
    ap.add_argument("--out", default=None, metavar="DIR",
                    help="escribir el resultado intermedio en un directorio")
    args = ap.parse_args()

    path = Path(args.documento)
    if not path.exists():
        print(f"ERROR no existe: {path}")
        return 1

    datos, h = parse(path)

    print(f"{path.name}")
    print(f"  corte bibliográfico  {datos['cutoff'] or 'NO DECLARADO'}")
    print(f"  afirmaciones         {len(datos['claims'])}")
    print(f"  fuentes              {len(datos['sources'])}")
    print(f"  entidades declaradas {len(datos['entities'])}")
    print(f"  eventos              {len(datos['events'])}")
    print(f"  hipótesis            {len(datos['hypotheses'])}")
    print(f"  fechas               {len(datos['dates'])}")
    print(f"  magnitudes           {len(datos['magnitudes'])}")
    print(f"  etiquetas distintas  {len(datos['labels'])}")

    reparto: dict[str, int] = {}
    for c in datos["claims"]:
        reparto[c["attribution"]] = reparto.get(c["attribution"], 0) + 1
    if reparto:
        print("  atribución           " + " · ".join(f"{k} {v}" for k, v in sorted(reparto.items())))
        expresas = reparto.get("expresa", 0)
        if datos["claims"] and expresas / len(datos["claims"]) < 0.6:
            h.aviso(f"sólo el {expresas * 100 // len(datos['claims'])} % de las filas son 'expresa'; "
                    "el prompt dice que debería ser la mayoría del documento")

    print()
    for e in h.errores:
        print(f"ERROR   {e}")
    for a in h.avisos:
        print(f"AVISO   {a}")
    print(f"\n{len(h.errores)} errores de conformidad, {len(h.avisos)} avisos")

    if args.out:
        d = Path(args.out)
        d.mkdir(parents=True, exist_ok=True)
        (d / "parsed.json").write_text(
            json.dumps(datos, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"\nresultado intermedio en {d / 'parsed.json'}")
        print("Las etiquetas NO se han convertido en entidades: eso es el paso 5 de §17")
        print("y es juicio humano. Revísalas antes de generar el delta.")

    return 1 if h.errores else 0


if __name__ == "__main__":
    sys.exit(main())
