# Fixture `game-projection-eukarya`

Fixture 6 de §27.9: **una simplificación jugable**, y el caso limpio de la familia `separation`.

## Qué capacidad prueba

Que la capa 8 pueda **referenciar** el núcleo científico sin **tocarlo**. §6.8 lo dice del lado
del almacenamiento: la proyección referencia entidades, afirmaciones, eventos y vistas, pero
mantiene sus propios datos, y esos datos *no se guardan dentro de cada nodo científico*.

`GAME-900201` referencia quince registros científicos por identificador y declara, en campos
propios, todo lo que el juego necesita y la ciencia no tiene:

| Campo | Qué contiene aquí |
|---|---|
| `scientific_reference_ids` | los cinco clados del corredor, los dos linajes, las cinco afirmaciones, el evento, la hipótesis y la vista |
| `abstraction` | que la unidad jugable es una población celular con variables, y que el núcleo no tiene tal cosa |
| `simplifications` | cuatro, cada una con su advertencia científica |
| `scientific_constraints` | seis, incluida la prohibición de alterar afirmaciones para equilibrar |
| `justification` | por qué la simplificación sigue siendo aceptable |
| `active_variables` | las variables del módulo, incluido el coste energético de la asociación |

**Ningún registro científico del fixture contiene costes, bonificaciones ni condiciones de
victoria.** La palabra «coste» aparece una sola vez en todo el directorio, dentro de
`projections/game-projections.jsonl`.

## La dirección de la dependencia

```text
projections/game-projections.jsonl      GAME-900201
                                            │
                          scientific_reference_ids
                                            ▼
  clades · lineages · claims · events · hypotheses · phylogenetic-views
                                            │
                                            ╳   nunca en este sentido
```

El fixture separa físicamente las dos capas, igual que §16.2 separa `knowledge/` de `game/`:

```text
game-projection-eukarya/
├── sources.jsonl  clades.jsonl  lineages.jsonl  claims.jsonl
├── events.jsonl   hypotheses.jsonl  issues.jsonl              ← como knowledge/records/
├── phylogenetic-views.jsonl                                    ← como knowledge/views/
└── projections/game-projections.jsonl                          ← como game/projections/
```

La familia `separation` decide la capa por el **prefijo del identificador**, no por la carpeta:
un `GAME-` entre los registros científicos es una violación aunque el fichero se llame como
toque. La separación en dos directorios permite además que una prueba reapunte
`separation.PROJECTION_DIRS` a `projections/` sin tocar el repositorio real, que es para lo que
esas rutas son constantes de módulo.

## Qué comprobación de `separation` falla si alguien invierte la dependencia

**La comprobación 4, «dirección de las referencias»** (`_check_direction`). Es la única que ve la
inversión. Verificado sobre este fixture inyectando `alias_ids: ["GAME-900201"]` en
`CLADE-900201`:

```text
ERROR  separación: clades.jsonl:CLADE-900201.alias_ids[0] apunta a GAME-900201, una
       GameProjection: la referencia sólo va en el sentido contrario (§6.8). Si el núcleo
       depende del juego, borrar el módulo de campaña rompe datos científicos (§27.10)
```

Lo importante es **quién no lo detecta**:

- **`schema` no lo detecta.** `entity.json/alias_ids` usa `common.json#/$defs/id`, que es la
  unión de todos los prefijos de §16.3 e incluye `GAME-`, `MECH-`, `CAMP-` y `CHAPTER-`. El
  patrón encaja y el registro es válido.
- **`references` tampoco.** Comprueba que todo identificador referenciado exista, y
  `GAME-900201` existe. Una referencia colgada sería un error; una referencia perfectamente
  resuelta en el sentido prohibido, no.

Es decir: la separación de capas **no se puede delegar en JSON Schema**. Si esa comprobación se
retira o se debilita, la inversión entra sin ruido, y con ella la consecuencia que §27.10
prohíbe: eliminar el módulo `c01-eukarya` pasaría a romper datos científicos. Registrado en
`ISSUE-900202`.

### Las otras dos mutaciones que deben seguir fallando

Este fixture es el caso limpio. Los casos sucios se derivan de él con una sola edición y cada uno
dispara una comprobación distinta:

| Mutación | Comprobación que dispara | Mensaje |
|---|---|---|
| `alias_ids: ["GAME-900201"]` en `CLADE-900201` | 4, dirección de las referencias | `…alias_ids[0] apunta a GAME-900201…` |
| `"upkeep_cost": 3` en `CLADE-900201` | 1, el núcleo no contiene mecánica | `…es vocabulario de mecánica (cost, upkeep) dentro del núcleo científico…` |
| `"predicate": "member_of"` en `GAME-900201` | 2, la proyección no reescribe | `…es un campo del núcleo científico ('predicate') dentro de la capa de juego…` |

La segunda mutación la atrapan **dos** familias: `schema`, porque todos los esquemas científicos
llevan `additionalProperties: false`, y `separation`, por el nombre de la clave. La redundancia
es deliberada: un coste escondido en un campo ya permitido, como `notes` o
`quantitative_support.measure_type`, se le escapa a `schema` y sólo queda `separation`.

## Lo demás que prueba

- **La ausencia no es dato.** `EVENT-900201` deja `result_entity_ids` y `temporal_expression_ids`
  vacíos porque el orden relativo de la integración mitocondrial sigue discutido y el fixture no
  ingiere ninguna fuente que lo fije. Rellenarlos elegiría un escenario o inventaría una fecha.
  Registrado en `ISSUE-900201`.
- **Roles, no aristas.** El evento tiene dos participantes con papeles distintos, `host` y
  `endosymbiont`. Un par de nodos dirigido no puede expresar eso.
- **Linajes sin nombre.** `LINEAGE-900201` y `LINEAGE-900202` no tienen `NAME-` asociado, tal
  como §22.5 exige para no inventar un taxón cuando la identidad es incierta.
- **Proyectar lo disputado obliga a declararlo.** La proyección referencia `HYP-900201`, que no
  es consenso amplio. La comprobación 2 bis de `separation` emite ERROR si una proyección
  referencia algo disputado sin declarar simplificaciones ni restricciones científicas: así es
  como una hipótesis se convierte en hecho.

## Cómo se comprueba

`scripts/validate/validate.py` lee `knowledge/records/`, no fixtures. Para ejecutar las familias
contra este directorio hay que cargar los `*.jsonl` de la raíz como `data`, reapuntar
`separation.PROJECTION_DIRS` a `projections/` y vaciar `SCIENCE_DIRS` y `GAME_DIRS`, que si no
apuntan al repositorio real.

Estado comprobado al escribir esto: **0 errores** en las familias `schema`, `references`,
`identity`, `time`, `geography`, `hypotheses`, `evidence`, `state` y `separation`.

Invariante comprobable con `grep`, porque el fixture no escribe ningún identificador de la capa 8
dentro de un registro científico, ni siquiera en texto libre:

```bash
grep -rE '\b(GAME|MECH|CAMP|CHAPTER)-[0-9]{6}' --include='*.jsonl' . --exclude-dir=projections
# sin salida
```

### Advertencias esperadas, con su justificación (§19.1)

| Advertencia | Por qué está y no se arregla |
|---|---|
| `hypotheses`: `HYP-900201` no registra contraevidencia ni fuentes opuestas | El fixture no ingiere fuentes. Anotado en el propio registro: el hueco no significa que la hipótesis no tenga objeciones |
| `hypotheses`: `HYP-900201` declara `mixed_acceptance` sin enlazar alternativa | La alternativa le corresponde al fixture `two-deep-topologies`. El conflicto se nombra en `conflict_group_ids` para que la ausencia no se lea como inexistencia |
| `provenance`: las dos fuentes no tienen DOI ni URL | No se inventan identificadores resolubles |

## Rango de identificadores

`900201`–`900299`, en el bloque `9xxxxx` reservado de hecho a fixtures. `CAMP-000001` es la
excepción y es deliberada: es la campaña real de `game/campaigns/c01-eukarya/manifest.json`, y
una proyección que apunte a una campaña inventada no probaría nada. Es un campo escalar, no una
lista `_ids`, así que no crea una referencia colgada dentro del fixture.

## Lo que este fixture no es

- **No es corpus.** El corredor `Eukaryota → Amorphea → Obazoa → Opisthokonta → Holozoa` está
  copiado del manifiesto de la campaña; el fixture no introduce topología nueva. Las dos fuentes
  están en `pending_verification`.
- **No es contenido de juego.** No hay capítulos, ni mecánicas con identificador `MECH-`, ni
  balance. §6.8 enumera además «efectos» y «condiciones de aparición», y `game-projection.json`
  no tiene campo para ninguno de los dos; mientras no lo tenga, viven en el módulo de campaña.
- **No prueba la retirada del módulo.** Que borrar `c01-eukarya` deje intactos los quince
  registros científicos es una prueba de §27.10 sobre el repositorio, no sobre este directorio.
  Lo que el fixture aporta es la lista de quince identificadores que deben sobrevivir.
