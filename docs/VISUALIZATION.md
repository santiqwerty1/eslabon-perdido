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
