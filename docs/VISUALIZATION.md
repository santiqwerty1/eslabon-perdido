# Leyenda visual

Convenciones iniciales de §20. Se amplían cuando el Atlas llegue en la Fase 8.

**Principio:** una visualización es una **vista derivada**, no el almacén de conocimiento.

## Relaciones

El trazo codifica el estado epistémico. No es decoración.

| Trazo | Significado |
|---|---|
| Línea continua | backbone seleccionado |
| Línea discontinua | hipótesis alternativa |
| Línea punteada | relación especulativa |
| Flecha lateral etiquetada | flujo génico o transferencia |
| Participantes conectados a un nodo-evento | hibridación, endosimbiosis o proceso n-ario |
| Borde tenue | clasificación histórica o superada |
| Signo de interrogación | posición no resuelta |

## Nodos

Se distinguen por **forma, etiqueta o patrón**, nunca sólo por color: taxón · concepto taxonómico · clado · población · linaje · espécimen · evento · rasgo · hipótesis · ancestro no muestreado.

## Hipótesis incompatibles

Se representan mediante vistas separadas, capas activables, pequeños múltiplos, overlays etiquetados o comparación lado a lado.

**No se dibujan todas las alternativas como si fueran simultáneamente verdaderas.** Es el equivalente visual de no mezclar topologías incompatibles en un solo árbol.

## Endosimbiosis

Nunca se dibuja como una bifurcación ordinaria. Es un evento n-ario con participantes y roles, y así debe verse.

## Accesibilidad

- Legible en blanco y negro.
- Formas y patrones redundantes con el color.
- Etiquetas textuales.
- Descripciones alternativas.
- Control de densidad y zoom semántico.
- Navegación por teclado en la interfaz futura.

Esto no es sólo accesibilidad. Como el trazo carga el significado epistémico, si el color fuera el portador, la distinción entre backbone e hipótesis alternativa desaparecería al imprimir o ante un daltonismo. El rigor y la accesibilidad piden aquí lo mismo.

## Eje de tiempo · «Relojes y rocas»

`make views` construye `generated/views/cronologia.html` desde los registros activos (`scripts/build_views/cronologia.py`). Es una vista derivada: no escribe en `knowledge/` y dos ejecuciones sobre los mismos registros dan los mismos bytes.

Pone en un eje en millones de años lo que dicen los relojes moleculares y lo que registran las rocas. Cada afirmación `dated_to` activa es una marca. Su datación decide el carril: la modelada por un método (`determination: modelled`) es un reloj; la observada o inferida del registro, una roca. Las estimaciones de un mismo evento conviven sin promediarse.

Un eje de tiempo no dibuja relaciones, así que el trazo de arriba no le sirve. Usa estas convenciones, redundantes con el texto y sin color:

| Marca | Significado |
|---|---|
| Barra | intervalo de una estimación o de una fecha |
| Rombo | fósil con fecha aproximada, sin intervalo |
| Barra de extremos redondos o círculo | biomarcador |
| Corchete | unidad de roca datada |
| Flecha en un extremo | la fecha sigue más allá del eje o no tiene ese límite |
| Relleno lleno, rayado, hueco o de borde discontinuo | fuerza de la evidencia de la afirmación: alta, media, baja o desconocida |
| Signo de interrogación | posición no resuelta |

La escala usa los límites y los colores de la carta cronoestratigráfica internacional (ICS v2023/09); el color acompaña siempre al rótulo de la unidad. Con esa carta se sitúan también las dataciones que el corpus da como intervalo con nombre («Mesoproterozoico»).

Toda afirmación activa queda en un solo sitio, y la página dice cuál: en el eje, en «por qué no coinciden» (métodos y lo que condiciona una fecha), en la ficha de una marca (lo que se afirma de lo que la marca data) o fuera, con su motivo. Las hipótesis rivales sobre un fósil se leen lado a lado en su ficha y no se dibujan en el eje.

## La red por hipótesis

`make views` construye también las vistas filogenéticas (`scripts/build_views/red.py`, `DEC-061`). Sus registros `PHYVIEW-` van a `knowledge/views/phylogenetic-views.jsonl` y su página a `generated/views/red.html`. Cada identificador sigue al conjunto de hipótesis de su vista, y la versión sube sólo si cambia el contenido. La fecha de corte es la del corpus congelado, así que dos ejecuciones sobre los mismos registros dan los mismos bytes.

Hay una vista del **tronco común**, que reúne las afirmaciones de topología sin alcance de hipótesis, y una por cada hipótesis con topología. Cada una es el tronco más una sola hipótesis. Las rivales del mismo grupo de conflicto no se dibujan juntas (§20.3), y los conflictos que la vista no decide quedan en politomía. La página pone las hipótesis de cada conflicto lado a lado, como pequeños múltiplos centrados en el nodo en disputa. Al elegir una se abre su ficha, con:

- el árbol entero;
- lo que la vista no dibuja;
- las exclusiones, por motivo;
- el Newick.

**Cómo se arma el árbol.**

- `member_of` cuelga cada nodo de su padre más interno.
- `sister_group_of` junta dos hermanos, y un nodo sin nombre los agrupa si comparten padre con otros.
- `stem_lineage_of` pone un linaje en el tronco de un clado, y `diverges_from` sólo se comprueba.
- Una población (LECA) no es rama: se anota en su nodo.
- En el conflicto de la raíz de Eukaryota, la afirmación hermana de la hipótesis es la primera divergencia. Si un lado es «el resto», recibe todo lo demás. Si el otro lado estaba en lo hondo del tronco, el árbol se re-enraíza, y los clados del camino dejan de serlo.

Cada afirmación seleccionada se cumple en el árbol; la que no, se excluye con su motivo. También quedan fuera:

- las derivadas;
- las de otras hipótesis;
- las históricas del tronco;
- las que cuelgan algo de un concepto taxonómico, que son clasificación según una fuente (§4.3) y no topología.

Lo que el libro mayor no declara y la vista necesita leer está en `knowledge/view-specs/red.json`. Allí se dice qué conflicto decide qué primera divergencia, qué clados son «el resto» y qué miembros tiene cada clado compuesto, y cada vista cita la lectura que usó.

| Marca | Significado |
|---|---|
| Rama continua | tronco común |
| Rama discontinua | la pone la hipótesis de la vista, o sale de su re-enraizado |
| Rama punteada y «?» | sin lado declarado en la raíz de la hipótesis |
| Círculo lleno | clado |
| Rombo hueco | concepto taxonómico, con su *sensu* |
| Triángulo | linaje |
| Círculo hueco | clado sin nombre |
| Cursiva | el resto de los eucariotas, según la hipótesis |
| Asterisco | miembros leídos de la especificación |
| +n | nodos plegados en la miniatura |

**Lo que encontró la primera construcción** (`REV-000010`), para el libro mayor:

- **H27 (raíz en Opisthokonta)** rompe Amorphea, Obazoa, CRuMs+Amorphea y Apusomonadida+Opisthokonta como clados con raíz. Además contradice once afirmaciones del tronco que HYP-000014 no declara en `excluded_claim_ids`.
- **Clados compuestos sin miembros:** CLADE-000025, CLADE-000036 y CLADE-000049 no tienen afirmaciones `member_of`. Los complementos CLADE-000018 y CLADE-000019 no tienen afirmación que los defina. Todo esto lo lee la especificación de sus fichas.
- **Raíces sin contenido:** H23 (Unikonta–Bikonta) y H28 (Opimoda+–Diphoda+) enraízan sobre nodos sin miembros declarados, y el resto queda sin lado. H26 no trae afirmación de raíz: sus afirmaciones clasifican.
- **Fuera del árbol:**
  - Discoba no aparece en el tronco, porque ninguna afirmación lo ubica en Eukaryota.
  - Ancyromonadida sólo se relaciona con CRuMs+Amorphea por `diverges_from`, que no lo ubica en el árbol.
  - El clado Pluriformea (CLADE-000039) y el concepto Pluriformea de Hehenberger et al. (TAXCONCEPT-000032) no están enlazados, así que Corallochytrea, *Syssomonas* y *Corallochytrium* quedan sueltos.

## Bandas poblacionales · `RETENIDO` para prototipo

Las poblaciones pueden representarse como bandas temporales cuya anchura exprese tamaño efectivo, abundancia relativa, diversidad o incertidumbre.

**Una semántica por vista.** El ancho no puede significar cuatro cosas a la vez. La elección concreta está abierta (`OPEN-008`).

## Herramientas

| Herramienta | Uso |
|---|---|
| Mermaid | diagramas pequeños y documentación |
| Graphviz DOT | relaciones complejas y salidas reproducibles |
| Newick / **Extended Newick** | intercambio filogenético; el extendido es el que admite reticulación |
| Interfaz interactiva | fases posteriores (`OPEN-005`) |
