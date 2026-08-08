# Fixture `future-specimen-assignment`

**Esto no es contenido de ninguna campaña.** No pertenece a la Campaña 1 «Eucaria» ni a
la campaña hominina. Es una prueba de que la arquitectura conserva una capacidad futura,
en el sentido del **Apéndice J.4** de la guía: «un espécimen con asignaciones
alternativas». También figura como fixture número 10 de §27.9. Los datos son de prueba;
**no son corpus** y no deben reingestarse como tales.

Rango de identificadores reservado: **740000–740999**.

## Qué capacidad prueba

Que **una afirmación negativa convive con la positiva sin borrarla**. Es el caso literal
de §9.2.

- `SPECIMEN-740010` tiene dos asignaciones alternativas de fuentes distintas:
  `CLAIM-740001` (a `TAXCONCEPT-740001`, según `SRC-740001`) y `CLAIM-740002` (a
  `TAXCONCEPT-740002`, según `SRC-740002`).
- **Ninguna está marcada como verdadera.** Las dos llevan la misma `acceptance` y
  `resolution: unresolved`.
- `CLAIM-740003` es la afirmación negativa: `SRC-740002` `rejects_claim` `CLAIM-740001`.
  El sujeto es la fuente y el objeto es la afirmación rechazada, porque lo que se registra
  es un acto de una fuente sobre una afirmación, no una relación biológica.
- **`CLAIM-740001` sigue con `record_status: active` después del rechazo.**
- `CLAIM-740004` registra el conflicto como afirmación derivada, y `ISSUE-740040` lo
  mantiene abierto.
- `EVID-740030` y `EVID-740031` apoyan una asignación y **cuestionan la rival con el mismo
  rango**: la misma observación material sostiene una lectura y ataca la otra.

## Por qué existe

Porque hay dos formas fáciles de perder esta información y las dos parecen limpieza.

La primera es poner un campo `taxon` en la entidad espécimen. Entonces sólo cabe una
asignación, y al incorporar la segunda hay que elegir. Por eso `SPECIMEN-740010` **no
tiene ningún campo taxonómico plano**: no existe el hueco que obligaría a decidir.

La segunda es tratar el rechazo como una retractación y desactivar la afirmación
rechazada. Eso convertiría la opinión de una fuente en un veredicto del proyecto. Aquí el
rechazo se añade al lado, no encima, y son las vistas las que deciden qué muestran y con
qué trazo — nunca las dos como simultáneamente ciertas.

Dos detalles del contenido son deliberados:

- **El espécimen no figura en `included_entity_ids` de ningún concepto.** La adscripción
  de un objeto físico a un concepto es una afirmación con fuente, no un hecho de la
  circunscripción. Meterlo dentro convertiría una asignación disputada en parte de la
  definición del taxón, y el conflicto desaparecería del registro sin que nadie lo
  borrase. Es el §7.7 aplicado: un espécimen no se convierte automáticamente en taxón.
- **Cada asignación transporta su propia contraevidencia** en `counterevidence_ids`. No
  vive en un apéndice aparte que se pueda leer por separado, ni depende de que alguien
  cruce los ficheros de evidencia para enterarse de que la afirmación está discutida.

## Qué debe fallar si el esquema se rompe

Este fixture deja de validar, y esa es su función, si alguien:

- **añade un campo taxonómico a la entidad espécimen** (`taxon`, `species`, `taxon_id`):
  sólo cabrá una asignación;
- **impone unicidad de `(subject_id, predicate)` en las afirmaciones**, o de
  `assigned_to` por espécimen;
- **saca `rejects_claim` del vocabulario de predicados**: la afirmación negativa no podrá
  expresarse y el rechazo tendrá que modelarse borrando o desactivando la positiva;
- **prohíbe que `subject_id` sea una fuente o que `object.entity_id` sea una afirmación**:
  el rechazo dejará de poder apuntar a lo que rechaza;
- **elimina `counterevidence_ids` de `claim.json`** o `challenges_claim_ids` de
  `evidence.json`: la contraevidencia dejará de viajar con la afirmación;
- **exige que una afirmación rechazada pase a `deprecated` o `superseded`**, o cualquier
  regla que obligue a resolver los conflictos antes de aceptarlos;
- **elimina `conflicting_claims` del enum de `issue_type`**.

La comprobación de invariantes verifica además tres cosas que el esquema por sí solo no
detecta: que `CLAIM-740001` **siga activa** tras el rechazo, que las dos asignaciones
conserven **dimensiones epistémicas simétricas**, y que el rechazo **proceda de una fuente
distinta** de la que hizo la asignación. Si alguien desempata las asignaciones o desactiva
la rechazada, el fixture seguirá validando contra el esquema pero habrá dejado de probar
lo único que le importa.
