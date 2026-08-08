# Fixture `research-format`

**Qué es:** el molde del formato que exige
[`docs/campaigns/C01-PROMPT-INVESTIGACION.md`](../../../docs/campaigns/C01-PROMPT-INVESTIGACION.md),
en tres piezas y para tres preguntas distintas:

| Fichero | Pregunta que contesta |
|---|---|
| `SEC-SAMPLE.md` | ¿reconoce el parser un documento bien formado? Debe pasar con 0 errores. |
| `SEC-SAMPLE-BAD.md` | ¿detecta el parser un documento mal formado? Debe fallar, y fallar por lo que se rompió a propósito. |
| `generate_scale.py` | ¿aguanta el parser el documento **de verdad**? Fabrica uno del mismo formato y las mismas dimensiones. |

`tests/run_tests.py` ejecuta los dos primeros. El tercero no se ejecuta en la
suite: produce un fichero de 1 MiB y su sitio es una medición deliberada, no un
test que corre en cada cambio.

**Qué NO es:** corpus. Ninguno de los tres ficheros contiene ciencia. Las
etiquetas llevan el prefijo `FIX-`, los DOI apuntan al prefijo reservado
`10.0000/` y los repositorios a dominios `.invalid`, que por RFC 2606 no
resuelven nunca. §5.1 prohíbe inventar contenido científico; esto no lo es y no
puede confundirse con ello. Por eso la salida del generador va a `generated/`
—que está en `.gitignore`— y no a `knowledge/`.

---

## Por qué hacía falta un fixture a escala

`SEC-SAMPLE.md` tiene seis filas. Prueba que el formato se reconoce y no prueba
nada sobre el coste. La investigación de la Campaña 1 llega declarando

> 8.330 líneas · 1.593 afirmaciones · 425 fuentes · 1.335 entidades · 99 eventos ·
> 77 hipótesis · 249 registros temporales · 384 magnitudes · 76 búsquedas negativas

y el paso 1 del [manual de ingestión](../../../docs/INGESTION-C01.md) es pasarle
`parse_research.py`. Conviene saber antes de que llegue si eso tarda un segundo o
un minuto, y qué comprobación se degrada al crecer. Medirlo con seis filas es
medir el arranque del intérprete.

## El generador

```bash
.venv/bin/python tests/fixtures/research-format/generate_scale.py
.venv/bin/python tests/fixtures/research-format/generate_scale.py --help
```

Todas las dimensiones son parámetros y sus valores por defecto son los reales
(`--afirmaciones`, `--fuentes`, `--entidades`, `--eventos`, `--fechas`,
`--hipotesis`, `--magnitudes`, `--busquedas-negativas`, `--lineas`). Genera las
ocho tablas de apéndices del prompt con sus columnas exactas —A fuentes, B
entidades, C eventos, D fechas, E hipótesis, F magnitudes, G material no
encajado, H recuento de control— más la capa narrativa, los árboles, la matriz de
compatibilidad, la vista de resumen por nodo, la tipología de desenlaces, la
tabla de costes y las búsquedas negativas.

### Determinismo

Misma semilla y mismos parámetros ⇒ **mismo fichero byte a byte**, comprobable
con `cmp`. Para conseguirlo:

- el generador aleatorio es propio (splitmix64, dentro del script). `random` no
  garantiza la misma secuencia entre versiones de Python, y aquí «determinista»
  significa que dos ejecuciones se comparan con `diff`;
- no se lee el reloj: la fecha de corte y la de consulta son `--corte`;
- los repartos se calculan con aritmética entera y desempate por nombre, no con
  coma flotante;
- se itera siempre sobre listas, nunca sobre `set`.

La extensión se ajusta en dos pasadas: la primera mide el esqueleto tabular, la
segunda añade párrafos de prosa —dos líneas cada uno— hasta clavar `--lineas`.
Si las tablas por sí solas ya superan el objetivo, avisa por `stderr` y **no
recorta**: perder filas para cuadrar una cifra sería el error que este fixture
existe para detectar en otros.

### Los dos parámetros que se atan entre sí

`--entidades` no puede superar `--afirmaciones`, porque cada fila introduce como
mucho una entidad. Y por debajo hay un segundo límite menos evidente: las
primeras doce filas tienen que introducir clados **sin depender de nada
anterior**, y esas filas salen del reparto de las entidades creadoras, es decir
de `--entidades` menos `--gemelos` y `--homonimos`. Con los valores por defecto de
gemelos y homónimos el mínimo practicable es `--entidades 41`; por debajo el
generador se planta y dice exactamente qué subir. **Subir `--afirmaciones` no
arregla ese caso**, y el mensaje lo dice para que nadie lo intente.

### Los casos difíciles que trae a propósito

Un documento de 1.593 filas iguales no probaría nada que no pruebe uno de seis.
Éstos son los que el documento real va a tener:

| Caso | Cómo aparece | Por qué importa |
|---|---|---|
| **Etiquetas casi idénticas que no son la misma entidad** | `FIX-Alfa-0001` y `FIX-Alfa-0001 sensu stricto`, dos filas de B y una fila del registro con predicado `no_sinonimo_de*`. Cada gemelo estrena base: `--gemelos 6` da seis parejas distintas, no cinco y un duplicado | es la trampa del paso 5 de §17: la resolución de identidad por parecido nominal. La regla es no fusionar (F.3) |
| **Homónimo conceptual** | la misma `etiqueta preferida` en dos filas de B, con dos circunscripciones y dos fuentes distintas | un nombre, dos contenidos. El prompt lo exige explícitamente: «una fila por circunscripción, con su fuente» |
| **Síntesis que citan otras filas** | `sintesis(C-0012, C-0031)`, **siempre hacia atrás** | ninguna síntesis puede depender de una fila posterior, y el generador lo garantiza por construcción |
| **Afirmación negativa junto a la positiva** | `carece_de_rasgo*` sobre el mismo sujeto y objeto que una fila `posee_rasgo` anterior, nombrándola | §9.2: la fila cuestionada se conserva intacta, no se corrige ni se suaviza |
| **Fuentes de calidad desigual** | preprints sin revisar, síntesis secundarias, trabajos corregidos, y **sin DOI**: unas con URL resoluble y otras con el literal `DOI no verificado` | el parser debe tolerarlas y las notas de calidad deben etiquetarlas, no descartarlas |

Las etiquetas gemelas y las homónimas entran además en el mismo repertorio que
las demás, así que circulan por la prosa, por los eventos y por las tablas de
resumen igual que cualquier otra: la ambigüedad no está aislada en un rincón del
documento, que es exactamente como llegará.

El documento generado cumple también los controles globales que la investigación
real declara limpios, y se han comprobado uno a uno sobre la salida: 0
referencias `C-…` colgantes, 0 huecos en las secuencias `C`/`S`/`E`/`H`, 0 filas
de tabla con distinto número de celdas que su cabecera, 0 síntesis con
dependencia posterior, 0 oraciones `[SIN FUENTE]`.

---

## Lo medido

Máquina: AMD Ryzen 7 5800H, 16 GiB, Linux 6.18 (WSL2), CPython 3.11.2 de
`.venv`. Documento canónico: semilla 20260807, 8.330 líneas, 1.046 KiB.

### A las dimensiones reales

| Medida | Valor |
|---|---|
| `parse()` en proceso, mediana de 9 pasadas | **89 ms** (mínimo 83 ms, máximo 105 ms) |
| comando completo `parse_research.py DOC` | **173 ms** de mediana, de los que ~24 ms son arranque del intérprete |
| comando completo con `--out DIR` | **245 ms**; `parsed.json` ocupa 1,8 MiB |
| memoria asignada por `parse()` (`tracemalloc`, pico) | **6,9 MiB** |
| RSS máximo del proceso de medida | **30 MiB** |
| conformidad | **0 errores, 0 avisos** |

**No se rompe nada y no se degrada nada perceptible.** El paso 1 de la ingestión
cuesta menos de dos décimas de segundo sobre el documento entero, y la memoria es
irrelevante: el fichero de 1 MiB en memoria más las estructuras derivadas caben
en 7 MiB. Leer el documento con `--out` cuesta más en serializar el intermedio
que en analizarlo.

Las cifras de milisegundos son de una máquina concreta y se mueven un 10–20 %
entre tandas; lo que no se mueve, y es lo que importa, son el orden de magnitud y
la forma de la curva de abajo.

### Cómo escala

El mismo generador con las dimensiones multiplicadas, para ver la forma de la
curva y no un solo punto:

| Escala | KiB | líneas | afirmaciones | `parse()` mediana | pico asignado |
|---|---|---|---|---|---|
| ×1 (real) | 1.046 | 8.330 | 1.593 | 89 ms | 6,9 MiB |
| ×2 | 2.102 | 16.660 | 3.186 | 245 ms | 13,7 MiB |
| ×4 | 4.231 | 33.320 | 6.372 | 927 ms | 27,5 MiB |
| ×8 | 8.510 | 66.640 | 12.744 | 5.181 ms | 55,0 MiB |

La memoria crece lineal, como debe. **El tiempo no**: ×2 de tamaño cuesta ×2,8
de tiempo, y ×8 cuesta ×58. Hay un término cuadrático.

### El término cuadrático, localizado

`cProfile` lo señala sin ambigüedad: una sola línea,
`scripts/ingest/parse_research.py:273`, se lleva el **73 %** del tiempo de
`parse()` en la escala ×8 (4,92 s de 6,72 s, en 1.446 llamadas) y el **16 %** a
las dimensiones reales (0,033 s de 0,210 s, en 180 llamadas). El perfilador infla
los absolutos; el reparto es el que cuenta.

```python
if a["attribution"].startswith("sintesis") or a["attribution"].startswith("síntesis"):
    for r in a["attribution_refs"]:
        if r not in {x["local_id"] for x in afirmaciones}:   # ← se reconstruye cada vez
```

El conjunto de identificadores locales se reconstruye entero **en cada
comprobación de cada referencia de cada síntesis**. Es O(síntesis × afirmaciones)
donde debería ser O(síntesis). Cuatro líneas más abajo, la comprobación de los
apéndices ya hace lo correcto —`locales = {a["local_id"] for a in afirmaciones}`,
una vez, fuera del bucle—, así que es un descuido puntual y no un patrón.

**A las dimensiones reales no importa:** son 180 reconstrucciones de un conjunto
de 1.593 elementos, 33 ms. La ingestión no va a notarlo. Se documenta porque es
el único punto del parser cuyo coste depende del cuadrado del tamaño, porque el
documento «aún crece», y porque arreglarlo es mover una línea: sacar el `setcomp`
fuera del bucle reutilizando el `locales` que ya se calcula cuatro líneas más
abajo.

---

## Cómo reproducir la medición

```bash
# 1. generar el documento canónico
.venv/bin/python tests/fixtures/research-format/generate_scale.py

# 2. comprobar que es determinista
.venv/bin/python tests/fixtures/research-format/generate_scale.py -o /tmp/a.md
.venv/bin/python tests/fixtures/research-format/generate_scale.py -o /tmp/b.md
cmp /tmp/a.md /tmp/b.md            # sin salida = idénticos byte a byte

# 3. medir el paso 1 de la ingestión
time .venv/bin/python scripts/ingest/parse_research.py generated/research-scale/SEC-SCALE.md

# 4. ver dónde se va el tiempo cuando crece
.venv/bin/python tests/fixtures/research-format/generate_scale.py -o /tmp/x8.md \
  --afirmaciones 12744 --entidades 10680 --fuentes 3400 --eventos 792 \
  --hipotesis 616 --fechas 1992 --magnitudes 3072 --busquedas-negativas 608 \
  --lineas 66640
.venv/bin/python -c "
import cProfile, pstats, sys
sys.path.insert(0, 'scripts/ingest'); import parse_research
from pathlib import Path
cProfile.run('parse_research.parse(Path(\"/tmp/x8.md\"))', '/tmp/perf')
pstats.Stats('/tmp/perf').sort_stats('cumulative').print_stats(8)"
```

Cuando cambien las dimensiones declaradas por la investigación, se cambian los
valores por defecto en la cabecera del generador (`DIM_*`) y se vuelve a medir.
