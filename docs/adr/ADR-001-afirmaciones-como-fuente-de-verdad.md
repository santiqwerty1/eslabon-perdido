# ADR-001 · Las afirmaciones son la fuente de verdad

**Estado:** aceptado · **Fecha:** 7 de agosto de 2026 · **Decisión de registro:** `DEC-002`, `DEC-001`, `DEC-003`

## Contexto

Un proyecto que representa filogenia puede organizarse alrededor del gráfico —nodos y aristas como dato primario— o alrededor de lo que las fuentes sostienen. La primera opción es más fácil de dibujar y más difícil de defender: obliga a elegir una topología antes de saber si la evidencia la respalda, y no deja sitio para taxonomías rivales, hipótesis minoritarias ni historia de las clasificaciones.

## Decisión

La unidad central del conocimiento es la **afirmación científica respaldada o cuestionada por evidencia**, no una arista. Árboles, redes y clasificaciones son **vistas derivadas** de conjuntos de afirmaciones compatibles y fechadas.

La cadena canónica es: corpus → menciones → entidades normalizadas → afirmaciones → evidencia y análisis → hipótesis compatibles → vistas → proyecciones de juego.

## Consecuencias

- El grafo global admite relaciones dirigidas, no dirigidas y simétricas, y la aciclicidad se exige **por subgrafo**, no globalmente.
- `EDGE-` queda reservado para aristas materializadas en exportaciones y **nunca** es la identidad canónica de una afirmación.
- Toda vista declara su fecha de corte, sus criterios editoriales y **lo que excluye**.
- El coste es real: nada se dibuja sin antes existir como afirmación con procedencia.

## Alternativas rechazadas

Un árbol único como dato primario (`DEC-001`), y almacenar las relaciones reticuladas como flechas binarias sin evento (`DEC-024`).
