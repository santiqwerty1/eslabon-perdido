# Fixture `observed-vs-inferred-time`

**Fixture de referencia 4 de §27.9**, «primera evidencia frente a origen». Dato de prueba, **no
corpus**. Rango de identificadores reservado: **`000301`–`000399`**.

---

## Qué capacidad prueba

Dos cosas que §11.3 exige y que son fáciles de perder al simplificar el modelo temporal:

1. **El primer fósil conocido no es el origen del linaje.** El mismo taxón lleva a la vez un
   `ObservedTaxonRange` y un `InferredLineageRange` claramente distintos, más un `DivergenceEstimate`
   con su método y su calibración. Los tres son tipos temporales separados, con `determination`
   distinta, y ninguno sustituye a otro.
2. **Una inversión aparente entre rangos observados genera ADVERTENCIA, no error.** El fixture
   construye la inversión a propósito y fija esa severidad.

## Por qué existe

El riesgo que ataja es concreto: colapsar el tiempo de una entidad en un solo par de fechas. En
cuanto un taxón tiene «una fecha de inicio», el límite antiguo de su registro fósil pasa a ser su
origen, y eso es una afirmación que nadie ha hecho. §11.1 separa ocho tipos temporales por esta razón
y avisa de que «un rango observado no es una duración inferida».

La segunda mitad es igual de importante. Si la validación tratara toda inversión temporal como error,
obligaría a falsear un rango observado para que el conjunto de datos pasara. El registro fósil es
incompleto: el hueco es información sobre el muestreo, no una contradicción entre afirmaciones.

## El caso, en cifras

Sujeto: **`CLADE-000302`, Rhodophyta**.

| Registro | Tipo | Intervalo | `determination` |
|---|---|---|---|
| `TIME-000301` | `observed_taxon_range` | 1047 – 0 Ma | `observed` |
| `TIME-000302` | `inferred_lineage_range` | 1600 – 0 Ma (IC 95 %: 1750–1400) | `inferred` |
| `TIME-000303` | `divergence_estimate` | 1600 – 1400 Ma (IC 95 %) | `modelled` |
| `TIME-000304` | `occurrence_date` | 1064 – 1030 Ma (1047 ± 17) | `observed` |

**553 Ma** separan el límite observado del inferido. Esa diferencia es el contenido del fixture.

`TIME-000303` declara método (`molecular_clock`), calibración (reloj relajado log-normal no
correlacionado con tres calibraciones fósiles) y nivel del intervalo creíble. `ANALYSIS-000301` usa
`TIME-000304` como **punto de calibración de límite mínimo**, nunca como edad de nodo: es la
traducción metodológica de la misma regla.

### Las dos inversiones

**A. Sobre una relación de ascendencia — la que la validación comprueba hoy.**

```text
CLADE-000304  (FIX-A, descendiente)  registro observado  1047 – 1020 Ma
LINEAGE-000301 (FIX-B, ancestro)     registro observado  1000 –  980 Ma
CLAIM-000317: CLADE-000304 descends_from LINEAGE-000301
```

El ancestro propuesto queda **entero posterior** a su descendiente. Como las dos envolventes son
`observed_taxon_range` con `determination: "observed"`, la familia `tiempo` emite:

```text
WARNING tiempo: CLAIM-000317 sitúa a LINEAGE-000301 como ancestro de CLADE-000304, pero
        LINEAGE-000301 es entero posterior a CLADE-000304; inversión entre rangos
        observados: advertencia (§11.3)
```

Justificada en `ISSUE-000306`, como exige §19.1. **La resolución correcta es registrar un
`inferred_lineage_range` para `LINEAGE-000301` que alcance a su descendiente —documentar el linaje
fantasma—, nunca recortar ni borrar los rangos observados.** El fixture lo deja sin registrar a
propósito: con él, la advertencia desaparece y no habría nada que comprobar.

**B. Entre un grupo y el grupo que lo contiene.**

`CLADE-000302` (1047 Ma) aparece en el registro 47 Ma antes que `CLADE-000301`, Archaeplastida
(1000 Ma), del que es miembro por `CLAIM-000304`. Registrada en `ISSUE-000301`. La familia `tiempo`
aún no cubre inversiones contenedor/miembro —solo ascendencia y eventos—, así que hoy la cuestión
documenta el caso y queda esperando a que lo haga.

### La lectura rechazada, conservada

§9.2 exige poder registrar una afirmación **y** su rechazo sin borrar la primera:

- `CLAIM-000313` iguala el origen del linaje con su primer fósil, apoyada en `TIME-000308`, cuya
  `determination` es `reported_without_basis`. Queda con `historical_status: "rejected"` y
  `record_status: "active"`: la idea está descartada, el registro sigue vivo. Son ejes distintos
  (§10.5 y §10.6) y confundirlos es un fallo frecuente.
- `CLAIM-000314` recoge el rechazo expreso, con **la fuente como sujeto**: «`SRC-000303` rechaza
  `CLAIM-000313`». Así queda claro quién sostiene el rechazo.

## Contenido

```text
corpus/SEC-000301.md        texto sintético de origen; su hash está en sections.jsonl
sections.jsonl              1   passages.jsonl            5    mentions.jsonl   8
sources.jsonl               3   taxonomic-names.jsonl     3    taxon-concepts.jsonl  1
clades.jsonl                4   lineages.jsonl            1    specimens.jsonl  1
sites.jsonl                 1   occurrences.jsonl         1
temporal-expressions.jsonl 10   claims.jsonl             18    evidence.jsonl   6
datasets.jsonl              1   analyses.jsonl            1    results.jsonl    1
issues.jsonl                6
```

## Qué debería FALLAR si el esquema se rompe

1. **Si `temporal_type` se reduce o `observed_taxon_range` e `inferred_lineage_range` se fusionan**,
   `TIME-000301` y `TIME-000302` colapsan en un solo registro y el fixture pierde su objeto: el
   primer fósil volvería a ser el origen.
2. **Si `determination` desaparece de `temporal-expression.json`**, se pierde la separación entre lo
   datado y lo estimado, y con ella la regla de severidad: `_observed_only` no podría decidir si una
   inversión es advertencia o error.
3. **Si `interval.unit` deja de ser obligatoria**, los intervalos dejan de ser comparables y
   `_check_intervals` debe dar ERROR: sin unidad explícita un intervalo no es interpretable (§11.4).
4. **Si `uncertainty` deja de ser obligatoria**, `TIME-000308` aparentaría la misma precisión que
   `TIME-000302`. La ausencia de dato no es precisión (§11.2).
5. **Si `calibration` desaparece**, una fecha de reloj molecular y una estratigráfica se compararían
   como si fueran lo mismo.
6. **Si la validación degrada la advertencia de la inversión A a ERROR**, el fixture deja de pasar.
   Es el fallo que más importa: forzaría a falsear un rango observado para que el conjunto validara.
7. **Y al revés: si `TIME-000310` se cambiara a `inferred_lineage_range` o a `divergence_estimate`
   sin tocar nada más, la misma configuración debe pasar a ERROR.** Una duración biológica inferida
   sí pretende cubrir la existencia del linaje, así que ahí la inversión ya no se explica por
   incompletitud del registro. Este es el contraste que fija la regla por los dos lados.
8. **Si `predicate` pierde `rejects_claim`, o `claim.json` deja de admitir `SRC-` como sujeto**,
   `CLAIM-000314` deja de validar y ya no se puede registrar un rechazo sin borrar lo rechazado.
9. **Si `historical_status` y `record_status` se unifican**, `CLAIM-000313` se vuelve
   irrepresentable: no habría forma de decir «idea rechazada, registro conservado».
10. **Si `analysis.json` pierde `calibration_ids`**, se pierde que la datación por reloj molecular use
    una fecha observada como límite mínimo, que es lo que ata el reloj al registro sin confundirlos.

## Cómo se comprueba

```bash
make test      # cuando tests/run_tests.py exista
```

Estado verificado al crearlo, con las siete familias de `scripts/validate/families/` cargadas sobre
este directorio: **0 errores y 2 advertencias, las dos buscadas** —la inversión de `CLAIM-000317` y
el `reported_without_basis` de `TIME-000308`—, ambas con su cuestión pendiente asociada. Los 72
registros validan contra su esquema.

## Advertencias sobre el contenido

- **Las tres fuentes son sintéticas** (`[FIXTURE]`, `verification_status: "unresolvable"`) y **las
  cifras son ilustrativas**: 1047, 1600 y 1400 Ma se eligieron para que la separación entre los tres
  tipos temporales se vea sin ambigüedad. **Nada de esto debe promoverse a `knowledge/records/`.** La
  advertencia de la familia `procedencia` por falta de DOI está justificada en `ISSUE-000303`.
- **`CLADE-000304` y `LINEAGE-000301` llevan etiqueta neutra a propósito** (FIX-A, FIX-B): la
  configuración temporal que ilustran no debe atribuirse a ningún taxón real.
- Las expresiones temporales viven en `temporal-expressions.jsonl` porque §16.2 no les asigna fichero
  propio. Convención local del fixture, registrada en `ISSUE-000305`.
