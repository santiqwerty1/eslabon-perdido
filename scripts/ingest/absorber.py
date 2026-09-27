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
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "validate"))

import convertir  # noqa: E402
import corredor  # noqa: E402
import freeze  # noqa: E402
import ingest as base  # noqa: E402

GENERATED = base.ROOT / "generated" / "absorcion"
SUCESIONES = "data/auditoria/sucesiones_afirmaciones.csv"
FUENTES = "data/apendices/A_fuentes.csv"
ENTIDADES = "data/apendices/B_entidades.csv"

EJES = ("Aceptación", "Fuerza", "Motivo", "Resolución", "Vigencia")
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
    avisos = []
    ruta = base.ROOT / conversion["spec"]["path"]
    if not ruta.exists():
        return {}, [f"{conversion['spec']['path']} no existe: no se sabe la primera fila de cada registro"]
    datos = ruta.read_bytes()
    if convertir.sha256(datos) != conversion["spec"]["sha256"]:
        avisos.append(f"{conversion['spec']['path']} no es el fichero que convirtió la sección: "
                      "las primeras filas pueden no ser éstas")
    entradas = json.loads(datos).get("records", [])
    delta = json.loads((base.DELTAS / conversion["delta"]).read_text(encoding="utf-8"))
    altas = [op for op in delta["operations"]
             if op["operation"] == "ADD_RECORD" and op["file"] != "sources.jsonl"]
    if len(altas) != len(entradas) or any(op["file"] != e["file"] for op, e in zip(altas, entradas)):
        return {}, [*avisos, f"{conversion['delta']} no sigue el orden de su fichero de conversión: "
                             "no se sabe la primera fila de cada registro"]
    return {op["record_id"]: e for op, e in zip(altas, entradas)}, avisos


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
    indice = ({t["id"]: t for t in json.loads(ruta_indice.read_text(encoding="utf-8")).get("tables", [])}
              if ruta_indice.exists() else {})

    def leer(relativa: str) -> str:
        # Sólo ficheros de la versión comparada, como exige la ingestión.
        ruta = (raiz / relativa).resolve()
        try:
            ruta.relative_to(raiz.resolve())
        except ValueError:
            return ""
        return ruta.read_text(encoding="utf-8") if ruta.is_file() else ""

    return corredor.anclar(filas, citadas, marcadores, indice, leer) if citadas else {}


def aparece(etiqueta: str, texto: str) -> bool:
    return re.search(r"(?<!\w)" + re.escape(etiqueta) + r"(?!\w)", texto, re.IGNORECASE) is not None


# ---------------------------------------------------------------------------
# Informe
# ---------------------------------------------------------------------------

def informe(anterior: str, nueva: str) -> dict:
    ruta, activa = corredor.congelacion(None)
    a = freeze.abrir(anterior)
    corredor.verificar(a, ruta, activa)
    b = freeze.abrir(nueva)
    dif = freeze.diferencia(a, b)
    af = dif["afirmaciones"]

    mapa = {x["de"]: x["a"] for x in af["correspondencia"]}
    retiradas = {x["id"] for x in af["retiradas"]}
    traduccion = {**mapa, **{i: f"{i}[retirada]" for i in retiradas}}
    inverso = {j: i for i, j in mapa.items()}
    modificadas = {m["de"]: m for m in af["modificadas"]}
    filas_a, filas_b = freeze.leer_afirmaciones(a.base), freeze.leer_afirmaciones(b.base)
    sucesiones = leer_sucesiones(b.base)
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
    menciones = {rid: r for rid, (f, r) in proy.items() if f == "mentions.jsonl"}

    salida_secciones = {}
    for sec, s in sorted(secciones.items()):
        entradas, av = entradas_de_conversion(s["conversion"]) if s["conversion"] else ({}, [])
        avisos += av
        primera = {rid: e["rows"][0] for rid, e in entradas.items() if e.get("rows")}
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
            if c in sucesiones:
                fila["successors"] = sucesiones[c]
            elif clase == "retirada":
                fila["aviso"] = "retirada sin sucesoras en sucesiones_afirmaciones.csv"
            elif (columnas.get("Vigencia") or ["", ""])[1].strip().lower() == "superada":
                fila["aviso"] = "pasa a vigencia superada sin sucesoras declaradas"
            filas.append(fila)

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
        viejos_p = base.PASSAGES / f"{s['section_id']}.json"
        prosa_rel = s["files"]["prose"]["path"]
        prosa_b = b.base / prosa_rel
        if not prosa_b.exists():
            try:
                prosa_b = corredor.ficheros_de_seccion(b.base, sec)[0]
            except SystemExit:
                prosa_b = None
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

        # Etiquetas que la versión nueva introduce en filas modificadas.
        etiquetas = {m["original_text"] for m in menciones.values() if m.get("section_id") == s["section_id"]}
        for f in filas:
            for col in ("Sujeto", "Objeto"):
                if col in f["columns"]:
                    nueva_et = f["columns"][col][1].strip()
                    if nueva_et and nueva_et not in etiquetas:
                        f.setdefault("new_labels", []).append(nueva_et)

        salida_secciones[sec] = {
            "section_id": s["section_id"], "converted": s["conversion"] is not None,
            "unchanged": sin_cambios, "rows": filas, "new_rows": nuevas_l,
            "passages": pasajes, "mentions": afectadas_m, "provenance": procedencia,
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
            nuevas_c = {inverso[x] for v in (ch["despues"] or {}).values() for x in freeze.C_REF.findall(v)
                        if x in inverso}
            ingeridas = sorted((viejas | nuevas_c) & fila_de.keys(), key=freeze._num)
            clave = ch["clave"] if ch["clave"] is not None else next(iter((ch["antes"] or ch["despues"]).values()))
            if ruta_r == FUENTES and ch["clave"] in existentes_src:
                rid, previa = existentes_src[ch["clave"]]
                col_doi = next((c for c in cab if c.strip().lower().startswith("doi")), "")
                if ch["despues"] is None:
                    cambia = ["retirada del apéndice A"]
                else:
                    # Todo lo que el registro guarda del apéndice, no sólo la
                    # bibliografía: también las notas de calidad y la fecha de
                    # consulta. La verificación y el estado son de este proyecto.
                    nueva_f = convertir.fuente_de_apendice(ch["despues"], col_doi)
                    cambia = [k for k in nueva_f if k not in ("verification_status", "record_status")
                              and previa.get(k) != nueva_f[k]]
                fuentes.append({"key": ch["clave"], "record_id": rid, "state": ch["estado"], "fields": cambia})
            if ruta_r == ENTIDADES:
                # Una entidad se ingiere con la sección de su primera fila. Si esa
                # fila cambia, cuentan las dos: la de antes pierde la entidad y la
                # de ahora la gana, aunque todavía no tenga mención.
                etiqueta = ((ch["antes"] or ch["despues"]).get("etiqueta preferida") or "").strip()
                cols = sorted(k for k in (ch["antes"] or {}) if ch["despues"] and ch["antes"][k] != ch["despues"].get(k))
                lados: dict[str, tuple[str, str]] = {}
                if ch["antes"]:
                    fila_v = (ch["antes"].get(corredor.COL_PRIMERA) or "").strip()
                    if fila_v in fila_de:
                        lados[fila_de[fila_v][0]] = ("antes", fila_v)
                if ch["despues"]:
                    fila_n = (ch["despues"].get(corredor.COL_PRIMERA) or "").strip()
                    if inverso.get(fila_n) in fila_de:
                        sec_n, fila_n = fila_de[inverso[fila_n]][0], inverso[fila_n]
                    else:
                        sec_n = filas_b.get(fila_n, (None,))[0]
                    if sec_n in secciones:
                        lados[sec_n] = ("ambos", lados[sec_n][1]) if sec_n in lados else ("despues", fila_n)
                for sec_e, (lado, fila_e) in sorted(lados.items()):
                    mids = sorted(mid for mid, m in menciones.items()
                                  if m.get("section_id") == secciones[sec_e]["section_id"]
                                  and m.get("original_text") == etiqueta)
                    entidades.append({"label": etiqueta, "state": ch["estado"], "section": sec_e, "side": lado,
                                      "mention_ids": mids, "columns": cols, "row": fila_e,
                                      "record_ids": fila_de[fila_e][1]["record_ids"] if fila_e in fila_de else []})
                continue
            if ingeridas:
                apendices.append({
                    "path": ruta_r, "key": clave, "state": ch["estado"], "rows": ingeridas,
                    "record_ids": sorted({r for c in ingeridas for r in fila_de[c][1]["record_ids"]}),
                    "sections": sorted({fila_de[c][0] for c in ingeridas}),
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
            filas[f["row"]] = e
        for n in s["new_rows"]:
            filas[n["row"]] = {"class": "nueva", "destination": None, "keys": [], "note": None,
                               **({"successor_of": n["successor_of"]} if n["successor_of"] else {})}
        menciones = {m["mention"]: {"label": m["label"], "state": m["state"], "decision": None, "reason": None}
                     for m in s["mentions"] if m["state"] != "desplazado"}
        procedencia = {c: {"record_ids": x["record_ids"], "mention_ids": x["mention_ids"],
                           "via_before": x["via_before"], "via_after": x["via_after"],
                           "paragraphs_after": x["paragraphs_after"], "decision": None, "reason": None}
                       for c, x in s["provenance"].items() if not x["mechanical"]}
        if filas or menciones or procedencia:
            secciones[sec] = {"section_id": s["section_id"], "rows": filas, "records": [], "mentions": menciones,
                              "provenance": procedencia}
    return {
        "from": {k: r["from"][k] for k in ("path", "fingerprint")},
        "to": {k: r["to"][k] for k in ("path", "fingerprint")},
        "decision": "DEC-059",
        "received_at": None,
        "pairing": {},
        "sections": secciones,
        "sources": {f["key"]: {"record_id": f["record_id"], "fields": f["fields"], "decision": None}
                    for f in r["sources"] if f["fields"]},
        # Una entidad puede tocar dos secciones si cambia su primera fila.
        "entities": [{"label": e["label"], "section": e["section"], "side": e["side"], "row": e["row"],
                      "state": e["state"], "columns": e["columns"], "mention_ids": e["mention_ids"],
                      "decision": None, "reason": None} for e in r["entities"]],
        # Una lista por apéndice: sin clave única (F_magnitudes), dos filas
        # cambiadas pueden empezar igual.
        "appendices": {ruta: [{"key": x["key"], "state": x["state"], "rows": x["rows"], "decision": None,
                               "reason": None} for x in r["appendices"] if x["path"] == ruta]
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
        if not (s["rows"] or s["new_rows"] or s["passages"] or s["provenance"] or marcas):
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
                if f.get("aviso"):
                    detalle.append(f["aviso"])
                if f.get("new_labels"):
                    detalle.append("etiquetas nuevas sin mención: " + ", ".join(f"«{x}»" for x in f["new_labels"]))
                if detalle:
                    lineas.append(f"- **{f['row']}**: " + ". ".join(detalle) + ".")
                for col, (antes, despues) in f["columns"].items():
                    lineas += [f"  - {col}", f"    - antes: {antes}", f"    - ahora: {despues}"]
            lineas.append("")
        if s["new_rows"]:
            lineas += ["Filas nuevas, que piden destino:", ""]
            for n in s["new_rows"]:
                de = f" (sucede a {', '.join(n['successor_of'])})" if n["successor_of"] else ""
                lineas.append(f"- {n['row']}{de}: {n['statement']}")
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
            lineas.append(f"- {f['key']} ({f['record_id']}), {f['state']}: cambia {que}")
        lineas.append("")
    if r["entities"]:
        lineas += ["## Entidades del apéndice B de secciones ingeridas", ""]
        for e in r["entities"]:
            cols = f" ({', '.join(e['columns'])})" if e["columns"] else ""
            lado = {"antes": "la pierde", "despues": "la gana", "ambos": ""}[e["side"]]
            lineas.append(f"- «{e['label']}», sección {e['section']}{', ' + lado if lado else ''}, {e['state']}{cols}: "
                          + (f"menciones {', '.join(e['mention_ids'])}" if e["mention_ids"]
                             else "sin mención en esta sección: pide una nueva"))
        lineas.append("")
    if r["appendices"]:
        lineas += ["## Filas de los apéndices que citan filas ingeridas", "",
                   "| Apéndice | Clave | Estado | Filas | Registros |", "|---|---|---|---|---|"]
        for x in r["appendices"]:
            clave = str(x["key"])[:60]
            lineas.append(f"| {Path(x['path']).name} | {clave} | {x['state']} | {', '.join(x['rows'])} | "
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


def cmd_informe(args) -> int:
    r = informe(args.anterior, args.nueva)
    salida = Path(args.salida) if args.salida else GENERATED / r["suffix"]
    salida.mkdir(parents=True, exist_ok=True)
    (salida / "diff.json").write_text(json.dumps({**r["diff"], "afirmaciones": {
        k: v for k, v in r["diff"]["afirmaciones"].items() if k != "mapa"}}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")
    (salida / "informe.md").write_text("\n".join(markdown(r)) + "\n", encoding="utf-8")
    nombre = f"corredor-{r['suffix']}.json"
    (salida / nombre).write_text(
        json.dumps(esqueleto(r), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
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
    i.set_defaults(func=cmd_informe)
    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
