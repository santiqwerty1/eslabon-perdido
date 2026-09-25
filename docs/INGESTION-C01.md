# Ingerir la investigación de la Campaña 1

Procedimiento concreto para ingerir la investigación encargada con [`C01-PROMPT-INVESTIGACION.md`](campaigns/C01-PROMPT-INVESTIGACION.md).

Llegó como repositorio propio, `corredor-eukaryota-holozoa`, con la capa de registro en CSV (`data/`) y la prosa por secciones (`docs/secciones/`). Se clona al lado de este repositorio; los ejemplos de abajo usan `../corredor-eukaryota-holozoa`. Y no llega una vez: su auditoría sigue abierta, así que la última sección de este documento explica cómo entra cada versión nueva.

Existe porque §4.6 dice que la conversación no es fuente de verdad, y eso vale también para el procedimiento, no sólo para los datos.

---

## Antes de nada: no lo leas entero

La guía se leyó por tramos porque había que **entenderla**. La investigación es corpus y hay que **procesarla**: su destino no es el contexto de nadie, sino `knowledge/records/*.jsonl`.

El documento tiene dos capas, y van por caminos distintos:

- **La capa de registro** —las tablas numeradas `C-001`, `C-002`…— **no se lee: se parsea.** Ya viene con sujeto, predicado, objeto, procedencia y los cuatro ejes epistémicos. Meterla en contexto sería gastar tokens en algo que un script hace mejor y sin equivocarse.
- **La capa narrativa** sí se lee, pero para segmentarla en pasajes localizables, que es lo que da procedencia a las filas.

---

## 1 · Contraste contra el prompt

```bash
.venv/bin/python scripts/ingest/parse_research.py ../corredor-eukaryota-holozoa
```

Comprueba conformidad, no contenido: columnas en orden, vocabularios cerrados, fuentes citadas que existen en el apéndice A, filas de síntesis que nombran su origen, fuerza de evidencia con motivo escrito, y el recuento de control contra lo que se cuenta de verdad.

**Un error aquí es un hallazgo sobre la investigación, no un fallo del parser.** Si el documento llega desviado del formato, eso se registra como `Issue` y se decide qué hacer: pedir corrección o adaptarse.

Lo que el parser **no** puede juzgar es si la ciencia es correcta. Para eso hace falta lectura humana de la capa narrativa y, llegado el caso, el modo auditoría de §18.2.

Sondeo dirigido a lo que más probablemente falle:

- **la sección terminológica**, donde el modelo tenderá a responder de memoria — el prompt exige fuente citable incluso para lo que «es de manual»;
- **las celdas de sinapomorfías**, donde inventar un carácter no publicado es el peor error posible;
- **las filas marcadas `glosa`**, que son comentario sin fuente y deben seguir siéndolo;
- **el reparto de esfuerzo**: si la eucariogénesis y la nomenclatura ocupan mucho más que la ecología y las magnitudes, el prompt no se respetó.

## 2 · Congelar el corpus

Antes de tocar nada, fijar qué versión se ingiere. Si la investigación se corrige o se amplía después, hay que poder demostrar qué versión se ingirió (`DEC-056`).

Con un documento único bastaban su hash y una copia en `inbox/`. El corpus es un repositorio con historia propia, así que no se copia: se registra el commit y la huella de su **capa canónica** —`data/` y `docs/secciones/`—, que es lo que se ingiere.

```bash
make corpus-freeze CORPUS=../corredor-eukaryota-holozoa@af7e799 DEC=DEC-056
make corpus-verify CORPUS=../corredor-eukaryota-holozoa \
     FREEZE=knowledge/corpus/manifests/corredor-v0.6.0-research-audit-af7e799.json
```

La primera congelación ya está hecha: `0.6.0-research-audit` en `af7e799`, 122 ficheros, huella `sha256:b53f15ad…a415`. Antes de cada sesión de ingestión, `corpus-verify` confirma que la copia de trabajo sigue siendo esa versión. Un commit que sólo regenere derivados del corredor —`exports/`, `manifest.json`, el informe— verifica igual; uno que toque `data/` o `docs/secciones/` es otra versión.

## 3 · Dividirla en secciones

**Una `SEC-` por sección de nivel 2 del documento, no una para todo.** En el repositorio del corredor esa partición ya viene hecha: cada sección es su prosa, `docs/secciones/NNN-….md`, más sus filas, `data/afirmaciones/NN.csv`.

Con diecinueve capítulos y miles de líneas, una sola sección daría un delta gigante, una tabla de cobertura inmanejable y ninguna forma de revertir una parte sin revertir el resto. Dividida, cada tramo tiene su delta, su auditoría, su informe y su snapshot, y se puede parar a mitad sin dejar el corpus en un estado intermedio.

## 4 · Probar el pipeline con el fixture, no con el corpus

```bash
make test
```

Si algo falla, se descubre con veinte menciones inventadas y no con tres mil reales. Es el orden que fija el Apéndice I: fixture en el paso 13, corpus real en el 21.

## 5 · Ingerir, sección por sección

```bash
make ingest FILE=knowledge/corpus/inbox/DOCUMENTO.md DRY=1   # ver sin escribir
make ingest FILE=knowledge/corpus/inbox/DOCUMENTO.md
```

Produce la sección con su hash, los pasajes con offsets, las menciones candidatas, el delta y el informe humano. **No aplica nada.**

> **Pendiente antes de la primera ingestión real.** `ingest.py` todavía recibe un único fichero de texto: está hecho para el documento Markdown que se esperaba. `parse_research.py` ya lee el repositorio de CSV, pero hay que enseñar a `ingest.py` a tomar una sección del corredor —su prosa y sus filas— y a anotar en el delta de qué congelación sale. Es el primer trabajo de la ingestión, y se prueba con el fixture antes de tocar el corpus, como dice el paso 4.

## 6 · Lo que hay que hacer a mano

Los pasos 5 a 9 de §17 son juicio y no se automatizan. Concretamente:

**Resolución de identidad.** Decidir si dos menciones son la misma entidad. La regla es ser conservador: **no se fusionan entidades por parecido nominal**. Ante duda, se deja sin resolver y se abre `Issue` — es lo que dice F.3, y bloquear el registro afectado no bloquea la sección entera.

**Integración de hipótesis.** Decidir si una afirmación apoya, contradice, parte una hipótesis existente o crea un grupo de conflicto. No se mezclan topologías incompatibles en un árbol.

Mientras queden menciones sin destino, `make validate` fallará por cobertura. Eso es correcto: §28.1 exige cobertura completa para dar una sección por terminada.

## 7 · Aplicar y verificar

```bash
.venv/bin/python scripts/ingest/delta.py SEC-000001.json --dry-run
.venv/bin/python scripts/ingest/delta.py SEC-000001.json
make check
```

Si algo salió mal:

```bash
.venv/bin/python scripts/ingest/delta.py SEC-000001.json --revert
```

## 8 · Cerrar la sección

```bash
make snapshot LABEL="SEC-000001 ingerida"
```

Una sección está terminada cuando la cobertura es completa, la procedencia está vinculada, las validaciones pasan, existen delta e informe, y **el estado se reconstruye sin la conversación**. Ese último punto se comprueba solo: `make check` en un clon limpio.

---

## Cuando llega una versión nueva del corpus

La auditoría del corredor sigue abierta y va a producir versiones nuevas. Ninguna se aplica encima de la congelada: cada una **se congela aparte, se compara con la anterior y sólo reingiere lo que cambió**.

```bash
# 1 · qué cambió, fila a fila
make corpus-diff ANTES=../corredor-eukaryota-holozoa@af7e799 DESPUES=../corredor-eukaryota-holozoa DETALLE=1

# 2 · congelar la versión nueva, enlazando la anterior
make corpus-freeze CORPUS=../corredor-eukaryota-holozoa@<commit> DEC=DEC-056 \
     SUSTITUYE=knowledge/corpus/manifests/corredor-v0.6.0-research-audit-af7e799.json
```

**Por qué hace falta un diff propio y no basta `git diff`.** El corredor renumera sus afirmaciones de forma global cuando se inserta una fila en una sección intermedia: una sola afirmación nueva en la sección 3 desplaza el `#` de todas las siguientes y reescribe todas las citas `C-…` de la prosa, las síntesis, los apéndices y las tablas. `git diff` diría que cambió casi todo. `freeze.py diff` empareja las afirmaciones por contenido, traduce las citas por el mapa de renumeración, y separa:

| Clase | Qué significa | Qué pide |
|---|---|---|
| sin cambios | misma fila, mismo `#` | nada |
| sólo renumeración | cambió el `#` o las citas `C-…`, y sólo por el desplazamiento | actualizar la correspondencia `#` → identificador opaco, sin delta de contenido |
| modificada | cambió alguna columna de verdad; dice cuáles y por qué vía se emparejó | delta de corrección sobre la afirmación existente: el original se conserva (§16.4, criterio de la Fase 2) |
| nueva | no tiene antecesora | ingestión ordinaria |
| retirada | no tiene sucesora | deprecar con motivo, nunca borrar |

Probado sobre el corpus real: una afirmación insertada en la sección 3 más una fuente corregida en la 9, renumeradas con el propio `renumber.py` del corredor, dan 1 nueva, 1 modificada y 1.774 «sólo renumeración», no 1.953 cambios.

**Qué no resuelve.** Si en un mismo hueco se reescribe una afirmación **y** se inserta otra, el diff no adivina cuál es cuál: las declara retirada y nuevas, y quien ingiere decide. Tampoco juzga si el cambio es correcto: eso sigue siendo §27.12.

**Por qué los identificadores opacos importan aquí.** El `C-0412` del corredor no es una identidad estable; el `CLAIM-000412` de este proyecto sí (`DEC-052`). Una afirmación renumerada conserva su identificador opaco y sólo cambia su localizador en el corpus. Si se hubieran usado las claves del corredor como identidad, cada pasada de auditoría las habría roto todas.

## Qué se cierra al ingerir

Seis cuestiones de `ISSUES.md` se escribieron para cerrarse ingiriendo. Cinco ya están cerradas sin haber ingerido nada, y la sexta cambió de campaña:

| | | Cómo quedó |
|---|---|---|
| `ISSUE-000010` | catálogo terminológico eucariota — el prompt lo pide con más de veinte términos | resuelta por contenido: sección 14 del corpus |
| `ISSUE-000013` | fecha de corte, que el documento declara al principio | resuelta por `DEC-056`: la fija la versión congelada |
| `ISSUE-000014` | ingerir la fuente y no el Apéndice A, que es un resumen sin citas | sin objeto: la Campaña 1 ya no parte de `Filogenia.md` |
| `ISSUE-000016` | la afirmación sin procedencia de C.16 tendrá fuente o será `Issue` | abierta, reencuadrada a la campaña del clado tardío |
| `ISSUE-000017` | la capa de procedencia entra por su vía correcta | resuelta por contenido: 492 DOI sobre 523 fuentes |
| `ISSUE-000021` | el contenido científico del corredor que los apéndices no traen | resuelta por contenido |

«Resuelta por contenido» quiere decir que el material existe y se puede contar, no que esté ingerido: al ingerir, esas afirmaciones siguen pasando por los pasos 5 a 9 como cualquier otra.

## Una advertencia sobre el Apéndice A

Es un **índice de cobertura**, no material de ingestión. No lleva citas, así que ingerirlo activaría la cláusula del paso 7 de §17 y todo su contenido entraría marcado «procedente de la sección, para verificación futura».

Se usa para comprobar que nada del inventario quedó sin representar. No para poblar el corpus.
