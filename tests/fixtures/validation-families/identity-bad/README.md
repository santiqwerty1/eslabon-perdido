# `identity-bad` · defectos sembrados

Cada registro de este conjunto viola una comprobación concreta de la familia
`identity` (§19.2). Ninguno es dato canónico.

| Registro | Línea de §19.2 | Qué debe detectarse |
|---|---|---|
| `CLADE-000001` / `CLADE-000003` | alias ambiguos | dos entidades activas reclaman `NAME-000009` |
| `CLADE-000001` / `CLADE-000002` | alias ambiguos | misma etiqueta y mismo `entity_type` (WARNING) |
| `CLADE-000004` | alias ambiguos | se declara alias de sí misma |
| `CLADE-000005` | alias ambiguos | alias contra otra entidad activa: fusión de hecho (§16.4) |
| `CLADE-000006` | alias ambiguos | alias repetido (WARNING) |
| `NAME-000001` / `NAME-000002` | homónimos no fusionados | misma grafía, autoría distinta, uno `merged` |
| `NAME-000003` / `NAME-000004` | homónimos no fusionados | misma grafía sin nada que las distinga (WARNING) |
| `NAME-000005` / `NAME-000006` | homónimos no fusionados | homonimia bien conservada (INFO, caso correcto) |
| `TAXCONCEPT-000006` / `-000007` | homónimos no fusionados | mismo nombre, fuentes distintas, uno `merged` |
| `TAXCONCEPT-000008` | homónimos no fusionados | `conceptual_homonym` declarado y registro `merged` |
| `TAXCONCEPT-000002` | nombre ≠ concepto | sin `name_id` y sin `according_to_source_id` (§7.3) |
| `TAXCONCEPT-000003` | nombre ≠ concepto | `name_id` que apunta a un concepto |
| `TAXCONCEPT-000004` / `-000005` | nombre ≠ concepto | `name_id` y fuente colgados |
| `NAME-000007` | nombre ≠ concepto | un nombre con circunscripción (§7.2) |
| `CLAIM-000001` | nombre ≠ concepto | `assigned_to` contra un nombre |
| `SPECIMEN-000001` | espécimen ≠ taxón | alias a un concepto taxonómico (§7.7) |
| `CLADE-000013` | espécimen ≠ taxón | alias a un espécimen |
| `CLAIM-000002` | espécimen ≠ taxón | `descends_from` con un espécimen |
| `TRAITOBS-000001` | espécimen ≠ taxón | `bearer_type` taxón con portador `SPECIMEN-` (§7.9) |
| `LINEAGE-000900` | integridad | `entity_type` que no concuerda con el prefijo (§16.3) |
| `CLADE-000008` | fusiones con redirección | `merged` sin redirección |
| `CLADE-000010` / `-000011` | fusiones con redirección | cadena de fusiones circular |
| `CLADE-000012` | fusiones con redirección | redirección a un identificador inexistente |
