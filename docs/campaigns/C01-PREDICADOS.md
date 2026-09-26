# Correspondencia de predicados · Campaña 1

**Estado:** decidida y aplicada para dos secciones del corredor:

- la **6**: `SEC-000001`, `DEC-057`, convertida por
  [`corredor-06.json`](../../knowledge/corpus/conversions/corredor-06.json);
- la **5**: `SEC-000002`, `DEC-058`, convertida por
  [`corredor-05.json`](../../knowledge/corpus/conversions/corredor-05.json).

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
| **J** | Evidencia sobre otra fila | Evidencias que apoyan o cuestionan la afirmación de otra fila (§14.5, `DEC-058`). La fila no crea afirmaciones |

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

`ISSUE-000040` declara que afecta al evento de LECA (`EVENT-000003`), pero el
evento no la listaba en `issue_ids`. `SEC-000001-correccion-4.json`
(REV-000005 → REV-000006) la enlaza, y `SNAP-000016` registra el estado.
`convertir.py` ya enlaza los dos sentidos de toda incidencia: su `affects` y
el `issue_ids` de lo que afecta.

# Sección 5 · El registro material: fósiles y biomarcadores

63 filas, 22 predicados (15 propios del corredor) y 29 fuentes, 25 de ellas
nuevas. Se convierte desde la versión congelada `af7e799`. El checkpoint de
trabajo del corredor del 26 de septiembre cambia la prosa de la sección y
algunos apéndices, pero no sus filas (`DEC-058`).

## Lo que enseñó la sección 5

**Las edades de los fósiles no son divergencias.** En la sección 6, cada fecha
era la de un nodo, y el destino A creaba un evento `divergence`. Aquí se fecha
dónde y cuándo aparece un fósil, y eso es una **ocurrencia** (§7.8):

- una `OCC-` con la entidad, su unidad estratigráfica y su precisión;
- una expresión temporal `occurrence_date`;
- una afirmación `dated_to` sobre la ocurrencia, de la que `convertir.py` deduce
  la fecha de la ocurrencia;
- la cadena del estudio, con conjuntos de datos de trazabilidad.

Cuando la fila fecha la propia formación (C-699, C-731), la afirmación
`dated_to` es sobre el yacimiento. Una acotación estratigráfica es `inferred` y
no `observed`: la de C-714 acota las unidades portadoras de las perforaciones,
no cada espécimen.

**Los biomarcadores no cabían en el esquema.** Un esterano no es un organismo,
ni un espécimen, ni un rasgo. El esquema `1.3.0` añade:

- las moléculas (`MOL-`, `molecules.jsonl`);
- el predicado `biomarker_of`, de la molécula a quien la produce;
- la evidencia `geochemical` y la mención `molecule`.

Si otro grupo produce la misma molécula, eso es contraevidencia (C-747 contra
C-746), no una segunda verdad.

**Cuestionar otra fila es aportar evidencia.** Seis filas tienen por sujeto otra
fila («afirmación C-711», «C-716»). Crear afirmaciones sobre afirmaciones dejaría
la contraevidencia sin enlazar. El destino **J** crea solo evidencias, que
cuestionan o apoyan la afirmación de la otra fila:

- C-712, C-717, C-730 y C-736 son J;
- C-742 y C-747 son B: además de cuestionar, afirman un hallazgo propio
  (contaminación, biosíntesis en Rhizaria), y su evidencia lo apoya a la vez que
  cuestiona la otra fila.

**El apéndice E tiene erratas y filas de otras secciones.**

- H41 cita C-739–C-740, que tratan de *Caveasphaera* y *Helicoforamina*; la
  afinidad algal que enuncia es C-737.
- H42 incluye C-822, de otra sección, que se enlazará al convertirla.
- H38 incluye C-730, que es contraevidencia (J): va en sus
  `counterevidence_ids`, no en sus filas.

Cada caso queda en las notas de su hipótesis.

## Reglas nuevas

| Predicado del corredor | Regla |
|---|---|
| `tiene_edad_estimada` | Fósil o conjunto: **A**, como ocurrencia fechada. Formación: `dated_to` sobre el yacimiento. Ga se pasa a Ma y la expresión original se conserva: «~1,75–1,4 Ga» usa coma decimal |
| `posee_rasgo`, `infiere*`, `tiene_valor_medido` y `posee_vector_de_medición*` con un organismo o un espécimen | **B**: rasgo (`TRAIT-`), su observación (`TRAITOBS-`) y la afirmación `shows_evidence_of` con su evidencia. Una medida va en la observación y en el `quantitative_support` de la afirmación. Una inferencia es `reconstruction` |
| `clasificado_como_por`, `tiene_estado*`, `tiene_posicion*`, `tiene_interpretacion*` | Hacia un clado: `assigned_to`, con la modalidad en una nota y en los ejes. Hacia una categoría: `classified_as_by` |
| `cuestionado_por` | Solo duda sobre otra fila: **J**. Con un hallazgo propio: **B** |
| `respaldado_por` | La afirmación implícita y su evidencia (**B**), o **G** si el sujeto es un método |
| `no_diagnostica_por_si_solo*`, `respaldado_por` metodológico, `no_equivale_a*` | **G** (`limits`, `depends_on`) o **F** si es síntesis del corredor |
| `observa_rasgo*` | **D**: la capacidad de un instrumento es una nota del análisis |
| `calibra_minimo*` | **F**, `provides_bound` en el ámbito de la hipótesis que lo condiciona (H36) |
| `pierde_valor_probatorio*` | **F**: la reclasificación que se sigue de la fila de la que depende |
| `linaje_troncal_de` | **B**, `stem_lineage_of` |
| `asociado_con*` | Un ambiente: `occurs_in` categórico. Una molécula con su productor: `biomarker_of` |
| `tiene_identidad*` indeterminada, `no_resuelve*`, `posee_restriccion_estratigrafica*` sin cifras | **I** |
| `no_localiza*` | **I**, con la búsqueda del corredor como localizador. Son glosas, pero H no puede anotar un clado que ya existe |

Y tres de representación:

- **Unidades estratigráficas.** Grupos, formaciones y dolomías son yacimientos
  (`SITE-`) con ocurrencias de precisión `regional`. No hay un tipo de unidad
  estratigráfica, y la sección no lo necesita para decir lo que dice.
- **Taxones fósiles y morfotipos.** Son nombre y concepto según su fuente, como
  *Bangiomorpha* en la sección 6. Los informales, como «acritarco» o los
  microfósiles con forma de vasija, llevan `nomenclatural_status: informal`.
- **Conjuntos y material.** La biota de Weng’an, los microfósiles perforados del
  Grupo Chuar, los acritarcos de Doushantuo y los fósiles de Lechte et al. son
  especímenes: objetos estudiados, no taxones.

## Sección 5, fila a fila

| Fila | Predicado | Destino | Qué se escribe |
|---|---|---|---|
| C-694 | `clasificado_como_por` | B | «Acritarco» (nombre informal y concepto según S152) `classified_as_by` taxón de forma artificial |
| C-695 | `posee_rasgo` | G | La asignación de afinidad eucariota a microfósiles de pared orgánica `depends_on` indicadores no exclusivos |
| C-696 | `no_diagnostica_por_si_solo*` | G | El tamaño de vesícula `limits` esa asignación |
| C-697 | `observa_rasgo*` | D | Datos y análisis de S151 con microscopía electrónica de transmisión; método TEM |
| C-698 | `respaldado_por` | G | La alteración térmica y la diagénesis `limits` la química de la pared |
| C-699 | `tiene_edad_estimada` | A | Grupo Roper, 1492 ± 4 a 1361 ± 21 Ma por U–Pb y Re–Os (S150), `dated_to` sobre el yacimiento |
| C-700 | `posee_rasgo` | B | *Tappania plana*: procesos ramificados y crecimiento complejo, en el Grupo Roper |
| C-701 | `posee_rasgo` | B | *Valeria lophostriata*: estriaciones concéntricas regulares |
| C-702 | `respaldado_por` | B | *Valeria* `assigned_to` Eukaryota, sin posición en la corona |
| C-703 | `posee_rasgo` | B | *Dictyosphaera* y *Shuiyousphaeridium*: ornamentación compleja de pared, en el Grupo Ruyang |
| C-704 | `posee_restriccion_estratigrafica*` | I | La edad de Ruyang no tiene cifras en el corpus |
| C-705 | `tiene_edad_estimada` | A | *Qingshania magnifica* en la Formación Chuanlinggou, ≈1630 Ma |
| C-706 | `posee_vector_de_medición*` | B | Diámetro de *Qingshania*: 20–194 µm, media 73, desviación 29, n = 262 |
| C-707 | `clasificado_como_por` | B | *Qingshania* `assigned_to` Eukaryota, multicelular de posición incierta |
| C-708 | `clasificado_como_por` | B | *Grypania spiralis* `assigned_to` Eukaryota (posible alga), y su ocurrencia en la Formación de Hierro Negaunee, ≈2100 Ma |
| C-709 | `tiene_estado*` | B | *Grypania* `assigned_to` Eukaryota según S152: muy probable, relaciones no restringidas |
| C-710 | `tiene_edad_estimada` | A | *Rafatazmia chitrakootensis* en la Dolomía Tirohan, ≈1600 Ma |
| C-711 | `clasificado_como_por` | B | *Rafatazmia* `assigned_to` Rhodophyta (corona) |
| C-712 | `cuestionado_por` | J | Contraevidencia de C-711 según S152 y S178 |
| C-713 | `clasificado_como_por` | B | Microfósiles con forma de vasija del Grupo Chuar `assigned_to` Amoebozoa o su grupo total |
| C-714 | `tiene_edad_estimada` | A | Microfósiles perforados del Grupo Chuar: unidades portadoras entre 780 y 740 Ma, acotación `inferred` |
| C-715 | `tiene_valor_medido` | B | Perforaciones de 0.1–3.4 µm en esos microfósiles |
| C-716 | `respaldado_por` | B | El perforador del Grupo Chuar `preys_on` esos microfósiles |
| C-717 | `cuestionado_por` | J | Contraevidencia de C-716: diagénesis, daño post mortem y preparación |
| C-718 | `tiene_valor_medido` | B | Perforaciones de ≈15–35 µm en microfósiles con forma de vasija |
| C-719 | `tiene_identidad*` | I | El perforador no está identificado |
| C-720 | `posee_rasgo` | B | *Bangiomorpha*: filamentos diferenciados y patrones de división bangiales |
| C-721 | `posee_rasgo` | B | *Bangiomorpha*: reproducción sexual, `reconstruction` |
| C-722 | `tiene_edad_estimada` | A | *Bangiomorpha*: la sucesión que la contiene, ≈1047 Ma, sin unidad nombrada |
| C-723 | `calibra_minimo*` | F | *Bangiomorpha* `provides_bound` edad mínima de Rhodophyta corona, en H36 |
| C-724 | `tiene_edad_estimada` | A | *Ourasphaira giraldae*, 1010–890 Ma, en la Formación Grassy Bay que da el apéndice B |
| C-725 | `clasificado_como_por` | B | *Ourasphaira* `assigned_to` Fungi, candidato |
| C-726 | `no_resuelve*` | I | Su afinidad fúngica no la sitúa en Fungi corona ni fecha Opisthokonta |
| C-727 | `tiene_edad_estimada` | A | *Bicellum brasieri* en la Formación Diabaig, ≈1000 Ma, depósitos lacustres |
| C-728 | `posee_rasgo` | B | *Bicellum*: dos morfotipos celulares diferenciados |
| C-729 | `clasificado_como_por` | B | *Bicellum* `assigned_to` Holozoa, posible |
| C-730 | `cuestionado_por` | J | Contraevidencia de C-729: paredes flexibles no excluidas |
| C-731 | `tiene_edad_estimada` | A | Formación Doushantuo, 635–551 Ma por U–Pb de circones |
| C-732 | `tiene_edad_estimada` | A | Biota de Weng’an: más antigua que 609 ± 5 Ma (U–Pb SIMS de una toba suprayacente, según S169) o próxima, límite antiguo abierto |
| C-733 | `clasificado_como_por` | B | *Tianzhushania* y *Megasphaera* `assigned_to` Metazoa, interpretación histórica |
| C-734 | `clasificado_como_por` | B | *Tianzhushania* `assigned_to` Holozoa: protistas holozoos enquistantes |
| C-735 | `posee_rasgo` | B | *Megasphaera*: diferenciación germen–soma, `reconstruction`, homología disputada |
| C-736 | `cuestionado_por` | J | Evidencia que apoya C-735 y cuestiona C-734 |
| C-737 | `clasificado_como_por` | B | Acritarcos de Doushantuo `classified_as_by` quistes algales |
| C-738 | `posee_rasgo` | B | *Caveasphaera*: desarrollo comparable al embrionario animal, `reconstruction` |
| C-739 | `tiene_posicion*` | B | *Caveasphaera* `assigned_to` Holozoa, posición no resuelta |
| C-740 | `clasificado_como_por` | B | *Helicoforamina* `assigned_to` Holozoa, posición indeterminada |
| C-741 | `tiene_interpretacion*` | B | Esteranos y hopanos arcaicos `classified_as_by` biomarcadores singenéticos, histórica |
| C-742 | `cuestionado_por` | B | Los mismos `classified_as_by` contaminación posterior a la litificación; su evidencia cuestiona C-741 |
| C-743 | `pierde_valor_probatorio*` | F | Los esteranos arcaicos, sin valor probatorio seguro para Eukaryota en el Arcaico |
| C-744 | `respaldado_por` | B | Protosteroides `biomarker_of` la biota de protosteroides |
| C-745 | `linaje_troncal_de` | B | La biota de protosteroides `stem_lineage_of` Eukaryota |
| C-746 | `clasificado_como_por` | B | 24-isopropilcolestano `biomarker_of` Demospongiae |
| C-747 | `cuestionado_por` | B | Rhizaria sintetiza sus precursores; su evidencia cuestiona C-746 |
| C-748 | `posee_rasgo` | B | Porifera: capacidad biosintética de esteroles C30, por genómica |
| C-749 | `tiene_valor_medido` | B | *Saccharomyces cerevisiae* produce esteroles con 7 nM de O₂ |
| C-750 | `no_equivale_a*` | F | Ese umbral `limits`: no se traduce en un valor de pO₂ atmosférica |
| C-751 | `tiene_edad_estimada` | A | Los fósiles eucariotas más antiguos de Lechte et al., 1750–1400 Ma, sin localidad |
| C-752 | `asociado_con*` | B | Esos fósiles `occurs_in` fondos marinos oxigenados |
| C-753 | `infiere*` | B | Aerobiosis y mitocondrias, `reconstruction` |
| C-754 | `infiere*` | B | Hábito bentónico, `reconstruction` |
| C-755 | `no_localiza*` | I | Sin fósil diagnóstico de Amorphea en la búsqueda Q-0171 |
| C-756 | `no_localiza*` | I | Sin fósil diagnóstico de Obazoa en la búsqueda Q-0172 |

Las hipótesis H35–H42 del apéndice E se crean con las filas que las componen,
en la sección 5. Su descripción y sus supuestos son literales del apéndice. La
primera de sus filas es la que enuncia la hipótesis, porque de ella salen sus
ejes.

## Resultado de la sección 5

| Registros | |
|---|---:|
| Afirmaciones | 59: 18 observaciones de rasgo (`shows_evidence_of`), 13 asignaciones, 11 dataciones, 7 clasificaciones, 5 metodológicas, 2 `biomarker_of`, 1 depredación, 1 linaje troncal y 1 ambiente |
| Ocurrencias | 9, siete de fósiles y dos sin localidad |
| Expresiones temporales | 11, todas `occurrence_date`: cuatro radiométricas, seis acotaciones estratigráficas (`inferred`) y un intervalo publicado |
| Estudios | 12 conjuntos de datos, 12 análisis y 11 resultados, en Ma |
| Evidencias | 66: 33 morfológicas, 8 metodológicas, 7 geoquímicas, 6 estratigráficas, 4 cronológicas, 3 sedimentológicas, 2 fósiles y una taxonómica, una genómica y una molecular |
| Entidades | 16 taxones fósiles y actuales (nombre y concepto), 8 clados, 9 unidades estratigráficas, 4 especímenes y conjuntos, 2 linajes, 5 moléculas, 16 rasgos con 18 observaciones y 8 métodos |
| Fuentes | 25 nuevas; S141, S160, S171 y S178 se reutilizan |
| Hipótesis y cuestiones | 8 (H35–H42) y 5 |

Las 140 menciones tienen destino: 64 crean entidad, 44 son atributo de un
registro, 17 repiten una entidad (grafías en cursiva del apéndice B, o
*Bangiomorpha* y Eukaryota, que ya existían), 7 son cuestiones pendientes y 5
señalan su evidencia. Se descartan con razón 3: Apoikozoa y Choanozoa *sensu
stricto*, que ninguna fila usa, y U–Pb CA-ID-TIMS, que el apéndice B sitúa en
C-721 sin que la fila ni la prosa lo liguen a una datación.

La conversión enlaza de vuelta tres registros de la sección 6, por las
afirmaciones nuevas que los nombran: Eukaryota, Metazoa y el concepto de
*Bangiomorpha*.

Antes de aplicar la conversión se hizo una auditoría fila a fila contra las
filas, la prosa y los apéndices. Encontró resultados en Ga con unidad Ma,
hipótesis cuya primera fila no las enunciaba, métodos de datación que la fila sí
daba, y detalles que el corpus no dice. Todo quedó corregido en el fichero de
conversión.
