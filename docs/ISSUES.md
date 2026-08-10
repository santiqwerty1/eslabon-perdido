# Registro de cuestiones pendientes

**Estado:** provisional, anterior a la Fase 0
**Origen:** lectura completa de `Guia_Maestra_Red_Evolutiva_v1.1.0.md` (§0–§30, apéndices A–J) y de `Filogenia.md`
**Fecha:** 7 de agosto de 2026
**Guía de referencia:** `1.1.0`

---

## Condición de este registro

El repositorio todavía no tiene la estructura de la §16.2, de modo que `knowledge/records/issues.jsonl` no existe. Este archivo es un **libro mayor provisional** que debe migrarse a ese JSONL en la Fase 2, cuando se implementen `Section`, `Passage`, `Mention`, `Source` e `Issue`.

Ninguna cuestión de aquí debe resolverse borrándola. Al cerrarse, se marca `resolution.status: "resolved"` y se enlaza la decisión o el ADR que la resolvió, según la regla de conservación de la §0.1 y el procedimiento del Apéndice H.10.

Las severidades reutilizan el vocabulario de la §19.1: `ERROR` impide aceptar un delta, `WARNING` permite continuar pero exige justificación, `INFO` no bloquea.

---

## Esquema de `Issue`

**El Apéndice E.12 ya define el esquema canónico** de `Issue`, añadido el 7 de agosto de 2026 al resolver `ISSUE-000009`. Está orientado a la ingestión: sus referencias apuntan a registros del corpus (`record_ids`, `claim_ids`, `mention_ids`).

Este fichero es anterior al corpus y sus cuestiones apuntan a secciones de la guía, así que usa la variante provisional siguiente. **Al migrar a `issues.jsonl` en la Fase 2 hay que traducir `affects` al esquema de E.12**, o registrar estas cuestiones con `affects` vacío y el localizador en `evidence_locators`:

```json
{
  "id": "ISSUE-000001",
  "issue_type": "schema_inconsistency",
  "title": "",
  "description": "",
  "severity": "WARNING",
  "raised_in": "SEC-000000",
  "affects": {
    "guide_sections": [],
    "record_types": [],
    "entity_ids": []
  },
  "evidence_locators": [],
  "proposed_resolution": "",
  "blocks_phase": null,
  "related_issue_ids": [],
  "resolution": {
    "status": "open",
    "resolved_in": null,
    "decision_id": null
  },
  "record_status": "active"
}
```

Valores previstos para `issue_type`: `schema_inconsistency`, `documentation_ambiguity`, `content_gap`, `unspecified_requirement`, `pending_decision`.

`raised_in: SEC-000000` designa esta lectura de la guía, que no es una sección de investigación ingerida por el protocolo de la §17.

---

## Resumen

| ID | Severidad | Tipo | Cuestión | Bloquea |
|---|---|---|---|---|
| `ISSUE-000001` | ERROR | `schema_inconsistency` | El `Claim` está definido dos veces con formas distintas — **resuelta** | — |
| `ISSUE-000002` | ERROR | `schema_inconsistency` | `"acceptance": "mixed"` no pertenece a la enumeración de §10.1 — **resuelta** | — |
| `ISSUE-000003` | ERROR | `schema_inconsistency` | El `Event` cambia de nombre de campo y de cardinalidad — **resuelta** | — |
| `ISSUE-000004` | WARNING | `schema_inconsistency` | E.6 anida las dimensiones epistémicas y E.9 las deja planas — **resuelta** | — |
| `ISSUE-000005` | ERROR | `documentation_ambiguity` | Las tres listas de familias de validación no coinciden — **resuelta** | — |
| `ISSUE-000006` | WARNING | `documentation_ambiguity` | Dos numeraciones distintas se llaman «fase» — **resuelta** | — |
| `ISSUE-000007` | WARNING | `documentation_ambiguity` | `superseded` designa dos cosas diferentes — **resuelta** | — |
| `ISSUE-000008` | INFO | `documentation_ambiguity` | El informe humano está especificado con 9 y con 13 apartados — **resuelta** | — |
| `ISSUE-000009` | ERROR | `schema_inconsistency` | No existe esquema mínimo para `Issue` — **resuelta** | — |
| `ISSUE-000010` | WARNING | `content_gap` | No hay catálogo terminológico para el ámbito de la Campaña 1 | Fase 1 |
| `ISSUE-000011` | WARNING | `unspecified_requirement` | La prueba de «ausencia de teleología» no está especificada — **resuelta** | — |
| `ISSUE-000012` | INFO | `unspecified_requirement` | `evidence_strength` carece de rúbrica — **resuelta** | — |
| `ISSUE-000013` | WARNING | `pending_decision` | `OPEN-016` ya tiene respuesta de facto y sigue abierta | Fase 1 |
| `ISSUE-000014` | WARNING | `pending_decision` | La ingestión debe partir de `Filogenia.md`, no del Apéndice A | Fase 2 |
| `ISSUE-000015` | INFO | `documentation_ambiguity` | Nombre del fixture hominino — **resuelta**, se conserva por trazabilidad | — |
| `ISSUE-000016` | ERROR | `content_gap` | Afirmación sin procedencia en C.16: flujo génico sapiens–denisovano | Fase 2 |
| `ISSUE-000017` | ERROR | `content_gap` | La capa de procedencia entera se perdió en la destilación | Fase 2 |
| `ISSUE-000018` | WARNING | `content_gap` | La convención de marcado `⚠` se perdió: 17 usos en la fuente, 0 en la guía — **resuelta** | — |
| `ISSUE-000019` | WARNING | `unspecified_requirement` | `crown` / `stem` / `total group` se listan como marcas y nunca se definen — **resuelta** | — |
| `ISSUE-000020` | WARNING | `content_gap` | Falta la distinción nombre disponible / taxón aceptado / clado respaldado — **resuelta** | — |
| `ISSUE-000021` | WARNING | `content_gap` | Contenido científico de la Campaña 1 ausente en los apéndices | Fase 1 |
| `ISSUE-000022` | WARNING | `documentation_ambiguity` | Reformulaciones que cambian el sentido del original — **resuelta** | — |
| `ISSUE-000023` | INFO | `unspecified_requirement` | Las 34 fuentes son de calidad muy desigual | Fase 4 |
| `ISSUE-000024` | ERROR | `documentation_ambiguity` | `DEC-016` y `DEC-017` se reescribieron en el sitio sin marcarse `SUPERSEDIDO` — **resuelta** | — |
| `ISSUE-000025` | ERROR | `unspecified_requirement` | La prueba de preservación §27.11 está codificada en duro — **resuelta** | — |
| `ISSUE-000026` | WARNING | `content_gap` | La reproducción sexual y el origen de la meiosis desaparecen sin exclusión ni disparador — **resuelta** | — |
| `ISSUE-000027` | WARNING | `unspecified_requirement` | §27.7 perdió la exigencia de evaluar la forma de la distribución de resultados — **resuelta** | — |
| `ISSUE-000028` | WARNING | `documentation_ambiguity` | Debilitamientos normativos no documentados como simplificaciones — **resuelta** | — |
| `ISSUE-000029` | WARNING | `validation_warning` | Falta pip en el Python de WSL — **resuelta**; vive en `issues.jsonl`, no aquí | — |
| `ISSUE-000030` | ERROR | `schema_inconsistency` | `provenance.origin` es obligatorio en `common.json` y no existe en E.6 ni §9.1 — **resuelta** | — |
| `ISSUE-000031` | ERROR | `schema_inconsistency` | Ningún esquema tiene campo para el reemplazo de un registro deprecado — **resuelta** | — |
| `ISSUE-000032` | WARNING | `schema_inconsistency` | `taxon-concept.json` no admite `epistemic_dimensions` — **resuelta** | — |
| `ISSUE-000033` | WARNING | `documentation_ambiguity` | §16.2 no asigna fichero JSONL ni a `TIME-` ni a las vistas — **resuelta** | — |
| `ISSUE-000034` | WARNING | `documentation_ambiguity` | Cuatro `entity_type` sin prefijo consolidado en §16.3 — **resuelta** | — |
| `ISSUE-000035` | WARNING | `schema_inconsistency` | `Occurrence` viaja por `entity.json`, que es delgada y no admite tiempo ni lugar — **resuelta** | — |
| `ISSUE-000036` | WARNING | `documentation_ambiguity` | `conflict_group_ids` son cadenas libres, no identificadores opacos | Fase 5 |
| `ISSUE-000037` | INFO | `content_gap` | El eje `acceptance` no tiene valor para «ya no la sostiene nadie» | Fase 4 |
| `ISSUE-000038` | INFO | `schema_inconsistency` | `game-projection.json` no cubre «efectos» ni «condiciones de aparición» de §6.8 — **resuelta** | — |

---

# A. Inconsistencias de esquema

### `ISSUE-000001` · El `Claim` está definido dos veces con formas distintas

- **Severidad:** `ERROR` · **Tipo:** `schema_inconsistency` · **Bloquea:** Fase 2
- **Afecta:** §9.1, Apéndice E.6 · tipo `Claim`
- **Localizadores:** `Guia_Maestra_Red_Evolutiva_v1.1.0.md:965`, `:5511`

§9.1 presenta un `Claim` plano con `context_ids` y `asserted_by`, sin `claim_type`, `scope`, `provenance`, `counterevidence_ids` ni `derivation`. E.6 anida las dimensiones bajo `epistemic_dimensions` e incluye todos esos campos. Son dos contratos distintos para el registro central del sistema.

**Resolución propuesta:** declarar E.6 canónico y reescribir el ejemplo de §9.1 para que remita a él. E.6 es más completo, usa valores de enumeración válidos y modela la procedencia como objeto, coherente con §4.5.

**RESUELTA el 7 de agosto de 2026.** El Apéndice E queda declarado canónico sobre los ejemplos inline, y §9.1 se reescribió con la forma de E.6: `claim_type`, `scope`, `provenance`, `epistemic_dimensions`, `evidence_ids`, `counterevidence_ids` y `derivation`.

---

### `ISSUE-000002` · `"acceptance": "mixed"` no pertenece a la enumeración

- **Severidad:** `ERROR` · **Tipo:** `schema_inconsistency` · **Bloquea:** Fase 2
- **Afecta:** §9.1, §10.1 · tipo `Claim`
- **Localizadores:** `Guia_Maestra_Red_Evolutiva_v1.1.0.md:974`, `:1048`

El ejemplo de §9.1 usa `"acceptance": "mixed"`, pero §10.1 define `mixed_acceptance`. Los otros cinco campos del ejemplo sí casan con sus enumeraciones. La validación de esquema de §19.2 rechazaría este registro.

**Resolución propuesta:** corregir a `mixed_acceptance`. Se resuelve junto con `ISSUE-000001` si se adopta E.6, que ya usa un valor válido.

**RESUELTA el 7 de agosto de 2026** al adoptar la forma de E.6 en §9.1. El ejemplo usa ahora `mixed_acceptance`.

---

### `ISSUE-000003` · El `Event` cambia de nombre de campo y de cardinalidad

- **Severidad:** `ERROR` · **Tipo:** `schema_inconsistency` · **Bloquea:** Fase 5
- **Afecta:** §13.2, Apéndice E.8 · tipo `Event`
- **Localizadores:** `Guia_Maestra_Red_Evolutiva_v1.1.0.md:1241`, `:5593`

§13.2 usa `participant_roles` y `temporal_expression_id` en singular. E.8 usa `participants` y `temporal_expression_ids` en plural, y añade `result_entity_ids`, que §13.2 no contempla.

**Resolución propuesta:** adoptar E.8. El plural es correcto porque un evento puede tener varios episodios (§13.1 lo dice expresamente), y `result_entity_ids` es necesario para `origina_linaje_hibrido_con` (§14.2).

**RESUELTA el 7 de agosto de 2026.** §13.2 adopta `participants`, `temporal_expression_ids` en plural y `result_entity_ids`. Se conservó el ejemplo de introgresión, más ilustrativo que el de hibridación de E.8, con los roles `donor` y `recipient`.

---

### `ISSUE-000004` · E.6 anida las dimensiones epistémicas y E.9 las deja planas

- **Severidad:** `WARNING` · **Tipo:** `schema_inconsistency` · **Bloquea:** Fase 4
- **Afecta:** Apéndice E.6, E.9 · tipos `Claim`, `Hypothesis`
- **Localizadores:** `Guia_Maestra_Red_Evolutiva_v1.1.0.md:5531`, `:5630`

Dentro del mismo apéndice, el `Claim` agrupa `acceptance`, `evidence_strength`, `resolution` e `historical_status` bajo `epistemic_dimensions`, mientras la `Hypothesis` los deja en la raíz. Dos registros con la misma semántica y distinta estructura complican la validación compartida de §19.2 («dimensiones epistemológicas no mezcladas»).

**Resolución propuesta:** unificar bajo `epistemic_dimensions` en ambos. Nótese que `record_status` va en la raíz en los dos casos, lo cual es correcto: pertenece al registro, no a la idea (ver `ISSUE-000007`).

**RESUELTA el 7 de agosto de 2026.** E.9 anida ahora las cuatro dimensiones bajo `epistemic_dimensions`, igual que E.6. La regla quedó escrita en la cabecera del Apéndice E: las dimensiones van siempre anidadas y `record_status` siempre en la raíz.

---

### `ISSUE-000009` · No existe esquema mínimo para `Issue`

- **Severidad:** `ERROR` · **Tipo:** `schema_inconsistency` · **Bloquea:** Fase 2
- **Afecta:** Apéndice E, §8, §16.2, §16.4, F.3 · tipo `Issue`
- **Localizadores:** `Guia_Maestra_Red_Evolutiva_v1.1.0.md:931`, `:1488`, `:5405`, `:5724`

El Apéndice E define once esquemas y omite `Issue`, pese a que es tipo de **fase 1** —la más temprana—, tiene prefijo `ISSUE-` (§16.3), archivo `issues.jsonl` propio (§16.2), operaciones `ADD_ISSUE` y `RESOLVE_ISSUE` (§16.4), campos `issue_ids` en E.5, entradas `issues_added` e `issues_resolved` en el delta (§17.13), y es la respuesta obligatoria ante ambigüedad (F.3) y ante conocimiento general no verificable (§4.7).

Es el tipo más referenciado del sistema sin contrato definido, y su ausencia es especialmente incómoda porque §19.1 establece que **todo `WARNING` exige un issue**: sin esquema, la validación no puede cumplir su propia regla.

**Resolución propuesta:** añadir `E.12. Cuestión pendiente` con el esquema propuesto en la cabecera de este archivo, y levantar ADR.

**RESUELTA el 7 de agosto de 2026.** Añadido el Apéndice E.12 con el esquema, ocho valores de `issue_type`, las tres severidades de §19.1 y un bloque `resolution` que exige cerrar sin borrar. Dos decisiones de fondo: `external_knowledge_flagged` es el destino obligatorio del conocimiento general que aparezca en ingestión (§4.7) y de lo pendiente de confirmar en auditoría (§18.2); y un `WARNING` de validación no justificado debe generar un `Issue`, que es lo que vuelve exigible la regla de §19.1.

---

# B. Ambigüedades de documentación

### `ISSUE-000005` · Las tres listas de familias de validación no coinciden

- **Severidad:** `ERROR` · **Tipo:** `documentation_ambiguity` · **Bloquea:** Fase 0
- **Afecta:** §17 paso 12, §19.2, §19.3
- **Localizadores:** `Guia_Maestra_Red_Evolutiva_v1.1.0.md:1799`, `:1934`, `:2005`

La misma lista aparece tres veces con contenidos distintos:

| Fuente | Nº | Contenido |
|---|---:|---|
| §17 paso 12 | 11 | esquema, referencias, cobertura, identidad, tiempo, geografía, hipótesis, **topología**, **procedencia**, estado, separación |
| §19.2 | 10 | esquema, integridad referencial, cobertura, identidad, tiempo, geografía, hipótesis, **evidencia**, estado, separación de capas |
| §19.3 | 9 | `schema`, `references`, `coverage`, `identity`, `time`, `geography`, `hypotheses`, **`provenance`**, `separation` |

En consecuencia **faltan `validate:evidence` y `validate:state`**, pese a que ambas familias son obligatorias en §19.2, y sobra `validate:provenance`, que no tiene cabecera propia allí.

**Resolución propuesta:** tomar §19.2 como canónica, añadir los dos comandos ausentes y decidir si `provenance` es familia propia o queda absorbida en `coverage`. Bloquea Fase 0 porque `scripts/validate/` se deriva de esta lista.

**RESUELTA el 7 de agosto de 2026.** §19.2 queda declarada canónica con **once familias**, y §17 paso 12 y §19.3 se alinean con ella.

Dos decisiones de fondo:

- **`Procedencia` pasa a ser familia propia.** Estaba repartida entre `Cobertura` y `Evidencia`, pero ninguna de las dos comprobaba dos de los seis requisitos de §4.5 —la operación que incorporó la afirmación y la revisión del conjunto de datos—, ni que las derivadas declaren su regla (§9.4), ni que lo incorporado en auditoría vaya marcado como externo (§18.2). El reparto queda explícito: *cobertura comprueba que la cadena exista; procedencia, que esté completa*.
- **`Topología` se integra en `Hipótesis`** en vez de ser familia suelta, porque sus comprobaciones son por hipótesis: la aciclicidad de §6.9 se define por subgrafo, no globalmente. Se añadieron a esa familia la ausencia de ciclos de ascendencia y la prohibición de mezclar topologías incompatibles en una vista.

Verificado por comparación automática: 11 familias, 11 comandos, ninguna familia sin comando y ningún comando sin familia.

---

### `ISSUE-000006` · Dos numeraciones distintas se llaman «fase»

- **Severidad:** `WARNING` · **Tipo:** `documentation_ambiguity` · **Bloquea:** Fase 0
- **Afecta:** §8, §24
- **Localizadores:** `Guia_Maestra_Red_Evolutiva_v1.1.0.md:905`, `:2934`

La columna *fase mínima* del catálogo de entidades va de 1 a 8 con un hueco sin explicar en 6–7. Las fases de la hoja de ruta van de 0 a 18. No son la misma escala: `Section`, `Mention` e `Issue` son «fase 1» en §8 pero se implementan en la **Fase 2** del roadmap; los tipos de identidad son «fase 2» en §8 y **Fase 3** allí. El desfase ronda una unidad pero no es constante.

**Resolución propuesta:** renombrar la columna de §8 a «nivel de implementación» o alinearla con las fases reales. El hueco en 6–7 se explica por sí solo en cuanto se acepte que es una escala independiente.

---

### `ISSUE-000007` · `superseded` designa dos cosas diferentes

- **Severidad:** `WARNING` · **Tipo:** `documentation_ambiguity` · **Bloquea:** Fase 4
- **Afecta:** §10.5, §10.6
- **Localizadores:** `Guia_Maestra_Red_Evolutiva_v1.1.0.md:1090`, `:1099`

`historical_status` (vigencia de la **idea científica**) y `record_status` (ciclo de vida del **registro**) comparten el valor `superseded`. «Esta hipótesis fue reemplazada por otra mejor» y «esta fila fue reemplazada por una corrección» son afirmaciones distintas que un lector, una consulta o un informe pueden confundir con facilidad.

**Resolución propuesta:** conservar `superseded` en `historical_status` y renombrar el de `record_status` a `replaced`, o exigir siempre el prefijo del eje al mostrarlo en la interfaz.

---

### `ISSUE-000008` · El informe humano está especificado con 9 y con 13 apartados

- **Severidad:** `INFO` · **Tipo:** `documentation_ambiguity` · **Bloquea:** Fase 6
- **Afecta:** §17 paso 14, Apéndice F.1
- **Localizadores:** `Guia_Maestra_Red_Evolutiva_v1.1.0.md:1839`, `:5686`

§17 lo describe en nueve apartados; F.1 en trece, añadiendo cobertura y excepciones, entidades nuevas o modificadas, afirmaciones y evidencia, y eventos como apartado propio. No es contradicción —F.1 es la versión completa— pero quien implemente leyendo solo §17 producirá un informe incompleto.

**Resolución propuesta:** que §17 paso 14 remita explícitamente al Apéndice F.1 en vez de enumerar una versión reducida.

---

# C. Huecos de contenido

### `ISSUE-000010` · No hay catálogo terminológico para el ámbito de la Campaña 1

- **Severidad:** `WARNING` · **Tipo:** `content_gap` · **Bloquea:** Fase 1
- **Afecta:** Apéndice D, Apéndice A.1, §4.3, §4.9
- **Localizadores:** `Guia_Maestra_Red_Evolutiva_v1.1.0.md:5366`, `Filogenia.md`

El Apéndice D cataloga seis categorías no cladísticas, **todas de primates y homininos**. El ámbito de la Campaña 1 tiene trampas equivalentes —«protista», «protozoo», «algas», «invertebrados»— que no aparecen en ninguna sección ni apéndice.

**Diagnóstico preciso:** la capacidad de expresar el problema ya existe y es general (A.1 define las marcas `grado parafilético`, `taxón histórico` y `nombre aproximadamente equivalente`). Lo que falta es contenido. Y la causa no es un descuido de edición: **`Filogenia.md`, la fuente de la que se destiló el Apéndice D, tampoco trata esos términos**, porque su alcance es el linaje humano. Cerrar este hueco **exige investigación y fuentes nuevas**, no releer material existente.

Mitigante parcial vigente: §23.1 ya prohíbe *inventar un «primer eucariota» nombrado para llenar un hueco*, que es el error más probable de la campaña.

**Resolución propuesta:** añadir un `D.7` eucariota durante la Fase 1, alimentado por fuentes nuevas dentro del corte bibliográfico que fije `ISSUE-000013`.

---

### `ISSUE-000011` · La prueba de «ausencia de teleología» no está especificada

- **Severidad:** `WARNING` · **Tipo:** `unspecified_requirement` · **Bloquea:** Fase 9
- **Afecta:** §27.7, §29.15, Apéndice H.6
- **Localizadores:** `Guia_Maestra_Red_Evolutiva_v1.1.0.md:4057`, `:4315`, `:5864`

§27.7 exige «ausencia de teleología» entre las pruebas de la simulación de Eucaria y H.6 la repite como casilla previa al prototipo, pero **en ningún punto se define qué mide ni cómo se falla**. Es la contrapartida ejecutable del riesgo §29.15 —que el sistema favorezca inevitablemente la integración, la multicelularidad o los cerebros grandes— y el único riesgo que ninguna regla textual puede evitar, porque la teleología se colaría por la dinámica.

**Resolución propuesta:** especificarla antes de la Fase 9. Una forma verificable: ejecutar N semillas con condiciones iniciales equivalentes y comprobar que los desenlaces se distribuyen —que la integración endosimbiótica no ocurre en una fracción cercana a 1, que existen trayectorias de extinción y de persistencia sin integración, y que ninguna variable crece monótonamente con el tiempo por construcción. Enlazar con §21.9, que ya admite la extinción como resultado válido.

---

### `ISSUE-000012` · `evidence_strength` carece de rúbrica

- **Severidad:** `INFO` · **Tipo:** `unspecified_requirement` · **Bloquea:** Fase 4
- **Afecta:** §10.3, §19.2
- **Localizadores:** `Guia_Maestra_Red_Evolutiva_v1.1.0.md:1070`

`high`/`medium`/`low`/`unknown` es un escalar grueso, justo el tipo de reducción que el resto de §10 evita al desdoblar el estado en seis ejes ortogonales. Se mitiga exigiendo una razón breve escrita, pero sigue siendo el eje donde dos personas —o la misma en dos momentos— divergirán primero, y §19.2 no puede validar coherencia entre juicios.

**Resolución propuesta:** una rúbrica breve por tipo de evidencia (§E.7 lista veinte), aunque sea de tres líneas por tipo. No convierte el eje en cuantitativo; solo hace reproducible el juicio.

---

# D. Decisiones pendientes

### `ISSUE-000013` · `OPEN-016` ya tiene respuesta de facto y sigue abierta

- **Severidad:** `WARNING` · **Tipo:** `pending_decision` · **Bloquea:** Fase 1
- **Afecta:** §26 `OPEN-016`, Apéndice I paso 7, Apéndice H.2
- **Localizadores:** `Guia_Maestra_Red_Evolutiva_v1.1.0.md:3949`, `Filogenia.md:5`

`OPEN-016` pide «fecha de corte y corpus científico exacto de Eucaria». `Filogenia.md` declara **corte bibliográfico el 4 de agosto de 2026**, aporta **34 referencias** (Nature, Science, Cell, PLOS Biology, eLife, Scientific Reports, MBE, Zoological Journal of the Linnean Society, Springer, Cambridge) y fija **Mammal Diversity Database v2.5** como referencia taxonómica. La decisión está tomada materialmente pero no registrada.

**Resolución propuesta:** levantar el ADR que cierre `OPEN-016` declarando `Filogenia.md` como corpus de partida y el 4 de agosto de 2026 como fecha de corte, y marcar la decisión abierta como resuelta con enlace.

---

### `ISSUE-000014` · La ingestión debe partir de `Filogenia.md`, no del Apéndice A

- **Severidad:** `WARNING` · **Tipo:** `pending_decision` · **Bloquea:** Fase 2
- **Afecta:** Apéndice A.1, §17 paso 7, §4.5
- **Localizadores:** `Guia_Maestra_Red_Evolutiva_v1.1.0.md:4401`, `:1750`

A.1 advierte que el inventario «no reemplaza la ingestión formal con fuentes y afirmaciones atómicas» y que todo debe reingresarse por el protocolo normal. Pero el Apéndice A **no lleva citas**: ingerirlo activaría la cláusula del §17 paso 7 y todo su contenido entraría marcado «procedente de la sección, para verificación futura».

`Filogenia.md` sí tiene procedencia. Ingerir la fuente en lugar del resumen permite anclar afirmaciones a publicaciones reales desde el primer delta, en vez de acumular un corpus entero pendiente de verificar.

**Resolución propuesta:** registrar `Filogenia.md` como `SEC-000001` y tratar el Apéndice A como índice de cobertura —lista de comprobación de qué debe quedar representado— y no como material de ingestión.

---

# E. Cuestiones cerradas

Se conservan por trazabilidad. No se borran (§0.1, Apéndice H.10).

### `ISSUE-000015` · Nombre del fixture hominino — **resuelta**

- **Severidad:** `INFO` · **Tipo:** `documentation_ambiguity`
- **Resolución:** `resolved`, sin necesidad de cambio
- **Localizadores:** `Guia_Maestra_Red_Evolutiva_v1.1.0.md:1520`, `:4083`, `:5944`

Se detectó que §16.2 lista `tests/fixtures/future-hominin-regression/` mientras el Apéndice I paso 14 y §27.9 nombran `future-hominini-homonym`. Lectura inicial: dos nombres para el mismo artefacto.

**Cerrada tras leer §27.9:** el catálogo de fixtures de referencia enumera diez artefactos, cuatro de ellos `future-*` (`future-hominini-homonym`, `future-denisovan-lineage`, `future-introgression`, `future-specimen-assignment`). El `future-hominin-regression/` de §16.2 es el **directorio contenedor** de esos cuatro, no un nombre alternativo. No hay conflicto.

---

# F. Pérdidas en la destilación `Filogenia.md` → apéndices

Estas cuestiones proceden de una comparación sistemática entre el documento fuente y los apéndices A–D. La derivación es unidireccional y está confirmada estructuralmente: los 102 nombres taxonómicos de C.1–C.5 existen todos en la fuente, el Apéndice B es un calco casi línea por línea de la §8 de la fuente, y A.3 recompone su tabla §7.

### `ISSUE-000016` · Afirmación sin procedencia en C.16: flujo génico sapiens–denisovano

- **Severidad:** `ERROR` · **Tipo:** `content_gap` · **Bloquea:** Fase 2
- **Afecta:** Apéndice C.16, §4.7
- **Localizadores:** `Guia_Maestra_Red_Evolutiva_v1.1.0.md:5278`, `Filogenia.md:1642-1643`

C.16 enumera los eventos que deben superponerse al clado tardío e incluye **«flujo génico sapiens–denisovano»**. La fuente documenta que los neandertales *«intercambiaron genes con* H. sapiens *en múltiples ocasiones»* y que *«también intercambiaron genes con denisovanos»* — es decir, sapiens↔neandertal y neandertal↔denisovano. **El flujo sapiens↔denisovano no aparece en ninguna línea de `Filogenia.md`**: no hay mención de ancestría denisovana en poblaciones actuales, ni de Oceanía, Melanesia o Papúa.

La afirmación es **correcta en la literatura real**, y eso es precisamente lo que la hace peligrosa: un dato verdadero pero sin procedencia es más difícil de detectar que uno falso. Es un ejemplo trabajado del fallo que §4.7 existe para impedir —*«no se agregan […] eventos, relaciones o fuentes que no aparezcan en el material»*— encontrado en el propio apéndice de la guía.

**Matiz de justicia:** §4.7 rige la *ingestión*, y los apéndices son explícitamente material previo al corpus, no producto de una ingestión formal. La cuestión no es que se haya infringido una regla vigente, sino que **al ingerir `Filogenia.md` como `SEC-000001` esta afirmación no tendrá pasaje al que apuntar**.

**Resolución propuesta:** al ingerir, o bien aportar fuente propia para el flujo sapiens–denisovano, o bien registrarla como `ISSUE` y marcarla para verificación futura según §17 paso 7. Revisar además si hay otros casos análogos en C.

---

### `ISSUE-000017` · La capa de procedencia entera se perdió en la destilación

- **Severidad:** `ERROR` · **Tipo:** `content_gap` · **Bloquea:** Fase 2
- **Afecta:** Apéndices A–D, §4.5, `OPEN-003`
- **Localizadores:** `Filogenia.md` (34 referencias, ~37 marcas de cita)

La guía completa contiene **cero URLs, cero DOIs y ninguna mención de revista**. `MDD` aparece una sola vez, sin expandir ni versionar. `ICZN` aparece **0 veces** en las 6054 líneas, pese a que la fuente explica que regula los nombres de superfamilia a subtribu pero **no determina qué clasificación es biológicamente correcta**, ni cubre los nombres por encima del grupo familia — que es exactamente por qué el corredor de la Campaña 1 son todos clados sin rango.

**Resolución propuesta:** no intentar reconstruir las citas dentro de los apéndices. Ingerir `Filogenia.md` como fuente (ver `ISSUE-000014`) y dejar que la procedencia entre por el protocolo, que es su vía correcta.

---

### `ISSUE-000018` · La convención de marcado `⚠` se perdió

- **Severidad:** `WARNING` · **Tipo:** `content_gap` · **Bloquea:** Fase 1
- **Afecta:** Apéndice A.1, A.2
- **Localizadores:** `Filogenia.md` (17 usos) frente a `Guia_Maestra_Red_Evolutiva_v1.1.0.md` (0 usos)

La fuente marca con `⚠` cada nodo de posición, contenido o validez discutidos, y aplica también `[R]` (rango formal) y `[C]` (clado sin rango) nodo por nodo. **El backbone A.2 de la guía elimina todas esas anotaciones**: pierde `Metazoa = Animalia [R/C]`, `Chordata [R]`, `Vertebrata ≈ Craniata [R/C]`, y el `⚠ nombre` sobre Choanozoa. A.1 conserva las marcas como lista en prosa, pero desaparece su **aplicación por nodo**, que es donde tenían utilidad.

Consecuencia colateral: el backbone A.2 queda como una cadena lineal de 67 niveles **sin ninguna advertencia adjunta**, que es el formato más propenso a la lectura ortogenética que §4.2 prohíbe. La fuente encabeza ese mismo árbol advirtiendo que *«no debe leerse como una marcha triunfal»*.

**Resolución propuesta:** restituir las marcas por nodo al ingerir, como atributos de entidad, no como decoración textual.

---

### `ISSUE-000019` · `crown` / `stem` / `total group` se listan como marcas y nunca se definen

- **Severidad:** `WARNING` · **Tipo:** `unspecified_requirement` · **Bloquea:** Fase 3
- **Afecta:** §7.4, Apéndice A.1
- **Localizadores:** `Guia_Maestra_Red_Evolutiva_v1.1.0.md:856-858`, `:4410-4412`, `Filogenia.md:34-35`

La guía enumera `crown group`, `stem group` y `total group` en tres lugares distintos como tipos de definición cladal y como marcas conceptuales, pero **no los define en ningún punto**. La fuente sí: *crown* = «último ancestro común de los representantes vivientes y todos sus descendientes»; *stem* = «linajes extinguidos más próximos al crown group que a cualquier grupo viviente externo».

Sin definición, la marca es una etiqueta vacía y quien modele la aplicará por intuición — lo que §19.2 no puede validar.

**Resolución propuesta:** incorporar ambas definiciones al glosario que exige la Fase 0, tarea 11.

---

### `ISSUE-000020` · Falta la distinción nombre disponible / taxón aceptado / clado respaldado

- **Severidad:** `WARNING` · **Tipo:** `content_gap` · **Bloquea:** Fase 3
- **Afecta:** §7.1–§7.4, §2.3
- **Localizadores:** `Filogenia.md:9-13`

La fuente abre distinguiendo tres cosas que suelen confundirse: **nombre nomenclaturalmente disponible** (publicado cumpliendo reglas), **taxón aceptado** (una base o comunidad decide usarlo) y **clado filogenéticamente respaldado** (un análisis lo recupera como monofilético).

Es la distinción epistemológica que **fundamenta el modelo claim-centric entero** — explica por qué un nombre puede existir sin taxón y un clado sin nombre, que es justo lo que §7.2 y §7.5 modelan. No aparece formulada en la guía.

**Resolución propuesta:** registrarla como afirmación atómica de primer orden al ingerir, y citarla en §7.1 como justificación de las distinciones obligatorias.

---

### `ISSUE-000021` · Contenido científico de la Campaña 1 ausente en los apéndices

- **Severidad:** `WARNING` · **Tipo:** `content_gap` · **Bloquea:** Fase 1
- **Afecta:** Apéndice A.2, A.3, §22.5
- **Localizadores:** `Filogenia.md:94`, `:106`, `:123-134`, `:151-155`

Material del corredor Eukaryota → Holozoa presente en la fuente y ausente en la guía:

- **`Archaea` y `Bacteria` aparecen 0 veces en la guía.** La fuente explica que los eucariotas surgieron por simbiosis entre linajes arqueanos y bacterianos. §22.5 habla de «linaje hospedador ancestral reconstruido» y «simbionte bacteriano ancestral» sin nombrar nunca la identidad arqueana del hospedador, que es el hecho central del arranque de la campaña.
- **`Corallochytrea` aparece 0 veces**: A.3 solo dice «Ichthyosporea y Pluriformea» y pierde el sinónimo.
- **Holomycota contiene Fungi** — la guía lo cita como rama hermana pero nunca dice qué contiene; el sistema no podría responder «dónde están los hongos».
- **Definiciones por contenido**: Holozoa como «animales y todos sus parientes unicelulares más próximos que los hongos» es el criterio por exclusión relativa que cierra la campaña, y no aparece.
- **La razón del conflicto Choanozoa/Apoikozoa**: la fuente explica que Choanozoa se ha usado históricamente con contenidos diferentes. Ver `ISSUE-000022`.

**Resolución propuesta:** todo se resuelve ingiriendo la fuente. Listado aquí para que el dossier C01 de la Fase 1 verifique explícitamente su presencia.

---

### `ISSUE-000022` · Reformulaciones que cambian el sentido del original

- **Severidad:** `WARNING` · **Tipo:** `documentation_ambiguity` · **Bloquea:** Fase 1
- **Afecta:** Apéndice A.2, C.3, C.4
- **Localizadores:** `Guia_Maestra_Red_Evolutiva_v1.1.0.md:4426`, `:4992-4995`, `:5015`

Casos donde la destilación no perdió contenido sino que **alteró su carga epistémica**:

1. **`Choanozoa sensu stricto / Apoikozoa según uso`** (A.2). «Según uso» sugiere preferencia estilística entre sinónimos; la fuente describe un **conflicto de circunscripción** — Choanozoa se ha empleado con contenidos distintos. §4.9 exige conservar la historia nomenclatural, y aquí se aplana.
2. **†Dendropithecoidea y afines asignados a «Stem Catarrhini»** (C.3), cuando la fuente los sitúa bajo Stem Hominoidea **advirtiendo que podrían ser cualquiera de las dos**. La guía resuelve una posición que el original dejaba deliberadamente abierta, contra §4.8.
3. **†*Masripithecus*: «propuesta reciente que requiere auditoría formal»** (C.4) sustituye al dato verificable de la fuente. El reencuadre es útil operativamente, pero deja de ser una afirmación con fecha.

**Resolución propuesta:** al ingerir, tomar la formulación de la fuente y no la del apéndice cuando difieran en carga epistémica. Los tres casos son afirmaciones distintas, no redacciones distintas.

---

### `ISSUE-000023` · Las 34 fuentes son de calidad muy desigual

- **Severidad:** `INFO` · **Tipo:** `unspecified_requirement` · **Bloquea:** Fase 4
- **Afecta:** §10.3, §18.2, `Filogenia.md` bibliografía
- **Relacionada:** `ISSUE-000012`

La bibliografía mezcla Nature, Science, Cell, PLOS Biology y eLife con **un preprint en ResearchGate y un blog personal**. `Filogenia.md` es además una **síntesis secundaria**, no literatura primaria.

Esto tiene dos consecuencias: refuerza la necesidad de la rúbrica de `ISSUE-000012`, y significa que al ingerir hay que atribuir cada afirmación a **su referencia concreta**, no al documento en bloque, porque la fuerza de evidencia varía por afirmación dentro del mismo texto.

**Resolución propuesta:** ingerir `Filogenia.md` como documento fuente cuyas afirmaciones se atribuyen individualmente a sus 34 referencias, y usar el modo auditoría (§18.2) para verificar las de menor solidez.

---

# G. Hallazgos de la verificación del patch `v1.0.0 → v1.1.0`

Se clasificaron las 657 eliminaciones del patch y se verificaron **112 candidatos de pérdida** contra el documento nuevo. **Ninguno resultó ser una pérdida real**: todos sobreviven de forma idéntica, reformulada, reubicada, generalizada o supersedida con enlace. La afirmación de migración no destructiva **se sostiene empíricamente** (ver la nota final de este archivo).

Lo que sí apareció son fallos de contabilidad y debilitamientos no declarados.

### `ISSUE-000024` · `DEC-016` y `DEC-017` se reescribieron en el sitio sin marcarse `SUPERSEDIDO`

- **Severidad:** `ERROR` · **Tipo:** `documentation_ambiguity` · **Bloquea:** Fase 0
- **Afecta:** §30, §0.1, §1.1
- **Localizadores:** `Guia_Maestra_Red_Evolutiva_v1.0.0_ARCHIVO.md:3144-3145`, `Guia_Maestra_Red_Evolutiva_v1.1.0.md:4352-4353`

Dos decisiones cambiaron de contenido conservando su identificador y su estado:

| ID | v1.0.0 | v1.1.0 | Estado en ambas |
|---|---|---|---|
| `DEC-016` | «Atlas **antes que** simulación completa» | «El Atlas es la primera superficie compartida, **integrada desde el primer lanzamiento**» | `DECIDIDO` |
| `DEC-017` | «Reconstrucción como **primer modo jugable**» | «Modo Reconstrucción completo; **reubicado a campañas con evidencia adecuada**» | `RETENIDO` |

No son matices de redacción. `DEC-016` invierte la secuencia: de Atlas como producto previo a componente del primer lanzamiento —lo que §2.6 confirma en prosa («no necesita lanzarse como producto aislado antes de toda jugabilidad»)—. `DEC-017` invierte por completo la prioridad del modo Reconstrucción, como reconoce §2.6 («deja de ser el primer prototipo jugable obligatorio»).

**El cambio está justificado y explicado en prosa; lo que falta es el registro.** §1.1 exige que `DECIDIDO → SUPERSEDIDO` pase por una nueva decisión identificada, y §0.1 que las decisiones reemplazadas se marquen y señalen su reemplazo. `DEC-018` y `DEC-032` recibieron ese tratamiento; estas dos no. Un lector que consulte solo §30 leerá `DEC-016` como si siempre hubiera dicho lo que dice hoy.

Casos menores del mismo patrón: `DEC-015` pierde «y juego» y `DEC-019` cambia «mundo» por «entorno», ambos editados en el sitio.

**Resolución propuesta:** restituir `DEC-016` y `DEC-017` con su texto original marcados `SUPERSEDIDO`, y añadir dos decisiones nuevas con el contenido actual que las reemplacen. Es exactamente el procedimiento del Apéndice H.10.

**RESUELTA el 7 de agosto de 2026** mediante el procedimiento del Apéndice H.10. Hash del archivo `1.0.0` verificado contra la cabecera (`6f17b03…`), snapshot previo guardado en `.snapshot_pre-DEC016-017_2026-08-07.md`. `DEC-016` y `DEC-017` restituidos con su texto original y marcados `SUPERSEDIDO`; añadidos `DEC-049` y `DEC-050` con el contenido vigente; §30.1 y el Apéndice J.3 actualizados.

---

### `ISSUE-000025` · La prueba de preservación está codificada en duro

- **Severidad:** `ERROR` · **Tipo:** `unspecified_requirement` · **Bloquea:** Fase 0
- **Afecta:** §27.11
- **Localizadores:** `Guia_Maestra_Red_Evolutiva_v1.1.0.md:4102`

§27.11 exige comprobar que «`DEC-018` y `DEC-032` permanecen como decisiones supersedidas». La prueba nombra **las dos decisiones concretas que se migraron bien**, de modo que pasaría en verde mientras `ISSUE-000024` sigue abierto. Una prueba que solo comprueba los casos correctos no es una prueba.

**Resolución propuesta:** reformular como invariante general y comprobable contra el archivo, en vez de nombrar identificadores concretos.

**RESUELTA el 7 de agosto de 2026.** §27.11 ahora exige comparar el registro completo contra el archivo, distinguiendo dos casos: cambio de contenido o alcance → `SUPERSEDIDO` con enlace; reformulación editorial → anotada en la matriz de preservación con su texto anterior.

Al ejecutar el invariante aparecieron **cuatro decisiones más** editadas en el sitio: `DEC-015`, `DEC-019`, `DEC-021` y `DEC-025`. Ninguna invierte su contenido —`DEC-019` renombra una vista, `DEC-025` amplía un rechazo, `DEC-015` y `DEC-021` precisan alcance—, así que **no se supersedieron**: quedan registradas en el nuevo Apéndice J.3.1 con su texto anterior. La primera versión del invariante, que exigía superseder ante cualquier diferencia textual, se descartó por generar ruido: una regla que marca «mundo → entorno» como decisión supersedida acaba ignorándose, que es como se produjo el fallo original.

---

### `ISSUE-000026` · La reproducción sexual y el origen de la meiosis desaparecen sin exclusión ni disparador

- **Severidad:** `WARNING` · **Tipo:** `content_gap` · **Bloquea:** Fase 1
- **Afecta:** §21.5, §22.5, §25

El sintagma no aparece en ninguna parte de la v1.1.0. Sobrevive de forma oblicua como «recombinación» y «reproducción» en la columna Eucaria de §21.5, pero **no figura entre las exclusiones declaradas de la Campaña 1 ni entre el trabajo pospuesto de §25 con su disparador**, que es lo que §1.1 exigiría.

El origen del sexo y de la meiosis es uno de los eventos mayores de la evolución eucariota temprana y cae de lleno en el corredor de la Campaña 1. Puede quedar fuera del primer lanzamiento sin problema, pero debe hacerlo **por decisión declarada**, no por omisión.

**Resolución propuesta:** decidir explícitamente en el dossier C01 si entra o no, y si no entra, registrarlo en §25 con disparador.

---

### `ISSUE-000027` · §27.7 perdió la exigencia de evaluar la forma de la distribución

- **Severidad:** `WARNING` · **Tipo:** `unspecified_requirement` · **Bloquea:** Fase 9
- **Afecta:** §27.7 · **Relacionada:** `ISSUE-000011`

La v1.0.0 exigía comprobar una **«distribución razonable de resultados»**; la v1.1.0 la sustituye por «múltiples trayectorias». No es lo mismo: «múltiples trayectorias» se satisface con dos desenlaces distintos, mientras que evaluar la distribución obliga a mirar su **forma** — que es precisamente donde se detectaría una simulación teleológica.

Este hallazgo refuerza y precisa `ISSUE-000011`: la formulación anterior era mejor y debería recuperarse al especificar la prueba de teleología.

**Resolución propuesta:** restituir «distribución razonable de resultados» en §27.7 y usarla como base de la especificación pendiente.

---

### `ISSUE-000028` · Debilitamientos normativos no documentados como simplificaciones

- **Severidad:** `WARNING` · **Tipo:** `documentation_ambiguity` · **Bloquea:** Fase 0
- **Afecta:** §0.1, §2.4, §5.3, §21.14

§0.1 establece que *«toda simplificación del primer lanzamiento debe documentar qué capacidad futura protege o posterga»*. Varias exigencias se relajaron sin esa documentación:

- **§5.3**: «dos o más hipótesis incompatibles» pasa a «una hipótesis principal y una alternativa **incompatible o parcialmente incompatible**». Admitir incompatibilidad parcial debilita la prueba de estrés del modelo de hipótesis, que era su razón de ser.
- **§2.4**: en la v1.0.0 la prohibición de «niveles de poder» cubría especies, taxones y clados; ahora se reduce a «los clados organizan ascendencia, no poder». Especies y taxones pierden protección explícita frente a §23.2, que sigue rechazando «rangos taxonómicos como niveles».
- **«Transferencia horizontal»** pasa a **«transferencia genética abstracta»** en el alcance de la Campaña 1, perdiendo la horizontalidad, que es justo lo que la hace reticulada.
- **§21.14**: los indicativos pasan a potenciales de forma sistemática («se evalúan» → «podrá considerar», «las poblaciones dejan rastros» → «podrán dejar»). Cada caso es defendible; el conjunto convierte especificación en posibilidad.
- **El inventario de campos del Atlas** pasa de lista uniforme a condicional («cuando corresponda»).

**Resolución propuesta:** revisar los cinco casos y, para cada uno, o bien restituir la formulación fuerte, o bien registrar la simplificación con la capacidad futura que protege, según exige §0.1.

---

# H. Detectadas al construir las fases 2 a 6

Salieron al implementar los esquemas, los fixtures y las familias de validación contra datos artificiales. Que aparecieran ahora y no al ingerir el corpus real es exactamente para lo que sirve construir el fixture antes que el dataset.

### `ISSUE-000030` · `provenance.origin` es obligatorio en el esquema y no existe en los ejemplos

- **Severidad:** `ERROR` · **Bloquea:** Fase 4 · **Afecta:** `common.json`, E.6, §9.1

`common.json#/$defs/provenance` declara `origin` como requerido —con valores `ingestion`, `audit`, `editorial`, `derived`— porque §18.2 exige que toda incorporación externa se marque como procedente de auditoría. Pero ni el ejemplo de E.6 ni el de §9.1 lo llevan, así que un `Claim` copiado literalmente del Apéndice E **no valida**.

**Resolución propuesta:** añadir `origin` a los ejemplos de la guía. El campo es correcto y necesario; lo que falta es que el apéndice lo refleje.

---

### `ISSUE-000031` · No hay campo para el reemplazo de un registro deprecado

- **Severidad:** `ERROR` · **Bloquea:** Fase 4 · **Afecta:** todos los esquemas de registro

§16.4 define `DEPRECATE_RECORD` y `SUPERSEDE_RECORD`, y §19.2 exige «deprecaciones con reemplazo o razón». Pero ningún esquema tiene `superseded_by`, `replaced_by` ni `merged_into`, y todos son `additionalProperties: false`. Hoy se puede marcar un registro como superado pero **no se puede decir por cuál**.

Es el mismo defecto que `ISSUE-000024` encontró en el registro de decisiones, ahora en el modelo de datos: marcar sin enlazar deja la trazabilidad a medias.

**Resolución propuesta:** añadir `superseded_by` y `merged_into` opcionales a `common.json` y referenciarlos desde cada esquema de registro.

---

### `ISSUE-000032` · `taxon-concept.json` no admite dimensiones epistémicas

- **Severidad:** `WARNING` · **Bloquea:** Fase 3

Un concepto taxonómico no puede llevar `historical_status: superseded`, que es justo lo que hace falta para conservar una circunscripción abandonada (§4.9). El fixture `historical-classification` lo rodea marcando la afirmación en vez del concepto, lo cual funciona pero desplaza la vigencia de la idea a un registro distinto del que la encarna.

---

### `ISSUE-000033` · §16.2 no asigna fichero a las expresiones temporales ni a las vistas

- **Severidad:** `WARNING` · **Bloquea:** Fase 4

`TIME-` tiene prefijo en §16.3 y esquema propio, pero ningún fichero en el árbol de §16.2. Lo mismo con `TAXVIEW-` y `PHYVIEW-`, que §16.2 sitúa en `knowledge/views/` sin nombrar ficheros. Los fixtures lo han resuelto cada uno a su manera, que es precisamente lo que hay que evitar antes de ingerir.

---

### `ISSUE-000034` · Cuatro tipos de entidad sin prefijo consolidado

- **Severidad:** `WARNING` · **Bloquea:** Fase 3

`entity.json` admite `technology`, `ecosystem`, `method` y `researcher` porque §6.2 los lista como entidades, pero §16.3 no les da prefijo, así que no tienen identificador válido.

---

### `ISSUE-000035` · `Occurrence` no puede llevar tiempo ni lugar

- **Severidad:** `WARNING` · **Bloquea:** Fase 4

§7.8 define la ocurrencia como «presencia documentada o inferida **en un lugar y un intervalo temporal**», pero viaja por `entity.json`, que E.5 exige delgada. El resultado es que un registro `OCC-` no puede expresar lo único que lo define.

Es una tensión real entre E.5 y §7.8, no un error de implementación. Conviene decidir si `Occurrence` merece esquema propio.

---

### `ISSUE-000036` · Los grupos de conflicto no son identificadores opacos

- **Severidad:** `WARNING` · **Bloquea:** Fase 5

§15.2 introduce los grupos de conflicto como mecanismo central de compatibilidad, pero §16.3 no les da prefijo, así que hoy son cadenas libres del tipo `CONFLICT-EUKARYOTE-ROOT-2026-08`. Legibles, pero fuera del sistema de identidad y sin comprobación referencial.

---

### `ISSUE-000037` · Falta un valor de aceptación para lo abandonado

- **Severidad:** `INFO` · **Bloquea:** Fase 4

El eje `acceptance` de §10.1 no tiene valor para «ya no la sostiene nadie». `minority_position` sugiere que alguien todavía la defiende y `not_assessed` que no se ha mirado. La vigencia se puede expresar con `historical_status: rejected`, pero entonces dos ejes independientes se usan de forma acoplada.

---

### `ISSUE-000038` · La proyección de juego no cubre dos campos de §6.8

- **Severidad:** `INFO` · **Bloquea:** Fase 8

§6.8 enumera «efectos» y «condiciones de aparición» entre los datos propios de la capa 8, y `game-projection.json` no los tiene.

---

# I. Resueltas por decisión del 8 de agosto de 2026

Cuatro cuestiones que exigían criterio y no podían cerrarse desde el análisis.

### `ISSUE-000007` · `superseded` designaba dos cosas — **resuelta**

`record_status` pasa a `replaced`; `historical_status` conserva `superseded`, que es el término natural para una idea reemplazada y el que usa §1 para las decisiones. Se añadió una **guardia de migración** en la familia `state`: cualquier registro que todavía use el valor antiguo produce un error que explica el cambio.

Efecto secundario que merece nota: el fixture `state-bad/record-status-as-synonym` existía para demostrar esa confusión, y renombrar el valor la hizo imposible. En vez de retirarlo, ahora demuestra que la guardia funciona.

### `ISSUE-000026` · Sexo y meiosis — **resuelta: entran en la Campaña 1**

Como contenido del Atlas **y** como mecánica. Registrado en §25.5.1 con su consecuencia declarada según exige §0.1: amplía el alcance de la primera campaña frente al riesgo §29.1, y añade variables de simulación que §21.5 no listaba. Propagado a §5.3, §21.5, §21.7, §22.5, al `scientific-scope.json` y al prompt de investigación, donde la sección 11 pasa a ser de primer orden.

Entra recombinación, ploidía, tipos de apareamiento y el costo del sexo frente a la reproducción clonal. Sigue fuera la genética de poblaciones a nivel de locus (§25.1).

### `ISSUE-000028` · Debilitamientos normativos — **resuelta la principal**

§5.3 recupera **dos o más hipótesis incompatibles**. La incompatibilidad parcial es un fenómeno distinto y no ejercita la prueba de estrés del modelo de hipótesis, que era la razón de existir del requisito. El material está: `Filogenia.md` documenta tres controversias del corredor con fuente y el fixture `two-deep-topologies` ya demuestra que la arquitectura lo soporta.

Los otros cuatro debilitamientos —niveles de poder acotados a clados, «transferencia horizontal» → «abstracta», modalidades potenciales en §21.14, campos del Atlas condicionales— quedan como están: son adaptaciones a la estructura por campañas, no recortes de compromiso.

### `ISSUE-000035` · `Occurrence` sin tiempo ni lugar — **resuelta con esquema propio**

`occurrence.json` con `entity_id`, `temporal_expression_id`, `region_id`, `site_id`, las seis clases de precisión de §12.2 y `evidence_basis` observado/inferido. No es una excepción a la delgadez de E.5: es su contraparte, y así queda escrito en §7.8.

Al migrar el fixture salió a la luz por qué importaba: `OCC-000301` expresaba su espécimen y su yacimiento **sólo en el texto de la etiqueta**, de modo que ninguna comprobación podía leerlos. Ahora son campos, y la familia `geography` los verifica.

## Notas que no son cuestiones pendientes


**Las controversias obligatorias de la Campaña 1 ya están identificadas y con fuente.** §5.3 exige «al menos una controversia o hipótesis alternativa real»; `Filogenia.md` documenta tres dentro del corredor Eukaryota → Holozoa:

1. Las ramificaciones profundas de los eucariotas dependen del muestreo y del modelo utilizado.
2. Las posiciones de los holozoos unicelulares no se resuelven porque las divergencias son muy antiguas, las ramas internas cortas y distintas selecciones de genes producen topologías diferentes. Es un caso de manual para distinguir `insufficient_information` de `unresolved` (§10.4).
3. El nodo Choanoflagellata + Metazoa se denomina **Choanozoa *sensu stricto*** o **Apoikozoa** según el autor: el clado no está en disputa, el nombre sí.

Fuera del alcance de la Campaña 1 pero disponibles para campañas posteriores: Ctenophora-first frente a Porifera-first por sintenia cromosómica, y el cuestionamiento de la monofilia de Deuterostomia por error sistemático.

---

**La migración no destructiva se sostiene empíricamente.** Se clasificaron las 657 eliminaciones del patch y se verificaron 112 candidatos de pérdida contra el documento nuevo: **ninguno resultó ser una pérdida real**. Varios candidatos eran falsos positivos por renumeración de secciones o por desduplicación —el documento anterior repetía inventarios en el resumen ejecutivo y en los apéndices, y el patch borró la copia, no el original—.

La evidencia más sólida no es el recuento sino la estructura: la v1.1.0 **añade** el aparato que hace comprobable su propia promesa —§24.1 con la matriz de migración fila por fila, §21.14 con nueve subsecciones de requisitos preservados, el Apéndice J, los fixtures `future-*` y las pruebas de preservación de §27.11—. El patrón de las 2033 adiciones frente a las 657 eliminaciones lo confirma: **se borró prosa de resumen y se añadió mecanismo verificable**. El documento perdió retórica y ganó fuerza normativa, con la excepción de los debilitamientos de `ISSUE-000028`.
