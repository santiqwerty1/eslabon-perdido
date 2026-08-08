# `time-bad` · defectos sembrados

Cada registro de este conjunto viola una comprobación concreta de la familia
`time` (§19.2, §11.2–§11.4, §6.9). Ninguno es dato canónico.

| Registro | Línea de §19.2 / §11.3 | Qué debe detectarse |
|---|---|---|
| `TIME-000001` | intervalos válidos | límite antiguo por debajo del reciente |
| `TIME-000002` | unidades explícitas | intervalo sin unidad |
| `TIME-000003` | unidades explícitas | unidad fuera de §11.4 |
| `TIME-000004` | intervalos válidos | ningún límite (WARNING) |
| `TIME-000005` | observado ≠ inferido | `observed_taxon_range` con determinación inferida |
| `TIME-000006` | observado ≠ inferido | `divergence_estimate` presentado como observado |
| `TIME-000007` | observado ≠ inferido | reloj molecular declarado observado |
| `TIME-000008` | intervalos válidos | sin incertidumbre y sin calibración |
| `TIME-000009` | observado ≠ inferido | `reported_without_basis` (WARNING, §19.1 exige issue) |
| `TIME-000010` | intervalos válidos | fecha de publicación sin `calendar_date` |
| `TIME-000011` | unidades explícitas | unidad geológica sin nombre de intervalo |
| `TIME-000012` | intervalos válidos | antigüedad negativa |
| `TIME-000013` | intervalos válidos | escala de calendario invertida |
| `TIME-000014` | intervalos válidos | intervalo creíble sin nivel (WARNING) |
| `TIME-000015` | observado ≠ inferido | sin `determination` |
| `TIME-000040` | — | unidad no comparable: queda fuera de la plausibilidad (INFO) |
| `TRAITOBS-000003` | observado ≠ inferido | inferencia filogenética fechada como observación |
| `EVENT-000001` | eventos plausibles | hibridación entre rangos **observados** disjuntos → **WARNING** (§11.3) |
| `EVENT-000002` | eventos plausibles | hibridación entre rangos **inferidos** disjuntos → **ERROR** |
| `EVENT-000004` | eventos plausibles | transferencia entre entidades que no coexisten |
| `EVENT-000003` | §11.3 | innovación antedatada respecto de su evidencia y declarada observada |
| `CLAIM-000026` | §11.3 | ancestro entero posterior al descendiente (rangos inferidos) |
| `CLAIM-000100` / `-000101` | aciclicidad | ciclo de ascendencia dentro de `HYP-000001` |
| `CLAIM-000300` | aciclicidad | una entidad que desciende de sí misma |
| `CLAIM-000400` / `-000401` | aciclicidad | ciclo que sólo cierra con predicados modales (WARNING, §14.1) |

El caso positivo de §6.9 vive en `time-ok`: `HYP-000002` y `HYP-000003`
invierten la misma relación, cada una es acíclica y la unión no lo es. Eso no
es un error, y la familia lo anota como INFO.
