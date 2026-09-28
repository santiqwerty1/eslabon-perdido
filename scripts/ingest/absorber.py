#!/usr/bin/env python3
"""Absorber una versión nueva del corpus en lo ya ingerido (DEC-059).

Una versión nueva del corredor no se ingiere encima de la congelada: se congela
aparte, se compara con la activa y sólo lo que cambió en las secciones ya
ingeridas pide trabajo (DEC-056). Qué hacer con cada cambio es juicio —una fila
corregida puede ser una errata o cambiar el nodo que fecha—, así que se decide
en un fichero de absorción que se revisa, como la conversión se decide en su
fichero (DEC-057). Este script hace lo mecánico.

    informe ANTES DESPUES   qué registros toca cada cambio, y el esqueleto del
                            fichero de absorción con las decisiones en blanco
    construir FICHERO ANTES DESPUES
                            el delta ABS-<commit> desde el fichero revisado: al
                            aplicarlo, la congelación activa pasa a DESPUES

ANTES tiene que ser la congelación activa: el informe cruza el diff con lo que
se ingirió de ella. `informe` no escribe nada en `knowledge/`; deja en
`generated/absorcion/<commit>/` el diff completo, el informe y el esqueleto.

Por sección ingerida, el informe dice:

- cada fila que cambió, con su clase —modificada, retirada, renumerada—, las
  columnas que cambian y los registros que salieron de ella. De cada registro
  dice si esa fila es la primera, porque de la primera salen sus ejes;
- las filas nuevas de la sección, que piden destino como en una conversión;
- las divisiones que declara `data/auditoria/sucesiones_afirmaciones.csv` y
  las filas retiradas que no declaran sucesoras;
- los pasajes cuya prosa cambió o se desplazó, y las menciones y la procedencia
  que dependen de ellos;
- las filas de los apéndices que citan filas ingeridas, y las fuentes del
  apéndice A que ya son registros y el apéndice nuevo describe de otra manera.

La correspondencia de cada fila con sus registros no vive en un fichero aparte:
`corredor.correspondencia()` la reconstruye de los deltas aplicados.

`construir` rehace el informe, exige que el fichero cubra justo sus puntos de
decisión y las ejecuta: conservar, corregir con parches (un enlace cambiado se
rehace en sus dos extremos), retirar, reemplazar, ampliar, dividir, reanclar,
dar mención a las etiquetas nuevas y actualizar o emparejar fuentes. Los
registros nuevos salen de `convertir.generar()`, la misma maquinaria que una
conversión. La prosa, el registro y los pasajes nuevos van a ficheros con
sufijo de versión; los de antes no se tocan. El estado resultante se valida
entero antes de escribir.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "validate"))

import convertir  # noqa: E402
import corredor  # noqa: E402
import freeze  # noqa: E402
import ingest as base  # noqa: E402

GENERATED = base.ROOT / "generated" / "absorcion"
ABSORCIONES = base.CORPUS / "absorptions"
SUCESIONES = "data/auditoria/sucesiones_afirmaciones.csv"
FUENTES = "data/apendices/A_fuentes.csv"
ENTIDADES = "data/apendices/B_entidades.csv"

EJES = ("Aceptación", "Fuerza", "Motivo", "Resolución", "Vigencia")
MENCION_EN_BLANCO = {"mention_type": None, "disposition": None, "targets": [], "reason": None}
QUE_TOCA = {
    "Afirmación": "el enunciado: revisar lo que afirma cada registro",
    "Sujeto": "el sujeto y su mención",
    "Predicado": "el predicado",
    "Objeto": "el objeto y su mención",
    "Atribución": "el origen de la procedencia (expresa, síntesis, glosa)",
    "Fuente": "source_ids, la procedencia y una evidencia por fuente",
    "(sección)": "la fila cambia de sección",
    **{e: "los ejes de los registros cuya primera fila es ésta; en una fila J, la nota de sus evidencias"
       for e in EJES},
}


# ---------------------------------------------------------------------------
# Lo que se ingirió
# ---------------------------------------------------------------------------

def entradas_de_conversion(conversion: dict) -> tuple[dict[str, dict], list[str]]:
    """Por registro convertido, su entrada del fichero de conversión: clave y filas.

    El delta de conversión añade las fuentes nuevas y después los registros del
    fichero, en su orden, así que se emparejan uno a uno. Sin esto no se sabría
    cuál es la primera fila de un registro, que es la que fija sus ejes.
    """
    ruta = base.ROOT / conversion["spec"]["path"]
    if not ruta.exists():
        return {}, [f"{conversion['spec']['path']} no existe: no se sabe la primera fila de cada registro"]
    datos = ruta.read_bytes()
    if convertir.sha256(datos) != conversion["spec"]["sha256"]:
        # Sus filas pueden ser otras que las que se convirtieron: no se usan.
        return {}, [f"{conversion['spec']['path']} cambió después de convertir la sección: "
                    "no se sabe la primera fila de cada registro"]
    entradas = json.loads(datos).get("records", [])
    delta = json.loads((base.DELTAS / conversion["delta"]).read_text(encoding="utf-8"))
    altas = [op for op in delta["operations"]
             if op["operation"] == "ADD_RECORD" and op["file"] != "sources.jsonl"]
    if len(altas) != len(entradas) or any(op["file"] != e["file"] for op, e in zip(altas, entradas)):
        return {}, [f"{conversion['delta']} no sigue el orden de su fichero de conversión: "
                    "no se sabe la primera fila de cada registro"]
    return {op["record_id"]: e for op, e in zip(altas, entradas)}, []


def filas_de_registros(s: dict) -> tuple[dict[str, list[str]], list[str]]:
    """De qué filas sale cada registro de una sección, en su orden, y los avisos.

    La primera fila fija sus ejes. Tras una absorción lo dice su delta, con los
    números de la versión absorbida; antes, el fichero de conversión.
    """
    if s.get("record_rows") is not None:
        return {rid: list(filas) for rid, filas in s["record_rows"].items()}, []
    if not s["conversion"]:
        return {}, []
    entradas, avisos = entradas_de_conversion(s["conversion"])
    return {rid: list(e.get("rows") or []) for rid, e in entradas.items()}, avisos


def pasajes_vigentes(s: dict) -> Path:
    """El fichero de los pasajes vigentes de una sección: el de su ingestión o su última absorción."""
    return base.PASSAGES / Path(s["files"]["passages"]).name


def leer_sucesiones(raiz: Path) -> dict[str, list[str]]:
    ruta = raiz / SUCESIONES
    if not ruta.exists():
        return {}
    _, filas = freeze.leer_csv(ruta)
    return {f["fila_retirada"].strip(): [x.strip() for x in f["filas_sustitutas"].split(";") if x.strip()]
            for f in filas if (f.get("fila_retirada") or "").strip()}


# ---------------------------------------------------------------------------
# Pasajes
# ---------------------------------------------------------------------------

def pasajes_cambiados(viejos: list[dict], texto: str) -> list[dict]:
    """Los pasajes de la versión anterior frente a los párrafos de la nueva.

    Se alinean por texto. Un pasaje igual en otro sitio está desplazado: sus
    menciones siguen valiendo, pero sus offsets no. Si en un tramo cambian tantos
    párrafos como había, se emparejan como cambiados; si no, se declaran
    retirados y nuevos, sin adivinar.
    """
    nuevos = base.segmentar(texto)
    sm = difflib.SequenceMatcher(a=[p["text"] for p in viejos], b=[c for _, _, c in nuevos], autojunk=False)
    salida = []

    def uno(estado: str, i: int | None, j: int | None) -> dict:
        return {"estado": estado,
                "antes": viejos[i]["id"] if i is not None else None,
                "texto_antes": viejos[i]["text"] if i is not None else None,
                "ordinal": j + 1 if j is not None else None,
                "texto": nuevos[j][2] if j is not None else None,
                "offsets": [nuevos[j][0], nuevos[j][1]] if j is not None else None}

    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for i, j in zip(range(i1, i2), range(j1, j2)):
                o = viejos[i]["character_offsets"]
                salida.append(uno("igual" if [o["start"], o["end"]] == [nuevos[j][0], nuevos[j][1]]
                                  else "desplazado", i, j))
        elif tag == "replace" and i2 - i1 == j2 - j1:
            salida += [uno("cambiado", i, j) for i, j in zip(range(i1, i2), range(j1, j2))]
        else:
            salida += [uno("retirado", i, None) for i in range(i1, i2)]
            salida += [uno("nuevo", None, j) for j in range(j1, j2)]
    return salida


def registros_actuales() -> dict[str, tuple[str, dict]]:
    """El libro mayor tal como está, sin superponer los deltas pendientes.

    `convertir.proyeccion()` los superpone porque convierte encima de ellos; el
    informe compara con lo aplicado, igual que `corredor.correspondencia()`.
    """
    salida = {}
    for ruta in sorted(base.RECORDS.glob("*.jsonl")):
        for r in convertir.registros(ruta.name):
            if isinstance(r.get("id"), str):
                salida[r["id"]] = (ruta.name, r)
    return salida


def anclaje_nuevo(raiz: Path, parrafos: list[tuple[int, int, str]], filas: list[str]) -> dict[str, tuple[list, str]]:
    """De qué párrafo de la prosa nueva colgaría cada fila, con la regla de la ingestión.

    Una tabla de síntesis o el índice de tablas pueden cambiar de qué párrafo
    cuelga una fila sin tocar la fila ni la prosa.
    """
    citadas = {n: corredor.citas(c) for n, (_, _, c) in enumerate(parrafos, 1)}
    marcadores = {}
    for n, (_, _, c) in enumerate(parrafos, 1):
        for tid in corredor.MARCADOR.findall(c):
            marcadores[tid] = n
    ruta_indice = raiz / "data" / "table_index.json"
    entradas = json.loads(ruta_indice.read_text(encoding="utf-8")).get("tables", []) if ruta_indice.exists() else []
    # Las mismas negativas que corredor.construir: con un id repetido o un
    # marcador sin entrada, la procedencia saldría de una elección que nadie hizo.
    repetidos = sorted({e["id"] for e in entradas if sum(1 for x in entradas if x["id"] == e["id"]) > 1})
    if repetidos:
        raise SystemExit(f"ERROR data/table_index.json repite identificadores: {', '.join(repetidos)}")
    indice = {t["id"]: t for t in entradas}
    sin_indice = sorted(tid for tid in marcadores if tid not in indice)
    if sin_indice:
        raise SystemExit("ERROR la prosa nueva inserta tablas que no están en data/table_index.json: "
                         + ", ".join(sin_indice))

    canonicos = {f["path"] for f in freeze.ficheros(raiz)}

    def leer(relativa: str) -> str:
        # Sólo ficheros de la capa canónica de la versión comparada: la ingestión
        # rechaza cualquier otro (corredor.construir), y un fichero de fuera
        # cambiaría el informe sin cambiar la huella.
        ruta = (raiz / relativa).resolve()
        try:
            rel = ruta.relative_to(raiz.resolve()).as_posix()
        except ValueError:
            rel = None
        if rel not in canonicos:
            raise SystemExit(f"ERROR data/table_index.json apunta a {relativa!r}, que no es un fichero de la "
                             "capa canónica de la versión nueva")
        return ruta.read_text(encoding="utf-8")

    return corredor.anclar(filas, citadas, marcadores, indice, leer) if citadas else {}


def aparece(etiqueta: str, texto: str) -> bool:
    return re.search(r"(?<!\w)" + re.escape(etiqueta) + r"(?!\w)", texto, re.IGNORECASE) is not None


# ---------------------------------------------------------------------------
# Informe
# ---------------------------------------------------------------------------

def informe(anterior: str, nueva: str) -> dict:
    return informe_de(freeze.abrir(anterior), freeze.abrir(nueva))


def informe_de(a: freeze.Fuente, b: freeze.Fuente) -> dict:
    ruta, activa = corredor.congelacion(None)
    corredor.verificar(a, ruta, activa)
    dif = freeze.diferencia(a, b)
    af = dif["afirmaciones"]

    mapa = {x["de"]: x["a"] for x in af["correspondencia"]}
    retiradas = {x["id"] for x in af["retiradas"]}
    traduccion = {**mapa, **{i: f"{i}[retirada]" for i in retiradas}}
    inverso = {j: i for i, j in mapa.items()}
    modificadas = {m["de"]: m for m in af["modificadas"]}
    filas_a, filas_b = freeze.leer_afirmaciones(a.base), freeze.leer_afirmaciones(b.base)
    sucesiones = leer_sucesiones(b.base)
    # El registro de sucesiones de antes, con los números de ahora: lo que
    # cambia en él pide decisión aunque la fila no cambie. Una sucesora que se
    # retiró queda marcada: su número puede ser ahora el de otra afirmación. La
    # clave no, porque nombra justamente la fila retirada.
    sucesiones_antes = {mapa.get(k, k): [traduccion.get(x, x) for x in v]
                        for k, v in leer_sucesiones(a.base).items()}
    sucesion_cambia = {k for k in set(sucesiones_antes) | set(sucesiones)
                       if sucesiones_antes.get(k) != sucesiones.get(k)}
    proy = registros_actuales()
    secciones = corredor.correspondencia()
    avisos: list[str] = []

    manifiesto = json.loads(base.MANIFEST.read_text(encoding="utf-8")) if base.MANIFEST.exists() else {}
    pendientes = base.revision_siguiente(manifiesto)[2]
    if pendientes:
        avisos.append(f"hay deltas sin aplicar ({', '.join(pendientes)}): el informe sólo ve lo aplicado")

    # Toda fila ingerida, de cualquier sección: las citas de los apéndices se
    # cruzan con ellas.
    fila_de: dict[str, tuple[str, dict]] = {c: (sec, o) for sec, s in secciones.items() for c, o in s["rows"].items()}
    menciones = {rid: r for rid, (f, r) in proy.items()
                 if f == "mentions.jsonl" and r.get("record_status", "active") == "active"}

    salida_secciones = {}
    for sec, s in sorted(secciones.items()):
        de_registro, av = filas_de_registros(s)
        avisos += av
        primera = {rid: filas_r[0] for rid, filas_r in de_registro.items() if filas_r}
        filas, sin_cambios = [], 0
        for c in sorted(s["rows"], key=freeze._num):
            o = s["rows"][c]
            if c in retiradas:
                clase = "retirada"
            elif c in modificadas:
                clase = "modificada"
            elif mapa.get(c) != c:
                clase = "renumerada"
            else:
                sin_cambios += 1
                continue
            columnas = modificadas.get(c, {}).get("columnas", {})
            fila = {
                "row": c, "class": clase, "to": mapa.get(c), "via": modificadas.get(c, {}).get("via"),
                "destination": o["destination"], "record_ids": o["record_ids"],
                "first_row_of": [r for r in o["record_ids"] if primera.get(r) == c],
                "columns": columnas,
                "touches": sorted({QUE_TOCA.get(col, col) for col in columnas}),
            }
            # El registro de la versión nueva usa los números nuevos. Si cambió
            # para esta fila, va también lo de antes: una sucesión borrada o
            # sustituida no puede desaparecer del informe.
            clave = mapa.get(c, c)
            if clave in sucesion_cambia:
                fila["successors_before"] = sucesiones_antes.get(clave, [])
            if clave in sucesiones:
                fila["successors"] = sucesiones[clave]
            elif fila.get("successors_before"):
                fila["aviso"] = ("el registro de sucesiones le quita sus sucesoras (antes: "
                                 + ", ".join(fila["successors_before"]) + ")")
            elif clase == "retirada":
                fila["aviso"] = "retirada sin sucesoras en sucesiones_afirmaciones.csv"
            elif (columnas.get("Vigencia") or ["", ""])[1].strip().lower() == "superada":
                fila["aviso"] = "pasa a vigencia superada sin sucesoras declaradas"
            filas.append(fila)

        # Sucesiones que cambian en el registro sin que cambie la fila.
        reportadas = {f["row"] for f in filas}
        sucesiones_s = {c: {"to": mapa.get(c, c), "before": sucesiones_antes.get(mapa.get(c, c), []),
                            "after": sucesiones.get(mapa.get(c, c), [])}
                        for c in sorted(s["rows"], key=freeze._num)
                        if mapa.get(c, c) in sucesion_cambia and c not in reportadas}

        # Filas que entran en la sección: nuevas, o que vienen de otra.
        nuevas = [n["id"] for n in af["nuevas"] if n["seccion"] == sec]
        nuevas += [m["a"] for m in af["modificadas"] if m["seccion"] == sec and m["de"] not in s["rows"]]
        nuevas_l = [{"row": n, "statement": filas_b[n][1].get("Afirmación", ""),
                     "successor_of": sorted(v for v, suc in sucesiones.items() if n in suc)}
                    for n in sorted(set(nuevas), key=freeze._num)]

        # Pasajes y menciones.
        pasajes, afectadas_m, procedencia = [], [], {}
        filas_de_mencion = defaultdict(list)
        for c, o in s["rows"].items():
            for mid in o["mention_ids"]:
                filas_de_mencion[mid].append(c)
        viejos_p = pasajes_vigentes(s)
        # La misma búsqueda que la ingestión: con dos prosas para la sección, la
        # ingestión se negaría, y el informe no puede elegir una.
        prosas = corredor.prosas_de_seccion(b.base, sec)
        if len(prosas) > 1:
            raise SystemExit(f"ERROR la sección {sec} tiene {len(prosas)} ficheros de prosa en docs/secciones/ "
                             "de la versión nueva; se esperaba uno")
        prosa_b = prosas[0] if prosas else None
        if prosa_b is None:
            avisos.append(f"la sección {sec} no tiene prosa en la versión nueva")
        if viejos_p.exists():
            # Sin prosa nueva, todos sus pasajes quedan retirados: sus menciones
            # y la procedencia de sus filas piden decisión igual.
            viejos = json.loads(viejos_p.read_text(encoding="utf-8"))
            texto_b = prosa_b.read_text(encoding="utf-8") if prosa_b is not None else ""
            parrafos = base.segmentar(texto_b)
            todos = pasajes_cambiados(viejos, texto_b)
            pasajes = [p for p in todos if p["estado"] != "igual"]
            por_antes = {p["antes"]: p for p in pasajes if p["antes"]}
            alineado = {p["antes"]: p["ordinal"] for p in todos if p["antes"] and p["ordinal"]}
            # Dónde cita la prosa nueva cada fila: ahí se reanclaría lo que
            # colgaba de un pasaje que cambió o desapareció.
            citada_en = defaultdict(list)
            for n, (_, _, cuerpo) in enumerate(parrafos, 1):
                for c in corredor.citas(cuerpo):
                    citada_en[c].append(n)
            anclaje = anclaje_nuevo(b.base, parrafos,
                                    sorted((i for i, (sv, _) in filas_b.items() if sv == sec), key=freeze._num))
            for mid, m in sorted(menciones.items()):
                p = por_antes.get(m.get("passage_id"))
                if m.get("section_id") != s["section_id"] or not p:
                    continue
                antes = aparece(m["original_text"], p["texto_antes"] or "")
                if p["estado"] == "desplazado":
                    que = "offsets desplazados: se reancla sin decidir nada"
                elif p["estado"] == "retirado":
                    que = "su pasaje desaparece"
                elif not antes:
                    que = ("su pasaje cambió; la etiqueta no aparecía literal y "
                           + ("ahora sí aparece" if aparece(m["original_text"], p["texto"]) else "sigue sin aparecer"))
                elif aparece(m["original_text"], p["texto"]):
                    que = "su pasaje cambió; la etiqueta sigue en él"
                else:
                    que = "su pasaje cambió y la etiqueta ya no aparece en él"
                # La prosa nueva cita las filas por su número nuevo.
                destino = sorted({n for c in filas_de_mencion.get(mid, []) for n in citada_en.get(mapa.get(c, c), [])})
                if p["estado"] != "desplazado":
                    que += (f"; su fila se cita ahora en el párrafo {', '.join(map(str, destino))}" if destino
                            else "; su fila no se cita en la prosa nueva")
                afectadas_m.append({"mention": mid, "label": m["original_text"], "passage": m["passage_id"],
                                    "state": p["estado"], "what": que, "cited_in": destino})
            # Al ingerirla ahora, ¿de qué párrafos colgaría cada fila, y por qué
            # vía? La prosa, una tabla de síntesis o el índice pueden cambiarlo.
            # Pide juicio si cambia la vía o si deja de colgar de un párrafo del
            # que colgaba: lo que decían sus registros venía de ahí. Si los
            # párrafos sólo se mueven, se reescriben en su sitio o se le suman
            # otros que también la citan, reanclarla es mecánico.
            for c, o in s["rows"].items():
                if c in retiradas:
                    continue
                parrafos_n, via_n = anclaje.get(mapa.get(c, c), ([], None))
                pierde = [pid for pid in o["passage_ids"] if alineado.get(pid, -1) not in parrafos_n]
                gana = sorted(set(parrafos_n) - {alineado.get(pid) for pid in o["passage_ids"]})
                juicio = via_n != o["via"] or bool(pierde)
                tocados = [pid for pid in o["passage_ids"] if pid in por_antes]
                if juicio or ((tocados or gana) and (o["record_ids"] or o["mention_ids"])):
                    procedencia[c] = {"passages": o["passage_ids"], "record_ids": o["record_ids"],
                                      "mention_ids": o["mention_ids"], "mechanical": not juicio,
                                      "via_before": o["via"], "via_after": via_n, "paragraphs_after": parrafos_n,
                                      "loses": pierde, "gains": gana}

        # Etiquetas que la versión nueva introduce: las de las columnas que
        # cambian en una fila modificada y las de una fila nueva. Cada una pide
        # una mención, en la primera fila que la usa, como al ingerir; lo que no
        # nombra nada —un hueco, una cifra— no la pide.
        etiquetas = {m["original_text"] for m in menciones.values() if m.get("section_id") == s["section_id"]}
        por_fila = {f["to"]: f for f in filas if f["to"]}
        por_nueva = {n["row"]: n for n in nuevas_l}
        for c in sorted(set(por_fila) | set(por_nueva), key=freeze._num):
            f = por_fila.get(c)
            for col in ("Sujeto", "Objeto"):
                if f is not None and col not in f["columns"]:
                    continue
                nueva_et = (filas_b[c][1].get(col) or "").strip()
                if nueva_et and not corredor.descartable(nueva_et) and nueva_et not in etiquetas:
                    (f if f is not None else por_nueva[c]).setdefault("new_labels", []).append(nueva_et)
                    etiquetas.add(nueva_et)

        salida_secciones[sec] = {
            "section_id": s["section_id"], "converted": s["conversion"] is not None,
            "unchanged": sin_cambios, "rows": filas, "new_rows": nuevas_l,
            "passages": pasajes, "mentions": afectadas_m, "provenance": procedencia,
            "successions": sucesiones_s,
        }
        if s["conversion"] is None:
            avisos.append(f"la sección {sec} está ingerida pero sin convertir: se absorbe sólo su ingestión")

    # --- apéndices -----------------------------------------------------------
    apendices, fuentes, entidades = [], [], []
    existentes_src = {r.get("citation_key"): (rid, r) for rid, (f, r) in proy.items()
                      if f == "sources.jsonl" and r.get("citation_key")}
    for ruta_r in sorted(dif["registros"]):
        pa, pb = a.base / ruta_r, b.base / ruta_r
        cab = (freeze.leer_csv(pb)[0] if pb.exists() else freeze.leer_csv(pa)[0])
        _, cambios = freeze.cambios_de_registro(pa if pa.exists() else None, pb if pb.exists() else None,
                                                traduccion)
        for ch in cambios:
            viejas = {x for v in (ch["antes"] or {}).values() for x in freeze.C_REF.findall(v)}
            # Una cita nueva sólo es de una fila ingerida si tiene antecesora: una
            # fila nueva puede reutilizar un número que otra dejó al renumerarse.
            citas_n = {x for v in (ch["despues"] or {}).values() for x in freeze.C_REF.findall(v)}
            nuevas_c = {inverso[x] for x in citas_n if x in inverso}
            ingeridas = sorted((viejas | nuevas_c) & fila_de.keys(), key=freeze._num)
            # Las que no tienen antecesora son filas nuevas: si son de una sección
            # ingerida, el cambio del apéndice va con ellas, sin registros viejos.
            filas_nuevas = sorted((x for x in citas_n if x not in inverso
                                   and filas_b.get(x, (None,))[0] in secciones), key=freeze._num)
            clave = ch["clave"] if ch["clave"] is not None else next(iter((ch["antes"] or ch["despues"]).values()))
            if ruta_r == FUENTES and ch["clave"] in existentes_src:
                rid, previa = existentes_src[ch["clave"]]
                col_doi = next((c for c in cab if c.strip().lower().startswith("doi")), "")
                candidatas = []
                if ch["despues"] is None:
                    cambia = ["retirada del apéndice A"]
                    # Si sólo cambió de clave, sale como una retirada y una nueva:
                    # se proponen las filas nuevas con el mismo DOI o el mismo título.
                    vieja = convertir.fuente_de_apendice(ch["antes"], col_doi)

                    def misma(n: dict) -> bool:
                        return bool((n["doi"] and n["doi"] == vieja["doi"])
                                    or (n["title"] and n["title"].casefold() == vieja["title"].casefold()))
                    candidatas = sorted(x["clave"] for x in cambios
                                        if x["estado"] == "nueva" and x["clave"] not in existentes_src
                                        and misma(convertir.fuente_de_apendice(x["despues"], col_doi)))
                else:
                    # Todo lo que el registro guarda del apéndice, no sólo la
                    # bibliografía: también las notas de calidad y la fecha de
                    # consulta. La verificación y el estado son de este proyecto.
                    nueva_f = convertir.fuente_de_apendice(ch["despues"], col_doi)
                    cambia = [k for k in nueva_f if k not in ("verification_status", "record_status")
                              and previa.get(k) != nueva_f[k]]
                fuentes.append({"key": ch["clave"], "record_id": rid, "state": ch["estado"], "fields": cambia,
                                "candidates": candidatas})
            if ruta_r == ENTIDADES:
                # Una entidad se ingiere con la sección de su primera fila. Si esa
                # fila cambia, cuentan las dos: la de antes pierde la entidad y la
                # de ahora la gana, aunque todavía no tenga mención.
                etiqueta = ((ch["antes"] or ch["despues"]).get("etiqueta preferida") or "").strip()
                # Las columnas de las dos versiones, con las citas de antes ya
                # renumeradas: una columna nueva cuenta donde tiene valor, y una
                # cita sólo renumerada no es un cambio.
                cols = []
                if ch["antes"] and ch["despues"]:
                    antes_t = {k: freeze.traducir(v, traduccion) for k, v in ch["antes"].items()}
                    cols = sorted(k for k in set(antes_t) | set(ch["despues"])
                                  if (antes_t.get(k) or "") != (ch["despues"].get(k) or ""))
                    if not cols:
                        continue
                # Por sección: la primera fila de antes (número viejo) y la de
                # ahora (número nuevo). Si las dos son de la misma sección, van
                # juntas y no se pierde ninguna.
                lados: dict[str, dict] = {}
                if ch["antes"]:
                    fila_v = (ch["antes"].get(corredor.COL_PRIMERA) or "").strip()
                    if fila_v in fila_de:
                        lados.setdefault(fila_de[fila_v][0], {})["antes"] = fila_v
                if ch["despues"]:
                    fila_n = (ch["despues"].get(corredor.COL_PRIMERA) or "").strip()
                    vieja = inverso.get(fila_n)
                    sec_n = fila_de[vieja][0] if vieja in fila_de else filas_b.get(fila_n, (None,))[0]
                    if sec_n in secciones:
                        lados.setdefault(sec_n, {})["despues"] = fila_n
                for sec_e, filas_e in sorted(lados.items()):
                    lado = "ambos" if len(filas_e) == 2 else next(iter(filas_e))
                    mids = sorted(mid for mid, m in menciones.items()
                                  if m.get("section_id") == secciones[sec_e]["section_id"]
                                  and m.get("original_text") == etiqueta)
                    # Sus registros, de la fila de antes o, si no la hay, de la
                    # antecesora de la de ahora.
                    origen = filas_e.get("antes") or inverso.get(filas_e.get("despues"))
                    entidades.append({"label": etiqueta, "state": ch["estado"], "section": sec_e, "side": lado,
                                      "mention_ids": mids, "columns": cols,
                                      "row_before": filas_e.get("antes"), "row_after": filas_e.get("despues"),
                                      # ¿Otra fila, o la misma con otro número?
                                      "moves": lado == "ambos" and inverso.get(filas_e["despues"]) != filas_e["antes"],
                                      "record_ids": fila_de[origen][1]["record_ids"] if origen in fila_de else []})
                continue
            if ingeridas or filas_nuevas:
                apendices.append({
                    "path": ruta_r, "key": clave, "state": ch["estado"], "rows": ingeridas,
                    "new_rows": filas_nuevas,
                    "record_ids": sorted({r for c in ingeridas for r in fila_de[c][1]["record_ids"]}),
                    "sections": sorted({fila_de[c][0] for c in ingeridas} | {filas_b[x][0] for x in filas_nuevas}),
                })

    # --- borradores de conversión anclados a la congelación activa -------------
    convertidos = {s["conversion"]["spec"]["path"] for s in secciones.values() if s["conversion"]}
    borradores = []
    for p in sorted(convertir.CONVERSIONS.glob("*.json")):
        try:
            spec = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        rel = corredor._rel(p)
        if rel in convertidos or (spec.get("freeze") or {}).get("fingerprint") != activa["fingerprint"]:
            continue
        sec_b = spec.get("section")
        # Una renumeración también deja el borrador desfasado: sus claves de
        # fila y los `rows` de sus registros siguen con el número viejo.
        # Una fila que cambia de sección desfasa los dos borradores: el de su
        # sección vieja la tiene con su número viejo, el de la nueva la necesita
        # con el nuevo.
        cambiadas = sorted({*(m["de"] for m in af["modificadas"] if filas_a.get(m["de"], (None,))[0] == sec_b),
                            *(m["a"] for m in af["modificadas"]
                              if m["seccion"] == sec_b and filas_a.get(m["de"], (None,))[0] != sec_b),
                            *(x["id"] for x in (*af["nuevas"], *af["retiradas"]) if x["seccion"] == sec_b),
                            *(x["de"] for x in af["solo_renumeracion"] if filas_a.get(x["de"], (None,))[0] == sec_b)},
                           key=freeze._num)
        borradores.append({"path": rel, "section": sec_b, "changed_rows": cambiadas})

    otras = {sec: c for sec, c in af["secciones_afectadas"].items() if sec not in secciones}
    # Una copia de trabajo con cambios sin confirmar no es su commit: se nombra
    # por su huella, o dos copias distintas compartirían nombre.
    commit_b = b.commit if b.limpia is not False else None
    sufijo = (commit_b or dif["nueva"]["fingerprint"].split(":")[1])[:7]
    return {
        "from": {"path": corredor._rel(Path(ruta)), "fingerprint": activa["fingerprint"],
                 "commit": activa.get("commit"), "version": activa.get("version")},
        "to": {"source": b.etiqueta, "fingerprint": dif["nueva"]["fingerprint"], "commit": commit_b,
               "version": dif["nueva"].get("version"),
               "path": corredor._rel(freeze.MANIFESTS / f"corredor-v{dif['nueva'].get('version') or 'sin-version'}"
                                                         f"-{sufijo}.json")},
        "suffix": sufijo,
        "sections": salida_secciones,
        "sources": fuentes,
        "entities": entidades,
        "appendices": apendices,
        "drafts": borradores,
        "other_sections": otras,
        "warnings": avisos,
        "diff": dif,
    }


def esqueleto(r: dict) -> dict:
    """El fichero de absorción por rellenar: una decisión por cambio, todas en blanco."""
    secciones = {}
    for sec, s in r["sections"].items():
        filas = {}
        for f in s["rows"]:
            e = {"class": f["class"], "to": f["to"], "record_ids": f["record_ids"],
                 "columns": sorted(f["columns"]), "decision": None, "reason": None}
            if "successors" in f:
                e["successors"] = {suc: [] for suc in f["successors"]}
            if "successors_before" in f:
                e["successors_before"] = f["successors_before"]
            # Una etiqueta nueva del sujeto o del objeto pide su mención, con el
            # mismo vocabulario que una conversión.
            if f.get("new_labels"):
                e["new_mentions"] = {et: dict(MENCION_EN_BLANCO) for et in f["new_labels"]}
            filas[f["row"]] = e
        # Aparte de las filas ingeridas: una fila nueva puede ocupar el número
        # que otra dejó al renumerarse o retirarse, y las dos piden decisión.
        nuevas = {n["row"]: {"destination": None, "keys": [], "note": None,
                             **({"successor_of": n["successor_of"]} if n["successor_of"] else {}),
                             **({"new_mentions": {et: dict(MENCION_EN_BLANCO) for et in n["new_labels"]}}
                                if n.get("new_labels") else {})}
                  for n in s["new_rows"]}
        menciones = {m["mention"]: {"label": m["label"], "state": m["state"], "decision": None, "reason": None}
                     for m in s["mentions"] if m["state"] != "desplazado"}
        procedencia = {c: {"record_ids": x["record_ids"], "mention_ids": x["mention_ids"],
                           "via_before": x["via_before"], "via_after": x["via_after"],
                           "paragraphs_after": x["paragraphs_after"], "decision": None, "reason": None}
                       for c, x in s["provenance"].items() if not x["mechanical"]}
        sucesiones = {c: {**x, "decision": None, "reason": None} for c, x in s["successions"].items()}
        if filas or nuevas or menciones or procedencia or sucesiones:
            secciones[sec] = {"section_id": s["section_id"], "rows": filas, "new_rows": nuevas, "records": [],
                              "mentions": menciones, "provenance": procedencia, "successions": sucesiones}
    return {
        "from": {k: r["from"][k] for k in ("path", "fingerprint")},
        "to": {k: r["to"][k] for k in ("path", "fingerprint")},
        "decision": "DEC-059",
        "received_at": None,
        "pairing": {},
        "sections": secciones,
        "sources": {f["key"]: {"record_id": f["record_id"], "fields": f["fields"], "decision": None,
                               **({"candidates": f["candidates"], "pair_with": None} if f["state"] == "retirada" else {})}
                    for f in r["sources"] if f["fields"]},
        # Una entidad puede tocar dos secciones si cambia su primera fila.
        "entities": [{"label": e["label"], "section": e["section"], "side": e["side"],
                      "row_before": e["row_before"], "row_after": e["row_after"],
                      "state": e["state"], "columns": e["columns"], "mention_ids": e["mention_ids"],
                      "decision": None, "reason": None} for e in r["entities"]],
        # Una lista por apéndice: sin clave única (F_magnitudes), dos filas
        # cambiadas pueden empezar igual.
        "appendices": {ruta: [{"key": x["key"], "state": x["state"], "rows": x["rows"], "new_rows": x["new_rows"],
                               "decision": None, "reason": None} for x in r["appendices"] if x["path"] == ruta]
                       for ruta in dict.fromkeys(x["path"] for x in r["appendices"])},
    }


def markdown(r: dict) -> list[str]:
    d = r["diff"]["afirmaciones"]
    lineas = [
        f"# Absorción · {r['from']['version']} ({(r['from']['commit'] or '')[:7]}) → "
        f"{r['to']['version']} ({(r['to']['commit'] or '')[:7] or 'copia de trabajo'})",
        "",
        f"- Congelación activa: `{r['from']['path']}`",
        f"- Versión nueva: {r['to']['source']} · huella `{r['to']['fingerprint']}`",
        f"- Afirmaciones {d['anterior']} → {d['nueva']}: {d['sin_cambios']} sin cambios, "
        f"{len(d['solo_renumeracion'])} sólo renumeradas, {len(d['modificadas'])} modificadas, "
        f"{len(d['nuevas'])} nuevas, {len(d['retiradas'])} retiradas",
        "",
    ]
    for aviso in r["warnings"]:
        lineas.append(f"> **Aviso.** {aviso}")
    if r["warnings"]:
        lineas.append("")

    for sec, s in r["sections"].items():
        estado = "convertida" if s["converted"] else "ingerida, sin convertir"
        lineas += [f"## Sección {sec} · {s['section_id']} ({estado})", ""]
        marcas = d["secciones_afectadas"].get(sec)
        if not (s["rows"] or s["new_rows"] or s["passages"] or s["provenance"] or s["successions"] or marcas):
            lineas += [f"Sin cambios: sus {s['unchanged']} filas y su prosa son las mismas.", ""]
            continue
        lineas.append(f"{s['unchanged']} filas sin cambios.")
        if marcas:
            lineas.append("El diff la marca por " + ", ".join(f"{k} ({n})" for k, n in sorted(marcas.items())) + ".")
        lineas.append("")
        if s["rows"]:
            lineas += ["| Fila | Clase | Columnas | Registros | Primera fila de |", "|---|---|---|---|---|"]
            for f in s["rows"]:
                destino = f"{f['row']} → {f['to']}" if f["to"] and f["to"] != f["row"] else f["row"]
                lineas.append(f"| {destino} | {f['class']} | {', '.join(f['columns']) or '—'} | "
                              f"{', '.join(f['record_ids']) or '—'} | {', '.join(f['first_row_of']) or '—'} |")
            lineas.append("")
            for f in s["rows"]:
                detalle = []
                if f["touches"]:
                    detalle.append("toca " + "; ".join(f["touches"]))
                if f.get("successors"):
                    detalle.append("sucesoras declaradas: " + ", ".join(f["successors"]))
                if f.get("successors_before"):
                    detalle.append("sucesoras antes: " + ", ".join(f["successors_before"]))
                if f.get("aviso"):
                    detalle.append(f["aviso"])
                if f.get("new_labels"):
                    detalle.append("etiquetas nuevas sin mención: " + ", ".join(f"«{x}»" for x in f["new_labels"]))
                if detalle:
                    lineas.append(f"- **{f['row']}**: " + ". ".join(detalle) + ".")
                for col, (antes, despues) in f["columns"].items():
                    lineas += [f"  - {col}", f"    - antes: {antes}", f"    - ahora: {despues}"]
            lineas.append("")
        if s["successions"]:
            lineas += ["Sucesiones que cambian en el registro sin que cambie su fila:", ""]
            for c, x in s["successions"].items():
                lineas.append(f"- {c}: {', '.join(x['before']) or '—'} → {', '.join(x['after']) or '—'}")
            lineas.append("")
        if s["new_rows"]:
            lineas += ["Filas nuevas, que piden destino:", ""]
            for n in s["new_rows"]:
                de = f" (sucede a {', '.join(n['successor_of'])})" if n["successor_of"] else ""
                et = ("; etiquetas nuevas sin mención: " + ", ".join(f"«{x}»" for x in n["new_labels"])
                      if n.get("new_labels") else "")
                lineas.append(f"- {n['row']}{de}: {n['statement']}{et}")
            lineas.append("")
        if s["passages"]:
            cuenta = defaultdict(int)
            for p in s["passages"]:
                cuenta[p["estado"]] += 1
            lineas.append("Pasajes: " + ", ".join(f"{n} {e}" for e, n in sorted(cuenta.items())) + ".")
            decidir = [m for m in s["mentions"] if m["state"] != "desplazado"]
            mecanicas = len(s["mentions"]) - len(decidir)
            if mecanicas:
                lineas.append(f"{mecanicas} menciones sólo cambian de offsets.")
            for m in decidir:
                lineas.append(f"- {m['mention']} «{m['label']}» ({m['passage']}): {m['what']}")
            lineas.append("")
        if s["provenance"]:
            juicio = sorted((c for c, x in s["provenance"].items() if not x["mechanical"]), key=freeze._num)
            mecanica = len(s["provenance"]) - len(juicio)
            if juicio:
                lineas.append("Filas que al ingerirlas ahora dejarían de colgar de un párrafo o cambiarían de vía:")
                for c in juicio:
                    x = s["provenance"][c]
                    via = (f"{x['via_before']} → {x['via_after'] or 'no está en la versión nueva'}"
                           if x["via_after"] != x["via_before"] else x["via_before"])
                    lineas.append(f"- {c}: {via}"
                                  + (f"; deja {', '.join(x['loses'])}" if x["loses"] else "")
                                  + (f"; ahora cuelga del párrafo {', '.join(map(str, x['paragraphs_after']))}"
                                     if x["paragraphs_after"] else "")
                                  + f"; registros {', '.join(x['record_ids']) or '—'}")
            ganan = sum(1 for x in s["provenance"].values() if x["mechanical"] and x["gains"])
            if mecanica:
                lineas.append(f"{mecanica} filas siguen colgando de sus párrafos, que sólo se mueven o se reescriben en "
                              f"su sitio" + (f" ({ganan} ganan además párrafos nuevos que las citan)" if ganan else "")
                              + ": se reanclan sin decidir nada.")
            lineas.append("")

    if r["sources"]:
        lineas += ["## Fuentes del apéndice A que ya son registros", ""]
        for f in r["sources"]:
            que = ", ".join(f["fields"]) if f["fields"] else "nada del registro (sólo columnas que no se ingieren)"
            pareja = (f"; posible clave nueva: {', '.join(f['candidates'])}" if f["candidates"]
                      else "; ninguna fila nueva con su DOI o su título" if f["state"] == "retirada" else "")
            lineas.append(f"- {f['key']} ({f['record_id']}), {f['state']}: cambia {que}{pareja}")
        lineas.append("")
    if r["entities"]:
        lineas += ["## Entidades del apéndice B de secciones ingeridas", ""]
        for e in r["entities"]:
            cols = f" ({', '.join(e['columns'])})" if e["columns"] else ""
            lado = {"antes": "la pierde", "despues": "la gana", "ambos": ""}[e["side"]]
            if e["moves"]:
                lado = f"pasa de {e['row_before']} a {e['row_after']}"
            lineas.append(f"- «{e['label']}», sección {e['section']}{', ' + lado if lado else ''}, {e['state']}{cols}: "
                          + (f"menciones {', '.join(e['mention_ids'])}" if e["mention_ids"]
                             else "sin mención en esta sección: pide una nueva"))
        lineas.append("")
    if r["appendices"]:
        lineas += ["## Filas de los apéndices que citan filas ingeridas", "",
                   "| Apéndice | Clave | Estado | Filas | Registros |", "|---|---|---|---|---|"]
        for x in r["appendices"]:
            clave = str(x["key"])[:60]
            filas = ", ".join([*x["rows"], *(f"{n} (nueva)" for n in x["new_rows"])])
            lineas.append(f"| {Path(x['path']).name} | {clave} | {x['state']} | {filas} | "
                          f"{', '.join(x['record_ids']) or '—'} |")
        lineas.append("")
    if r["drafts"]:
        lineas += ["## Borradores de conversión anclados a la congelación activa", ""]
        for bdr in r["drafts"]:
            lineas.append(f"- `{bdr['path']}` (sección {bdr['section']}): "
                          + (f"cambian {', '.join(bdr['changed_rows'])}" if bdr["changed_rows"]
                             else "su sección no cambia"))
        lineas.append("")
    if r["other_sections"]:
        lineas += ["## Secciones sin ingerir", "",
                   "Se ingerirán desde la versión nueva; no hay nada que absorber en ellas: "
                   + ", ".join(sorted(r["other_sections"])) + ".", ""]
    return lineas


# ---------------------------------------------------------------------------
# Construir el delta de absorción
# ---------------------------------------------------------------------------

# Qué decisión vale en cada punto de decisión.
DECISIONES = {
    "rows": {"conservar", "corregir", "retirar", "ampliar", "reemplazar", "dividir"},
    "mentions": {"reanclar", "retirar"},
    "provenance": {"aceptar", "fijar"},
    "successions": {"conservar", "corregir"},
    "sources": {"actualizar", "conservar"},
    "entities": {"conservar", "corregir", "retirar"},
    "appendices": {"conservar", "corregir"},
}
CON_MOTIVO = {"conservar", "corregir", "retirar", "ampliar", "reemplazar", "dividir"}
# Las decisiones que tocan registros con parches, y las que dan de alta.
CON_PARCHES = {"corregir", "ampliar", "reemplazar", "dividir"}
# Lo que se rellena a mano. Lo demás lo escribió el informe y tiene que seguir
# igual: un fichero rellenado para otro diff no describe éste.
RELLENABLES = {
    "rows": {"decision", "reason", "patches", "new_mentions", "keys", "replaced_by", "successors"},
    "new_rows": {"destination", "keys", "note", "new_mentions"},
    "mentions": {"decision", "reason", "passage"},
    "provenance": {"decision", "reason", "paragraphs"},
    "successions": {"decision", "reason", "patches"},
    "sources": {"decision", "reason", "pair_with"},
    "entities": {"decision", "reason", "patches"},
    "appendices": {"decision", "reason", "patches"},
}
# Enlaces que un parche puede cambiar: el otro lado se rehace solo. Los demás
# se deducen, o son el ciclo de vida del registro, y no se fijan a mano.
ENLACES_REHECHOS = {"subject_id", "object", "supports_claim_ids", "challenges_claim_ids", "analysis_id"}
ENLACES_FIJOS = {"result_ids", "temporal_expression_ids", "temporal_expression_id", "issue_ids", "affects",
                 "superseded_by", "merged_into"}
FECHA = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def revisar(spec: dict, esq: dict) -> list[str]:
    """Lo que falla en un fichero de absorción frente al esqueleto del informe rehecho.

    Tiene que cubrir exactamente sus puntos de decisión, con lo que escribió el
    informe intacto y una decisión válida en cada uno.
    """
    errores: list[str] = []

    def entrada(donde: str, tipo: str, hecho: dict, pedido: dict) -> None:
        if not isinstance(hecho, dict):
            errores.append(f"{donde}: no es un objeto")
            return
        fijos = {k: v for k, v in pedido.items() if k not in RELLENABLES[tipo]}
        puestos = {k: v for k, v in hecho.items() if k not in RELLENABLES[tipo]}
        if fijos != puestos:
            distintos = sorted(k for k in set(fijos) | set(puestos) if fijos.get(k) != puestos.get(k))
            errores.append(f"{donde}: {', '.join(distintos)} no es lo que dice el informe de esta versión")
        nuevas = hecho.get("new_mentions") or {}
        if set(nuevas) != set(pedido.get("new_mentions") or {}):
            errores.append(f"{donde}: `new_mentions` no son las etiquetas nuevas que da el informe")
            nuevas = {}
        if tipo == "new_rows":
            destino = hecho.get("destination")
            if destino is None:
                errores.append(f"{donde}: sin destino")
            elif destino not in convertir.DESTINOS:
                errores.append(f"{donde}: destino {destino!r} fuera de A–J")
            for etiqueta, m in sorted(nuevas.items()):
                errores.extend(f"{donde}, mención nueva «{etiqueta}»: {e}" for e in mencion_mal(m))
            return
        decision = hecho.get("decision")
        if decision is None:
            # Una fila sólo renumerada se arrastra sin decidir nada.
            if not (tipo == "rows" and pedido.get("class") == "renumerada"):
                errores.append(f"{donde}: sin decisión")
        elif decision not in DECISIONES[tipo]:
            errores.append(f"{donde}: decisión «{decision}» desconocida; aquí vale "
                           + ", ".join(sorted(DECISIONES[tipo])))
        motivo = (hecho.get("reason") or "").strip()
        if decision in CON_MOTIVO and not motivo:
            errores.append(f"{donde}: «{decision}» sin `reason`")
        if decision == "corregir" and not hecho.get("patches"):
            errores.append(f"{donde}: «corregir» sin `patches`")
        if decision not in CON_PARCHES and hecho.get("patches"):
            errores.append(f"{donde}: `patches` sólo acompaña a «corregir», «ampliar», «reemplazar» o «dividir»")
        if tipo == "rows":
            clase = pedido.get("class")
            if clase == "retirada" and decision not in (None, "retirar", "conservar", "dividir"):
                errores.append(f"{donde}: la fila ya no está en la versión nueva; se retira, se conserva o se divide")
            if decision == "retirar" and clase != "retirada":
                errores.append(f"{donde}: sólo se retira una fila que la versión nueva retira; los registros de "
                               "una fila que sigue se corrigen o se reemplazan")
            if decision == "ampliar" and not hecho.get("keys"):
                errores.append(f"{donde}: «ampliar» sin `keys`, los registros nuevos de la fila")
            if decision not in ("ampliar", "reemplazar") and hecho.get("keys"):
                errores.append(f"{donde}: `keys` sólo acompaña a «ampliar» o «reemplazar»; los registros de una "
                               "sucesora van en su fila nueva")
            sustitutos = hecho.get("replaced_by") or {}
            if decision == "reemplazar" and not sustitutos:
                errores.append(f"{donde}: «reemplazar» sin `replaced_by`")
            if decision not in ("reemplazar", "dividir") and sustitutos:
                errores.append(f"{donde}: `replaced_by` sólo acompaña a «reemplazar» o «dividir»")
            if not isinstance(sustitutos, dict):
                errores.append(f"{donde}: `replaced_by` va de registro a su sustituto")
                sustitutos = {}
            ajenos = sorted(set(sustitutos) - set(pedido.get("record_ids") or []))
            if ajenos:
                errores.append(f"{donde}: `replaced_by` nombra {', '.join(ajenos)}, que no salió de esta fila")
            pedidas = pedido.get("successors")
            sucesoras = hecho.get("successors")
            if (pedidas is None) != (sucesoras is None) or (pedidas is not None and set(pedidas) != set(sucesoras)):
                errores.append(f"{donde}: `successors` no son las sucesoras que declara el registro de sucesiones")
            elif decision == "dividir":
                if pedidas is None:
                    errores.append(f"{donde}: «dividir» sin sucesoras declaradas en sucesiones_afirmaciones.csv")
                else:
                    repartidos = [rid for v in sucesoras.values() for rid in v] + list(sustitutos)
                    faltan = sorted(set(pedido.get("record_ids") or []) - set(repartidos))
                    dobles = sorted({rid for rid in repartidos if repartidos.count(rid) > 1})
                    extra = sorted(set(repartidos) - set(pedido.get("record_ids") or []))
                    if faltan:
                        errores.append(f"{donde}: {', '.join(faltan)} no se reasigna a ninguna sucesora ni se sustituye")
                    if dobles:
                        errores.append(f"{donde}: {', '.join(dobles)} va a más de un sitio")
                    if extra:
                        errores.append(f"{donde}: {', '.join(extra)} no salió de esta fila")
            elif pedidas is not None and any(sucesoras.values()):
                errores.append(f"{donde}: sólo «dividir» reparte registros entre las sucesoras")
            if decision not in (None, "retirar"):
                for etiqueta, m in sorted(nuevas.items()):
                    errores.extend(f"{donde}, mención nueva «{etiqueta}»: {e}" for e in mencion_mal(m))
        if tipo == "mentions" and hecho.get("passage") is not None and (
                not isinstance(hecho["passage"], int) or decision != "reanclar"):
            errores.append(f"{donde}: `passage` es el número de párrafo al que se reancla")
        if tipo == "provenance":
            parrafos = hecho.get("paragraphs")
            if decision == "fijar" and not (isinstance(parrafos, list) and parrafos
                                             and all(isinstance(n, int) for n in parrafos)):
                errores.append(f"{donde}: «fijar» necesita `paragraphs`, los números de párrafo de la prosa nueva")
            if decision != "fijar" and parrafos:
                errores.append(f"{donde}: `paragraphs` sólo acompaña a «fijar»")
        if tipo == "sources" and hecho.get("pair_with") is not None:
            if pedido.get("candidates") is None:
                errores.append(f"{donde}: `pair_with` sólo empareja una fuente que el apéndice nuevo retira")
            elif decision != "actualizar" or not isinstance(hecho["pair_with"], str):
                errores.append(f"{donde}: `pair_with` es la clave nueva de la fuente, y va con «actualizar»")

    def diccionario(donde: str, tipo: str, hechos, pedidos: dict) -> None:
        hechos = hechos if isinstance(hechos, dict) else {}
        for k in sorted(set(pedidos) - set(hechos)):
            errores.append(f"{donde}: falta {k}")
        for k in sorted(set(hechos) - set(pedidos)):
            errores.append(f"{donde}: {k} no es un cambio de esta versión")
        for k in sorted(set(pedidos) & set(hechos)):
            entrada(f"{donde} {k}", tipo, hechos[k], pedidos[k])

    def lista(donde: str, tipo: str, hechas, pedidas: list) -> None:
        hechas = hechas if isinstance(hechas, list) else []
        if len(hechas) != len(pedidas):
            errores.append(f"{donde}: {len(hechas)} entradas, y el informe da {len(pedidas)}")
            return
        for n, (h, p) in enumerate(zip(hechas, pedidas), 1):
            entrada(f"{donde} #{n}", tipo, h, p)

    secciones = spec.get("sections") if isinstance(spec.get("sections"), dict) else {}
    for sec in sorted(set(esq["sections"]) - set(secciones)):
        errores.append(f"faltan las decisiones de la sección {sec}")
    for sec in sorted(set(secciones) - set(esq["sections"])):
        errores.append(f"la sección {sec} no pide decisiones en esta versión")
    for sec in sorted(set(secciones) & set(esq["sections"])):
        h, e = secciones[sec], esq["sections"][sec]
        if h.get("section_id") != e["section_id"]:
            errores.append(f"sección {sec}: `section_id` no es {e['section_id']}")
        if not isinstance(h.get("records", []), list):
            errores.append(f"sección {sec}: `records` es la lista de registros nuevos")
        for tipo in ("rows", "new_rows", "mentions", "provenance", "successions"):
            diccionario(f"sección {sec}, {tipo}", tipo, h.get(tipo), e[tipo])
    diccionario("sources", "sources", spec.get("sources"), esq["sources"])
    lista("entities", "entities", spec.get("entities"), esq["entities"])
    apendices = spec.get("appendices") if isinstance(spec.get("appendices"), dict) else {}
    for ruta in sorted(set(esq["appendices"]) - set(apendices)):
        errores.append(f"appendices: falta {ruta}")
    for ruta in sorted(set(apendices) - set(esq["appendices"])):
        errores.append(f"appendices: {ruta} no cambia en esta versión")
    for ruta in sorted(set(apendices) & set(esq["appendices"])):
        lista(f"appendices {ruta}", "appendices", apendices[ruta], esq["appendices"][ruta])
    return errores


def mencion_mal(m) -> list[str]:
    """Lo que falla en la decisión sobre una mención nueva: el vocabulario de una conversión."""
    if not isinstance(m, dict):
        return ["no es un objeto"]
    errores = []
    if not m.get("mention_type"):
        errores.append("sin `mention_type`")
    if not m.get("disposition"):
        errores.append("sin `disposition`")
    elif m["disposition"] in convertir.SIN_OBJETIVO:
        if not (m.get("reason") or "").strip():
            errores.append("descartada sin `reason`")
    elif not m.get("targets"):
        errores.append(f"{m['disposition']} sin `targets`")
    raros = [t for t in m.get("targets") or []
             if not (isinstance(t, str) and (convertir.LITERAL.match(t) or convertir.CLAVE.match(t)))]
    if raros:
        errores.append(f"`targets` {', '.join(map(str, raros))} no son identificadores ni claves «@…»")
    return errores


def es_de_localizacion(nota: str) -> bool:
    """Si una nota de mención es de las que escribe corredor.localizar sobre su pasaje."""
    return (nota.startswith("en el pasaje aparece como «")
            or nota == "la etiqueta no aparece literal en el pasaje; los offsets cubren el pasaje entero")


def nota_j(fila: str, datos: dict) -> str:
    """La nota de evaluación de una evidencia de una fila J, como la escribe convertir.py."""
    e = convertir.ejes(datos)
    return (f"Evaluación de la fila {fila} (destino J): acceptance={e['acceptance']}; "
            f"evidence_strength={e['evidence_strength']}"
            + (f" ({e['evidence_strength_reason']})" if e["evidence_strength_reason"] else "")
            + f"; resolution={e['resolution']}; historical_status={e['historical_status']}")


def claves_de_fuente(filas: list[str], datos: dict[str, tuple[str, dict]]) -> list[str]:
    return sorted({k for c in filas for k in convertir.CITA.findall(datos[c][1].get("Fuente", ""))},
                  key=lambda k: int(k[1:]))


def punteros(rec: dict, fichero: str) -> dict[str, set[str]]:
    """Adónde apunta un registro por cada enlace que un parche puede cambiar, por campo de vuelta."""
    salida: dict[str, set[str]] = defaultdict(set)
    if fichero == "claims.jsonl":
        for rid in (rec.get("subject_id"), (rec.get("object") or {}).get("entity_id")):
            if isinstance(rid, str):
                salida["claim_ids"].add(rid)
        t = (rec.get("object") or {}).get("temporal_expression_id")
        if rec.get("predicate") == "dated_to" and isinstance(rec.get("subject_id"), str) and isinstance(t, str):
            salida["temporal_expression_ids"].add(rec["subject_id"])
    if fichero == "evidence.jsonl":
        salida["evidence_ids"] |= set(rec.get("supports_claim_ids") or [])
        salida["counterevidence_ids"] |= set(rec.get("challenges_claim_ids") or [])
    if fichero == "results.jsonl" and isinstance(rec.get("analysis_id"), str):
        salida["result_ids"].add(rec["analysis_id"])
    return salida


def valor_de_vuelta(campo: str, destino: str, estado: dict[str, tuple[str, dict]]) -> list[str]:
    """Lo que dice ahora el estado entero que tiene que haber en `destino[campo]`."""
    if campo == "temporal_expression_ids":
        return [c["object"]["temporal_expression_id"] for f, c in estado.values()
                if f == "claims.jsonl" and c.get("predicate") == "dated_to" and c.get("subject_id") == destino
                and c.get("record_status", "active") == "active"
                and isinstance((c.get("object") or {}).get("temporal_expression_id"), str)]
    return [rid for rid, (f, r) in estado.items() if destino in punteros(r, f).get(campo, set())]


def validar_estado(cambios: dict, altas: list[tuple[str, dict]]) -> list[str]:
    """Los errores de validación que el delta añadiría al libro mayor.

    Se valida el estado entero tal como quedaría, con todas las familias, y se
    compara con el de partida: sólo cuenta lo nuevo, no lo que ya estaba.
    """
    import tempfile
    import validate

    def normal(errores: list[str]) -> set[str]:
        return {re.sub(r":\d+:", ":", e) for e in errores}

    antes = normal(validate.run(list(validate.FAMILY_ORDER), base.RECORDS).errors)
    with tempfile.TemporaryDirectory(prefix="absorcion-") as tmp:
        por_fichero = {p.name: convertir.registros(p.name) for p in sorted(base.RECORDS.glob("*.jsonl"))}
        for rid, (fichero, _, despues) in cambios.items():
            por_fichero[fichero] = [despues if r.get("id") == rid else r for r in por_fichero[fichero]]
        for fichero, rec in altas:
            por_fichero.setdefault(fichero, []).append(rec)
        for fichero, recs in por_fichero.items():
            (Path(tmp) / fichero).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in recs),
                                             encoding="utf-8")
        despues = normal(validate.run(list(validate.FAMILY_ORDER), Path(tmp)).errors)
    return sorted(despues - antes)


def construir(ruta_spec: Path, anterior: str, nueva: str) -> dict:
    """El delta de absorción de un fichero revisado, sin escribir nada.

    Devuelve el delta, las copias y los pasajes que hay que escribir junto a él,
    y lo que dice el informe de la construcción.
    """
    # La entrada revisada queda donde el snapshot la registra, como un fichero
    # de conversión: fuera de ahí, cambiarla o perderla no lo notaría nadie.
    if ruta_spec.resolve().parent != ABSORCIONES.resolve() or ruta_spec.suffix != ".json":
        raise SystemExit(f"ERROR el fichero de absorción tiene que estar en knowledge/corpus/absorptions/ "
                         f"({ruta_spec})")
    spec_bytes = ruta_spec.read_bytes()
    spec = json.loads(spec_bytes)
    try:
        import jsonschema  # noqa: F401
    except ImportError:
        raise SystemExit("ERROR jsonschema no está instalado: absorber.py no escribe un delta sin validarlo "
                         "contra los esquemas (make setup)")

    # --- de dónde parte ---------------------------------------------------------
    manifiesto = json.loads(base.MANIFEST.read_text(encoding="utf-8"))
    rev_antes, rev_despues, pendientes = base.revision_siguiente(manifiesto)
    if pendientes:
        raise SystemExit(f"ERROR hay deltas sin aplicar ({', '.join(pendientes)}): una absorción parte del libro "
                         "mayor aplicado, y se aplica o se retira lo pendiente antes")
    secciones = corredor.correspondencia()
    sin_convertir = sorted(sec for sec, s in secciones.items() if not s["conversion"])
    if sin_convertir:
        raise SystemExit(f"ERROR secciones ingeridas sin convertir: {', '.join(sin_convertir)}. Se convierten "
                         "antes de absorber: su conversión parte de la versión de la que se ingirieron")
    a, b = freeze.abrir(anterior), freeze.abrir(nueva)
    r = informe_de(a, b)

    destino = spec.get("to") if isinstance(spec.get("to"), dict) else {}
    ruta_to = base.ROOT / destino["path"] if destino.get("path") else None
    if ruta_to is None or not ruta_to.exists():
        raise SystemExit(f"ERROR falta la congelación de la versión nueva ({destino.get('path')}): se congela "
                         "antes de absorberla (make corpus-freeze) y su ruta va en `to`")
    congelada = json.loads(ruta_to.read_text(encoding="utf-8"))
    if freeze.huella(congelada["files"]) != congelada.get("fingerprint"):
        raise SystemExit(f"ERROR {destino['path']} es incoherente: su huella no corresponde a sus ficheros")
    if congelada["fingerprint"] != r["to"]["fingerprint"]:
        raise SystemExit(f"ERROR {b.etiqueta} no es la versión congelada en {destino['path']}")
    if destino.get("fingerprint") != congelada["fingerprint"]:
        raise SystemExit(f"ERROR `to` declara la huella {destino.get('fingerprint')}, y {destino['path']} "
                         f"congela {congelada['fingerprint']}")
    if spec.get("from") != {"path": r["from"]["path"], "fingerprint": r["from"]["fingerprint"]}:
        raise SystemExit("ERROR el fichero de absorción parte de otra congelación que la activa "
                         f"({r['from']['path']})")
    if not FECHA.match(str(spec.get("received_at") or "")):
        raise SystemExit("ERROR `received_at` tiene que ser la fecha de la absorción (AAAA-MM-DD): el delta sale "
                         "de ella, no del día en que se construye")
    if spec.get("pairing"):
        raise SystemExit("ERROR `pairing` corrige emparejamientos del diff, y eso todavía no se ejecuta: hoy "
                         "tiene que estar vacío")
    errores = revisar(spec, esqueleto(r))
    if errores:
        raise SystemExit("ERROR el fichero de absorción no cubre esta versión:\n  " + "\n  ".join(errores))
    por_seccion = spec.get("sections") or {}

    af = r["diff"]["afirmaciones"]
    mapa = {x["de"]: x["a"] for x in af["correspondencia"]}
    inverso = {j: i for i, j in mapa.items()}
    modificadas = {m["de"]: m for m in af["modificadas"]}
    filas_a, filas_b = freeze.leer_afirmaciones(a.base), freeze.leer_afirmaciones(b.base)
    proy = registros_actuales()
    suf = r["suffix"]
    avisos = list(r["warnings"])
    cambios: dict[str, list] = {}
    retirados: dict[str, str] = {}
    sustituidos: dict[str, str] = {}
    altas: list[tuple[str, dict]] = []
    ficheros: dict[Path, bytes] = {}
    nuevo = convertir.asignador()
    emitidos: set[str] = set()

    def tocar(rid: str) -> dict:
        if rid not in cambios:
            fichero, antes = proy[rid]
            cambios[rid] = [fichero, antes, json.loads(json.dumps(antes))]
        return cambios[rid][2]

    def retirar(rid: str, motivo: str) -> None:
        rec = tocar(rid)
        rec["record_status"] = "deprecated"
        if "notes" in rec or cambios[rid][0] == "mentions.jsonl":
            rec["notes"] = [*(rec.get("notes") or []), f"absorción {suf}: retirado; {motivo}"]
        retirados[rid] = motivo

    def vigente() -> dict[str, tuple[str, dict]]:
        """El libro mayor como va quedando: lo de partida, lo cambiado y lo nuevo."""
        estado = dict(proy)
        estado.update({rid: (f, despues) for rid, (f, _, despues) in cambios.items()})
        estado.update({rec["id"]: (f, rec) for f, rec in altas})
        return estado

    # --- parches: sólo registros que salieron del corpus, uno por sitio ------------
    derivados = {rid for s in secciones.values() for o in s["rows"].values() for rid in o["record_ids"]}
    parches: dict[str, tuple[str, str | None, dict]] = {}

    def recoger(donde: str, sec: str | None, d: dict) -> None:
        if d.get("decision") not in CON_PARCHES or not d.get("patches"):
            return
        if not isinstance(d["patches"], dict):
            errores.append(f"{donde}: `patches` va de registro a {{campo: valor}}")
            return
        for rid, parche in sorted(d["patches"].items()):
            if not isinstance(parche, dict) or not parche:
                errores.append(f"{donde}: el parche de {rid} tiene que ser un objeto {{campo: valor}} con algo dentro")
                continue
            if rid in parches:
                errores.append(f"{donde}: {rid} ya se corrige en {parches[rid][0]}; un registro se corrige en un sitio")
                continue
            if rid not in proy:
                errores.append(f"{donde}: {rid} no existe")
                continue
            if rid not in derivados:
                errores.append(f"{donde}: {rid} no salió de ninguna fila ingerida; una absorción sólo corrige eso")
                continue
            fichero = proy[rid][0]
            prohibidos = sorted(set(parche) & {*convertir.DERIVADOS, *convertir.DERIVADOS_POR_FICHERO.get(fichero, ())})
            fijos = sorted(set(parche) & ENLACES_FIJOS)
            ajenos = sorted(set(parche) - convertir.propiedades(fichero)) if fichero in convertir.ESQUEMA else []
            if prohibidos:
                errores.append(f"{donde}: {rid}: {', '.join(prohibidos)} se deduce, no se corrige a mano")
            if fijos:
                errores.append(f"{donde}: {rid}: {', '.join(fijos)} se deduce de otros registros o es su ciclo de "
                               "vida; no se fija con un parche")
            if ajenos:
                errores.append(f"{donde}: {rid}: {', '.join(ajenos)} no es un campo de {fichero}")
            parches[rid] = (donde, sec, parche)

    for sec, h in sorted(por_seccion.items()):
        for tipo in ("rows", "successions"):
            for k, d in sorted(h.get(tipo, {}).items()):
                recoger(f"sección {sec}, {tipo} {k}", sec, d)
    for n, d in enumerate(spec.get("entities") or [], 1):
        recoger(f"entities #{n}", None, d)
    for ruta, entradas in sorted((spec.get("appendices") or {}).items()):
        for n, d in enumerate(entradas, 1):
            recoger(f"appendices {ruta} #{n}", None, d)

    # --- menciones que se retiran por su entidad --------------------------------------
    menciones_fuera: dict[str, str] = {}
    for n, e in enumerate(spec.get("entities") or [], 1):
        if e.get("decision") == "retirar":
            for mid in e["mention_ids"]:
                menciones_fuera[mid] = f"la entidad «{e['label']}» sale del apéndice B: {e['reason']}"

    # --- fuentes ----------------------------------------------------------------------------
    fuente_de_clave = {rec.get("citation_key"): rid for rid, (f, rec) in proy.items()
                       if f == "sources.jsonl" and rec.get("citation_key")}
    # Las claves de la versión de antes: con ellas se sabe si las fuentes de un
    # registro salían de sus filas, aunque una fuente cambie de clave.
    fuente_de_clave_antes = dict(fuente_de_clave)
    cab, filas_ap = freeze.leer_csv(b.base / FUENTES) if (b.base / FUENTES).exists() else ([], [])
    col_doi = next((c for c in cab if c.strip().lower().startswith("doi")), "")
    apendice_a = {f["clave"].strip(): f for f in filas_ap if (f.get("clave") or "").strip()}

    def fuente(clave: str, donde: str) -> str | None:
        if clave in fuente_de_clave:
            return fuente_de_clave[clave]
        if clave not in apendice_a:
            errores.append(f"{donde}: cita {clave}, que el apéndice A de la versión nueva no tiene")
            return None
        rid = nuevo("SRC")
        altas.append(("sources.jsonl", {"id": rid, **convertir.fuente_de_apendice(apendice_a[clave], col_doi)}))
        fuente_de_clave[clave] = rid
        return rid

    for clave, d in sorted((spec.get("sources") or {}).items()):
        if d.get("decision") != "actualizar":
            continue
        # Una fuente que sólo cambió de clave se empareja con su fila nueva: el
        # registro es el mismo y pasa a citarse por la clave nueva.
        pareja = d.get("pair_with")
        nueva_clave = pareja or clave
        if pareja is not None:
            if pareja in fuente_de_clave:
                errores.append(f"sources {clave}: {pareja} ya es la clave de {fuente_de_clave[pareja]}")
                continue
        if nueva_clave not in apendice_a:
            errores.append(f"sources {clave}: el apéndice A de la versión nueva no tiene {nueva_clave}; no hay "
                           "con qué actualizarla")
            continue
        rec = tocar(d["record_id"])
        for k, v in convertir.fuente_de_apendice(apendice_a[nueva_clave], col_doi).items():
            if k not in ("verification_status", "record_status"):
                rec[k] = v
        if pareja is not None:
            fuente_de_clave.pop(clave, None)
            fuente_de_clave[pareja] = d["record_id"]

    # --- secciones ----------------------------------------------------------------------------
    siguiente_pasaje = base.siguiente_libre("PASSAGE", base.ids_de_pasajes())
    siguiente_mencion = base.siguiente_libre("MENTION", base.ids_en_uso("mentions.jsonl", "MENTION")
                                             | base.reservados_por_deltas("MENTION"))
    bloque: dict[str, dict] = {}
    resumen: dict[str, dict] = {}
    ids_de: dict[str, dict[str, str]] = {}
    pendientes_sust: list[tuple[str, str, str, str]] = []
    for sec, s in sorted(secciones.items()):
        sid = s["section_id"]
        h = por_seccion.get(sec, {})
        filas_h = h.get("rows", {})
        nuevas_h = h.get("new_rows", {})
        propias = sorted((c for c, (sv, _) in filas_b.items() if sv == sec), key=freeze._num)
        # Una fila que cambia de sección se lleva sus registros a otra: eso es
        # rehacer dos secciones a la vez, y todavía no se ejecuta.
        for c in propias:
            if c in inverso and inverso[c] not in s["rows"]:
                errores.append(f"{c} llega a la sección {sec} desde otra ({inverso[c]}); mover filas entre "
                               "secciones todavía no se ejecuta")
        for c in s["rows"]:
            if c in mapa and filas_b[mapa[c]][0] != sec:
                errores.append(f"{c} deja la sección {sec} ({mapa[c]}); mover filas entre secciones todavía no "
                               "se ejecuta")
        prosas = corredor.prosas_de_seccion(b.base, sec)
        registro_b = b.base / "data" / "afirmaciones" / f"{sec}.csv"
        if not prosas or not registro_b.exists():
            errores.append(f"la sección {sec} desaparece de la versión nueva; retirarla entera todavía no se "
                           "ejecuta")
            continue
        prosa_b = prosas[0]
        texto_bytes, registro_bytes = prosa_b.read_bytes(), registro_b.read_bytes()
        texto = texto_bytes.decode("utf-8")
        prosa_cambia = base.sha256(texto_bytes) != s["files"]["prose"]["sha256"]
        registro_cambia = base.sha256(registro_bytes) != s["files"]["registry"]["sha256"]
        viejos = json.loads(pasajes_vigentes(s).read_text(encoding="utf-8"))
        parrafos = base.segmentar(texto)

        # Copias y pasajes de la versión nueva. Los de antes no se tocan: son el
        # texto del que salieron los registros hasta hoy.
        files = {k: dict(v) if isinstance(v, dict) else v for k, v in s["files"].items()}
        if prosa_cambia:
            ruta_p = base.PASSAGES / f"{sid}.{suf}.json"
            forma = [(c, i, f) for i, f, c in parrafos]
            if ruta_p.exists():
                # Un intento anterior, revertido: sus pasajes ya se emitieron y
                # se reutilizan, o el mismo texto tendría dos juegos de ids.
                nuevos = json.loads(ruta_p.read_text(encoding="utf-8"))
                if [(p["text"], p["character_offsets"]["start"], p["character_offsets"]["end"])
                        for p in nuevos] != forma:
                    raise SystemExit(f"ERROR {corredor._rel(ruta_p)} ya existe y no son los párrafos de esta versión")
            else:
                nuevos = [{"id": f"PASSAGE-{siguiente_pasaje + n:06d}", "section_id": sid, "ordinal": n + 1,
                           "text": c, "character_offsets": {"start": i, "end": f}, "record_status": "active"}
                          for n, (c, i, f) in enumerate(forma)]
                siguiente_pasaje += len(nuevos)
            emitidos.update(p["id"] for p in nuevos)
            ficheros[ruta_p] = (json.dumps(nuevos, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
            ficheros[base.SECTIONS / f"{sid}.{suf}.md"] = texto_bytes
            files["prose"] = {"path": prosa_b.relative_to(b.base).as_posix(), "sha256": base.sha256(texto_bytes),
                              "copy": f"knowledge/corpus/sections/{sid}.{suf}.md"}
            files["passages"] = f"knowledge/corpus/passages/{sid}.{suf}.json"
            alineacion = pasajes_cambiados(viejos, texto)
            por_ordinal = {p["ordinal"]: p["id"] for p in nuevos}
            mapa_p = {x["antes"]: (por_ordinal[x["ordinal"]] if x["ordinal"] else None)
                      for x in alineacion if x["antes"]}
            estado_p = {x["antes"]: x["estado"] for x in alineacion if x["antes"]}
        else:
            nuevos = viejos
            por_ordinal = {n: p["id"] for n, p in enumerate(nuevos, 1)}
            mapa_p = {p["id"]: p["id"] for p in viejos}
            estado_p = {p["id"]: "igual" for p in viejos}
        if registro_cambia:
            ficheros[base.SECTIONS / f"{sid}.{suf}.registro.csv"] = registro_bytes
            files["registry"] = {"path": registro_b.relative_to(b.base).as_posix(),
                                 "sha256": base.sha256(registro_bytes),
                                 "copy": f"knowledge/corpus/sections/{sid}.{suf}.registro.csv"}
        pasaje = {p["id"]: p for p in nuevos}
        viejo_p = {p["id"]: p for p in viejos}

        # De qué párrafos cuelga cada fila en la versión nueva: la regla de la
        # ingestión, salvo donde el fichero fija otros.
        anclaje = anclaje_nuevo(b.base, parrafos, propias)
        fijadas = {c: d for c, d in h.get("provenance", {}).items() if d.get("decision") == "fijar"}
        for c, d in sorted(fijadas.items()):
            fuera = [n for n in d["paragraphs"] if n not in por_ordinal]
            if fuera:
                errores.append(f"sección {sec}, provenance {c}: la prosa nueva no tiene el párrafo "
                               f"{', '.join(map(str, fuera))}")

        def colgar(c_nuevo: str) -> tuple[list[str], str | None]:
            viejo = inverso.get(c_nuevo)
            if viejo in fijadas:
                ords = [n for n in fijadas[viejo]["paragraphs"] if n in por_ordinal]
                return [por_ordinal[n] for n in ords], "fijada en la absorción"
            ords, via = anclaje.get(c_nuevo, ([], None))
            return [por_ordinal[n] for n in ords], via

        # --- menciones ------------------------------------------------------------------
        de_la_seccion = {mid: m for mid, (f, m) in proy.items()
                         if f == "mentions.jsonl" and m.get("section_id") == sid
                         and m.get("record_status", "active") == "active"}
        informadas = {m["mention"]: m for m in r["sections"][sec]["mentions"]}
        retiradas_m: set[str] = set()
        reancladas = 0
        for mid, m in sorted(de_la_seccion.items()):
            d = h.get("mentions", {}).get(mid)
            if mid in menciones_fuera:
                if d is not None and d.get("decision") == "reanclar":
                    errores.append(f"sección {sec}, mentions {mid}: se reancla, y su entidad la retira")
                retirar(mid, menciones_fuera[mid])
                retiradas_m.add(mid)
                continue
            if not prosa_cambia:
                continue
            estado = estado_p.get(m.get("passage_id"))
            if estado is None:
                continue  # cuelga de un pasaje de otra versión: ya no es de la prosa vigente
            if estado in ("igual", "desplazado"):
                nuevo_p = pasaje[mapa_p[m["passage_id"]]]
                salto = nuevo_p["character_offsets"]["start"] - viejo_p[m["passage_id"]]["character_offsets"]["start"]
                rec = tocar(mid)
                rec["passage_id"] = nuevo_p["id"]
                rec["character_offsets"] = {k: v + salto for k, v in m["character_offsets"].items()}
                reancladas += 1
                continue
            if d is None:
                errores.append(f"sección {sec}: la mención {mid} cuelga de un pasaje {estado} y no tiene decisión")
                continue
            if d["decision"] == "retirar":
                retirar(mid, d["reason"])
                retiradas_m.add(mid)
                continue
            ordinal = d.get("passage")
            if ordinal is None:
                citada = (informadas.get(mid) or {}).get("cited_in") or []
                if not citada:
                    errores.append(f"sección {sec}, mentions {mid}: su fila no se cita en la prosa nueva; di a "
                                   "qué párrafo se reancla (`passage`) o retírala")
                    continue
                ordinal = citada[0]
            if ordinal not in por_ordinal:
                errores.append(f"sección {sec}, mentions {mid}: la prosa nueva no tiene el párrafo {ordinal}")
                continue
            ini, fin, nota = corredor.localizar(m["original_text"], pasaje[por_ordinal[ordinal]])
            rec = tocar(mid)
            rec["passage_id"] = por_ordinal[ordinal]
            rec["character_offsets"] = {"start": ini, "end": fin}
            # La nota de cómo aparece la etiqueta era del pasaje de antes: la
            # sustituye la del nuevo, y otra deja constancia del cambio.
            rec["notes"] = [n for n in rec.get("notes") or [] if not es_de_localizacion(n)]
            rec["notes"] += [f"absorción {suf}: reanclada al párrafo {ordinal}", *([nota] if nota else [])]
            reancladas += 1

        # Menciones nuevas: las etiquetas que la versión nueva introduce, en su
        # fila dueña (modificada o nueva). Nacen pendientes y las resuelve la
        # misma maquinaria que una conversión, que admite claves de registros
        # nuevos de la sección.
        pendientes_m: dict[str, dict] = {}
        decisiones_m: dict[str, dict] = {}
        con_etiqueta_nueva: list[tuple[str, dict]] = []
        for viejo, d in sorted(filas_h.items(), key=lambda x: freeze._num(x[0])):
            if d.get("decision") not in (None, "retirar") and viejo in mapa:
                con_etiqueta_nueva.append((mapa[viejo], d))
        con_etiqueta_nueva += sorted(nuevas_h.items(), key=lambda x: freeze._num(x[0]))
        for c, d in con_etiqueta_nueva:
            pids, _ = colgar(c)
            for etiqueta, dm in sorted((d.get("new_mentions") or {}).items()):
                if not pids:
                    errores.append(f"sección {sec}, {c}: la fila no cuelga de ningún párrafo nuevo; no hay dónde "
                                   f"anclar «{etiqueta}»")
                    continue
                ini, fin, nota = corredor.localizar(etiqueta, pasaje[pids[0]])
                mid = f"MENTION-{siguiente_mencion:06d}"
                siguiente_mencion += 1
                pendientes_m[mid] = {
                    "id": mid, "section_id": sid, "passage_id": pids[0], "original_text": etiqueta,
                    "normalized_form": base.normalizar(etiqueta), "mention_type": "unresolved",
                    "character_offsets": {"start": ini, "end": fin},
                    "resolution": {"status": "pending", "target_ids": [], "reason": None},
                    "disposition": None, "issue_ids": [],
                    "notes": [f"absorción {suf}: etiqueta nueva de {c}", *([nota] if nota else [])],
                    "record_status": "active"}
                decisiones_m[mid] = dm

        # --- qué pasa con los registros que ya existían -----------------------------------
        # Los que se sustituyen dejan de derivarse; los que una división
        # reasigna pasan a colgar de su sucesora.
        reasignados: dict[str, str] = {}
        sustituye: dict[str, str] = {}
        for viejo, d in filas_h.items():
            for rid, otro in (d.get("replaced_by") or {}).items():
                sustituye[rid] = otro
                pendientes_sust.append((sec, rid, otro, d["reason"]))
            if d.get("decision") == "dividir":
                for sucesora, rids in (d.get("successors") or {}).items():
                    for rid in rids:
                        reasignados[rid] = sucesora

        de_registro, av = filas_de_registros(s)
        if av:
            errores.extend(f"sección {sec}: {x}" for x in av)
        decision_fila = {c: d.get("decision") for c, d in filas_h.items()}
        filas_nuevas_de: dict[str, list[str]] = {}
        for rid in sorted({rid for o in s["rows"].values() for rid in o["record_ids"]}):
            if rid not in proy:
                errores.append(f"sección {sec}: {rid} está en la correspondencia y no en el libro mayor")
                continue
            viejas = de_registro.get(rid) or [c for c, o in s["rows"].items() if rid in o["record_ids"]]
            fichero, antes = proy[rid]
            if rid in sustituye or antes.get("record_status", "active") != "active":
                continue
            # Un registro reasignado cambia su fila dividida por la sucesora.
            pares = [(c, reasignados[rid] if rid in reasignados and decision_fila.get(c) == "dividir" else mapa.get(c))
                     for c in viejas]
            pares = [(v, n) for v, n in pares if n]
            vivas = list(dict.fromkeys(n for _, n in pares))
            filas_nuevas_de[rid] = vivas
            if not vivas:
                # Todas sus filas se van. Si alguna se conserva, el registro sigue
                # tal cual; si todas se retiran, se retira con ellas.
                if all(decision_fila.get(c) == "retirar" for c in viejas):
                    motivos = "; ".join(dict.fromkeys(filas_h[c]["reason"] for c in viejas))
                    retirar(rid, f"sus filas ({', '.join(viejas)}) salen del corpus: {motivos}")
                continue
            # Procedencia: los párrafos nuevos de sus filas y, si cambió la
            # columna Fuente y sus fuentes salían de ella, las fuentes nuevas.
            prov = antes.get("provenance")
            reasignado = rid in reasignados
            if isinstance(prov, dict):
                nueva_prov = dict(prov)
                esperados = list(dict.fromkeys(p for c in viejas if c in s["rows"] for p in s["rows"][c]["passage_ids"]))
                colgados = list(dict.fromkeys(p for c in vivas for p in colgar(c)[0]))
                if prov.get("passage_ids") == esperados or reasignado:
                    nueva_prov["passage_ids"] = colgados
                elif prosa_cambia:
                    nueva_prov["passage_ids"] = [mapa_p[p] for p in prov.get("passage_ids", []) if mapa_p.get(p)]
                    avisos.append(f"{rid}: sus pasajes no eran los de sus filas; se traducen a la prosa nueva "
                                  "sin recalcularlos")
                if reasignado or any("Fuente" in modificadas.get(c, {}).get("columnas", {}) for c in viejas):
                    automaticas = [fuente_de_clave_antes.get(k) for k in claves_de_fuente(viejas, filas_a)]
                    if prov.get("source_ids") == automaticas:
                        fuentes_r = [fuente(k, f"{rid} ({', '.join(vivas)})") for k in claves_de_fuente(vivas, filas_b)]
                        nueva_prov["source_ids"] = [x for x in fuentes_r if x]
                    else:
                        avisos.append(f"{rid}: sus filas cambiaron de fuente, pero sus fuentes no salían de ellas; "
                                      "se dejan como están")
                if nueva_prov != prov:
                    nueva_prov["dataset_revision"] = rev_despues
                    rec = tocar(rid)
                    rec["provenance"] = nueva_prov
                    if "source_ids" in antes:
                        rec["source_ids"] = list(nueva_prov.get("source_ids", []))
            # Ejes: salen de la primera fila. Se rehacen si esa fila cambió sus
            # columnas de evaluación o si la primera es ahora otra.
            if fichero in ("claims.jsonl", "hypotheses.jsonl") and "epistemic_dimensions" in antes:
                primera_v = inverso.get(vivas[0])
                cols = modificadas.get(primera_v, {}).get("columnas", {})
                if primera_v != viejas[0] or any(e in cols for e in EJES):
                    ejes_n = convertir.ejes(filas_b[vivas[0]][1])
                    if ejes_n != antes["epistemic_dimensions"]:
                        tocar(rid)["epistemic_dimensions"] = ejes_n
            if fichero == "evidence.jsonl" and antes.get("quality_notes"):
                notas = list(antes["quality_notes"])
                for v, n in pares:
                    if s["rows"].get(v, {}).get("destination") != "J":
                        continue
                    previa = f"Evaluación de la fila {v} (destino J)"
                    notas = [nota_j(n, filas_b[n][1]) if x.startswith(previa) else x for x in notas]
                if notas != antes["quality_notes"]:
                    tocar(rid)["quality_notes"] = notas

        # --- registros nuevos ---------------------------------------------------------------
        # Los de las filas nuevas, los que amplían o reemplazan una fila que
        # sigue, y los de las sucesoras de una división: la misma maquinaria que
        # una conversión, con las filas y la procedencia de la versión nueva.
        registros_h = h.get("records") or []
        destino_de = {}
        for c in propias:
            viejo = inverso.get(c)
            if viejo is None:
                destino_de[c] = (nuevas_h.get(c) or {}).get("destination") or "H"
            elif decision_fila.get(viejo) == "dividir":
                destino_de[c] = "H"
            else:
                destino_de[c] = (s["rows"].get(viejo) or {}).get("destination", "H")
        claves_de_fila: dict[str, list[str]] = {}
        for c, d in nuevas_h.items():
            claves_de_fila[c] = list(d.get("keys") or [])
        for viejo, d in filas_h.items():
            if d.get("keys") and viejo in mapa:
                claves_de_fila[mapa[viejo]] = list(d["keys"])
        filas_g = {c: filas_b[c][1] for c in propias}
        filas_spec = {c: {"destination": destino_de[c], "keys": claves} for c, claves in claves_de_fila.items()}
        _, fallos = convertir.revisar_registros(registros_h, filas_spec, filas_g, sec)
        errores.extend(f"sección {sec}: {x}" for x in fallos)
        ids: dict[str, str] = {}
        if (registros_h or pendientes_m) and not fallos:
            try:
                g = convertir.generar(
                    sec_id=sid, records=registros_h,
                    rows={c: {"destination": destino_de[c]} for c in propias}, filas=filas_g,
                    origen={c: {"passage_ids": colgar(c)[0]} for c in propias},
                    decisiones=decisiones_m, menciones=pendientes_m, fechas=h.get("occurrence_dates") or {},
                    apendice=b.base / FUENTES, rev=rev_despues, proy=vigente(), nuevo=nuevo,
                    ya_emitidos=frozenset(emitidos))
            except SystemExit as e:
                errores.append(f"sección {sec}: {str(e).removeprefix('ERROR ')}")
                g = None
            if g is not None:
                ids = g["ids"]
                altas.extend(g["salida"])
                altas.extend(("mentions.jsonl", despues) for _, despues in g["actualizadas"])
                for rid, (fichero, _, despues) in g["cambios"].items():
                    if rid in cambios:
                        cambios[rid][2] = despues
                    elif rid in proy:
                        cambios[rid] = [fichero, proy[rid][1], despues]
                    else:
                        # Un registro nuevo de otra sección de esta misma absorción.
                        altas[:] = [(f, despues if x["id"] == rid else x) for f, x in altas]
                for fichero, rec in g["salida"]:
                    if fichero == "sources.jsonl":
                        fuente_de_clave[rec["citation_key"]] = rec["id"]
        ids_de[sec] = ids
        nuevos_de_fila: dict[str, list[str]] = defaultdict(list)
        for rspec in registros_h:
            if rspec["key"] in ids:
                for c in rspec.get("rows", []):
                    nuevos_de_fila[c].append(ids[rspec["key"]])
                filas_nuevas_de[ids[rspec["key"]]] = list(rspec.get("rows", []))
        for c, claves in claves_de_fila.items():
            for k in claves:
                if k in ids and ids[k] not in nuevos_de_fila[c]:
                    nuevos_de_fila[c].append(ids[k])

        # --- el mapa de filas de la versión nueva ----------------------------------------------
        activas = {m["original_text"]: mid for mid, m in de_la_seccion.items() if mid not in retiradas_m}
        activas.update({m["original_text"]: mid for mid, m in pendientes_m.items()})
        filas_mapa = {}
        for c in propias:
            viejo = inverso.get(c)
            pids, via = colgar(c)
            if viejo is None or viejo not in s["rows"]:
                clase, o = "nueva", {"destination": destino_de[c], "record_ids": [], "mention_ids": []}
            else:
                o = s["rows"][viejo]
                clase = ("modificada" if viejo in modificadas else "renumerada" if viejo != c else "sin cambios")
            etiquetas = [(filas_b[c][1].get(col) or "").strip() for col in ("Sujeto", "Objeto")]
            menciones_c = [m for m in o["mention_ids"] if m not in retiradas_m]
            menciones_c += [activas[e] for e in etiquetas if e in activas]
            # Lo que la fila deriva ahora: lo suyo que sigue, lo reasignado a
            # ella y lo nuevo.
            propios = [x for x in o["record_ids"] if x not in sustituye and not
                       (x in reasignados and decision_fila.get(viejo) == "dividir")]
            propios += [x for x, suc in reasignados.items() if suc == c]
            filas_mapa[c] = {"from": viejo, "class": clase, "passage_ids": pids, "via": via,
                             "mention_ids": list(dict.fromkeys(menciones_c)),
                             "destination": destino_de[c],
                             "record_ids": list(dict.fromkeys([*propios, *nuevos_de_fila[c]]))}
        bloque[sec] = {"section_id": sid, "files": files,
                       **({"passages": mapa_p} if prosa_cambia else {}),
                       "rows": filas_mapa,
                       "record_rows": {rid: filas_nuevas_de.get(rid, []) for rid in sorted(filas_nuevas_de)}}
        resumen[sec] = {"section_id": sid, "prose": prosa_cambia, "registry": registro_cambia,
                        "passages": len(nuevos) if prosa_cambia else 0, "reanchored": reancladas,
                        "new_records": sum(1 for rspec in registros_h if rspec["key"] in ids)}

    # --- sustituciones ------------------------------------------------------------------------
    estado = vigente()
    for sec, rid, otro, motivo in pendientes_sust:
        destino_id = ids_de.get(sec, {}).get(otro) if convertir.CLAVE.match(otro) else otro
        if destino_id is None or destino_id not in estado:
            errores.append(f"sección {sec}: {rid} se sustituye por {otro}, que no existe ni es un registro nuevo "
                           "de la sección")
            continue
        if destino_id == rid:
            errores.append(f"sección {sec}: {rid} no se sustituye por sí mismo")
            continue
        rec = tocar(rid)
        rec["record_status"] = "replaced"
        rec["superseded_by"] = destino_id
        rec["notes"] = [*(rec.get("notes") or []), f"absorción {suf}: sustituido por {destino_id}; {motivo}"]
        sustituidos[rid] = destino_id

    # --- parches ------------------------------------------------------------------------------
    antes_de_parches = {rid: json.loads(json.dumps(r_)) for rid, (_, r_) in vigente().items() if rid in parches}
    for rid, (donde, sec, parche) in sorted(parches.items()):
        if rid in retirados or rid in sustituidos:
            errores.append(f"{donde}: {rid} se corrige y se {'retira' if rid in retirados else 'sustituye'} a la vez")
            continue
        faltan: set[str] = set()
        valor = convertir.sustituir(json.loads(json.dumps(parche)), ids_de.get(sec, {}) if sec else {}, faltan)
        if faltan:
            errores.append(f"{donde}: {rid}: claves sin definir en la sección: {', '.join(sorted(faltan))}")
            continue
        tocar(rid).update(valor)
    # Un enlace cambiado se rehace en sus dos extremos: sale del destino de
    # antes y entra en el de ahora.
    estado = vigente()
    tocados_vuelta: set[tuple[str, str]] = set()
    for rid in sorted(parches):
        if rid not in antes_de_parches or rid in retirados or rid in sustituidos:
            continue
        fichero = estado[rid][0]
        antes_p, ahora_p = punteros(antes_de_parches[rid], fichero), punteros(estado[rid][1], fichero)
        for campo in set(antes_p) | set(ahora_p):
            for destino_id in antes_p.get(campo, set()) ^ ahora_p.get(campo, set()):
                tocados_vuelta.add((destino_id, campo))
    for destino_id, campo in sorted(tocados_vuelta):
        if destino_id not in estado:
            errores.append(f"un parche enlaza con {destino_id}, que no existe")
            continue
        fichero, rec_d = estado[destino_id]
        if campo == "temporal_expression_ids" and fichero == "occurrences.jsonl":
            errores.append(f"{destino_id}: cambiar la datación de una ocurrencia no se rehace sola; su fecha "
                           "se fija a mano")
            continue
        if fichero in convertir.ESQUEMA and campo not in convertir.propiedades(fichero):
            continue
        debe = valor_de_vuelta(campo, destino_id, estado)
        previo = list(rec_d.get(campo) or [])
        nuevo_v = [x for x in previo if x in debe] + [x for x in sorted(set(debe)) if x not in previo]
        if nuevo_v != previo:
            if destino_id in proy:
                tocar(destino_id)[campo] = nuevo_v
            else:
                rec_d[campo] = nuevo_v
    # Una evidencia dice de qué obra sale: tiene que ser una de su procedencia.
    for rid, (fichero, _, rec) in sorted(cambios.items()):
        prov = rec.get("provenance")
        if isinstance(prov, dict):
            ajenas = convertir.valores_de(rec, "source_id") - set(prov.get("source_ids") or [])
            if ajenas:
                errores.append(f"{rid}: `source_id` {', '.join(sorted(ajenas))} no está entre las fuentes de su "
                               "procedencia; corrígelo con un parche")
    if errores:
        raise SystemExit("ERROR la absorción no se puede construir:\n  " + "\n  ".join(errores))

    # Lo que no cambia no es una operación.
    for rid in [rid for rid, (_, antes, despues) in cambios.items() if antes == despues]:
        del cambios[rid]
    invalidos = validar_estado(cambios, altas)
    if invalidos:
        raise SystemExit("ERROR el libro mayor dejaría de validar:\n  " + "\n  ".join(invalidos))

    # --- delta ---------------------------------------------------------------------------------
    def operacion(rid: str) -> str:
        return ("DEPRECATE_RECORD" if rid in retirados else "SUPERSEDE_RECORD" if rid in sustituidos
                else "UPDATE_RECORD")

    operaciones = [{"operation": "ADD_RECORD", "file": f, "record_id": rec["id"], "before": None, "after": rec}
                   for f, rec in altas]
    operaciones += [{"operation": operacion(rid), "file": f, "record_id": rid, "before": antes, "after": despues}
                    for rid, (f, antes, despues) in sorted(cambios.items())]
    de_partida = dict(manifiesto["corpus_freeze"])
    llegada = {"path": destino["path"], "version": congelada.get("version"), "commit": congelada.get("commit"),
               "fingerprint": congelada["fingerprint"], "decision": spec.get("decision") or "DEC-059"}
    nuevos_de = lambda f: [rec["id"] for g_, rec in altas if g_ == f]  # noqa: E731
    delta = {
        "schema_version": base.SCHEMA_VERSION,
        "dataset_revision_before": rev_antes,
        "dataset_revision_after": rev_despues,
        "operations": operaciones,
        "records_added": [rec["id"] for _, rec in altas],
        "records_updated": sorted(rid for rid in cambios if rid not in retirados and rid not in sustituidos),
        "claims_added": nuevos_de("claims.jsonl"), "events_added": nuevos_de("events.jsonl"),
        "hypotheses_added": nuevos_de("hypotheses.jsonl"), "issues_added": nuevos_de("issues.jsonl"),
        "issues_resolved": [],
        "records_deprecated": sorted([*retirados, *sustituidos]),
        "views_invalidated": [], "views_built": [], "validation_results": {},
        "absorption": {
            "spec": {"path": corredor._rel(ruta_spec), "sha256": convertir.sha256(spec_bytes)},
            "decision": spec.get("decision"),
            "received_at": spec["received_at"],
            "freeze": {"from": de_partida, "to": llegada},
            "sections": bloque,
        },
    }
    return {"suffix": suf, "delta": delta, "files": ficheros, "summary": resumen, "warnings": avisos,
            "rev": (rev_antes, rev_despues), "added": altas, "changed": cambios, "deprecated": retirados,
            "replaced": sustituidos, "from": de_partida, "to": llegada}


def informe_construccion(c: dict) -> list[str]:
    d = c["delta"]
    lineas = [
        f"# Absorción {c['suffix']}",
        "",
        f"- Revisión: {c['rev'][0]} → {c['rev'][1]}",
        f"- Congelación: `{c['from']['path']}` → `{c['to']['path']}`",
        f"- Fichero de absorción: `{d['absorption']['spec']['path']}` ({d['absorption']['spec']['sha256'][:19]}…)",
        f"- Fecha: {d['absorption']['received_at']}",
        "",
        "## Secciones",
        "",
        "| Sección | SEC | Prosa | Registro | Pasajes nuevos | Menciones reancladas | Registros nuevos |",
        "|---|---|---|---|---:|---:|---:|",
    ]
    for sec, x in c["summary"].items():
        lineas.append(f"| {sec} | {x['section_id']} | {'cambia' if x['prose'] else 'igual'} | "
                      f"{'cambia' if x['registry'] else 'igual'} | {x['passages']} | {x['reanchored']} | "
                      f"{x['new_records']} |")
    por_fichero: dict[str, int] = defaultdict(int)
    for rid, (f, _, _) in c["changed"].items():
        if rid not in c["deprecated"] and rid not in c["replaced"]:
            por_fichero[f] += 1
    lineas += ["", "## Operaciones", "", "| Operación | Fichero | Registros |", "|---|---|---:|"]
    for f, n in sorted(Counter(f for f, _ in c["added"]).items()):
        lineas.append(f"| alta | `{f}` | {n} |")
    for f, n in sorted(por_fichero.items()):
        lineas.append(f"| actualización | `{f}` | {n} |")
    if c["deprecated"]:
        lineas += ["", "## Retirados", ""] + [f"- {rid}: {m}" for rid, m in sorted(c["deprecated"].items())]
    if c["replaced"]:
        lineas += ["", "## Sustituidos", ""] + [f"- {rid} → {otro}" for rid, otro in sorted(c["replaced"].items())]
    if c["warnings"]:
        lineas += ["", "## Avisos", ""] + [f"- {a}" for a in c["warnings"]]
    lineas += ["", f"Se aplica con `python scripts/ingest/delta.py ABS-{c['suffix']}.json` y se revierte con `--revert`: "
               "al aplicarlo la congelación activa pasa a la versión nueva, y al revertirlo vuelve la de antes."]
    return lineas


def cmd_construir(args) -> int:
    c = construir(Path(args.fichero).resolve(), args.anterior, args.nueva)
    lineas = informe_construccion(c)
    print("\n".join(lineas))
    if args.dry_run:
        print("\n(en seco: no se ha escrito nada)")
        return 0
    # Las copias de la versión nueva no se reescriben: si ya están, tienen que
    # ser las mismas (un intento anterior, revertido).
    for ruta, contenido in c["files"].items():
        if ruta.exists() and ruta.read_bytes() != contenido:
            raise SystemExit(f"ERROR {corredor._rel(ruta)} ya existe con otro contenido; no se sobrescribe")
    nombre, n = f"ABS-{c['suffix']}", 2
    # Una absorción revertida se queda como constancia; la nueva lleva otro nombre.
    while (base.DELTAS / f"{nombre}.json").exists():
        nombre, n = f"ABS-{c['suffix']}-{n}", n + 1
    for ruta, contenido in c["files"].items():
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_bytes(contenido)
    base.DELTAS.mkdir(parents=True, exist_ok=True)
    base.REPORTS.mkdir(parents=True, exist_ok=True)
    (base.DELTAS / f"{nombre}.json").write_text(json.dumps(c["delta"], indent=2, ensure_ascii=False) + "\n",
                                                encoding="utf-8")
    (base.REPORTS / f"{nombre}.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    for ruta in c["files"]:
        print(f"  copia     {corredor._rel(ruta)}")
    print(f"  delta     knowledge/deltas/{nombre}.json")
    print(f"  informe   generated/reports/{nombre}.md")
    print(f"\n  el delta NO se ha aplicado:\n    python scripts/ingest/delta.py {nombre}.json")
    return 0


def cmd_informe(args) -> int:
    r = informe(args.anterior, args.nueva)
    salida = Path(args.salida) if args.salida else GENERATED / r["suffix"]
    nombre = f"corredor-{r['suffix']}.json"
    texto_esqueleto = json.dumps(esqueleto(r), indent=2, ensure_ascii=False) + "\n"
    # El esqueleto se rellena a mano: volver a generar el informe no puede
    # borrar decisiones ya tomadas sin que se pida.
    previo = salida / nombre
    if previo.exists() and previo.read_text(encoding="utf-8") != texto_esqueleto and not args.sobrescribir:
        raise SystemExit(f"ERROR {corredor._rel(previo)} ya existe y no es el esqueleto en blanco: puede tener "
                         "decisiones. Muévelo, o vuelve a ejecutar con --sobrescribir si quieres perderlas")
    salida.mkdir(parents=True, exist_ok=True)
    (salida / "diff.json").write_text(json.dumps({**r["diff"], "afirmaciones": {
        k: v for k, v in r["diff"]["afirmaciones"].items() if k != "mapa"}}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")
    (salida / "informe.md").write_text("\n".join(markdown(r)) + "\n", encoding="utf-8")
    (salida / nombre).write_text(texto_esqueleto, encoding="utf-8")
    for sec, s in r["sections"].items():
        print(f"sección {sec} ({s['section_id']}): {len(s['rows'])} filas cambiadas, {len(s['new_rows'])} nuevas, "
              f"{len(s['passages'])} pasajes y {len(s['mentions'])} menciones afectados")
    print(f"fuentes {len(r['sources'])} · entidades {len(r['entities'])} · filas de apéndices {len(r['appendices'])}"
          f" · borradores {len(r['drafts'])}")
    for aviso in r["warnings"]:
        print(f"AVISO {aviso}")
    print(f"\n  informe    {corredor._rel(salida / 'informe.md')}")
    print(f"  esqueleto  {corredor._rel(salida / nombre)}")
    print(f"  diff       {corredor._rel(salida / 'diff.json')}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Absorbe una versión nueva del corpus en lo ya ingerido (DEC-059)")
    sub = ap.add_subparsers(dest="orden", required=True)
    i = sub.add_parser("informe", help="qué registros toca cada cambio, y el esqueleto del fichero de absorción")
    i.add_argument("anterior", help="la congelación activa: directorio del corpus, o directorio@ref")
    i.add_argument("nueva", help="la versión nueva: directorio, o directorio@ref")
    i.add_argument("--salida", default=None, help="carpeta de salida (por defecto, generated/absorcion/<commit>/)")
    i.add_argument("--sobrescribir", action="store_true",
                   help="reescribir un fichero de absorción que ya existe, aunque tenga decisiones")
    i.set_defaults(func=cmd_informe)
    c = sub.add_parser("construir", help="el delta de absorción desde el fichero de absorción revisado")
    c.add_argument("fichero", help="knowledge/corpus/absorptions/corredor-<commit>.json")
    c.add_argument("anterior", help="la congelación activa: directorio del corpus, o directorio@ref")
    c.add_argument("nueva", help="la versión congelada en `to`: directorio, o directorio@ref")
    c.add_argument("--dry-run", action="store_true", help="comprobar y mostrar sin escribir nada")
    c.set_defaults(func=cmd_construir)
    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
