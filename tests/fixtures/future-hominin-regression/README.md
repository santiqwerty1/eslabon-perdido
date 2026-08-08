# `future-hominin-regression`

**Este directorio no contiene registros.** Es el contenedor conceptual de los cuatro fixtures `future-*`, que viven como hermanos suyos en `tests/fixtures/`:

| Fixture | Capacidad que protege |
|---|---|
| [`future-hominini-homonym`](../future-hominini-homonym/) | dos conceptos taxonómicos distintos con el mismo nombre `Hominini` |
| [`future-denisovan-lineage`](../future-denisovan-lineage/) | un linaje con identidad y evidencia pero sin nombre formal consensuado |
| [`future-introgression`](../future-introgression/) | un evento de flujo génico con roles `donor` y `recipient` |
| [`future-specimen-assignment`](../future-specimen-assignment/) | un espécimen con asignaciones alternativas y una afirmación negativa que convive con la positiva |

## Por qué existe con este nombre

§16.2 lista `tests/fixtures/future-hominin-regression/` en el árbol del repositorio, mientras §27.9 y el Apéndice I nombran los cuatro fixtures individuales. Se leyó al principio como una discrepancia de nombres; no lo es. **El del árbol es el contenedor, los del catálogo son sus miembros.** Queda registrado en `docs/ISSUES.md` como `ISSUE-000015`, cerrada.

## Qué prueban, y qué NO son

No son contenido de ninguna campaña. La Campaña 1 cubre Eukaryota → Holozoa y no toca homininos ni de lejos. Existen porque el Apéndice J.4 exige que el esquema siga admitiendo siete capacidades que no se implementarán hasta la Fase 17, y la única forma de garantizarlo es **comprobarlo en cada ejecución de las pruebas**, no confiar en que alguien se acuerde.

Las tres capacidades restantes de J.4 las cubren fixtures ordinarios: [`historical-classification`](../historical-classification/) para una taxonomía superada, [`observed-vs-inferred-time`](../observed-vs-inferred-time/) para un rango observado distinto del inferido, y [`two-deep-topologies`](../two-deep-topologies/) para una vista de consenso con alternativas.

## Qué debería fallar

Si alguien simplificara el modelo de identidad de modo que un nombre implicara una circunscripción única, `future-hominini-homonym` dejaría de validar. Ése es exactamente el punto: **el fixture es la alarma que suena cuando una decisión de hoy cierra una puerta de la Fase 17.**
