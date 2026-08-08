# Fixture `future-hominini-homonym`

**Esto no es contenido de ninguna campaña.** No pertenece a la Campaña 1 «Eucaria» ni a
la campaña hominina. Es una prueba de que la arquitectura conserva una capacidad futura,
en el sentido del **Apéndice J.4** de la guía: «el esquema debe seguir pasando estos
casos, aunque no se implementen en Campaña 1». También figura como fixture número 7 de
§27.9. Los datos son de prueba; **no son corpus** y no deben reingestarse como tales.

Rango de identificadores reservado: **710000–710999**.

## Qué capacidad prueba

Que **dos conceptos taxonómicos distintos pueden compartir el mismo nombre**.

- `NAME-710001` «Hominini» es un **único** registro de nombre.
- `TAXCONCEPT-710001`, según `SRC-710001`, lo circunscribe como *Pan* + *Homo*.
- `TAXCONCEPT-710002`, según `SRC-710002`, lo reserva al linaje humano posterior a la
  separación de *Pan*, y **excluye a *Pan* expresamente**.
- Los dos quedan relacionados a la vez como `incompatible` y como `conceptual_homonym`,
  y cada relación respalda su anotación con una afirmación real (`CLAIM-710001` y
  `CLAIM-710002`), no con una nota al margen.

Es el caso central del modelo de identidad: **el nombre no contiene circunscripción**
(§7.2). El ejemplo está tomado literalmente del árbol conceptual de §7.3.

## Por qué existe

Porque es el caso que rompe el atajo más tentador: guardar «Hominini» como una etiqueta
con un contenido fijo. Si el sistema hiciera eso, ingerir la segunda fuente sólo podría
terminar de tres maneras, y las tres son pérdidas de información:

1. sobrescribir la circunscripción anterior;
2. crear un segundo nombre `Hominini (sensu B)`, que convierte una diferencia de
   circunscripción en una diferencia de grafía;
3. elegir un uso «correcto» y descartar el otro.

El fixture fija la cuarta salida: un nombre, dos conceptos, cada uno atado a su fuente
por `according_to_source_id`. Ese campo es obligatorio precisamente por esto (§7.3): sin
él las dos circunscripciones quedarían confundidas bajo la misma etiqueta.

Tres decisiones del contenido merecen atención porque son deliberadas:

- **Los dos conceptos están `accepted`.** No es contradicción: `taxonomic_status` es el
  estado dentro de la clasificación de su fuente, no un veredicto del proyecto.
- **`phylogenetic_interpretation` es `not_assessed` en ambos.** §7.4 prohíbe inferir que
  un taxón formal sea monofilético por el hecho de existir.
- **La exclusión de *Pan* viaja en `excluded_entity_ids`, no en el silencio.** Un lector
  que sólo mire `included_entity_ids` no puede distinguir «excluido» de «no mencionado»;
  el segundo concepto dice expresamente lo primero.

No existe ninguna afirmación de no pertenencia: el vocabulario cerrado de §14 no tiene
`not_member_of`. La negación expresa se modela con `excluded_entity_ids` y, cuando una
fuente rechaza a otra, con el predicado `rejects_claim` — ver el fixture
`future-specimen-assignment`.

## Qué debe fallar si el esquema se rompe

Este fixture deja de validar, y esa es su función, si alguien:

- **hace `name_id` único por concepto**, o mete la circunscripción dentro de
  `TaxonomicName`: los dos conceptos ya no podrán compartir `NAME-710001`;
- **vuelve opcional `according_to_source_id`**: se podrán crear dos conceptos
  indistinguibles y el fixture dejará de demostrar nada, aunque siga validando;
- **quita `excluded_entity_ids` de `circumscription`**: la exclusión expresa de *Pan* se
  vuelve indistinguible de una omisión;
- **recorta el enum de `relation_to_other_concepts`** eliminando `incompatible` o
  `conceptual_homonym`;
- **saca `incompatible_with` o `alternative_to` del vocabulario de predicados** de
  `claim.json`;
- **exige que `phylogenetic_interpretation` sea concluyente**, sin `not_assessed`;
- **impone unicidad de `(name_id, rank)`** o cualquier restricción que obligue a que un
  nombre tenga una sola circunscripción vigente.

Además, la comprobación de invariantes debe seguir verificando que las dos
circunscripciones **difieren de verdad**: si alguien «arregla» el fixture igualándolas,
sigue validando contra el esquema pero ya no prueba nada.
