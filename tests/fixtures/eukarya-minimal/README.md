# Fixture `eukarya-minimal`

**Qué es:** el corredor `Eukaryota → Amorphea → Obazoa → Opisthokonta → Holozoa`
con sus ramas hermanas inmediatas, más un nombre taxonómico que sirve a dos
circunscripciones incompatibles.

**Qué NO es:** corpus. `section-000100.md` es un texto sintético escrito para este
fixture. Sus cuatro fuentes son `section_provided` y quedan `pending_verification`
a propósito: ninguna afirmación de aquí puede pasar a `knowledge/records/` sin
volver a ingerirse desde una fuente real con DOI o URL resoluble. `ISSUE-000100` e
`ISSUE-000101` dejan constancia de ello dentro del propio fixture.

Es el fixture número 1 de §27.9 y el conjunto con el que se depura el canal de
ingestión antes de tocar corpus real: cubre los pasos 1–10 del protocolo de §17
sobre un caso lo bastante pequeño para leerlo entero de una sentada.

---

## Qué capacidad prueba

### 1. La cadena de procedencia completa (§4.5, §17 pasos 1–2)

`section-000100.md` → `sections.jsonl` → `passages.jsonl` → `mentions.jsonl` →
`claims.jsonl`. Cada eslabón es reconstruible sin salir del fixture:

- `SEC-000100.content_hash` es el SHA-256 real del fichero `.md`;
- los 5 pasajes cubren la sección **entera**, sin huecos ni solapes: concatenar sus
  `text` en orden de `ordinal` devuelve el fichero carácter a carácter;
- los offsets de las 25 menciones son **absolutos sobre la sección**, no relativos
  al pasaje, de modo que se cumple `texto_sección[start:end] == original_text` y
  además `start`/`end` caen dentro de los límites del pasaje declarado.

Esa doble invariante es lo que hace verificable el paso 2 de §17 («toda mención y
afirmación debe poder volver al pasaje exacto»).

### 2. La regla de promoción de menciones (§8.1, §17 paso 10)

Las 25 menciones agotan la sección y ejercitan cinco destinos distintos:

| Destino | Ejemplo | Por qué está |
|---|---|---|
| `new_entity` | `MENTION-000100` «Eukaryota» | el caso normal |
| `repetition` | `MENTION-000101` «Eukaryota» (2.ª aparición) | una repetición registrada no es una omisión |
| `contextual_attribute` | `MENTION-000108` «grupo hermano» | locución relacional que sostiene una afirmación pero no es entidad |
| `discarded_with_reason` | `MENTION-000106` «progreso» | aparece dentro de una negación del propio texto; se descarta **con razón escrita** |
| `alias` (vía `alias_ids`) | `NAME-000100`/`NAME-000101` en `CLADE-000120` | dos nombres que designan la misma entidad |

`MENTION-000106` es deliberado por partida doble: comprueba el destino
`discarded_with_reason` y da al filtro antiteleológico un caso positivo que
reconocer sin que el texto afirme nada teleológico.

### 3. Nombre ≠ concepto ≠ clado (§7.2–§7.4) — el núcleo del fixture

Éste es el motivo principal de que exista el fixture. Tres registros distintos para
tres cosas distintas:

```
NAME-000100 «Choanozoa»            ← una grafía, sin circunscripción
├── TAXCONCEPT-000100  según SRC-000101   incluye {Choanoflagellata, Metazoa}
│                                          excluye {Filasterea, Ichthyosporea, Pluriformea}
└── TAXCONCEPT-000101  según SRC-000103   incluye {Choanoflagellata, Ichthyosporea,
                                                   Pluriformea, Filasterea}
                                           excluye {Metazoa}

NAME-000101 «Apoikozoa»
└── TAXCONCEPT-000102  según SRC-000102   incluye {Choanoflagellata, Metazoa}   (congruente con 000100)

CLADE-000120 «Clado que reúne Choanoflagellata y Metazoa»
             alias_ids → los dos nombres y los dos conceptos congruentes
```

Hay por tanto **dos rivalidades diferentes**, y no son la misma cosa:

- **rivalidad de circunscripción:** `TAXCONCEPT-000100` frente a
  `TAXCONCEPT-000101`. Comparten grafía y se contradicen término a término —
  `CLADE-000119` (Metazoa) está *incluido* en uno y *excluido* en el otro, y
  `CLADE-000116` (Filasterea) exactamente al revés. `CLAIM-000120` registra la
  incompatibilidad y ninguno de los dos borra al otro (§9.2). Las exclusiones
  expresas son información, no ausencia de información: el concepto histórico no
  es el moderno con menos datos, es **otro contenido**.
- **rivalidad nominal:** `TAXCONCEPT-000100` frente a `TAXCONCEPT-000102`.
  Circunscripción idéntica, nombres distintos. `CLADE-000120` se asigna a los dos
  a la vez (`CLAIM-000118` y `CLAIM-000119`) y eso **no** es un conflicto.

`CLADE-000120` se etiqueta por su contenido y no por ninguno de los dos nombres en
disputa. La etiqueta preferida no es identidad (§16.3): si el fixture llamara
«Choanozoa» al clado, el dato ya habría elegido bando antes de que ninguna vista lo
decidiera.

`phylogenetic_interpretation` vale `paraphyletic` en el concepto histórico y
`monophyletic` en los dos modernos: §7.4 prohíbe inferir que todo taxón formal sea
monofilético, así que el campo se rellena, no se supone.

### 4. Clado ≠ linaje (§7.5)

`LINEAGE-000120` y `LINEAGE-000121` son linajes troncales anteriores a los grupos
corona de Opisthokonta y Holozoa. Entran en el dataset **sin nombre nomenclatural**
y se relacionan con los clados por `stem_lineage_of`, no por `member_of`. Un linaje
troncal no es el grupo corona, y el fixture lo mantiene separado para que ninguna
vista los pueda confundir.

### 5. Afirmaciones derivadas frente a afirmaciones expresas (§9.4)

Dos de las 25 afirmaciones llevan `derivation` y `provenance.origin: "derived"`:

- `CLAIM-000124`: `contains ← inversa de member_of`, depende de `CLAIM-000100`;
- `CLAIM-000121`: `historically_classified_as`, derivada del concepto histórico.

Ninguna de las dos es una frase literal de la sección, y el registro lo dice.

### 6. Seis ejes epistémicos, nunca un número (§10)

Las 25 afirmaciones llevan `epistemic_dimensions` anidado con los cuatro campos
obligatorios, `record_status` en la raíz y `evidence_strength_reason` escrita
siempre que `evidence_strength` no sea `unknown`. `CLAIM-000121` es el caso donde
`historical_status: "historical"` y `record_status: "active"` divergen: la idea está
superada, el registro sigue vivo.

---

## Contenido

| Fichero | Registros | Nota |
|---|---|---|
| `section-000100.md` | — | original inmutable; su SHA-256 está en `sections.jsonl` |
| `sections.jsonl` | 1 | `SEC-000100` |
| `passages.jsonl` | 5 | `PASSAGE-000100`–`000104` |
| `mentions.jsonl` | 25 | `MENTION-000100`–`000124` |
| `sources.jsonl` | 4 | `SRC-000100`–`000103`, todas `section_provided` |
| `taxonomic-names.jsonl` | 2 | `NAME-000100`–`000101` |
| `taxon-concepts.jsonl` | 3 | `TAXCONCEPT-000100`–`000102` |
| `clades.jsonl` | 16 | `CLADE-000100`–`000104` (corredor), `000110`–`000120` (ramas y nodo en disputa) |
| `lineages.jsonl` | 2 | `LINEAGE-000120`–`000121` |
| `claims.jsonl` | 25 | `CLAIM-000100`–`000124` |
| `issues.jsonl` | 2 | `ISSUE-000100`–`000101`, ambas abiertas a propósito |

**Rango de identificadores:** `000100`–`000124` en todos los prefijos. El fixture
`endosymbiosis-event` usa `000200`–`000299`, de modo que los dos pueden cargarse a
la vez sin colisión.

`sections.jsonl` y `passages.jsonl` no tienen homólogo en `knowledge/records/`
—§16.2 coloca ese material en `knowledge/corpus/`— pero se incluyen aquí para que
el fixture sea autocontenido y la cadena de procedencia se pueda comprobar sin
depender de nada externo.

---

## Qué debería FALLAR si el esquema se rompe

Cada punto es una comprobación ejecutable. Se han verificado rompiendo el fixture
en una copia y confirmando que el fallo aparece.

1. **Si `character_offsets` deja de referirse a la sección**, o alguien reescribe
   `section-000100.md` sin recalcular el hash: `texto[start:end] == original_text`
   falla en la primera mención, y `content_hash` deja de coincidir. El original es
   inmutable (§6.1); esta comprobación es lo que lo hace cierto en vez de deseable.
2. **Si `passage.character_offsets` deja de ser contiguo**, la concatenación de los
   5 pasajes ya no reconstruye el fichero y aparece un hueco o un solape.
3. **Si `mention.disposition` admite `null`** o se relaja la exigencia de nota en
   `discarded_with_reason`: la auditoría de cobertura de §17 paso 10 pasa en verde
   con `MENTION-000106` sin justificar, que es exactamente el fallo silencioso que
   la regla existe para impedir.
4. **Si `TaxonConcept.according_to_source_id` deja de ser obligatorio**, o si los
   dos conceptos que comparten `NAME-000100` acaban citando la misma fuente:
   `TAXCONCEPT-000100` y `TAXCONCEPT-000101` se vuelven indistinguibles y el
   fixture pierde su razón de ser. Sin fuente no hay concepto, sólo un nombre.
5. **Si alguien «resuelve» la ambigüedad fusionando los dos conceptos**, la
   comprobación de que las circunscripciones se contradicen —`CLADE-000119`
   incluido en una y excluido en la otra, `CLADE-000116` al revés— deja de
   cumplirse. Una fusión aquí sería una pérdida de información disfrazada de
   limpieza.
6. **Si `excluded_entity_ids` desaparece del esquema**, `TAXCONCEPT-000101` ya no
   puede decir que Metazoa queda **fuera**, y pasa a leerse como una versión
   incompleta del concepto moderno en vez de como un contenido distinto.
7. **Si `preferred_label` se convierte en identidad**, `CLADE-000120` tendría que
   llamarse «Choanozoa» o «Apoikozoa» y el dato elegiría bando. La comprobación
   verifica que la etiqueta no contiene ninguno de los dos nombres.
8. **Si el prefijo `LINEAGE-` se colapsa con `CLADE-`**, `stem_lineage_of` pierde
   sentido: un linaje troncal pasaría a ser miembro de su propio grupo corona.
9. **Si `derivation` deja de ser obligatorio en las calculadas**, `CLAIM-000124`
   (`contains`) se vuelve indistinguible de una afirmación expresa de la fuente, y
   la inversa de `member_of` empieza a contar como evidencia independiente.
10. **Si `epistemic_dimensions` se aplana** a un `epistemic_status` único o a un
    porcentaje de confianza: `additionalProperties: false` rechaza el campo nuevo,
    y `CLAIM-000121` deja de poder expresar que la idea es histórica mientras el
    registro sigue activo.
11. **Si los identificadores admiten menos de seis dígitos** (`DEC-052`), el patrón
    de `common.json` rechaza el registro.
12. **Si se borra una fuente citada**, la integridad referencial detecta el
    `source_ids` colgante, incluido cuando cuelga dentro de `provenance`.
13. **Si `source_type: "section_provided"` deja de exigir
    `pending_verification`**, las cuatro fuentes del fixture pasarían por
    verificadas y el fixture se leería como corpus. Es precisamente lo que no es.

---

## Cómo se comprueba

Todas las invariantes de arriba se derivan de los ficheros y se pueden reconstruir
sin herramienta especial: cargar los `.jsonl`, cargar `section-000100.md` y
comparar. Mientras la Fase 1 no añada un cargador de fixtures a
`scripts/validate/`, el validador del núcleo (`scripts/validate/validate.py`) sólo
lee `knowledge/records/` y **no ve este directorio** — que es lo correcto: un
fixture no es el libro mayor.
