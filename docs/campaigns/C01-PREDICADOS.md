# Correspondencia de predicados · Campaña 1

**Estado:** decidida para la sección 6 del corredor (`DEC-057`) y aplicada:
`SEC-000001`, convertida por
[`knowledge/corpus/conversions/corredor-06.json`](../../knowledge/corpus/conversions/corredor-06.json).
Las reglas se extienden al resto del corpus sección a sección.

El esquema admitía 48 predicados (§14 y `schemas/json-schema/claim.json`). El
corredor usa 330 en sus 1.952 filas, y **ninguno de ellos es uno de los 48**:
todas las filas necesitan correspondencia antes de ser afirmaciones.

## Lo que enseñó la sección 6

**La correspondencia no puede ser de predicado a predicado.** El corredor usa el
mismo predicado para cosas distintas:

| Predicado | Uso biológico | Uso que no lo es |
|---|---|---|
| `posee_rasgo` | C-1537: *Dictyostelium discoideum* → agregación por inanición | C-761: análisis de Parfrey et al. 2011 → muestreo ampliado; C-775: *Bangiomorpha pubescens* → calibración influyente |
| `pierde_rasgo` | C-991: *Monocercomonoides exilis* → orgánulo derivado de la mitocondria | C-781: secuencias antiguamente divergentes → señal temporal por saturación |
| `clasificado_como_por` | C-694: acritarco → taxón de forma artificial | C-767: corrección de Strassert et al. → corrección del mismo estudio |

Traducir `pierde_rasgo` por `loses_trait` diría que unas secuencias pierden un
carácter biológico. Por eso **el destino se decide por fila**: el predicado y el
tipo de sujeto dan una regla, y un fichero de conversión por sección fija el
destino de cada fila y de cada mención, con los valores ya leídos, para
revisarlo antes de escribir nada. `scripts/ingest/convertir.py` hace lo mecánico
y se niega si queda una fila o una mención sin destino.

Tampoco se pueden leer las cifras con un analizador genérico. El corredor escribe
«1.776 Ma» por mil setecientos setenta y seis millones de años (C-790) y
«1.05 Ga» por uno coma cero cinco mil millones (C-769). El fichero de conversión
guarda el valor leído y la expresión original.

**Una parte de la sección no habla de organismos.** De sus 36 filas, 9 son
conocimiento sobre métodos: qué supone un reloj relajado, qué aporta una
calibración, cómo sesga la heterotaquia. §14 no tenía vocabulario para eso, y
el esquema `1.2.0` lo añade (§14.6).

## Las cuatro decisiones

1. **Métodos: se amplía el esquema.** Seis predicados de §14.6 —`assumes`,
   `provides_bound`, `depends_on`, `may_bias`, `limits` y `calibrates`— y
   entidades de método (`METHOD-`, `methods.jsonl`). Su evidencia es de tipo
   `methodological`, una por fuente citada en la fila.
2. **Un evento por nodo.** Cada nodo datado es un evento `divergence`, y cada
   datación, una afirmación `dated_to` sobre él con su expresión temporal. Las
   dataciones de un mismo nodo conviven sin promediarse. LECA es una población
   reconstruida, como la tipa el apéndice B, y participa en su evento como
   población ancestral. Cuando la fila no nombra los linajes que divergen, el
   clado participa con el papel neutro `participant`: no se adivinan.
3. **Cadena completa para todos los estudios.** Cada estudio que produce una
   datación lleva conjunto de datos, análisis, resultado y evidencia (§6.4).
   Cuando el corpus no describe los datos, el conjunto es de trazabilidad: lo
   declara en su descripción y en sus notas, y no inventa ninguno.
4. **Las hipótesis se crean al convertir.** C-770 y C-784 forman
   `Origen tardío de la diversidad eucariota viviente`, con S178, S179 y S171 a
   favor y S181 en contra.

Y dos de oficio: las glosas del corredor no se ingieren como afirmaciones
(quedan como nota del registro al que se refieren, o su mención se descarta con
razón), y el estado del conocimiento que sintetiza una fila —«no hay estimación
de consenso»— es una cuestión `pending_question`.

## Destinos

| | Destino | Qué se crea |
|---|---|---|
| **A** | Datación | Evento `divergence`, expresión temporal `TIME-`, y la afirmación `dated_to`; con la cadena de su estudio |
| **B** | Relación del vocabulario | Una afirmación con el predicado de §14 que corresponda, y su evidencia |
| **C** | Soporte cuantitativo | Una entrada de `quantitative_support` en la afirmación a la que se refiere la medida (§10.7) |
| **D** | Descripción de un estudio | Su conjunto de datos o su análisis: método, programa, parámetros, muestreo |
| **E** | Hipótesis | Un registro `HYP-` (paso 9) |
| **F** | Derivada | Una afirmación con `derivation`: regla y afirmaciones de las que depende (§9.4) |
| **G** | Relación metodológica | Una afirmación con un predicado de §14.6 sobre entidades de método, y su evidencia |
| **H** | Glosa editorial del corredor | Nada: nota en el registro al que se refiere, o descarte justificado |
| **I** | Estado del conocimiento | Una cuestión `ISSUE-` de tipo `pending_question` |

## Reglas para los 20 predicados de la sección 6

| Predicado del corredor | Filas en el corpus | Regla |
|---|---:|---|
| `tiene_valor_medido` | 309 | Sobre un organismo o un proceso: **C**, soporte de la afirmación a la que se refiere. Sobre un estudio: **D** |
| `posee_rasgo` | 281 | Portador biológico: observación de rasgo `TRAITOBS-`. Estudio o modelo: **D**. Papel metodológico: **G** |
| `clasificado_como_por` | 117 | Varía mucho: asignación taxonómica, categoría operativa, hipótesis. **Por fila**; no hay regla general |
| `tiene_edad_estimada` | 62 | **A**, con `divergence_estimate` si el sujeto es un nodo o una población ancestral |
| `incompatible_con` | 20 | `incompatible_with`, entre hipótesis o, desde §14.6, entre métodos |
| `pierde_rasgo` | 12 | Portador biológico: `loses_trait`. Si no: **G** |
| `posee_metodo*` | 4 | **D** |
| `tiene_estimacion_de_consenso*` | 4 | **I** |
| `tiene_resumen_de_medianas*` | 2 | **A**, con la mediana en la expresión original |
| `tiene_limite_observado*` | 1 | Datación observada: `observed_taxon_range`, `determination: observed`, sin evento |
| `tiene_rango_publicado*` | 1 | **F**, envolvente de las estimaciones que sintetiza |
| `tiene_afinidad_propuesta*` | 1 | **B**, `assigned_to`, que conserva la modalidad en la aceptación y en una nota |
| `retirado_por*` | 1 | **H** |
| `cambia_resultado_de*`, `posee_incertidumbre*` | 1 cada uno | **G**, `depends_on` |
| `aporta_limite*` | 1 | **G**, `provides_bound` |
| `distingue*` | 1 | **G**, `assumes`, una afirmación por modelo |
| `puede_sesgar*` | 1 | **G**, `may_bias` |
| `posee_restriccion*` | 1 | **G**, `limits` |
| `resuelto_por_propuesta*` | 1 | **E** |

## Sección 6, fila a fila

| Fila | Predicado | Destino | Qué se escribe |
|---|---|---|---|
| C-757 | `tiene_edad_estimada` | A | Principales divergencias internas de Eukaryota según S142, 950–1259 Ma. No es la edad de la corona, y la etiqueta lo dice |
| C-758 | `tiene_edad_estimada` | A | Divergencia Choanoflagellata–Metazoa según S142, 761–957 Ma; los dos clados son `diverging_lineage` |
| C-759 | `posee_metodo*` | D | Análisis de S142: reloj relajado bayesiano con seis calibraciones fósiles |
| C-760 | `tiene_edad_estimada` | A | LECA según S139, 1679–1866 Ma |
| C-761 | `posee_rasgo` | D | Muestreo de los datos de S139: ampliado a eucariotas microbianos |
| C-762 | `tiene_edad_estimada` | A | LECA según S141, 1007–1898 Ma, lo que abarcan varios análisis |
| C-763 | `tiene_edad_estimada` | A | Corona de Opisthokonta según S141, 904–1579 Ma |
| C-764 | `tiene_valor_medido` | C | Soporte de C-763: duración del tallo LECA–Opisthokonta, 23–334 Ma |
| C-765 | `tiene_edad_estimada` | A | LECA según S140, 1958–2386 Ma |
| C-766 | `posee_metodo*` | D | Análisis de S140: varios modelos de reloj relajado, calibraciones alternativas y dos raíces |
| C-767 | `clasificado_como_por` | H | Nota del análisis de S140: la corrección publicada no es una estimación independiente |
| C-768 | `posee_metodo*` | D | Datos y análisis de S177: integración de datos genómicos y fósiles |
| C-769 | `tiene_limite_observado*` | A | Eukaryota corona: registro fósil inequívoco desde ≈1050 Ma según S178, con la cadena de su revisión |
| C-770 | `clasificado_como_por` | E | Hipótesis de origen tardío de la diversidad eucariota viviente |
| C-771 | `tiene_edad_estimada` | A | LECA según S181, preprint: mínimo ≈1696 Ma, límite antiguo abierto |
| C-772 | `tiene_estimacion_de_consenso*` | I | `ISSUE-000040`: la edad de LECA no tiene estimación de consenso |
| C-773 | `tiene_rango_publicado*` | F | LECA, 1007–2386 Ma, envolvente de C-762 y C-765 |
| C-774 | `retirado_por*` | H | Cálculo propio del corredor ya retirado. No se ingiere |
| C-775 | `posee_rasgo` | G | *Bangiomorpha pubescens* `calibrates` la datación de divergencias profundas |
| C-776 | `cambia_resultado_de*` | G | Esa datación `depends_on` *Bangiomorpha* |
| C-777 | `aporta_limite*` | G | La calibración fósil nodal `provides_bound` edad mínima del nodo |
| C-778 | `posee_incertidumbre*` | G | El límite máximo de calibración `depends_on` ausencia fósil y modelos de preservación |
| C-779 | `distingue*` | G | Reloj estricto `assumes` tasa única; reloj relajado `assumes` variación entre ramas |
| C-780 | `incompatible_con` | G | Reloj relajado autocorrelacionado `incompatible_with` no autocorrelacionado |
| C-781 | `pierde_rasgo` | G | La saturación de sustituciones `limits` la datación de divergencias profundas |
| C-782 | `puede_sesgar*` | G | La heterotaquia `may_bias` los relojes que no modelan cambios de tasa por sitio |
| C-783 | `posee_restriccion*` | G | La lejanía del grupo externo `limits` el enraizamiento y la datación del árbol eucariota |
| C-784 | `resuelto_por_propuesta*` | E | Conciliación tallo–corona, supuesto de la misma hipótesis que C-770 |
| C-785 | `tiene_afinidad_propuesta*` | B | Material orgánico de la Formación Capas Blancas `assigned_to` Choanoflagellata, putativo, según S500 |
| C-786 | `tiene_valor_medido` | D | Datos de S548: 75.975 OTU |
| C-787 | `tiene_valor_medido` | D | Análisis de S548: 77 calibraciones |
| C-788 | `tiene_valor_medido` | D | Análisis de S548: 32 árboles |
| C-789 | `tiene_valor_medido` | D | Análisis de S548: 100 réplicas de TreePL |
| C-790 | `tiene_resumen_de_medianas*` | A | Raíz de Discoba según S548: mediana 1776 Ma, medianas entre 1670 y 1897 Ma |
| C-791 | `tiene_resumen_de_medianas*` | A | Amorphea según S548: mediana 1773 Ma, medianas entre 1703 y 1934 Ma |
| C-792 | `tiene_edad_estimada` | A | LECA según S548 con *Rafatazmia* dudosa: 2054 Ma, entre 1967 y 2104 Ma |

## Resultado

| Registros | |
|---|---:|
| Afirmaciones | 24: 11 dataciones, una envolvente derivada, una asignación y 11 metodológicas |
| Expresiones temporales | 12 |
| Eventos de divergencia | 6 |
| Conjuntos de datos y análisis | 8 y 8, seis de los conjuntos de trazabilidad |
| Resultados | 11 |
| Evidencias | 29: 12 de estudios y 17 metodológicas |
| Entidades | LECA, seis clados, un espécimen, *Bangiomorpha pubescens* (nombre y concepto) y 12 métodos |
| Fuentes | las 12 que cita la sección |
| Hipótesis y cuestiones | una y una |

Las 68 menciones tienen destino: 17 crean entidad, 34 son atributo de un
registro, 9 señalan su evidencia, 5 son parte de un evento, una es una cuestión
pendiente y 2 se descartan con razón. Las 36 filas son trazables: el delta de la
conversión dice, por fila, su destino y los registros que produjo.

La envolvente de C-773 (`CLAIM-000009`) entró con origen `ingestion` aunque
lleva regla de derivación. `SEC-000001-correccion-1.json` (REV-000002 →
REV-000003) la marca como `derived`, como pide §9.4, y `SNAP-000013` registra el
estado corregido. `convertir.py` ya marca así toda afirmación con derivación.

El mapa por fila de `SEC-000001-conversion.json` recoge las claves que lista cada
fila del fichero de conversión, y no los registros que sólo declaran su fila en
`rows`. Faltan cuatro entidades, que el fichero de conversión (cuyo hash guarda
el delta) sitúa así: LECA en C-760, C-762, C-765, C-771, C-772, C-773 y C-792;
Eukaryota en C-757 y C-769; Opisthokonta en C-763; Metazoa en C-758.
`convertir.py` ya une las dos cosas: toda conversión nueva lista en cada fila
también los registros que la declaran.

Errata en el mismo mapa: la fila C-757 lista el análisis de Douzery et al.
(`ANALYSIS-000001`), que sale de C-759; C-757 sólo usa su resultado. La
procedencia del análisis es la correcta, la de C-759. El fichero de conversión
no se corrige porque su hash es el que guarda el delta aplicado; `convertir.py`
rechaza ya que una fila liste un registro que no la declara en `rows`.

Los seis eventos de divergencia entraron con `temporal_expression_ids` vacío,
aunque sus afirmaciones `dated_to` los fechan. `SEC-000001-correccion-2.json`
(REV-000003 → REV-000004) les enlaza las expresiones temporales de esas
afirmaciones (seis en el de LECA), y `SNAP-000014` registra el estado.
`convertir.py` ya las deduce.

La mención «no existe» (`MENTION-000028`) señala `ISSUE-000040` solo por
`resolution.target_ids`: ni su `issue_ids` ni el `affects.mention_ids` de la
incidencia la enlazaban. `SEC-000001-correccion-3.json` (REV-000004 →
REV-000005) enlaza los dos sentidos, y `SNAP-000015` registra el estado.
`convertir.py` ya lo hace con toda mención que señala una incidencia.
