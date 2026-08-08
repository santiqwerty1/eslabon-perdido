# Fixture `future-denisovan-lineage`

**Esto no es contenido de ninguna campaña.** No pertenece a la Campaña 1 «Eucaria» ni a
la campaña hominina. Es una prueba de que la arquitectura conserva una capacidad futura,
en el sentido del **Apéndice J.4** de la guía: «un linaje denisovano sin nombre
específico estable». También figura como fixture número 8 de §27.9. Los datos son de
prueba; **no son corpus** y no deben reingestarse como tales.

Rango de identificadores reservado: **720000–720999**.

## Qué capacidad prueba

Que una **entidad puede tener identidad y evidencia sin tener nombre**.

- `LINEAGE-720010` existe, tiene descripción, evidencia y afirmaciones.
- Su identidad se sostiene sobre `CLAIM-720001`, respaldada por `EVID-720040` (evidencia
  genómica sobre `SPECIMEN-720020`), **no sobre una denominación**.
- Hay tres denominaciones registradas y ninguna es un hecho:
  - `NAME-720001` y `NAME-720002` son propuestas (`nomenclatural_status: informal`),
    cada una con su fuente;
  - `NAME-720003` es el nombre vernáculo.
- Cada propuesta se materializa como concepto con fuente (`TAXCONCEPT-720001` y
  `TAXCONCEPT-720002`), ambos `provisional`. **Ninguno está `accepted`.**
- `ISSUE-720050` mantiene abierta la cuestión de la denominación.

Es el caso de §7.5: un linaje «puede existir sin nombre taxonómico formal».

## Por qué existe

Porque el impulso natural al modelar es hacer del nombre la clave de la entidad. Si lo
fuera, un linaje sin nombre consensuado no podría registrarse hasta que alguien zanjara
la nomenclatura, y el sistema estaría obligado a esperar a que la literatura se pusiera
de acuerdo para poder decir algo que la evidencia ya sostiene.

Aquí el identificador es opaco (§16.3) y no deriva de ningún nombre. La consecuencia
práctica es la que importa: si mañana una denominación llega a adoptarse, se cambia el
`taxonomic_status` del concepto correspondiente y **no hay que reescribir el
identificador ni romper una sola referencia**.

Dos decisiones del contenido son deliberadas y conviene no «corregirlas»:

- **Las propuestas no figuran en `alias_ids` del linaje.** Sólo el nombre vernáculo lo
  hace. Un alias afirma que dos etiquetas designan lo mismo; una propuesta afirma que
  alguien *sugiere* llamarlo así. Meter la propuesta entre los alias la convertiría en un
  hecho por la puerta de atrás. Las propuestas se enlazan como conceptos con fuente y
  como afirmaciones (`CLAIM-720002`, `CLAIM-720003`).
- **Las dos adscripciones rivales llevan exactamente las mismas dimensiones
  epistémicas.** El sistema no desempata. `CLAIM-720004` registra la rivalidad, y lo hace
  como afirmación **derivada**, porque ninguna de las dos fuentes menciona a la otra:
  atribuirles una comparación que no hicieron sería inventar procedencia.
- **`authorship` es `null` en los tres nombres.** El fixture no atestigua autoría y §7.2
  prohíbe reconstruirla de memoria. La ausencia se declara, no se rellena.

Este fixture es el reverso exacto de `future-hominini-homonym`: allí un nombre servía a
dos circunscripciones distintas; aquí dos nombres compiten por una circunscripción
idéntica. Los dos casos tienen que caber en el mismo esquema.

## Qué debe fallar si el esquema se rompe

Este fixture deja de validar, y esa es su función, si alguien:

- **hace obligatorio un `name_id` en la entidad**, o convierte el nombre en clave de
  identidad: `LINEAGE-720010` dejará de poder existir;
- **exige que todo `TaxonConcept` tenga `taxonomic_status: accepted`**, o elimina
  `provisional` del enum: las propuestas ya no podrán registrarse como propuestas;
- **elimina `informal` o `vernacular` de `nomenclatural_status`**: no habrá forma de
  distinguir una denominación propuesta de una establecida;
- **prohíbe que dos conceptos declaren la misma circunscripción**: las dos propuestas
  rivales dejarán de caber;
- **hace obligatorio `authorship`**: el fixture tendrá que inventar autoría para validar,
  que es exactamente lo que §7.2 prohíbe;
- **quita `derivation` de `claim.json`**: `CLAIM-720004` no podrá distinguirse de una
  comparación que alguna fuente hubiera hecho;
- **exige que todo `Issue` tenga `proposed_resolution` cerrada**: la cuestión abierta
  tendrá que fingir una respuesta.

La comprobación de invariantes verifica además que **ningún concepto esté `accepted`** y
que las dos adscripciones conserven la misma aceptación. Si alguien «mejora» el fixture
promoviendo una propuesta, seguirá validando contra el esquema pero habrá dejado de
probar la capacidad.
