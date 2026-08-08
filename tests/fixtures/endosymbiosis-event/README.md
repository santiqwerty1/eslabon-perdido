# Fixture `endosymbiosis-event`

**Qué es:** un evento n-ario de endosimbiosis con dos participantes de papel
declarado, una entidad resultante, dos dataciones incompatibles, evidencia,
contraevidencia y las afirmaciones que lo sostienen.

**Qué NO es:** corpus. `section-000200.md` es un texto sintético. Las tres fuentes
son `section_provided` y quedan `pending_verification`. **Los límites numéricos de
las dos dataciones son marcadores del fixture**: existen para probar intervalo,
unidad, punto de referencia, calibración, método y determinación, no para afirmar
cuándo ocurrió nada. `ISSUE-000200` lo deja escrito dentro del propio fixture y
bloquea su uso canónico.

Es el fixture número 2 de §27.9. Según la matriz de preservación (§ Apéndice J), la
endosimbiosis sustituye a la introgresión como **primer fixture real de
reticulación**: es el caso mínimo que obliga al modelo a demostrar que un proceso
reticulado no cabe en un árbol.

---

## Por qué existe: la reticulación no es una bifurcación

El riesgo que este fixture vigila es concreto. Alguien —una migración, un
constructor de vistas, una simplificación para el juego, un `git merge`
descuidado— sustituye el evento por una arista binaria del tipo
`LINEAGE-000202 descends_from LINEAGE-000200` y da el modelo por equivalente. No lo
es, y el fixture está construido para que esa sustitución sea **detectable**, no
opinable.

Lo que se pierde al aplanar, punto por punto:

| Se pierde | Dónde vive en el fixture |
|---|---|
| **Quién fue hospedador y quién endosimbionte** | `EVENT-000200.participants[].role` |
| **Que la asociación produjo un tercero** | `EVENT-000200.result_entity_ids` |
| **Que el tercero tiene dos antecesores** | `CLAIM-000204` y `CLAIM-000205` |
| **Que hay dos dataciones que no se promedian** | `EVENT-000200.temporal_expression_ids` (plural) |
| **Que la evidencia no fija la fecha** | `EVID-000202` en `counterevidence_ids` |

### El papel no cabe en el predicado

`CLAIM-000200` es la afirmación que sostiene el evento:

```
LINEAGE-000200  endosymbiosis_with  LINEAGE-000201
```

Es **simétrica y ciega a los papeles**. No dice cuál de los dos linajes alojó al
otro, ni que la asociación produjera un tercer linaje. Está así a propósito: es la
demostración de que el par `(sujeto, predicado, objeto)` no basta y de que el nodo
evento no es un adorno. Intercambiar sujeto y objeto en `CLAIM-000200` produce la
misma afirmación; intercambiar `host` y `endosymbiont` en `EVENT-000200` produce
una afirmación **distinta**.

### El descendiente tiene dos progenitores

`LINEAGE-000202` recibe exactamente dos aristas `contributes_ancestry_to`, una por
participante. Ninguna topología de bifurcación admite ese nodo: un árbol da un
progenitor por nodo, y aquí sobra uno. Las dos afirmaciones llevan `derivation` con
`depends_on_ids: ["EVENT-000200"]` y `origin: "derived"` — se calculan **desde** el
evento con papeles, no al revés, de modo que borrar el evento invalida las dos en
lugar de dejarlas huérfanas y creíbles.

---

## La comprobación que fallaría si alguien lo aplanara

Cinco asertos sobre los ficheros de este directorio. Los cinco pasan hoy; los cinco
se han verificado rompiendo el fixture en una copia y confirmando el fallo.

```python
ev     = events["EVENT-000200"]
parts  = {p["entity_id"] for p in ev["participants"]}
roles  = [p["role"] for p in ev["participants"]]

# A. El evento es n-ario CON papeles asimétricos.
assert len(ev["participants"]) >= 2
assert set(roles) == {"host", "endosymbiont"}       # no {"participant", "participant"}

# B. Hay un producto, y no es ninguno de los participantes.
res = set(ev["result_entity_ids"])
assert res and not (res & parts)

# C. LA CLAVE: el resultante recibe DOS ascendencias, una por participante.
padres = {s for s, o in aristas("contributes_ancestry_to") if o == "LINEAGE-000202"}
assert padres == parts and len(padres) == 2

# D. Ninguna arista binaria de árbol ha ocupado el lugar del evento.
assert not claims_con_predicado("descends_from", "diverges_from", "possible_ancestor_of")

# E. Las dos dataciones conviven, cada una en su afirmación, sin promediarse.
assert len(ev["temporal_expression_ids"]) == 2
assert len(claims_con_predicado("dated_to")) == 2
assert len({intervalo(t) for t in ev["temporal_expression_ids"]}) == 2
```

Qué caza cada uno:

- **A** cae si alguien uniforma los papeles a `participant` —la forma más
  educada de perder la asimetría, porque el registro sigue validando contra el
  esquema y sólo el aserto nota que ya no dice nada.
- **B** cae si se borra `result_entity_ids` y el proceso se queda sin producto.
- **C** es el aserto central. Cae en cuanto la reticulación se aplana: si alguien
  cambia `contributes_ancestry_to` por `descends_from`, o elimina una de las dos
  contribuciones, `LINEAGE-000202` pasa a tener un solo antecesor y el fixture
  denuncia que se ha convertido en un árbol.
- **D** es el aserto complementario: prohíbe que reaparezca la lectura
  bifurcante por la puerta de atrás, con el evento aún presente pero ya
  irrelevante.
- **E** cae si alguien «resuelve» las dos dataciones quedándose con una o
  promediándolas.

---

## Qué más prueba

### Tiempo con incertidumbre declarada (§11.1–§11.4)

Dos `TemporalExpression` de tipo `event_date` para el **mismo** episodio:

| | `TIME-000200` | `TIME-000201` |
|---|---|---|
| intervalo | 2100–1200 | 1900–1400 |
| unidad | `million_years` | `million_years` |
| referencia | `before_present` | `before_present` |
| calibración | `stratigraphic` | `molecular_clock` |
| `method_type` | `stratigraphic_correlation` | `molecular_clock` |
| `determination` | `inferred` | `modelled` |

Sólo se solapan en parte y proceden de métodos que no son comparables entre sí, así
que **no se promedian ni se elige entre ellas en la capa de datos**: `ISSUE-000201`
deja la cuestión abierta y señala que elegir corresponde a una vista editorial
fechada. La incertidumbre es `range_only` en las dos: el ancho del intervalo *es* la
incertidumbre, y `original_expression` conserva la redacción de la sección para que
ninguna conversión redondee en silencio.

### Evidencia y contraevidencia con el mismo rango (§6.4)

`EVID-000200` (genómica) y `EVID-000201` (molecular) apoyan `CLAIM-000200`.
`EVID-000202` **cuestiona** las dos dataciones a la vez, y sale de una advertencia
de la propia sección: la evidencia genómica respalda la asociación pero no fija la
fecha. Está en `counterevidence_ids` del evento y en `challenges_claim_ids` de la
evidencia. `limitations` está poblado en las tres: lo que la evidencia **no**
permite concluir se registra aunque la fuente sea entusiasta.

### Rasgo separado de su portador (§7.9)

`TRAIT-000200` (mitocondria) es una entidad aparte, unida a `LINEAGE-000202` por
`CLAIM-000203` (`acquires_trait`). El rasgo no es un campo del linaje.

### Menciones que son papeles, no entidades (§8.1)

«hospedador» y «endosimbionte» se registran con `disposition: "event_part"` y
`resolution.target_ids: ["EVENT-000200"]`: son papeles dentro del evento y no se
promueven a entidad. «dos antecesores» va como `contextual_attribute` y apunta a
las dos afirmaciones de ascendencia.

---

## Contenido

| Fichero | Registros | Nota |
|---|---|---|
| `section-000200.md` | — | original inmutable; su SHA-256 está en `sections.jsonl` |
| `sections.jsonl` | 1 | `SEC-000200` |
| `passages.jsonl` | 5 | `PASSAGE-000200`–`000204` |
| `mentions.jsonl` | 14 | `MENTION-000200`–`000213` |
| `sources.jsonl` | 3 | `SRC-000200`–`000202`, todas `section_provided` |
| `lineages.jsonl` | 3 | hospedador, endosimbionte y resultante |
| `traits.jsonl` | 1 | `TRAIT-000200` |
| `temporal-expressions.jsonl` | 2 | `TIME-000200`–`000201` |
| `events.jsonl` | 1 | `EVENT-000200` |
| `claims.jsonl` | 6 | `CLAIM-000200`–`000205` |
| `evidence.jsonl` | 3 | `EVID-000200`–`000202` |
| `issues.jsonl` | 2 | `ISSUE-000200`–`000201`, ambas abiertas a propósito |

**Rango de identificadores:** `000200`–`000213` en todos los prefijos, separado del
`000100`–`000124` de `eukarya-minimal`, de modo que los dos fixtures pueden
cargarse a la vez sin colisión.

`temporal-expressions.jsonl` no tiene homólogo en `knowledge/records/`: §16.2 no
asigna fichero propio a las expresiones `TIME-`, que se referencian desde
afirmaciones y eventos. Se incluye aquí para que el fixture sea autocontenido.
Lo mismo vale para `sections.jsonl` y `passages.jsonl`, cuyo material canónico vive
en `knowledge/corpus/`.

---

## Qué más debería FALLAR si el esquema se rompe

Además de los cinco asertos de arriba:

1. **Si `participants[].role` desaparece o se abre a texto libre**, la distinción
   entre hospedador y endosimbionte deja de ser comprobable y el evento se
   convierte en una lista de nodos.
2. **Si `participants` admite menos de dos elementos**, el tipo `endosymbiosis`
   pierde sentido: no hay simbiosis con un solo participante.
3. **Si `result_entity_ids` o `temporal_expression_ids` se vuelven singulares**,
   el evento no puede tener a la vez dos dataciones incompatibles ni declarar un
   producto distinto de sus participantes. Los plurales del esquema son
   deliberados.
4. **Si `interval.unit` deja de ser obligatorio**, `2100–1200` es un número sin
   interpretación: años, miles o millones. §11.4 lo prohíbe y el esquema lo
   rechaza.
5. **Si `uncertainty` deja de ser obligatorio**, un intervalo sin incertidumbre
   declarada se lee como una precisión que nadie afirmó. Ausencia de dato no es
   precisión.
6. **Si `determination` desaparece**, `TIME-000200` (`inferred`) y `TIME-000201`
   (`modelled`) se vuelven indistinguibles de una fecha observada, que es
   exactamente lo que §11.3 prohíbe presentar sin marcar.
7. **Si `counterevidence_ids` o `challenges_claim_ids` se recortan**,
   `EVID-000202` se queda sin sitio y el límite que la propia sección declara
   desaparece del registro.
8. **Si `derivation` deja de ser obligatorio en las calculadas**,
   `CLAIM-000204`/`CLAIM-000205` dejan de depender de `EVENT-000200` y sobreviven
   como ascendencias sueltas y creíbles después de que el evento se borre.
9. **Si `source_type: "section_provided"` deja de exigir
   `pending_verification`**, los intervalos marcadores de este fixture pasarían
   por dataciones verificadas.

---

## Cómo se comprueba

Los asertos se derivan de los ficheros de este directorio, sin herramienta
especial: cargar los `.jsonl` y comparar. `scripts/validate/validate.py` sólo lee
`knowledge/records/` y **no ve este directorio**, que es lo correcto: un fixture no
es el libro mayor. Un cargador de fixtures para `scripts/validate/` corresponde a
la Fase 1.
