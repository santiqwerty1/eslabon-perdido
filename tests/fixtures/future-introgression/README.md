# Fixture `future-introgression`

**Esto no es contenido de ninguna campaña.** No pertenece a la Campaña 1 «Eucaria» ni a
la campaña hominina. Es una prueba de que la arquitectura conserva una capacidad futura,
en el sentido del **Apéndice J.4** de la guía: «un evento de introgresión entre
poblaciones». También figura como fixture número 9 de §27.9. Los datos son de prueba;
**no son corpus** y no deben reingestarse como tales.

Rango de identificadores reservado: **730000–730999**.

## Qué capacidad prueba

Que **la dirección de un proceso vive en los papeles del evento, no en la arista**, y que
lo que se sigue de esos papeles se registra como afirmación derivada y no como cita.

- `EVENT-730030` es de tipo `introgression` y tiene dos participantes con papeles
  distintos: `POP-730010` como `donor` y `POP-730011` como `recipient`.
- `CLAIM-730001` (`introgression_from`) es lo que la fuente afirma: sujeto la población
  receptora, objeto la donante.
- `CLAIM-730002` (`contributes_ancestry_to`) recorre **el mismo par en sentido
  contrario**, y es correcta. No es una contradicción: el sentido lo fija el predicado.
  Lleva `derivation.rule`, `derivation.depends_on_ids: [EVENT-730030, EVID-730040]` y
  `provenance.origin: "derived"`.
- `TIME-730050` data el evento por referencia. `EVID-730040` declara sus limitaciones.

Es el caso de §9.4 (`contributes_ancestry_to` se deriva de un evento de introgresión con
papeles) y de §14.2.

## Por qué existe

Porque un grafo de aristas etiquetadas no sabe expresar esto. Si la introgresión se
guardara como una arista `A → B`, harían falta convenios implícitos sobre qué significa la
punta de la flecha, y la respuesta cambia según el predicado que se lea: en
`introgression_from` apunta hacia el donante y en `contributes_ancestry_to` hacia el
receptor. El evento resuelve el problema poniendo la dirección donde es inequívoca —en el
papel de cada participante— y dejando que las afirmaciones se deriven de ahí.

El fixture prueba de paso que la derivación es **reversible**: `CLAIM-730002` declara de
qué depende, así que retirar o corregir los papeles de `EVENT-730030` la invalida de forma
detectable. Una derivada que no declarase su dependencia se quedaría en el registro como
un hecho huérfano cuando su origen desapareciera.

Cuatro decisiones del contenido son deliberadas:

- **`proportion` es `null` en los dos participantes.** El campo existe y §13.1 lo prevé
  para porcentajes, pero cuantificar la aportación exige una fuente que la mida. El
  fixture no fabrica cifras. Que el campo quede vacío no es un descuido: es la respuesta
  correcta cuando la fuente no cuantifica.
- **`result_entity_ids` va vacío.** Una introgresión no crea un linaje nuevo. El campo
  existe para los eventos que sí lo hacen (`hybrid_origin`), y distinguir ambos casos es
  parte de lo que se prueba.
- **`TIME-730050` tiene los dos límites a `null`.** Un límite nulo significa extremo
  abierto, no cero (§11.2). La incertidumbre se declara igualmente (`kind: unknown`),
  porque ausencia de dato no es precisión, y `determination: inferred` impide que una
  estimación se lea como una medición.
- **`EVID-730040` declara que no distingue introgresión de estructura ancestral
  compartida.** La alternativa se conserva escrita como limitación en vez de descartarse
  en silencio.

## Qué debe fallar si el esquema se rompe

Este fixture deja de validar, y esa es su función, si alguien:

- **reduce `Event` a un par de nodos**, o elimina `participants[].role`: la distinción
  donante/receptor desaparece y las dos afirmaciones se vuelven contradictorias;
- **recorta el enum de papeles** quitando `donor` o `recipient`;
- **elimina `introgression` del enum de `event_type`**, o fusiona los tipos reticulados en
  uno solo;
- **quita `derivation` de `claim.json`**, o hace opcionales `rule` y `depends_on_ids`:
  `CLAIM-730002` pasará a ser indistinguible de algo que una fuente escribió;
- **saca `contributes_ancestry_to` o `introgression_from`** del vocabulario de predicados;
- **impone que un par de entidades tenga una sola relación**, o que la relación sea
  simétrica: las dos afirmaciones de sentido opuesto dejarán de convivir;
- **hace obligatorio `result_entity_ids` no vacío**;
- **exige límites numéricos en `interval`**, o elimina `uncertainty.kind: unknown` o
  `determination`: el evento tendrá que inventarse una fecha para poder datarse;
- **singulariza `temporal_expression_ids`**: dos dataciones incompatibles ya no podrán
  convivir sin promediarse.

La comprobación de invariantes verifica además que el sentido de la derivada **coincide
con los papeles del evento** y que es inverso al de la afirmación expresa. Si alguien
alinea las dos en el mismo sentido, el fixture seguirá validando pero habrá dejado de
probar que la dirección no está en la arista.
