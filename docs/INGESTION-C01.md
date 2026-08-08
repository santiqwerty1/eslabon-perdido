# Ingerir la investigación de la Campaña 1

Procedimiento concreto para cuando llegue el documento encargado con [`C01-PROMPT-INVESTIGACION.md`](campaigns/C01-PROMPT-INVESTIGACION.md).

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
.venv/bin/python scripts/ingest/parse_research.py RUTA/AL/DOCUMENTO.md
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

Antes de tocar nada, hash y copia inmutable. Si la investigación se corrige o se amplía después, hay que poder demostrar qué versión se ingirió.

```bash
sha256sum RUTA/AL/DOCUMENTO.md
cp RUTA/AL/DOCUMENTO.md knowledge/corpus/inbox/
```

## 3 · Dividirla en secciones

**Una `SEC-` por sección de nivel 2 del documento, no una para todo.**

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

## Qué se cierra al ingerir

Seis cuestiones de `ISSUES.md` no se arreglan editando, sino ingiriendo:

| | |
|---|---|
| `ISSUE-000010` | catálogo terminológico eucariota — el prompt lo pide con más de veinte términos |
| `ISSUE-000013` | fecha de corte, que el documento declara al principio |
| `ISSUE-000014` | ingerir la fuente y no el Apéndice A, que es un resumen sin citas |
| `ISSUE-000016` | la afirmación sin procedencia de C.16 tendrá fuente o será `Issue` |
| `ISSUE-000017` | la capa de procedencia entra por su vía correcta |
| `ISSUE-000021` | el contenido científico del corredor que los apéndices no traen |

## Una advertencia sobre el Apéndice A

Es un **índice de cobertura**, no material de ingestión. No lleva citas, así que ingerirlo activaría la cláusula del paso 7 de §17 y todo su contenido entraría marcado «procedente de la sección, para verificación futura».

Se usa para comprobar que nada del inventario quedó sin representar. No para poblar el corpus.
