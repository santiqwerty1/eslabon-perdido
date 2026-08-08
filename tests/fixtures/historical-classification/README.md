# Fixture `historical-classification`

Fixture 5 de §27.9: **una clasificación superada que se conserva**.

## Qué capacidad prueba

Que el modelo pueda **seguir leyendo un nombre viejo** sin declararlo vigente y sin borrarlo.
§4.9 obliga a conservar nombres alternativos, grafías originales, recombinaciones, erratas y
sinonimias propuestas, y a fusionar identidades sólo cuando la equivalencia está confirmada.
Este fixture pone las cuatro piezas que eso exige:

| Pieza | Registro | Qué demuestra |
|---|---|---|
| Concepto de una clasificación abandonada | `TAXCONCEPT-900101` (Protista *según* Haeckel, 1866) | `record_status: active` con `validity_period_id` a un período histórico: el registro se conserva, lo histórico es la idea |
| Idea superada, registro vivo | `CLAIM-900103` | `historical_status: superseded` con `record_status: active` |
| Grafías alternativas | `NAME-900101` (`Protista` / `Protisten`), `NAME-900103` (`Amoeba` / `Amœba`) | la literatura antigua sigue siendo localizable |
| Sinonimia **disputada** | `CLAIM-900101`, con `EVID-900102` en contra | se modela como afirmación, no como fusión ni como borrado |
| Vista histórica | `TAXVIEW-900101` | incluye la clasificación superada y declara que lo es |

La distinción central del fixture es el par `CLAIM-900103` / `CLAIM-900104`: **mismo sujeto,
mismo objeto, distinto predicado, distinta vigencia**.

- `CLADE-900101 assigned_to TAXCONCEPT-900101` → `historical_status: superseded`
- `CLADE-900101 historically_classified_as TAXCONCEPT-900101` → `historical_status: current`

«Esto se clasificó así» sigue siendo verdad hoy. «Esto es así» está superado. Colapsar las dos
afirmaciones en una obliga a elegir entre borrar historia y declarar vigente una clasificación
abandonada, y las dos salidas incumplen §4.9.

## Por qué existe

Porque la tentación de limpiar es permanente. Un nombre que ya nadie usa parece basura, y la
operación «obvia» sobre dos nombres que designan más o menos lo mismo es fusionarlos. Las dos
cosas destruyen la capacidad de leer la bibliografía anterior, que es de donde sale el
conocimiento. Este fixture es el registro de que el modelo aguanta la tentación:
**ningún registro está en `deprecated` ni en `merged`**. Todo está en `active`.

También es la prueba de estrés de `according_to_source_id`. El nombre `Protoctista`
(`NAME-900102`) sostiene dos conceptos incompatibles entre sí, `TAXCONCEPT-900102` y
`TAXCONCEPT-900103`, distinguidos únicamente por su fuente. Sin ese campo obligatorio los dos
colapsarían en una etiqueta y la incompatibilidad sería irrepresentable.

## Qué debería fallar si el esquema se rompe

Cada punto nombra la comprobación de §19.2 que lo atrapa.

1. **Si `TaxonomicName.original_spellings` desaparece o se normaliza a una sola grafía**
   (`schema`): `Amœba` y `Protisten` se pierden y la bibliografía del siglo XIX deja de ser
   localizable. La prueba es que la grafía con ligadura siga presente y siga siendo distinta de
   la canónica.
2. **Si alguien fusiona `NAME-900101` y `NAME-900102`** porque «son sinónimos» (`references`):
   `CLAIM-900101` se queda sin sujeto o sin objeto y la referencia colgada es un ERROR. Ése es
   el mecanismo que impide una fusión sin `MERGE_CONFIRMED_IDENTITIES` (§16.4).
3. **Si `according_to_source_id` deja de ser obligatorio** (`schema`, `identity`): los dos
   conceptos que comparten `NAME-900102` dejan de ser distinguibles. La familia `identity` ya
   informa hoy de que ese nombre sostiene dos conceptos según fuentes distintas y de que se
   conservan por separado; ese INFO debe seguir apareciendo.
4. **Si `historical_status` se fusiona con `record_status`** (`state`, `schema`):
   `CLAIM-900103` pasa a ser irrepresentable. O se borra el registro, o se declara vigente una
   clasificación abandonada. La prueba es que exista al menos un registro con
   `record_status: active` y `historical_status: superseded`.
5. **Si el par `CLAIM-900103` / `CLAIM-900104` se colapsa en una sola afirmación**: se pierde la
   diferencia entre el hecho historiográfico y la asignación. `EVID-900103` es el testigo: la
   misma evidencia **sostiene** una y **cuestiona** la otra, y eso sólo tiene sentido si son dos.
6. **Si `ClassificationView` deja de exigir `editorial_criteria` o `cutoff_date`**
   (`schema`, `separation`): la vista histórica pasa por clasificación vigente. La comprobación
   3 de la familia `separation` («las vistas generadas identifican sus simplificaciones») emite
   ERROR si `simplifications` o `editorial_criteria` faltan o están vacíos.
7. **Si `taxonomic_status` se lee como veredicto del proyecto**: `TAXCONCEPT-900101` aparece
   como `accepted` y eso es exactamente lo que **no** significa. Es aceptado *dentro de*
   `SRC-900102`. El campo describe la clasificación de la fuente citada, no la opinión del
   proyecto.

## Cómo se comprueba

`scripts/validate/validate.py` lee `knowledge/records/`, no fixtures. Para ejecutar las familias
contra este directorio hay que cargar sus `*.jsonl` como `data` y llamar a `check`, igual que hace
`tests/validation/test_families.py` con los fixtures de `validation-families/`.

Estado comprobado al escribir esto: **0 errores** en las familias `schema`, `references`,
`identity`, `time`, `geography`, `hypotheses`, `evidence`, `state` y `separation`.

### Advertencias esperadas, con su justificación (§19.1)

| Advertencia | Por qué está y no se arregla |
|---|---|
| `evidence`: `EVID-900101`, `EVID-900102` y `EVID-900103` citan su fuente sin localizador | Citar una página sin haber abierto el original sería fabricar la referencia. Registrado en `ISSUE-900102`, enlazado desde los tres registros |
| `provenance`: las cuatro fuentes no tienen DOI ni URL | Mismo motivo. No se inventan identificadores resolubles |

## Rango de identificadores

`900101`–`900199`, en el bloque `9xxxxx` reservado de hecho a fixtures. No colisiona con la
asignación secuencial del conjunto de datos real, que va por `ISSUE-000030`, ni con los demás
fixtures, que usan `0001xx`–`0003xx`.

## Lo que este fixture no es

- **No es corpus.** Los nombres son reales porque la historia nomenclatural no se puede ilustrar
  con nombres inventados, pero las cuatro fuentes están en `pending_verification` y no se han
  cotejado contra el original. Ningún registro de aquí puede promocionarse a
  `knowledge/records/` sin pasar por el protocolo de §17.
- **No es una clasificación que el proyecto sostenga.** `TAXVIEW-900101` reproduce un sistema
  abandonado y lo dice en sus criterios editoriales.
- **No cubre erratas conservadas.** `Amœba` es una variante tipográfica documentada, no una
  errata. El caso `preserved_typo` de §8.1 necesita una mención con su pasaje y le corresponde a
  un fixture con corpus.
