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


def parse(path: Path) -> tuple[dict, Hallazgos]:
    texto = path.read_text(encoding="utf-8")
    h = Hallazgos()

    corte = re.search(r"[Ff]echa de corte bibliográfico[:\s]*\**\s*([0-9]{4}-[0-9]{2}-[0-9]{2})", texto)
    if not corte:
        corte = re.search(r"[Cc]orte bibliográfico[:\s]*\**\s*([^\n*]{4,40})", texto)
    if not corte:
        h.error("no se declara fecha de corte bibliográfico; el prompt la exige al principio")

    afirmaciones: list[dict] = []
    fuentes: list[dict] = []
    entidades: list[dict] = []
    control: dict[str, str] = {}
    etiquetas: set[str] = set()

    for cab, filas in tablas(texto):
        if es_registro(cab):
            comprobar_registro(cab, h)
            idx = {c: i for i, c in enumerate(cab)}

            def col(f: list[str], nombre: str) -> str:
                i = idx.get(nombre)
                return f[i].strip() if i is not None and i < len(f) else ""

            for f in filas:
                num = col(f, "#")
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
        elif cab and cab[0].lower() == "clave":
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
            for f in filas:
                entidades.append(dict(zip(cab, f)))
        elif cab and cab[0].lower() == "magnitud":
            for f in filas:
                if len(f) >= 2:
                    control[f[0]] = f[1]

    if not afirmaciones:
        h.error("no se encontró ninguna tabla de registro de afirmaciones")
    if not fuentes:
        h.error("no se encontró el apéndice A de fuentes")

    # El recuento de control es un autoinforme: comprobarlo es barato y detecta
    # que el documento se generó por partes o se truncó.
    if control:
        pares = [("filas del registro", len(afirmaciones)), ("fuentes distintas", len(fuentes))]
        for etiqueta, real in pares:
            declarado = next((v for k, v in control.items() if etiqueta in k.lower()), None)
            if declarado and declarado.strip().isdigit() and int(declarado) != real:
                h.error(f"recuento de control: declara {declarado} en «{etiqueta}» y se cuentan {real}")
    else:
        h.aviso("no se encontró el apéndice H de recuento de control")

    claves = {f["key"] for f in fuentes}
    for a in afirmaciones:
        ref = a["source_ref"].split()[0] if a["source_ref"] else ""
        if ref and ref not in claves and ref not in ("n/a", "-"):
            h.error(f"{a['local_id']}: cita la fuente {ref!r}, que no está en el apéndice A")
        if a["attribution"].startswith("sintesis") or a["attribution"].startswith("síntesis"):
            for r in a["attribution_refs"]:
                if r not in {x["local_id"] for x in afirmaciones}:
                    h.error(f"{a['local_id']}: su síntesis cita {r}, que no existe en el registro")

    return {
        "cutoff": corte.group(1).strip() if corte else None,
        "claims": afirmaciones,
        "sources": fuentes,
        "entities": entidades,
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
