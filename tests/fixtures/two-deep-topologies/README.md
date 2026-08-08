# Fixture `two-deep-topologies`

**Fixture de referencia 3 de §27.9.** Dato de prueba, **no corpus**.
Rango de identificadores reservado: **`000401`–`000499`**.

---

## Qué capacidad prueba

Que el sistema **aloja dos hipótesis incompatibles sobre el mismo conjunto de entidades sin
fundirlas, sin promediarlas y sin elegir una por defecto**.

Concretamente, que se puede sostener a la vez, en un solo conjunto de datos:

| Exigencia | Dónde vive |
|---|---|
| dos hipótesis con sus afirmaciones incluidas | `hypotheses.jsonl` · `included_claim_ids` |
| lo que cada una necesita para sostenerse | `required_claim_ids` |
| lo que cada una descarta sin borrarlo | `excluded_claim_ids` |
| supuestos de cada una | `assumptions` |
| evidencia favorable **y** contraevidencia | `supporting_evidence_ids` / `counterevidence_ids` |
| fuentes favorables **y** fuentes opuestas | `supporting_source_ids` / `opposing_source_ids` |
| un grupo de conflicto que las declara excluyentes | `conflict_group_ids` |
| dos vistas derivadas, una por hipótesis | `phylogenetic-views.jsonl` |
| lo que cada vista **excluye**, declarado | `excluded_claim_ids` + `editorial_criteria` |

## Por qué existe

§2.2 dice que no se construirá un árbol único y §15.4 que el «consenso principal» será una vista
editorial fechada, no una verdad. Eso solo se puede comprobar con dos topologías que de verdad no
quepan en el mismo árbol. Sin este fixture, nada impide que el esquema evolucione hacia un modelo
donde la alternativa perdedora se guarde como una nota al pie de la ganadora —que es exactamente lo
que §0.1 y §9.2 prohíben.

El caso elegido es la posición de Eukaryota respecto de Archaea, dentro del alcance de la Campaña 1:

- **`HYP-000401`, dos dominios.** Eukaryota dentro de Asgardarchaeota y, por tanto, dentro de
  Archaea; Archaea queda parafilética.
- **`HYP-000402`, tres dominios.** Eukaryota como grupo hermano de una Archaea monofilética.

Las dos ordenan los **mismos siete clados** de forma distinta, y comparten cuatro afirmaciones no
disputadas: el desacuerdo está acotado y se ve dónde empieza.

## Contenido

```text
corpus/SEC-000401.md          texto sintético de origen; su hash está en sections.jsonl
sections.jsonl                1  · SEC-000401
passages.jsonl                5  · PASSAGE-000401..405, con desplazamientos reales
mentions.jsonl                6  · todas con destino (§17 paso 10)
sources.jsonl                 4  · 2 favorables, 2 críticas — SINTÉTICAS
taxonomic-names.jsonl         3
taxon-concepts.jsonl          2  · el MISMO nombre Archaea con dos interpretaciones incompatibles
clades.jsonl                  7  · CLADE-000401..407
claims.jsonl                 15  · 4 compartidas, 4+3 exclusivas, 3 epistemológicas, 1 derivada
evidence.jsonl                5  · una de ellas cuestiona a las DOS hipótesis
datasets.jsonl                2
analyses.jsonl                4
results.jsonl                 4  · dos topologías Newick incompatibles
hypotheses.jsonl              2
classification-views.jsonl    2  · TAXVIEW-000401 / 000402
phylogenetic-views.jsonl      2  · PHYVIEW-000401 / 000402
issues.jsonl                  4
```

### Las dos topologías

```text
PHYVIEW-000401  (CLADE-000401,(CLADE-000406,(CLADE-000407,(CLADE-000404,CLADE-000405))CLADE-000403)CLADE-000402);
PHYVIEW-000402  (CLADE-000401,((CLADE-000406,(CLADE-000407,CLADE-000404)CLADE-000403)CLADE-000402,CLADE-000405));
```

Mismas hojas, distinto orden de ramificación. Las etiquetas son identificadores opacos: el formato de
intercambio no reintroduce el nombre como identidad (§16.3).

### Detalles que el fixture fija a propósito

- **`DATASET-000401` es el mismo para `ANALYSIS-000401` y `ANALYSIS-000402`.** Las dos topologías
  salen de los mismos datos con modelos distintos. Registrar conjunto de datos y análisis por
  separado (§6.4) es lo que permite leer eso.
- **`EVID-000405` cuestiona las dos hipótesis** y no respalda ninguna. Una evidencia no tiene por qué
  repartirse en bandos.
- **`0,99` de probabilidad posterior y `82` de bootstrap conviven sin compararse** (§10.7).
- **`CLAIM-000441` es derivada** (`contains ← inversa de member_of`), declara su regla y su
  dependencia, y las dos vistas la **excluyen**: una vista dibuja afirmaciones expresas y recalcula
  las derivadas al construirse (§9.4).
- **`CLAIM-000431` y `CLAIM-000432` dejan `evidence_strength` en `unknown`.** Una incompatibilidad
  estructural no se sostiene en evidencia empírica, y §10 no permite rellenar un eje con un valor que
  no le corresponde.
- **`HYP-000402` es posición minoritaria y aun así tiene vista propia, supuestos y fuentes.** Ser
  minoritaria no la convierte en registro de segunda (§20.3).

## Qué debería FALLAR si el esquema se rompe

Cada punto es una regresión que este fixture detecta:

1. **Si `hypothesis.json` pierde `counterevidence_ids` u `opposing_source_ids`**, las dos hipótesis
   dejan de validar. E.9 los exige precisamente para que una hipótesis no sea una conclusión
   disfrazada.
2. **Si `excluded_claim_ids` desaparece de `hypothesis.json` o de las vistas**, se pierde la
   diferencia entre «no seleccionado» y «declarado incompatible», y ya no se puede comprobar que
   excluir no es borrar (§9.2).
3. **Si `conflict_group_ids` desaparece**, la exclusión mutua deja de ser dato y pasa a ser
   convención implícita: §15.2 la quiere explícita.
4. **Si el predicado `incompatible_with` sale del vocabulario cerrado de `claim.json`**,
   `CLAIM-000431` y `CLAIM-000432` dejan de validar y la familia `hipótesis` pierde los pares duros
   que comprueba.
5. **Si `taxon-concept.json` deja de exigir `according_to_source_id`**, `TAXCONCEPT-000401` y
   `TAXCONCEPT-000402` se vuelven indistinguibles: mismo nombre, misma lista de miembros, y sin
   fuente no habría nada que los separe salvo un campo interpretativo. Sería el fallo de §7.3 en
   estado puro.
6. **Si `phylogenetic-view.json` deja de exigir `editorial_criteria`, `simplifications` o
   `cutoff_date`**, las vistas aparentan ser atemporales y sin criterio, que es lo que §15.4 impide.
7. **Si alguien «arregla» el fixture fusionando las dos vistas en un árbol**, la familia `hipótesis`
   debe dar ERROR: §17 paso 9 y `_check_view_mixing` no permiten que una vista materialice dos
   hipótesis del mismo grupo de conflicto.
8. **Si una vista selecciona `CLAIM-000411` y `CLAIM-000421` a la vez**, debe dar ERROR por
   incompatibilidad declarada.
9. **Si `epistemic_dimensions` se aplana a un único `epistemic_status`**, se pierde que `HYP-000402`
   sea a la vez posición minoritaria, de evidencia baja, no resuelta y vigente. Son cuatro ejes
   independientes (§10) y aquí no coinciden.

## Cómo se comprueba

```bash
make test      # cuando tests/run_tests.py exista
```

Estado verificado al crearlo, con las siete familias de `scripts/validate/families/` cargadas sobre
este directorio: **0 errores, 0 advertencias**. Los 68 registros validan contra su esquema con
`jsonschema`, y sin `jsonschema` la comprobación degrada a JSON bien formado, como `validate.py`.

## Advertencias sobre el contenido

- **Las cuatro fuentes son sintéticas** (`[FIXTURE]`, `verification_status: "unresolvable"`). No
  corresponden a publicaciones reales y **no deben citarse ni promoverse a `knowledge/records/`**.
  Que no lleven DOI ni URL provoca una advertencia de la familia `procedencia`: `ISSUE-000403` es su
  justificación, como exige §19.1.
- Los nombres de clado son reales porque el fixture necesita dos reconstrucciones que de verdad
  compitan, pero los valores de soporte, los tamaños de matriz y los resultados son **ilustrativos**.
- Las vistas y los conceptos taxonómicos se guardan en `phylogenetic-views.jsonl` y
  `classification-views.jsonl`: §16.2 no fija nombre de fichero para las vistas. Es convención local
  del fixture y está registrada en `ISSUE-000404`.
