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
