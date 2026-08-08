# ADR-004 · Python para el tooling inicial

**Estado:** aceptado · **Fecha:** 7 de agosto de 2026 · **Resuelve:** `OPEN-001` · **Decisión de registro:** `DEC-051`

## Contexto

Las fases 0 a 7 son trabajo de datos: ingestión, validación de esquema, integridad referencial, deltas reversibles, snapshots reconstruibles, comprobaciones de aciclicidad por subgrafo y generación de diagramas reproducibles. No hay juego todavía, y el motor de juego (`OPEN-006`) está deliberadamente sin decidir hasta antes de la Fase 9.

## Decisión

**Python** para el tooling del núcleo científico.

## Razones

- El ecosistema de datos y grafos es el adecuado para lo que exige §19.2: `jsonschema` para las enumeraciones cerradas, recorridos de grafo para la aciclicidad de §6.9, bindings de Graphviz para las salidas reproducibles de §20.4.
- La Fase 0 exige como criterio de aceptación que **no exista dependencia del motor de juego**. Elegir el lenguaje del juego para el tooling acoplaría el núcleo en la dirección que §2.1 prohíbe.
- El Atlas de la Fase 8 consumirá JSONL, no código del tooling, así que puede escribirse en otro lenguaje sin fricción.

## Consecuencias

- El proyecto tendrá al menos dos lenguajes: uno para el núcleo y otro para Atlas y juego. Es el precio de la separación, y es deliberado.
- Las dependencias se declaran en `requirements.txt` y la CI las instala.

## Alternativas consideradas

TypeScript unificaría tooling y Atlas, pero tienta a acoplar el núcleo con la capa de juego. Rust daría garantías más fuertes de validación, pero ralentiza la iteración justo en las fases exploratorias y choca con el riesgo §29.2 de sobreingeniería antes de tener una campaña.
