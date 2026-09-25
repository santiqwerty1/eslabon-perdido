#!/usr/bin/env python3
"""Congelación y comparación de versiones del corpus de investigación.

La Campaña 1 no ingiere «el corpus del corredor»: ingiere **una versión
concreta** de él, y tiene que poder demostrar cuál (§4.5, paso 1 de §17). Con un
documento único bastaba su hash (`docs/INGESTION-C01.md`, paso 2). El corpus
llegó como repositorio de CSV que sigue cambiando mientras su auditoría avanza,
así que la versión se fija por la huella de su **capa canónica** —`data/` y
`docs/secciones/`— y por el commit del que sale (`DEC-056`).

Tres órdenes:

    create  FUENTE             congela: escribe el manifiesto de la versión
    verify  FUENTE MANIFIESTO  comprueba que una copia es la versión congelada
    diff    ANTERIOR NUEVA     qué cambió entre dos versiones, fila a fila

FUENTE es un directorio con el corpus, o `directorio@ref` para leer un commit de
su historia sin tocar la copia de trabajo: `../corredor@af7e799`.

La huella cubre sólo la capa canónica, no el repositorio entero. Un commit que
regenere derivados —`exports/`, el informe, `manifest.json`— o toque
documentación sigue verificando contra la misma congelación, porque lo que se
ingiere no cambió. Cualquier cambio en `data/` o `docs/secciones/`, en cambio,
es una versión distinta.

**Por qué el diff empareja por contenido y no sólo por `#`.** El corredor
renumera sus afirmaciones de forma global (`scripts/renumber.py`) cuando se
inserta una fila en una sección intermedia, así que el mismo `C-0412` puede
designar dos afirmaciones distintas en dos versiones. Emparejar por número
declararía modificada una afirmación que sólo se desplazó y, peor, daría por
continuación de una afirmación a otra que ocupa su número. Se empareja primero
por número y contenido, después por contenido, después por el texto de la
afirmación y sólo al final por número dentro de la misma sección; cada
emparejamiento dice por qué vía se hizo.

Una vez emparejadas, las referencias `C-…` de la versión anterior se traducen
por el mapa de renumeración antes de comparar. Una síntesis que citaba `C-0411`
y ahora cita `C-0412` porque su fuente se desplazó no ha cambiado: se cuenta
como renumeración, no como modificación.

Lo que NO hace: decidir si un cambio es correcto. Clasifica y cuenta; el juicio
sobre lo que cambió es de quien ingiere (§27.12).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFESTS = ROOT / "knowledge" / "corpus" / "manifests"

CAPA_CANONICA = ("data", "docs/secciones")
# Fuera de la capa canónica, pero la describen: versión declarada, corte y
# recuentos. Se leen si existen; no entran en la huella.
METADATOS = ("VERSION", "manifest.json")

AFIRMACIONES = "data/afirmaciones"
REGISTROS = ("data/apendices", "data/busquedas_negativas")
PROSA = "docs/secciones"
TABLAS = "data/tablas"

C_REF = re.compile(r"\bC-\d{3,}\b")
C_RANGO = re.compile(r"\bC-(\d{3,})\s*[–—-]\s*C-(\d{3,})\b")
RANGO_MAX = 400


# ---------------------------------------------------------------------------
# Fuentes: un directorio, o un commit de su historia
# ---------------------------------------------------------------------------

@dataclass
class Fuente:
    base: Path
    etiqueta: str
    commit: str | None
    limpia: bool | None  # ¿coincide la capa canónica con el commit?
    _tmp: tempfile.TemporaryDirectory | None = field(default=None, repr=False)


def _git(directorio: Path, *args: str, binario: bool = False):
    r = subprocess.run(["git", "-C", str(directorio), *args], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout if binario else r.stdout.decode("utf-8").strip()


def abrir(spec: str) -> Fuente:
    directorio, ref = spec, None
    if "@" in spec:
        izq, _, der = spec.rpartition("@")
        if der and Path(izq).is_dir():
            directorio, ref = izq, der
    base = Path(directorio)
    if not base.is_dir():
        raise SystemExit(f"ERROR no existe el directorio {base}")

    if ref is None:
        # Sólo se atribuye commit si el directorio ES la raíz de un repositorio:
        # una carpeta dentro de otro repo heredaría un commit que no la describe.
        raiz = _git(base, "rev-parse", "--show-toplevel")
        es_raiz = raiz is not None and Path(raiz).resolve() == base.resolve()
        commit = _git(base, "rev-parse", "HEAD") if es_raiz else None
        limpia = None
        if commit:
            # --ignored también: un fichero ignorado entra en la huella de la
            # copia de trabajo pero ningún commit lo reproduce.
            sucio = _git(base, "status", "--porcelain", "--untracked-files=all", "--ignored",
                         "--", *CAPA_CANONICA)
            limpia = sucio == ""
        return Fuente(base, str(base), commit, limpia)

    commit = _git(base, "rev-parse", "--verify", f"{ref}^{{commit}}")
    if not commit:
        raise SystemExit(f"ERROR {base} no tiene el commit {ref}")
    rutas = [r for r in (*CAPA_CANONICA, *METADATOS)
             if _git(base, "cat-file", "-e", f"{commit}:{r}") is not None]
    crudo = _git(base, "archive", "--format=tar", commit, "--", *rutas, binario=True)
    if crudo is None:
        raise SystemExit(f"ERROR no se pudo extraer {commit[:7]} de {base}")
    tmp = tempfile.TemporaryDirectory(prefix="corpus-")
    with tarfile.open(fileobj=io.BytesIO(crudo)) as tar:
        if hasattr(tarfile, "data_filter"):  # Python ≥ 3.11.4
            tar.extractall(tmp.name, filter="data")
        else:
            tar.extractall(tmp.name)
    return Fuente(Path(tmp.name), f"{base}@{commit[:7]}", commit, True, tmp)


# ---------------------------------------------------------------------------
# Huella
# ---------------------------------------------------------------------------

def ficheros(base: Path) -> list[dict]:
    faltan = [c for c in CAPA_CANONICA if not (base / c).is_dir()]
    if faltan:
        raise SystemExit(f"ERROR {base} no parece el corpus: falta {', '.join(faltan)}/")
    salida = []
    for capa in CAPA_CANONICA:
        # Un enlace simbólico se hashearía por lo que hay al otro lado, que
        # puede cambiar sin que cambie el commit, o no existir en otra copia.
        # Una huella así no se reproduce: se rechaza.
        for dirpath, dirnames, filenames in os.walk(base / capa, followlinks=False):
            for nombre in (*dirnames, *filenames):
                if (Path(dirpath) / nombre).is_symlink() or (base / capa).is_symlink():
                    ruta = (Path(dirpath) / nombre).relative_to(base).as_posix()
                    raise SystemExit(f"ERROR {ruta} es un enlace simbólico dentro de la capa "
                                     "canónica: la huella no puede depender de a dónde apunte")
            for nombre in filenames:
                p = Path(dirpath) / nombre
                datos = p.read_bytes()
                salida.append({
                    "path": p.relative_to(base).as_posix(),
                    "sha256": hashlib.sha256(datos).hexdigest(),
                    "bytes": len(datos),
                })
    return sorted(salida, key=lambda f: f["path"])


def huella(lista: list[dict]) -> str:
    """Una sola cifra para toda la capa: ruta y hash de cada fichero, en orden."""
    texto = "".join(f"{f['path']}\t{f['sha256']}\n" for f in lista)
    return "sha256:" + hashlib.sha256(texto.encode("utf-8")).hexdigest()


def metadatos(base: Path) -> dict:
    version = (base / "VERSION").read_text(encoding="utf-8").strip() if (base / "VERSION").exists() else None
    man = {}
    if (base / "manifest.json").exists():
        man = json.loads((base / "manifest.json").read_text(encoding="utf-8"))
    return {
        "corpus": man.get("corpus"),
        "version": version,
        "cutoff": man.get("fecha_de_corte_bibliografico"),
        "declared_state": man.get("estado"),
        "counts": man.get("counts"),
    }


# ---------------------------------------------------------------------------
# create / verify
# ---------------------------------------------------------------------------

def cmd_create(args) -> int:
    src = abrir(args.fuente)
    if src.limpia is False:
        print("ERROR la capa canónica tiene cambios sin confirmar o ficheros ignorados: "
              "ningún commit la reproduce.")
        print("      Confírmalos, o congela un commit concreto con directorio@ref.")
        return 1
    lista = ficheros(src.base)
    meta = metadatos(src.base)
    registro = {
        **meta,
        "repository": args.repositorio,
        "commit": src.commit,
        "frozen_on": args.fecha or date.today().isoformat(),
        "decision": args.decision,
        "supersedes": args.sustituye,
        "canonical_layer": [f"{c}/" for c in CAPA_CANONICA],
        "fingerprint": huella(lista),
        "file_count": len(lista),
        "files": lista,
    }

    if args.salida:
        salida = Path(args.salida)
    else:
        sufijo = (src.commit or registro["fingerprint"].split(":")[1])[:7]
        salida = MANIFESTS / f"corredor-v{meta['version'] or 'sin-version'}-{sufijo}.json"

    # Una congelación no se reescribe: si hace falta otra, es otra versión.
    if salida.exists():
        previa = json.loads(salida.read_text(encoding="utf-8"))
        if previa.get("fingerprint") == registro["fingerprint"]:
            print(f"ya congelada en {salida}: misma huella, no se toca")
            return 0
        print(f"ERROR {salida} ya existe con otra huella. Una congelación no se sobrescribe.")
        return 1

    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps(registro, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"congelada {src.etiqueta}")
    print(f"  versión  {meta['version']} · corte {meta['cutoff']} · commit {(src.commit or '—')[:12]}")
    print(f"  huella   {registro['fingerprint']}")
    print(f"  {len(lista)} ficheros de {', '.join(registro['canonical_layer'])}")
    print(f"  escrito en {_rel(salida)}")
    return 0


def cmd_verify(args) -> int:
    src = abrir(args.fuente)
    registro = json.loads(Path(args.manifiesto).read_text(encoding="utf-8"))
    # Un manifiesto editado a mano o mal fusionado puede declarar una huella que
    # sus propios ficheros no dan. Entonces no hay contra qué verificar.
    if huella(registro["files"]) != registro.get("fingerprint") or \
            registro.get("file_count", len(registro["files"])) != len(registro["files"]):
        print(f"ERROR {Path(args.manifiesto).name} es incoherente: su huella o su recuento "
              "no corresponden a la lista de ficheros que declara")
        return 1
    actual = {f["path"]: f["sha256"] for f in ficheros(src.base)}
    esperado = {f["path"]: f["sha256"] for f in registro["files"]}

    cambiados = sorted(p for p in actual.keys() & esperado.keys() if actual[p] != esperado[p])
    nuevos = sorted(actual.keys() - esperado.keys())
    retirados = sorted(esperado.keys() - actual.keys())

    print(f"verificando {src.etiqueta} contra {Path(args.manifiesto).name}")
    if src.limpia is False:
        print("  aviso: la capa canónica tiene cambios sin confirmar o ficheros ignorados")
    if not (cambiados or nuevos or retirados):
        print(f"  COINCIDE · {len(actual)} ficheros · {registro['fingerprint']}")
        return 0
    for etiqueta, lista in (("cambiado", cambiados), ("nuevo", nuevos), ("retirado", retirados)):
        for p in lista:
            print(f"  {etiqueta:9} {p}")
    print(f"  NO COINCIDE · {len(cambiados)} cambiados, {len(nuevos)} nuevos, {len(retirados)} retirados")
    print("  Es otra versión del corpus: congélala aparte y compárala con `diff`.")
    return 1


# ---------------------------------------------------------------------------
# diff
# ---------------------------------------------------------------------------

def leer_csv(p: Path) -> tuple[list[str], list[dict]]:
    with p.open(encoding="utf-8", newline="") as fh:
        filas = list(csv.reader(fh))
    if not filas:
        return [], []
    cab = filas[0]
    # Una fila más ancha o más estrecha que su cabecera no se recorta ni se
    # rellena: recortarla haría que un cambio real en las celdas sobrantes
    # pasara por «sin cambios».
    for n, f in enumerate(filas[1:], 2):
        if f and len(f) != len(cab):
            raise SystemExit(f"ERROR {p}: la línea {n} tiene {len(f)} celdas y la cabecera {len(cab)}")
    return cab, [dict(zip(cab, f)) for f in filas[1:] if f]


def leer_afirmaciones(base: Path) -> dict[str, tuple[str, dict]]:
    salida: dict[str, tuple[str, dict]] = {}
    for p in sorted((base / AFIRMACIONES).glob("*.csv")):
        _, filas = leer_csv(p)
        for f in filas:
            # Un # repetido haría desaparecer una fila del diff sin aviso.
            # parse_research.py ya lo trata como error de conformidad.
            if f["#"] in salida:
                raise SystemExit(f"ERROR {base}: {f['#']} aparece en {salida[f['#']][0]}.csv "
                                 f"y en {p.name}; el diff no puede emparejar un # repetido")
            salida[f["#"]] = (p.stem, f)
    return salida


def _num(cid: str) -> tuple[int, str]:
    m = re.search(r"\d+", cid)
    return (int(m.group()) if m else 10**9, cid)


def _mascara(valor: str) -> str:
    # Las síntesis citan otras filas —«sintesis(C-0411)»— y la renumeración
    # cambia esas citas aunque la afirmación sea la misma. Para emparejar se
    # comparan con los números tapados; la comparación final, ya con el mapa de
    # renumeración, dirá si la cita cambió de verdad.
    return C_REF.sub("C-#", valor)


def _contenido(fila: dict) -> str:
    return json.dumps(sorted((k, _mascara(v)) for k, v in fila.items() if k != "#"), ensure_ascii=False)


def _expandir(valor: str) -> str:
    """Escribe cada rango «C-001–C-003» como la lista de claves que cubre.

    Traducir sólo los extremos de un rango esconde cambios de verdad: si se
    inserta una fila entre C-001 y C-002, «C-001–C-003» pasa a «C-001–C-004» y
    parece pura renumeración, aunque ahora cita también la fila nueva; y una
    fila retirada dentro del rango no aparece nunca. Se compara lo que el rango
    cita, no cómo se escribe. Un rango disparatado se deja como está.
    """
    def lista(m: re.Match) -> str:
        ta, tb = m.group(1), m.group(2)
        a, b = int(ta), int(tb)
        if b < a or b - a > RANGO_MAX:
            return m.group(0)
        return ", ".join(f"C-{n:0{len(ta)}d}" for n in range(a, b + 1))
    return C_RANGO.sub(lista, valor)


def equivale(antes: str, despues: str, mapa: dict[str, str]) -> bool:
    """¿Dice lo mismo `antes`, renumerado, que `despues`?"""
    return traducir(_expandir(antes), mapa) == _expandir(despues)


def traducir(valor: str, mapa: dict[str, str]) -> str:
    return C_REF.sub(lambda m: mapa.get(m.group(), m.group()), valor)


def emparejar(viejas: dict, nuevas: dict) -> tuple[list[tuple[str, str, str]], set, set]:
    orden_v, orden_n = sorted(viejas, key=_num), sorted(nuevas, key=_num)
    pos_v = {c: k for k, c in enumerate(orden_v)}
    pos_n = {c: k for k, c in enumerate(orden_n)}
    libres_v, libres_n = set(viejas), set(nuevas)
    pares: dict[str, tuple[str, str]] = {}

    def unir(i: str, j: str, via: str) -> None:
        pares[i] = (j, via)
        libres_v.discard(i)
        libres_n.discard(j)

    def elegir(i: str, candidatos: list[str]) -> str | None:
        vivos = [j for j in candidatos if j in libres_n]
        if not vivos:
            return None
        # Mismo número; si no, misma sección; si no, la posición más parecida.
        return min(vivos, key=lambda j: (j != i, nuevas[j][0] != viejas[i][0], abs(pos_n[j] - pos_v[i])))

    # 1 · mismo número y mismo contenido
    for i in orden_v:
        if i in libres_n and viejas[i][1] == nuevas[i][1]:
            unir(i, i, "número y contenido")

    # 2 · mismo contenido con otro número: una renumeración
    por_contenido = defaultdict(list)
    for j in orden_n:
        if j in libres_n:
            por_contenido[_contenido(nuevas[j][1])].append(j)
    for i in [c for c in orden_v if c in libres_v]:
        j = elegir(i, por_contenido[_contenido(viejas[i][1])])
        if j:
            unir(i, j, "contenido")

    # 3 · mismo texto de afirmación: se corrigió alguna otra columna
    por_texto = defaultdict(list)
    for j in orden_n:
        texto = _mascara(nuevas[j][1].get("Afirmación", "").strip())
        if j in libres_n and texto:
            por_texto[texto].append(j)
    for i in [c for c in orden_v if c in libres_v]:
        texto = _mascara(viejas[i][1].get("Afirmación", "").strip())
        j = elegir(i, por_texto[texto]) if texto else None
        if j:
            unir(i, j, "texto de la afirmación")

    # 4 · posición: entre dos vecinos ya emparejados quedan tantas filas viejas
    # como nuevas, en la misma sección. Es una reescritura en el sitio. Si los
    # números no cuadran —se reescribió una y se insertó otra— no se adivina:
    # quedan como retiradas y nuevas, y el informe lo dice.
    k = 0
    while k < len(orden_v):
        if orden_v[k] not in libres_v:
            k += 1
            continue
        inicio = k
        while k < len(orden_v) and orden_v[k] in libres_v:
            k += 1
        hueco_v = orden_v[inicio:k]
        antes = pos_n[pares[orden_v[inicio - 1]][0]] if inicio > 0 else -1
        despues = pos_n[pares[orden_v[k]][0]] if k < len(orden_v) else len(orden_n)
        if antes >= despues:
            continue  # los vecinos se cruzaron: no hay hueco que alinear
        hueco_n = [j for j in orden_n[antes + 1:despues] if j in libres_n]
        if len(hueco_v) == len(hueco_n) and all(
                viejas[i][0] == nuevas[j][0] for i, j in zip(hueco_v, hueco_n)):
            for i, j in zip(hueco_v, hueco_n):
                unir(i, j, "posición")

    lista = [(i, j, via) for i, (j, via) in pares.items()]
    return sorted(lista, key=lambda p: _num(p[1])), libres_v, libres_n


def comparar_afirmaciones(a: Path, b: Path) -> dict:
    viejas, nuevas = leer_afirmaciones(a), leer_afirmaciones(b)
    pares, retiradas, anadidas = emparejar(viejas, nuevas)
    mapa = {i: j for i, j, _ in pares}
    # Una cita a una afirmación retirada ya no apunta a nada, o apunta a otra
    # si su número lo ocupa ahora una fila renumerada. Se traduce a una forma
    # que no coincide con ningún número, para que nunca pase por igual.
    for i in retiradas:
        mapa[i] = f"{i}[retirada]"

    sin_cambios, renumeradas, modificadas = 0, [], []
    afectadas: dict[str, Counter] = defaultdict(Counter)
    for i, j, via in pares:
        (sec_v, fv), (sec_n, fn) = viejas[i], nuevas[j]
        # Nada se da por igual antes de traducir: una fila idéntica byte a byte
        # cuya cita apunta a una afirmación renumerada ya no dice lo mismo.
        columnas = {}
        for col in sorted(set(fv) | set(fn)):
            if col == "#":
                continue
            antes, despues = fv.get(col, ""), fn.get(col, "")
            if not equivale(antes, despues, mapa):
                columnas[col] = [antes, despues]
        if sec_v != sec_n:
            columnas["(sección)"] = [sec_v, sec_n]
        if columnas:
            modificadas.append({"de": i, "a": j, "via": via, "seccion": sec_n, "columnas": columnas})
            afectadas[sec_n]["modificadas"] += 1
            if sec_v != sec_n:
                # La sección de origen perdió la fila: también hay que reingerirla.
                afectadas[sec_v]["salidas"] += 1
        elif i == j and fv == fn:
            sin_cambios += 1
        else:
            renumeradas.append({"de": i, "a": j})

    nuevas_l = [{"id": j, "seccion": nuevas[j][0]} for j in sorted(anadidas, key=_num)]
    retiradas_l = [{"id": i, "seccion": viejas[i][0]} for i in sorted(retiradas, key=_num)]
    for n in nuevas_l:
        afectadas[n["seccion"]]["nuevas"] += 1
    for r in retiradas_l:
        afectadas[r["seccion"]]["retiradas"] += 1

    return {
        "anterior": len(viejas),
        "nueva": len(nuevas),
        "sin_cambios": sin_cambios,
        "solo_renumeracion": renumeradas,
        "modificadas": modificadas,
        "nuevas": nuevas_l,
        "retiradas": retiradas_l,
        "secciones_afectadas": {s: dict(c) for s, c in sorted(afectadas.items())},
        "mapa": mapa,
    }


def comparar_registro(pa: Path | None, pb: Path | None, mapa: dict[str, str]) -> dict:
    cab_a, filas_a = leer_csv(pa) if pa and pa.exists() else ([], [])
    cab_b, filas_b = leer_csv(pb) if pb and pb.exists() else ([], [])
    clave = (cab_b or cab_a or [None])[0]
    # Las dos versiones se comparan con los rangos ya expandidos.
    filas_a = [{k: _expandir(v) for k, v in f.items()} for f in filas_a]
    filas_b = [{k: _expandir(v) for k, v in f.items()} for f in filas_b]
    traducidas = [{k: traducir(v, mapa) for k, v in f.items()} for f in filas_a]

    # La clave también se traduce —B_entidades tiene etiquetas como «afirmación
    # C-1015», que la renumeración cambia sin cambiar la entidad—, y por eso la
    # unicidad se comprueba después de traducir: retirar C-001 y renumerar C-002
    # a C-001 hace colisionar dos claves que antes eran distintas. Y la clave
    # tiene que existir en las dos cabeceras.
    unica = (clave is not None
             and all(clave in cab for cab in (cab_a, cab_b) if cab)
             and len({t[clave] for t in traducidas}) == len(traducidas)
             and len({f[clave] for f in filas_b}) == len(filas_b))
    res = {"filas": [len(filas_a), len(filas_b)], "cabecera_cambiada": bool(cab_a and cab_b and cab_a != cab_b)}

    # Las filas que cambiaron de verdad, en su versión: sus citas C-… dicen qué
    # secciones del corredor las usan, y por tanto cuáles hay que reingerir.
    viejas_cambiadas: list[dict] = []
    nuevas_cambiadas: list[dict] = []

    if unica:
        va = {t[clave]: (f, t) for f, t in zip(filas_a, traducidas)}
        vb = {f[clave]: f for f in filas_b}
        comunes = va.keys() & vb.keys()
        modificadas = sorted(k for k in comunes if va[k][1] != vb[k])
        res.update({
            "clave": clave,
            "nuevas": sorted(vb.keys() - va.keys()),
            "retiradas": sorted(va.keys() - vb.keys()),
            "modificadas": modificadas,
            "solo_renumeracion": sorted(k for k in comunes if va[k][0] != vb[k] and va[k][1] == vb[k]),
        })
        viejas_cambiadas = [va[k][0] for k in (*res["retiradas"], *modificadas)]
        nuevas_cambiadas = [vb[k] for k in (*res["nuevas"], *modificadas)]
    else:
        # Sin clave única (F_magnitudes repite magnitud): una fila corregida
        # aparece como una retirada más una nueva, y así se declara.
        forma = lambda f: json.dumps(f, sort_keys=True, ensure_ascii=False)
        fa, fb = Counter(forma(t) for t in traducidas), Counter(forma(f) for f in filas_b)
        # De las filas viejas que casan con una nueva, cuántas casan sólo gracias
        # a la traducción: se cuentan primero las que ya eran idénticas, y el
        # resto es renumeración. Nunca puede salir negativo.
        cambiadas = Counter(forma(t) for f, t in zip(filas_a, traducidas) if f != t)
        renumeradas = 0
        for k, n in (fa & fb).items():
            identicas = fa[k] - cambiadas[k]
            renumeradas += n - min(n, identicas)
        res.update({
            "clave": None,
            "nuevas": sum((fb - fa).values()),
            "retiradas": sum((fa - fb).values()),
            "modificadas": [],
            "solo_renumeracion": renumeradas,
        })
        solo_a, solo_b = fa - fb, fb - fa
        viejas_cambiadas = [f for f, t in zip(filas_a, traducidas) if solo_a[forma(t)] > 0]
        nuevas_cambiadas = [f for f in filas_b if solo_b[forma(f)] > 0]
    res["citas_viejas"] = sorted({c for f in viejas_cambiadas for v in f.values() for c in C_REF.findall(v)})
    res["citas_nuevas"] = sorted({c for f in nuevas_cambiadas for v in f.values() for c in C_REF.findall(v)})
    return res


def cmd_diff(args) -> int:
    a, b = abrir(args.anterior), abrir(args.nueva)
    fa = {f["path"]: f["sha256"] for f in ficheros(a.base)}
    fb = {f["path"]: f["sha256"] for f in ficheros(b.base)}
    cambiados = sorted(p for p in fa.keys() & fb.keys() if fa[p] != fb[p])
    nuevos, retirados = sorted(fb.keys() - fa.keys()), sorted(fa.keys() - fb.keys())
    tocados = set(cambiados) | set(nuevos) | set(retirados)

    af = comparar_afirmaciones(a.base, b.base)
    registros = {}
    for carpeta in REGISTROS:
        nombres = {Path(p).name for p in tocados if p.startswith(carpeta + "/") and p.endswith(".csv")}
        for nombre in sorted(nombres):
            registros[f"{carpeta}/{nombre}"] = comparar_registro(
                a.base / carpeta / nombre, b.base / carpeta / nombre, af["mapa"])

    # Un fichero idéntico byte a byte también puede haber cambiado de sentido:
    # si cita C-0412 y C-0412 se renumeró, su cita apunta ahora a otra fila.
    # Cuando el mapa mueve algo, se revisan todos los que citan.
    desfasados: set[str] = set()
    if any(i != j for i, j in af["mapa"].items()):
        for ruta in sorted(fa.keys() & fb.keys()):
            if ruta in tocados or ruta.startswith(AFIRMACIONES + "/"):
                continue
            texto = (a.base / ruta).read_text(encoding="utf-8", errors="replace")
            if C_REF.search(texto) and not equivale(texto, texto, af["mapa"]):
                desfasados.add(ruta)
    tocados |= desfasados
    for carpeta in REGISTROS:
        for ruta in sorted(desfasados):
            if ruta.startswith(carpeta + "/") and ruta.endswith(".csv"):
                registros[ruta] = comparar_registro(a.base / ruta, b.base / ruta, af["mapa"])

    def estado(ruta: str) -> str:
        if ruta in nuevos:
            return "nuevo"
        if ruta in retirados:
            return "retirado"
        if ruta in desfasados:
            return "citas desactualizadas"
        antes = (a.base / ruta).read_text(encoding="utf-8", errors="replace")
        despues = (b.base / ruta).read_text(encoding="utf-8", errors="replace")
        return "sólo renumeración" if equivale(antes, despues, af["mapa"]) else "cambiado"

    def en(prefijo: str) -> list[dict]:
        return [{"path": p, "estado": estado(p)} for p in sorted(tocados) if p.startswith(prefijo + "/")]

    # La sección se ingiere con su prosa y sus tablas, no sólo con sus filas:
    # un cambio sólo de prosa también la manda a reingerir.
    prosa, tablas = en(PROSA), en(TABLAS)
    afectadas = af["secciones_afectadas"]
    # Y con las filas de los apéndices que citan sus afirmaciones: una entidad
    # del apéndice B cuya primera fila es de la sección 3 se ingiere con la 3.
    sec_vieja = {i: s for i, (s, _) in leer_afirmaciones(a.base).items()}
    sec_nueva = {i: s for i, (s, _) in leer_afirmaciones(b.base).items()}
    # El índice de tablas decide qué tabla es el registro de una sección y cuál
    # una síntesis, y con eso de qué pasaje sale una fila. Cambiar una entrada
    # cambia la sección que la usa.
    indice = "data/table_index.json"
    if indice in tocados:
        def entradas(base: Path) -> dict[str, dict]:
            ruta = base / indice
            if not ruta.exists():
                return {}
            return {e["id"]: e for e in json.loads(ruta.read_text(encoding="utf-8")).get("tables", [])}
        ea, eb = entradas(a.base), entradas(b.base)
        for tid in sorted(ea.keys() | eb.keys()):
            if ea.get(tid) == eb.get(tid):
                continue
            # Las dos: si una entrada cambia de sección, la de origen la pierde y
            # la de destino la gana, y las dos cambian de procedencia.
            secciones = set()
            for e in (ea.get(tid), eb.get(tid)):
                partes = Path((e or {}).get("csv_path", "")).parts
                sec = (Path(partes[-1]).stem if partes[:2] == ("data", "afirmaciones")
                       else partes[2] if partes[:2] == ("data", "tablas") and len(partes) > 3 else None)
                if sec:
                    secciones.add(sec)
            for sec in secciones:
                afectadas.setdefault(sec, {})
                afectadas[sec]["índice"] = afectadas[sec].get("índice", 0) + 1

    for ruta, r in registros.items():
        tocadas = ({sec_vieja[c] for c in r.get("citas_viejas", []) if c in sec_vieja}
                   | {sec_nueva[c] for c in r.get("citas_nuevas", []) if c in sec_nueva})
        for sec in tocadas:
            afectadas.setdefault(sec, {})
            afectadas[sec]["apéndices"] = afectadas[sec].get("apéndices", 0) + 1
    for lista, clave, seccion in ((prosa, "prosa", lambda r: [s for s in Path(r).name.split("-")[1:2] if s.isdigit()]),
                                  (tablas, "tablas", lambda r: Path(r).parts[2:3])):
        for x in lista:
            sec = seccion(x["path"])
            if x["estado"] != "sólo renumeración" and sec:
                afectadas.setdefault(sec[0], {})
                afectadas[sec[0]][clave] = afectadas[sec[0]].get(clave, 0) + 1
    af["secciones_afectadas"] = dict(sorted(afectadas.items()))

    conocidas = (AFIRMACIONES, *REGISTROS, PROSA, TABLAS)
    informe = {
        "anterior": {"fuente": a.etiqueta, "commit": a.commit, **metadatos(a.base), "fingerprint": huella(ficheros(a.base))},
        "nueva": {"fuente": b.etiqueta, "commit": b.commit, **metadatos(b.base), "fingerprint": huella(ficheros(b.base))},
        "ficheros": {"cambiados": cambiados, "nuevos": nuevos, "retirados": retirados},
        "afirmaciones": {k: v for k, v in af.items() if k != "mapa"},
        "registros": registros,
        "prosa": prosa,
        "tablas_de_sintesis": tablas,
        "otros": [{"path": p, "estado": estado(p)} for p in sorted(tocados)
                  if not any(p.startswith(c + "/") for c in conocidas)],
    }

    imprimir(informe, args.detalle)
    if args.json:
        Path(args.json).write_text(json.dumps(informe, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"\ninforme completo en {args.json}")
    return 0


def imprimir(inf: dict, detalle: bool) -> None:
    va, vn = inf["anterior"], inf["nueva"]
    print(f"{va['fuente']} ({va['version']}) → {vn['fuente']} ({vn['version']})")
    f = inf["ficheros"]
    if va["fingerprint"] == vn["fingerprint"]:
        print("  misma huella: la capa canónica es idéntica")
        return
    print(f"  capa canónica: {len(f['cambiados'])} ficheros cambiados, {len(f['nuevos'])} nuevos, "
          f"{len(f['retirados'])} retirados")

    af = inf["afirmaciones"]
    print(f"\nafirmaciones  {af['anterior']} → {af['nueva']}")
    print(f"  sin cambios          {af['sin_cambios']:>5}")
    print(f"  sólo renumeración    {len(af['solo_renumeracion']):>5}")
    cols = Counter(c for m in af["modificadas"] for c in m["columnas"])
    print(f"  modificadas          {len(af['modificadas']):>5}"
          + (f"   {' · '.join(f'{c} {n}' for c, n in cols.most_common())}" if cols else ""))
    print(f"  nuevas               {len(af['nuevas']):>5}")
    print(f"  retiradas            {len(af['retiradas']):>5}")
    if af["secciones_afectadas"]:
        print("  secciones que reingerir:")
        for s, c in af["secciones_afectadas"].items():
            print(f"    {s}  " + " · ".join(f"{n} {k}" for k, n in sorted(c.items())))

    if inf["registros"]:
        print("\nregistros   (+ nuevas · − retiradas · ~ modificadas · = sólo renumeración)")
        for ruta, r in inf["registros"].items():
            extra = "" if r["clave"] else "  sin clave única: una corrección cuenta como − y +"
            print(f"  {Path(ruta).name[:44]:44} +{_n(r['nuevas'])} −{_n(r['retiradas'])} "
                  f"~{_n(r['modificadas'])} ={_n(r['solo_renumeracion'])}{extra}")

    for titulo, clave in (("prosa", "prosa"), ("tablas de síntesis", "tablas_de_sintesis"), ("otros", "otros")):
        if inf[clave]:
            reales = [x for x in inf[clave] if x["estado"] != "sólo renumeración"]
            print(f"\n{titulo}: {len(inf[clave])} ficheros tocados, "
                  f"{len(inf[clave]) - len(reales)} sólo por renumeración")
            for x in reales:
                print(f"  {x['estado']:9} {x['path']}")

    if detalle:
        for m in af["modificadas"]:
            print(f"\n{m['de']} → {m['a']}  (por {m['via']}, sección {m['seccion']})")
            for col, (antes, despues) in m["columnas"].items():
                print(f"  {col}\n    − {antes}\n    + {despues}")
        for etiqueta, lista in (("nueva", af["nuevas"]), ("retirada", af["retiradas"])):
            for x in lista:
                print(f"\n{etiqueta}: {x['id']} (sección {x['seccion']})")


def _n(x) -> int:
    return x if isinstance(x, int) else len(x)


def _rel(p: Path) -> str:
    try:
        return str(p.resolve().relative_to(ROOT))
    except ValueError:
        return str(p)


def main() -> int:
    ap = argparse.ArgumentParser(description="Congela y compara versiones del corpus de investigación")
    sub = ap.add_subparsers(dest="orden", required=True)

    c = sub.add_parser("create", help="congela una versión")
    c.add_argument("fuente", help="directorio del corpus, o directorio@ref")
    c.add_argument("--salida", help="ruta del manifiesto (por defecto, en knowledge/corpus/manifests/)")
    c.add_argument("--repositorio", default="santiqwerty1/corredor-eukaryota-holozoa")
    c.add_argument("--decision", default=None, help="DEC-… que autoriza esta congelación")
    c.add_argument("--sustituye", default=None, help="manifiesto de la congelación anterior")
    c.add_argument("--fecha", default=None, help="fecha de congelación (por defecto, hoy)")
    c.set_defaults(func=cmd_create)

    v = sub.add_parser("verify", help="comprueba una copia contra una congelación")
    v.add_argument("fuente")
    v.add_argument("manifiesto")
    v.set_defaults(func=cmd_verify)

    d = sub.add_parser("diff", help="qué cambió entre dos versiones")
    d.add_argument("anterior")
    d.add_argument("nueva")
    d.add_argument("--detalle", action="store_true", help="columna a columna, afirmación por afirmación")
    d.add_argument("--json", default=None, metavar="FICHERO", help="escribir el informe completo")
    d.set_defaults(func=cmd_diff)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
