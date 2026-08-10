# Guía maestra de desarrollo
## Red evolutiva desde Eukaryota hasta la historia humana, base de conocimiento científico y juego

**Estado:** documento rector activo  
**Fecha de consolidación original:** 5 de agosto de 2026  
**Fecha de revisión estratégica:** 5 de agosto de 2026  
**Versión de la guía:** 1.1.0  
**Alcance:** arquitectura científica, modelo de datos, flujo de investigación, visualización, validación, desarrollo cronológico por campañas y diseño progresivo del juego.  
**Primera campaña decidida:** Eukaryota → Holozoa.  
**Campaña culminante prevista:** Hominini → *Homo sapiens*, conservando el diseño paleoantropológico ya desarrollado.
**SHA-256 de la guía archivada `1.0.0`:** `6f17b038e9b15fef6f3040b458bcda638ad32b6b4bc82187abd7216c19d7aa88`

## Historial de revisiones

| Versión | Estado | Cambio principal |
|---|---|---|
| `1.0.0` | ARCHIVADA | Arquitectura claim-centric completa, inventario científico y hoja de ruta inicial orientada a un piloto hominino de 400.000–40.000 años. |
| `1.1.0` | ACTIVA | Invierte el orden de producción: el juego se desarrolla y publica cronológicamente por campañas, comenzando en Eukaryota. Reubica, sin eliminar, el trabajo de homininos como especificación de destino, prueba de estrés y campaña culminante. |

## Regla de conservación de trabajo previo

Esta revisión es una **migración no destructiva**. La versión `1.0.0` se conserva íntegra como archivo histórico y ninguna decisión científica, modelo de datos, inventario taxonómico, escenario hominino o sistema futuro se elimina por cambiar el orden de desarrollo.

Cada elemento previo debe quedar en uno de estos estados:

- vigente e implementable en la campaña actual;
- vigente como capacidad compartida del núcleo;
- reubicado en una campaña posterior;
- retenido como prueba de arquitectura;
- pospuesto con un disparador explícito;
- supersedido únicamente como prioridad u orden de ejecución, nunca borrado silenciosamente.

La matriz completa de preservación se encuentra en el Apéndice J.

---

## Índice de navegación

### Fundamentos y arquitectura

- [0. Propósito](#0-propósito-de-esta-guía)
- [1. Estados de decisión](#1-cómo-interpretar-el-estado-de-una-decisión)
- [2. Resumen ejecutivo](#2-resumen-ejecutivo-de-las-decisiones-actuales)
- [3. Visión del producto](#3-visión-del-producto)
- [4. Principios no negociables](#4-principios-no-negociables)
- [5. Alcance científico](#5-alcance-científico)
- [6. Arquitectura conceptual](#6-arquitectura-conceptual-definitiva)
- [7–15. Modelo de conocimiento](#7-modelo-de-identidad)

### Implementación

- [16. Persistencia y versionado](#16-persistencia-archivos-y-versionado)
- [17. Protocolo de ingestión](#17-protocolo-de-ingestión-de-una-sección)
- [18. Modos de trabajo científico](#18-modos-de-trabajo-científico)
- [19. Validación](#19-validación)
- [20. Visualización](#20-visualización)

### Juego y hoja de ruta

- [21. Diseño del juego](#21-diseño-del-juego-consolidado)
- [22. Campañas](#22-campañas-y-escalas-de-juego)
- [23. Qué no se hará](#23-qué-no-se-hará)
- [24. Hoja de ruta](#24-hoja-de-ruta-de-desarrollo)
- [25. Trabajo pospuesto](#25-trabajo-pospuesto)
- [26. Decisiones abiertas](#26-decisiones-todavía-abiertas)
- [27. Pruebas](#27-estrategia-de-pruebas)
- [28. Definiciones de terminado](#28-definiciones-de-terminado)
- [29. Riesgos](#29-riesgos-y-mitigaciones)
- [30. Registro de decisiones](#30-registro-consolidado-de-decisiones)

### Apéndices

- [A. Inventario científico](#apéndice-a-inventario-científico-de-partida)
- [B. Clasificación de primates](#apéndice-b-clasificación-de-primates-que-el-sistema-debe-poder-representar)
- [C. Inventario fósil](#apéndice-c-inventario-fósil-y-paleoantropológico-de-partida)
- [D. Advertencias terminológicas](#apéndice-d-categorías-no-cladísticas-y-advertencias-terminológicas)
- [E. Esquemas mínimos](#apéndice-e-esquemas-conceptuales-mínimos)
- [F. Salida por sección](#apéndice-f-salida-estándar-por-sección)
- [G. Inicialización](#apéndice-g-inicialización-del-proyecto)
- [H. Checklist completo](#apéndice-h-checklist-operativo-completo)
- [I. Próximo orden de trabajo](#apéndice-i-próximo-orden-de-trabajo-recomendado)
- [J. Preservación y migración](#apéndice-j-matriz-de-preservación-y-migración-del-plan-anterior)

---

# 0. Propósito de esta guía

Esta guía consolida todo lo discutido hasta ahora sobre el proyecto y organiza las decisiones en un orden implementable. No es un prompt operativo ni una especificación cerrada de producto. Es el documento rector que explica:

1. qué se está construyendo;
2. qué problemas científicos y técnicos debe resolver;
3. qué decisiones ya se adoptaron;
4. qué propuestas se conservan como dirección de diseño;
5. qué alternativas se rechazaron;
6. qué trabajo se pospuso y bajo qué condición debe retomarse;
7. qué decisiones siguen abiertas;
8. en qué orden debe desarrollarse el sistema;
9. cómo comprobar que cada etapa está terminada;
10. cómo conectar la base científica con el juego sin deformar ninguna de las dos;
11. cómo publicar el juego campaña por campaña sin perder la capacidad de representar los casos más complejos del final;
12. cómo conservar el trabajo anterior cuando cambie una prioridad estratégica.

La guía debe mantenerse versionada. Cualquier cambio importante en identidad de entidades, semántica de campos, tratamiento de hipótesis, persistencia, visualización, orden de campañas o mecánicas debe registrarse mediante una decisión arquitectónica explícita y no mediante una modificación silenciosa.

## 0.1. Principio de migración no destructiva

El cambio de una hoja de ruta no autoriza a reescribir retrospectivamente el proyecto como si nunca hubiera existido una estrategia anterior. Por tanto:

- la guía `1.0.0` se conserva íntegra;
- las decisiones históricas permanecen en el registro;
- las decisiones reemplazadas se marcan como `SUPERSEDIDO` y señalan su reemplazo;
- el trabajo hominino se mantiene como contenido científico, especificación funcional y conjunto de fixtures futuros;
- los sistemas que ya no pertenecen al primer lanzamiento pasan a una fase posterior con criterios claros de activación;
- ningún inventario o apéndice científico se elimina por no pertenecer a la primera campaña;
- toda simplificación del primer lanzamiento debe documentar qué capacidad futura protege o posterga.

## 0.2. Nuevo principio de producción

El juego se desarrollará siguiendo el corredor evolutivo en orden cronológico general:

```text
Eukaryota
→ animales
→ cordados y tetrápodos
→ sinápsidos
→ mamíferos
→ primates
→ homininos
```

Cada campaña debe ser simultáneamente:

- una experiencia jugable completa;
- una ampliación científica del Atlas;
- una prueba de una nueva escala evolutiva;
- una extensión controlada del núcleo técnico compartido;
- un paso hacia la campaña final de homininos.

La secuencia cronológica no implica progreso teleológico. Es un orden de exposición y producción centrado en el corredor que conduce a la humanidad, no una jerarquía de organismos superiores e inferiores.

# 1. Cómo interpretar el estado de una decisión

Cada decisión de esta guía utiliza uno de estos estados:

| Estado | Significado |
|---|---|
| **DECIDIDO** | Forma parte de la arquitectura o estrategia actual y debe implementarse salvo que una decisión posterior la reemplace. |
| **RETENIDO** | Es una propuesta valiosa que se conserva, pero debe validarse mediante prototipo antes de tratarla como definitiva. |
| **POSPUESTO** | Está contemplado por la arquitectura, pero no debe implementarse todavía. Debe incluir el criterio que habilitará retomarlo. |
| **RECHAZADO** | No debe utilizarse porque contradice los objetivos científicos, técnicos o de diseño. |
| **ABIERTO** | Hace falta decidirlo en una fase posterior, cuando existan datos y requisitos suficientes. |
| **SUPERSEDIDO** | Fue una decisión válida en una versión anterior, pero una decisión posterior reemplazó su prioridad, alcance u orden. Se conserva por trazabilidad y debe enlazar su reemplazo. |

Una idea puede ser científicamente válida y, aun así, estar pospuesta por costo o falta de dependencias. Posponer no equivale a descartar. Del mismo modo, superseder el antiguo orden de lanzamiento no invalida el trabajo realizado para homininos: cambia su momento de implementación.

## 1.1. Reglas para cambiar estados

- `DECIDIDO → SUPERSEDIDO` exige una nueva decisión identificada.
- `POSPUESTO → DECIDIDO` exige que se cumpla su disparador.
- `RETENIDO → DECIDIDO` exige evidencia de prototipo o una decisión explícita.
- `RECHAZADO` solo puede reabrirse mediante un ADR que explique qué premisa cambió.
- Nunca se elimina una fila histórica para hacer que el registro parezca más ordenado.

# 2. Resumen ejecutivo de las decisiones actuales

## 2.1. Naturaleza del producto

**DECIDIDO:** el proyecto está formado por dos sistemas relacionados pero separados:

1. un **núcleo científico**, que organiza investigación, entidades biológicas, afirmaciones, evidencia, eventos, hipótesis y vistas;
2. una **capa de juego**, que selecciona y transforma partes del núcleo científico en simulaciones, campañas, interfaces y mecánicas.

El núcleo científico no debe depender del motor de juego. La capa de juego debe referenciar entidades científicas mediante identificadores estables, sin modificar sus relaciones para favorecer la jugabilidad.

## 2.2. No se construirá un árbol único

**DECIDIDO:** la representación global será un **grafo de conocimiento temporal, multicapa y de relaciones mixtas**, capaz de generar proyecciones filogenéticas dirigidas.

El sistema debe representar:

- ascendencia vertical;
- divergencia;
- taxonomías alternativas;
- topologías incompatibles;
- incertidumbre;
- hibridación;
- introgresión;
- flujo génico;
- endosimbiosis;
- transferencia horizontal;
- integración viral;
- relaciones ecológicas;
- transmisión cultural;
- evidencia y procedencia;
- historia de las clasificaciones.

No todas esas relaciones pertenecen al mismo subgrafo ni deben dibujarse de la misma manera.

## 2.3. La fuente de verdad no será el gráfico

**DECIDIDO:** la unidad central del conocimiento será la **afirmación científica respaldada o cuestionada por evidencia**, no una arista dibujada en una red.

La secuencia conceptual será:

```text
CORPUS
  ↓
MENCIONES
  ↓
ENTIDADES NORMALIZADAS
  ↓
AFIRMACIONES
  ↓
EVIDENCIA Y ANÁLISIS
  ↓
HIPÓTESIS COMPATIBLES
  ↓
VISTAS TAXONÓMICAS Y FILOGENÉTICAS
  ↓
PROYECCIONES PARA EL JUEGO
```

Los árboles, redes y clasificaciones serán vistas derivadas de conjuntos de afirmaciones compatibles y fechadas.

## 2.4. La población será la unidad principal de simulación

**DECIDIDO como dirección transversal:** el jugador no controlará especies como unidades rígidas ni comprará mutaciones en un árbol de habilidades. Controlará, observará o reconstruirá **poblaciones biológicas contextualizadas en una escala concreta**.

En la primera campaña serán poblaciones de organismos unicelulares o protoeucariotas. En campañas posteriores podrán ser poblaciones animales, mamalianas, primates o humanas. La implementación concreta cambia por escala, pero se conserva la idea común:

- las poblaciones se reproducen, varían, interactúan y cambian de frecuencia;
- los linajes registran continuidad histórica;
- las especies y taxones son conceptos científicos o agrupaciones emergentes;
- los clados organizan ascendencia, no poder;
- los individuos solo se modelan cuando la campaña los necesita.

La palabra `Population` no obliga a usar el mismo modelo demográfico desde células hasta homininos. Define una interfaz conceptual común, no un simulador universal idéntico.

## 2.5. Tres niveles de realidad

**RETENIDO como principio central del juego:** el sistema distinguirá:

```text
HISTORIA BIOLÓGICA OCURRIDA
        ↓ deja señales o restos parciales
REGISTRO OBSERVABLE
        ↓ es interpretado
HIPÓTESIS DEL JUGADOR O DE LA COMUNIDAD CIENTÍFICA
```

El tipo de registro cambia según la campaña:

- señales genómicas, comparativas y celulares en historia profunda;
- anatomía, fósiles y estratigrafía en campañas animales;
- genética de poblaciones, arqueología y cultura en homininos.

La arquitectura se conserva aunque cambien los medios de observación.

## 2.6. Estrategia de implementación por campañas

**DECIDIDO:** el proyecto se desarrollará y publicará siguiendo el corredor evolutivo en campañas cronológicas. La plataforma crecerá junto con el contenido, en vez de intentar implementar primero el caso paleoantropológico más complejo.

Orden general:

1. preservar y versionar el núcleo científico mínimo;
2. definir el alcance exacto de la Campaña 1;
3. construir el dataset científico acotado de Eukaryota → Holozoa;
4. crear el Atlas y la red temporal necesarios para esa campaña;
5. implementar su módulo de simulación celular y poblacional;
6. integrar una lente científica ligera para comparar evidencia e hipótesis;
7. producir y lanzar una campaña completa;
8. revisar el núcleo después del lanzamiento;
9. extenderlo únicamente con las capacidades exigidas por la siguiente campaña;
10. llegar a homininos con sistemas probados, sin perder los requisitos complejos ya documentados.

El Atlas sigue siendo la primera superficie compartida que debe funcionar, pero no necesita lanzarse como producto aislado antes de toda jugabilidad. Formará parte del primer lanzamiento.

El modo Reconstrucción completo se conserva, pero deja de ser el primer prototipo jugable obligatorio. La primera campaña tendrá una **lente científica** más pequeña: consulta de evidencia, comparación de hipótesis y cambio de vistas.

## 2.7. Primer recorte vertical y primer lanzamiento

**DECIDIDO:** el primer recorte vertical será la campaña provisionalmente titulada **Eucaria: una célula dentro de otra**, con este corredor:

```text
prólogo de eucariogénesis
→ Eukaryota
→ Amorphea
→ Obazoa
→ Opisthokonta
→ Holozoa
```

Debe cubrir, con el nivel mínimo suficiente:

- poblaciones ancestrales reconstruidas sin nombres inventados;
- origen e integración mitocondrial como evento reticulado;
- cooperación y conflicto intracelular;
- transferencia genética abstracta cuando sea necesaria;
- diversificación eucariota temprana;
- origen del sexo y de la meiosis, y su costo frente a la reproducción clonal;
- ramas hermanas indispensables para comprender cada divergencia;
- al menos una controversia o hipótesis alternativa real;
- rasgos, costos, evidencia y procedencia;
- una campaña jugable con principio, desarrollo y final;
- un Atlas inicial y una red temporal navegable.

La campaña termina en Holozoa, en el umbral de la historia animal. No intentará poblar exhaustivamente todos los eucariotas conocidos.

## 2.8. Cono de foco

**DECIDIDO:** cada campaña controla su alcance mediante cuatro anillos:

1. **Corredor principal:** se modela con la mayor resolución necesaria para la campaña.
2. **Ramas hermanas inmediatas:** se incluyen para explicar las divergencias del corredor.
3. **Grupos externos representativos:** se añaden solo si aclaran un rasgo, hipótesis, interacción o comparación.
4. **Diversidad periférica:** se registra como expansión futura y no bloquea el lanzamiento.

La exhaustividad significa que nada relevante dentro del alcance declarado se omite, no que la primera campaña deba convertirse en un catálogo completo de la diversidad eucariota.

## 2.9. Conservación del recorte hominino anterior

**RETENIDO y reubicado:** el período aproximado entre **400.000 y 40.000 años**, centrado en *Homo sapiens*, neandertales, denisovanos y otros humanos, deja de ser el primer recorte de producción. Se conserva como:

- capítulo avanzado de la campaña final de homininos;
- caso de prueba de máxima complejidad para la arquitectura;
- futuro piloto del modo Reconstrucción completo;
- fixture para taxonomías incompatibles, linajes sin nombre estable, especímenes, paleogenómica, migración e introgresión;
- referencia para evitar que el núcleo temprano cierre posibilidades necesarias después.

No se elimina ningún inventario, escenario, bucle o requisito desarrollado para ese período.

## 2.10. Modularidad y continuidad

**DECIDIDO:** habrá un núcleo compartido y módulos de campaña.

El núcleo compartido gestiona:

- identidad;
- afirmaciones;
- evidencia;
- eventos;
- tiempo;
- hipótesis;
- vistas;
- Atlas;
- versionado;
- guardado y procedencia.

Cada módulo de campaña define:

- escala temporal;
- unidad poblacional concreta;
- variables de simulación;
- ambiente;
- rasgos;
- eventos;
- interfaz especializada;
- objetivos y condiciones de cierre;
- simplificaciones científicas.

La continuidad inicial entre campañas será narrativa, enciclopédica y de desbloqueos en el Atlas. Transferir una única partida biológica desde Eukaryota hasta *Homo sapiens* se pospone como `Modo Gran Linaje`.

# 3. Visión del producto

## 3.1. Nombre provisional

**RAMAS: Una historia de la humanidad** se conserva como título provisional histórico. Al comenzar en Eukaryota, probablemente necesite un subtítulo o un nombre comercial más amplio, por ejemplo “Desde la célula hasta nosotros”. La decisión permanece abierta hasta que el primer prototipo establezca tono, audiencia y alcance narrativo.

## 3.2. Tesis del proyecto

El proyecto no trata la evolución como una escalera que culmina inevitablemente en *Homo sapiens*. Debe mostrarla como un proceso:

- ramificado;
- contingente;
- poblacional;
- temporal;
- geográfico;
- ecológico;
- reticulado;
- parcialmente observable;
- interpretado mediante modelos científicos revisables.

## 3.3. Experiencia deseada

La experiencia debe permitir comprender que:

- una población puede dividirse sin convertirse inmediatamente en una especie;
- dos linajes diferenciados pueden volver a intercambiar genes;
- una clasificación puede cambiar sin que la historia biológica haya cambiado;
- un fósil no es automáticamente una especie;
- una especie fósil no es automáticamente un antepasado directo;
- una semejanza puede deberse a herencia, convergencia, paralelismo o error de interpretación;
- la ausencia de fósiles no demuestra ausencia biológica;
- distintos genes pueden conservar historias diferentes;
- el consenso científico es una síntesis revisable, no una etiqueta de certeza absoluta.

## 3.4. Vistas principales del producto

**RETENIDO:** tres vistas sincronizadas y adaptables a la escala:

1. **Mundo o entorno:** condiciones físicas, recursos, hábitats, barreras, regiones y poblaciones. En Eucaria puede representar microambientes y condiciones celulares; en homininos, geografía y clima continental.
2. **Red evolutiva:** divergencias, persistencias, extinciones, reticulaciones, eventos y cambios de interpretación.
3. **Tablero científico:** fuentes, señales, dataciones, caracteres, análisis, hipótesis, controversias y, cuando corresponda, especímenes.

Cada modo podrá priorizar una vista, pero las tres deben compartir la misma identidad de entidades. No se obliga a que toda campaña tenga la misma densidad ni las mismas herramientas en cada vista.

# 4. Principios no negociables

## 4.1. Rigor sin falsa certeza

El sistema debe conservar explícitamente:

- desacuerdos;
- información ausente;
- ambigüedad;
- hipótesis minoritarias;
- clasificaciones históricas;
- rangos temporales inciertos;
- diferencias entre evidencia directa e inferencia.

No se asignarán porcentajes arbitrarios de confianza. Los valores cuantitativos solo se almacenarán cuando una fuente proporcione bootstrap, probabilidad posterior, intervalo, margen de error u otra medida explícita.

## 4.2. Prohibición de teleología

No se describirá a un linaje como:

- superior;
- inferior;
- más evolucionado;
- destinado a producir humanos;
- un intento fallido;
- un paso obligatorio hacia otra especie.

Se hablará de adaptación, especialización, persistencia, divergencia, extinción, contingencia, restricción histórica y cambio de nicho.

## 4.3. Taxonomía y filogenia separadas

Un rango taxonómico no demuestra ascendencia. Un nombre no identifica necesariamente un único concepto. Un género puede ser parafilético. Una misma circunscripción puede recibir rangos distintos según la clasificación.

## 4.4. Ciencia y juego separadas

La jugabilidad puede:

- seleccionar;
- resumir;
- agrupar;
- representar;
- ocultar complejidad;
- convertir relaciones en mecánicas.

No puede:

- alterar una relación científica;
- convertir una hipótesis en hecho;
- borrar una controversia;
- inventar una superioridad evolutiva;
- utilizar razas humanas modernas como ramas biológicas discretas.

## 4.5. Procedencia obligatoria

Toda afirmación incorporada desde una sección debe poder rastrearse hasta:

- la sección de origen;
- la mención exacta;
- la fuente, si fue proporcionada;
- el análisis o evidencia pertinente, si fue proporcionado;
- la operación que la incorporó;
- la versión del conjunto de datos.

## 4.6. Estado persistente fuera de la conversación

La conversación puede ayudar a extraer, revisar y explicar. No será la fuente de verdad. El estado debe guardarse desde el comienzo en archivos versionados y reconstruibles.

## 4.7. No inventar información

Durante ingestión no se agregan especies, fechas, genes, fósiles, eventos, relaciones o fuentes que no aparezcan en el material. Cuando haga falta representar estructura sin identidad conocida, se utilizarán etiquetas explícitas como:

- ancestro común no identificado;
- linaje ancestral no muestreado;
- linaje fantasma;
- posición pendiente;
- nodo estructural provisional;
- taxón flotante.

Esas etiquetas no reciben nombres científicos inventados. El conocimiento general puede generar una advertencia o un issue, nunca un dato silencioso del corpus.

## 4.8. No forzar ubicaciones

Cuando una entidad no pueda ubicarse con seguridad, debe registrarse como:

- `incertae_sedis`;
- ubicación no resuelta;
- afinidad incierta;
- posible miembro de;
- posible grupo hermano de;
- posible ancestro;
- posición dependiente de hipótesis.

La ausencia de ubicación es información válida. Una rama arbitraria solo consigue que el diagrama luzca ordenado mientras el conocimiento queda peor.

## 4.9. Conservar historia nomenclatural y sinónimos

Los nombres alternativos, grafías originales, recombinaciones, errores de transcripción y sinonimias propuestas deben conservarse. Solo se fusionan identidades cuando la equivalencia está confirmada según los criterios del proyecto. Una sinonimia disputada se modela como afirmación, no como borrado.

## 4.10. Conservar requisitos futuros sin implementarlos prematuramente

La Campaña 1 debe ser simple en alcance, no simplista en arquitectura. Cada decisión temprana debe comprobar que no impide representar después:

- conceptos taxonómicos incompatibles;
- linajes sin nombre formal consensuado;
- especímenes con asignaciones alternativas;
- poblaciones y flujo génico;
- paleogenómica;
- arqueología y cultura;
- historias ocultas y evidencia parcial;
- la campaña hominina completa.

Esta compatibilidad se garantiza mediante interfaces, fixtures y decisiones documentadas. No exige implementar ahora todos esos sistemas.

# 5. Alcance científico

## 5.1. Alcance total previsto

El sistema debe poder cubrir, sin cambiar su semántica fundamental:

1. historia profunda de la vida;
2. eucariotas;
3. animales;
4. cordados;
5. vertebrados;
6. sinápsidos;
7. mamíferos;
8. primates;
9. hominoideos;
10. homínidos;
11. homininos;
12. géneros y especies;
13. poblaciones;
14. individuos fósiles;
15. genomas y loci concretos;
16. eventos de mezcla, migración, innovación y extinción;
17. historia taxonómica y epistemológica.

## 5.2. Resoluciones visuales previstas

La interfaz deberá soportar al menos estos niveles:

1. historia profunda de la vida;
2. eucariotas y animales;
3. cordados y vertebrados;
4. mamíferos;
5. primates;
6. hominoideos;
7. homínidos;
8. homininos;
9. géneros y especies;
10. poblaciones y linajes genéticos;
11. especímenes y genomas concretos;
12. eventos de mezcla, migración e innovación.

La fuente de verdad no será una imagen gigantesca. Cada nivel será una vista filtrada y materializada a partir del mismo sistema.

## 5.3. Alcance de la primera implementación

La primera implementación debe demostrar la arquitectura con un caso pequeño, pero estructuralmente representativo: Eukaryota → Holozoa.

Debe incluir como mínimo:

- el corredor principal de la Campaña 1;
- ramas hermanas inmediatas necesarias;
- un concepto taxonómico o cladal con interpretación alternativa;
- poblaciones o linajes ancestrales explícitamente reconstruidos;
- un evento de endosimbiosis con participantes y roles;
- al menos un evento de divergencia;
- rasgos y compensaciones;
- intervalos temporales con incertidumbre;
- varias fuentes y afirmaciones trazables;
- **dos o más hipótesis incompatibles** sobre el mismo conjunto de entidades, con sus afirmaciones, su evidencia y su contraevidencia. No basta con una alternativa parcialmente incompatible: la incompatibilidad parcial es un fenómeno distinto y no ejercita la prueba de estrés del modelo de hipótesis (`ISSUE-000028`);
- una vista de trabajo fechada;
- una vista histórica o de fuente;
- una proyección de campaña;
- una red temporal navegable;
- un bucle jugable mínimo.

No exige todavía:

- especímenes fósiles individualizados;
- yacimientos;
- paleoproteómica;
- arqueología;
- cultura;
- geografía continental detallada;
- genes o alelos individuales;
- genética de poblaciones humanas;
- el modo Reconstrucción completo.

Además se mantendrá un **fixture de regresión futura hominino** pequeño, sin integrarlo al contenido jugable inicial, para comprobar que las decisiones del esquema no bloquean dos conceptos llamados Hominini, un linaje denisovano sin nombre estable y un evento de introgresión.

# 6. Arquitectura conceptual definitiva

## 6.1. Capa 1: corpus

Contiene el material recibido y su contexto de ingestión.

Entidades principales:

- sección de investigación;
- fuente bibliográfica;
- pasaje;
- figura o tabla referenciada;
- mención textual;
- archivo de origen;
- fecha de incorporación;
- hash del contenido.

El corpus debe conservarse de forma inmutable. Las correcciones se registran como versiones o anotaciones, nunca sobrescribiendo silenciosamente el texto original.

## 6.2. Capa 2: entidades

Contiene objetos con identidad estable:

- nombres taxonómicos;
- conceptos taxonómicos;
- clados definidos;
- linajes biológicos;
- poblaciones;
- especies como conceptos utilizados por fuentes;
- especímenes;
- yacimientos;
- regiones;
- genes;
- rasgos;
- tecnologías;
- ecosistemas;
- métodos;
- publicaciones;
- investigadores cuando sean necesarios para procedencia.

## 6.3. Capa 3: afirmaciones

Una afirmación expresa que una fuente, sección o análisis sostiene algo acerca de una o más entidades.

Ejemplos:

```text
El concepto taxonómico A incluye las poblaciones X e Y.
El espécimen S fue asignado al taxón T.
El clado A es grupo hermano de B dentro de la hipótesis H.
La divergencia entre A y B ocurrió en el intervalo D.
El evento E aportó ancestría de P1 a P2.
El rasgo R está observado en el espécimen S.
Dos nombres son sinónimos según la clasificación C.
```

La afirmación, no el nodo, es la unidad principal de aceptación, evidencia, disputa y vigencia.

## 6.4. Capa 4: evidencia y análisis

Relaciona:

```text
fuente → conjunto de datos → método/análisis → resultado → afirmación
```

Debe conservar:

- tipo de evidencia;
- descripción;
- procedencia;
- muestra;
- método;
- modelo;
- soporte cuantitativo, si existe;
- limitaciones;
- localizador dentro de la fuente;
- afirmaciones respaldadas;
- afirmaciones cuestionadas.

## 6.5. Capa 5: eventos

Los procesos temporales o que involucran más de dos participantes se modelan como eventos explícitos.

Ejemplos:

- divergencia;
- migración;
- dispersión;
- hibridación;
- introgresión;
- cuello de botella;
- efecto fundador;
- extinción;
- radiación;
- transferencia horizontal;
- endosimbiosis;
- integración viral;
- transmisión cultural;
- sustitución tecnológica;
- construcción de nicho.

## 6.6. Capa 6: hipótesis

Una hipótesis es un conjunto coherente de afirmaciones, supuestos, identificaciones, fechas y relaciones.

No se limita a una topología. Puede incluir:

- una clasificación;
- una asignación de especímenes;
- una fecha de divergencia;
- un evento de flujo génico;
- una interpretación de carácter;
- una definición de especie;
- una explicación causal.

## 6.7. Capa 7: vistas

Las vistas son productos derivados:

- clasificación según una fuente;
- backbone de trabajo actual;
- topología de un estudio;
- vista histórica;
- vista por escala;
- vista por tipo de evidencia;
- vista para una campaña;
- vista didáctica simplificada.

Cada vista debe declarar:

- fecha de corte;
- fuentes;
- hipótesis incluidas;
- afirmaciones seleccionadas;
- criterios editoriales;
- simplificaciones;
- elementos excluidos;
- versión.

## 6.8. Capa 8: proyección de juego y módulos de campaña

La proyección de juego referencia entidades, afirmaciones, eventos y vistas científicas, pero mantiene sus propios datos:

- rol jugable;
- abstracción utilizada;
- campaña y capítulo;
- escala temporal;
- unidad de simulación;
- variables activas;
- mecánicas;
- efectos;
- condiciones de aparición;
- simplificaciones;
- advertencias científicas;
- justificación de diseño;
- política de continuidad con campañas anteriores y posteriores.

No se almacenará dentro de cada nodo científico.

La capa se divide en:

```text
NÚCLEO COMPARTIDO DE JUEGO
├── Atlas
├── red temporal
├── identidad y referencias científicas
├── guardado y progresión
├── interfaz común
└── telemetría y validación

MÓDULO DE CAMPAÑA
├── reglas de simulación
├── escala
├── ambiente
├── rasgos
├── eventos
├── contenido
├── tutorial
├── objetivos
└── interfaz especializada
```

Una campaña puede usar solo una parte del modelo científico. Esa selección debe registrarse como proyección, no como eliminación de los datos restantes.

## 6.9. Dirección y ciclos

El grafo completo contiene relaciones dirigidas, no dirigidas, simétricas, jerárquicas y epistemológicas. No debe imponerse una única semántica de dirección a todo el sistema.

La restricción de aciclicidad se aplica a subgrafos concretos, especialmente a la ascendencia vertical dentro de una hipótesis. Relaciones como `alternativa_a`, `coexiste_con` o `grupo_hermano_de` pueden ser simétricas; las referencias entre afirmaciones e hipótesis pueden formar ciclos semánticos sin crear una paradoja evolutiva.

---

# 7. Modelo de identidad

## 7.1. Distinciones obligatorias

El sistema nunca debe confundir:

- nombre taxonómico;
- concepto taxonómico;
- clado;
- grado evolutivo;
- linaje;
- población;
- especie;
- subespecie;
- individuo;
- espécimen;
- yacimiento;
- ocurrencia;
- genoma;
- gen;
- alelo;
- rasgo;
- observación de un rasgo;
- innovación;
- evento;
- hipótesis;
- análisis;
- fuente;
- publicación.

## 7.1.1. Tres cosas que suelen mezclarse

Antes de las distinciones concretas, la que las fundamenta a todas:

1. **Nombre nomenclaturalmente disponible** — fue publicado cumpliendo las reglas del código aplicable.
2. **Taxón aceptado** — una base taxonómica o una comunidad de especialistas decide utilizarlo.
3. **Clado filogenéticamente respaldado** — un análisis lo recupera como monofilético.

Son independientes. Un nombre puede existir sin taxón aceptado, un clado puede estar bien respaldado sin nombre formal, y un taxón aceptado puede no corresponder a ningún clado. Es la razón de que §7.2 y §7.5 existan por separado y de que el modelo sea claim-centric: sin esta distinción, el sistema no puede representar por qué un nombre no contiene una circunscripción.

*Procedencia: `knowledge/corpus/inbox/Filogenia.md`, §1. Pendiente de reingestar por el protocolo de §17 (`ISSUE-000020`).*

## 7.2. Nombre taxonómico

Representa una denominación nomenclatural, su grafía y autoría cuando esté disponible.

Un mismo nombre puede haber sido utilizado para conceptos diferentes. Por tanto, el nombre no contiene por sí solo una circunscripción biológica.

## 7.3. Concepto taxonómico

Representa el uso de un nombre con una circunscripción concreta según una fuente o clasificación.

Ejemplo conceptual:

```text
NAME-HOMININI
├── TAXCONCEPT-HOMININI-CLASIFICACION-A
│   └── incluye Pan + Homo
└── TAXCONCEPT-HOMININI-CLASIFICACION-B
    └── incluye solo el linaje humano posterior a la separación de Pan
```

Esos conceptos pueden relacionarse como:

- congruentes;
- uno incluido en otro;
- superpuestos;
- incompatibles;
- homónimos conceptuales.

## 7.4. Clado

Representa un grupo definido por ascendencia. Debe conservar su definición, por ejemplo:

- basada en nodos;
- basada en ramas;
- basada en apomorfías;
- crown group;
- total group;
- stem group.

No debe inferirse automáticamente que todo taxón formal sea monofilético.

## 7.5. Linaje

Representa continuidad biológica histórica inferida. Puede existir sin nombre taxonómico formal, como ocurre con algunos linajes genéticos o poblaciones fantasma.

## 7.6. Población

Representa una unidad biológica localizada temporal y geográficamente. Es la entidad principal para:

- migración;
- aislamiento;
- flujo génico;
- deriva;
- selección;
- demografía;
- cultura;
- simulación.

## 7.7. Espécimen

Representa un objeto físico individual o muestra concreta. No debe convertirse automáticamente en taxón, especie, población o ancestro.

## 7.8. Ocurrencia

Representa la presencia documentada o inferida de una entidad en un lugar y un intervalo temporal. Separa la identidad del taxón o población de la evidencia de su presencia.

Tiene **esquema propio** (Apéndice E.13) y no viaja por la entidad biológica común. No es una excepción a la delgadez que E.5 exige: es su contraparte. Una entidad no lleva tiempo ni lugar propios precisamente porque los expresa mediante ocurrencias, y una ocurrencia sin ambos no afirma nada (`ISSUE-000035`).

## 7.9. Rasgo y observación

Un rasgo abstracto debe distinguirse de su observación en:

- un espécimen;
- una población;
- un taxón;
- una reconstrucción;
- un análisis.

Esto permite conservar incertidumbre, preservación parcial y homología discutida.

---

# 8. Catálogo canónico de entidades

La implementación inicial debe permitir estos tipos. No todos necesitan una interfaz completa en la primera fase.

La columna **Nivel** es un orden de construcción propio de este catálogo y **no son las fases de §24**. Se llamaba «fase mínima» y se confundía con ellas: `Section` es de nivel 1 pero se implementa en la Fase 2 de la hoja de ruta, y los tipos de identidad son de nivel 2 y llegan en la Fase 3. El desfase ronda una unidad pero no es constante (`ISSUE-000006`).

| Tipo | Responsabilidad | Nivel |
|---|---|---:|
| `Section` | Unidad de investigación ingresada | 1 |
| `Passage` | Fragmento localizable dentro de una sección o fuente | 1 |
| `Mention` | Aparición textual exacta | 1 |
| `Source` | Publicación, documento o material de procedencia | 1 |
| `TaxonomicName` | Nombre nomenclatural o histórico | 2 |
| `TaxonConcept` | Circunscripción de un taxón según una fuente | 2 |
| `CladeConcept` | Clado definido filogenéticamente | 2 |
| `BiologicalLineage` | Continuidad biológica inferida | 2 |
| `Population` | Unidad poblacional temporal y geográfica | 2 |
| `Specimen` | Fósil, muestra o individuo estudiado | 2 |
| `Site` | Yacimiento o localidad | 2 |
| `Region` | Unidad geográfica o paleogeográfica | 2 |
| `Occurrence` | Presencia en tiempo y espacio | 3 |
| `Trait` | Carácter abstracto | 3 |
| `TraitObservation` | Observación o inferencia de un carácter | 3 |
| `Claim` | Afirmación científica atómica | 3 |
| `EvidenceItem` | Evidencia que respalda o cuestiona | 3 |
| `Dataset` | Matriz, secuencia, muestra o colección analizada | 3 |
| `Analysis` | Método aplicado a un conjunto de datos | 3 |
| `Result` | Resultado de un análisis | 3 |
| `Event` | Proceso temporal con participantes y roles | 4 |
| `Hypothesis` | Conjunto coherente de afirmaciones | 4 |
| `ClassificationView` | Jerarquía taxonómica contextual | 5 |
| `PhylogeneticView` | Topología o red derivada | 5 |
| `Issue` | Pregunta, contradicción o dato pendiente | 1 |
| `GameProjection` | Traducción independiente a contenido jugable | 8 |
| `Gene`, `Allele`, `Genome` | Granularidad molecular | POSPUESTO |
| `CulturalTradition` | Transmisión cultural detallada | POSPUESTO |
| `EcosystemState` | Simulación ecológica profunda | POSPUESTO |

## 8.1. Regla de promoción desde menciones

Toda mención científicamente relevante debe registrarse en el libro mayor de menciones. No toda mención debe convertirse en una entidad.

Una mención puede terminar como:

- nueva entidad;
- alias de una entidad existente;
- evidencia para una afirmación;
- atributo contextual;
- parte de un evento;
- cuestión pendiente;
- repetición;
- error tipográfico conservado;
- término descartado con justificación.

Esta regla mantiene cobertura exhaustiva sin transformar cada palabra en un nodo ceremonial.

---

# 9. Modelo de afirmaciones

## 9.1. Afirmación atómica

Una afirmación debe expresar una sola proposición verificable o disputable.

Estructura conceptual:

```json
{
  "id": "CLAIM-000001",
  "subject_id": "ENTITY-A",
  "predicate": "assigned_to",
  "object": { "entity_id": "TAXCONCEPT-000001" },
  "scope": {
    "hypothesis_ids": ["HYP-000003"],
    "classification_view_ids": [],
    "temporal_expression_ids": [],
    "region_ids": []
  },
  "provenance": {
    "section_ids": ["SEC-000001"],
    "passage_ids": ["PASSAGE-000991"],
    "source_ids": ["SRC-000017"],
    "operation_id": null,
    "dataset_revision": "REV-000001",
    "origin": "ingestion"
  },
  "epistemic_dimensions": {
    "acceptance": "mixed_acceptance",
    "evidence_strength": "medium",
    "resolution": "partially_resolved",
    "historical_status": "current"
  },
  "quantitative_support": [],
  "evidence_ids": [],
  "counterevidence_ids": [],
  "derivation": null,
  "record_status": "active",
  "notes": []
}
```

El objeto puede ser:

- otra entidad;
- una fecha;
- un intervalo;
- un valor;
- una categoría;
- una expresión estructurada.

## 9.2. Afirmaciones positivas y negativas

Debe poder registrarse tanto:

```text
La fuente A asigna el espécimen S al taxón T.
```

como:

```text
La fuente B rechaza la asignación de S a T.
```

No se borrará la primera afirmación al incorporar la segunda. Se registrará el conflicto y se decidirá qué vistas incluyen cada una.

## 9.3. Alcance de una afirmación

Una afirmación puede estar restringida por:

- fuente;
- clasificación;
- hipótesis;
- región;
- intervalo temporal;
- conjunto de datos;
- método;
- muestra;
- versión del análisis.

Una afirmación sin contexto no debe generalizarse automáticamente.

## 9.4. Afirmaciones derivadas

Algunas relaciones se calcularán a partir de otras.

Ejemplos:

- `contains` se deriva de `member_of`;
- `sister_to` se deriva de una topología concreta;
- `temporally_overlaps_with` se deriva de intervalos compatibles;
- `may_have_coexisted_with` se deriva de ocurrencias geográficas y temporales;
- `contributes_ancestry_to` se deriva de un evento de introgresión con roles;
- `historically_classified_as` se deriva de un concepto taxonómico y una vista histórica.

Las afirmaciones derivadas deben indicar su regla y dependencia. No deben confundirse con afirmaciones expresas de una fuente.

---

# 10. Modelo epistemológico multidimensional

Un único campo `epistemic_status` fue rechazado porque mezclaba preguntas diferentes. El estado se divide en dimensiones independientes.

## 10.1. Aceptación científica

```text
broad_consensus
majority_acceptance
mixed_acceptance
minority_position
abandoned
not_assessed
```

Describe la recepción general, no la fuerza lógica interna de una hipótesis.

`abandoned` es cero apoyo actual: ya no la sostiene nadie. No se confunde con
`not_assessed`, que es «no se ha mirado», ni con `minority_position`, que
supone defensores aunque sean pocos.

Y no se sustituye por `historical_status: rejected`. Son ejes independientes
(§10) y responden a preguntas distintas: una idea puede estar rechazada por el
consenso y conservar quien la defienda, y una idea puede quedarse sin
defensores sin que nadie haya declarado formalmente que se rechaza. Expresar la
recepción con el eje de vigencia acoplaría dos cosas que la guía separa a
propósito (`ISSUE-000037`).

## 10.2. Papel dentro de una vista

```text
selected_backbone
selected_overlay
alternative
excluded
not_evaluated
```

Una afirmación puede ser minoritaria y, aun así, seleccionarse en una vista dedicada a esa hipótesis.

## 10.3. Fuerza de evidencia

```text
high
medium
low
unknown
```

Debe incluir una razón breve. No se sustituye por números inventados.

## 10.4. Resolución

```text
resolved
partially_resolved
unresolved
insufficient_information
```

## 10.5. Vigencia histórica

```text
current
historical
superseded
rejected
```

## 10.6. Estado del registro

```text
active
deprecated
merged
replaced
archived
```

`replaced` se llamaba `superseded`. Se renombró porque compartía nombre con el valor de §10.5, que designa una **idea** reemplazada, mientras éste designa un **registro** sustituido. Eran dos afirmaciones muy distintas bajo la misma palabra (`ISSUE-000007`).

## 10.7. Soporte cuantitativo

Cuando exista, se almacena con:

- tipo de medida;
- valor;
- escala;
- método;
- nodo o relación a la que aplica;
- fuente;
- localizador;
- condiciones del análisis.

No se convertirán medidas diferentes en una escala común ficticia.

---

# 11. Modelo temporal

## 11.1. Tipos temporales separados

El sistema distinguirá al menos:

| Tipo | Qué representa |
|---|---|
| `OccurrenceDate` | Edad de una ocurrencia o espécimen. |
| `ObservedTaxonRange` | Rango conocido por evidencias observadas. |
| `InferredLineageRange` | Duración biológica inferida. |
| `DivergenceEstimate` | Fecha estimada de separación. |
| `EventDate` | Intervalo de un evento. |
| `TraitEvidenceDate` | Primera, última o determinada evidencia de un rasgo. |
| `PublicationDate` | Fecha de una fuente o propuesta. |
| `ClassificationValidityPeriod` | Período de uso de una clasificación, cuando corresponda. |

## 11.2. Intervalos

Todo intervalo debe permitir:

- límite más antiguo;
- límite más reciente;
- unidad;
- incertidumbre;
- calibración o sistema cronológico;
- tipo de fecha;
- método;
- fuente;
- condición de observado o inferido.

## 11.3. Validación temporal

La validación debe comprobar:

- que una ascendencia inferida sea temporalmente plausible;
- que participantes de hibridación puedan coexistir;
- que una transferencia no conecte entidades separadas por intervalos imposibles;
- que una innovación no se presente como anterior a la evidencia citada sin marcar inferencia;
- que no haya ciclos en el subgrafo de ascendencia de una hipótesis.

No debe asumir que el primer fósil conocido es el origen real de un linaje. Una aparente inversión entre rangos observados genera una advertencia, no necesariamente un error.

## 11.4. Tiempo profundo y escalas

La interfaz debe aceptar unidades adecuadas a cada nivel:

- años;
- miles de años;
- millones de años;
- intervalos geológicos;
- fechas calibradas;
- generaciones, cuando el modelo poblacional lo requiera.

Las conversiones deben conservar el valor original y no redondear silenciosamente.

---

# 12. Modelo geográfico

## 12.1. Entidades geográficas

Debe distinguirse:

- yacimiento;
- localidad;
- región moderna;
- región paleogeográfica;
- formación geológica;
- cuenca;
- paleocontinente;
- área inferida de distribución.

## 12.2. Incertidumbre espacial

Una ubicación puede ser:

- puntual;
- poligonal;
- regional;
- aproximada;
- desconocida;
- inferida.

## 12.3. Geografía cambiante

**POSPUESTO en detalle, previsto por el esquema:** la paleogeografía dinámica, costas, corredores y biomas variables se incorporarán después de estabilizar tiempo, ocurrencias y eventos.

La primera versión puede utilizar regiones abstractas y coordenadas modernas con notas de contexto. No debe fingir que una costa actual representa el Pleistoceno sin advertencia.

---

# 13. Eventos evolutivos y reticulación

## 13.1. Por qué son entidades

Hibridación, migración, divergencia o endosimbiosis no son simples pares de nodos. Pueden involucrar:

- varios participantes;
- roles diferentes;
- múltiples episodios;
- intervalos;
- regiones;
- descendencia resultante;
- evidencia contradictoria;
- porcentajes o direcciones parciales.

Por eso se modelan mediante un nodo-evento.

## 13.2. Estructura mínima

```json
{
  "id": "EVENT-000001",
  "event_type": "introgression",
  "participants": [
    { "entity_id": "POP-000001", "role": "donor" },
    { "entity_id": "POP-000002", "role": "recipient" }
  ],
  "result_entity_ids": [],
  "temporal_expression_ids": ["TIME-000030"],
  "region_ids": ["REGION-000010"],
  "claim_ids": ["CLAIM-000210"],
  "evidence_ids": ["EVID-000044"],
  "hypothesis_ids": ["HYP-000012"],
  "notes": []
}
```

## 13.3. Tipos de eventos previstos

### Evolutivos y demográficos

- divergencia;
- especiación;
- extinción;
- radiación adaptativa;
- cuello de botella;
- efecto fundador;
- expansión;
- contracción;
- aislamiento;
- reconexión;
- migración;
- dispersión;
- reemplazo parcial;
- absorción poblacional.

### Reticulados

- hibridación;
- introgresión;
- flujo génico;
- origen híbrido;
- transferencia horizontal;
- transferencia mediada por vectores;
- integración viral;
- endosimbiosis;
- captura de orgánulos.

### De caracteres

- adquisición;
- pérdida;
- reversión;
- duplicación;
- convergencia;
- paralelismo;
- innovación.

### Ecológicos y culturales

- competencia;
- depredación;
- relación huésped-patógeno;
- construcción de nicho;
- presión selectiva;
- coevolución;
- transmisión cultural;
- aprendizaje intergrupal;
- sustitución tecnológica.

Los dos últimos grupos pueden comenzar como afirmaciones simples y promocionarse a eventos cuando el material exija participantes, tiempo y lugar detallados.

---

# 14. Vocabulario de relaciones y tratamiento final

La lista original se conserva, pero no todos los predicados se almacenarán de la misma manera.

## 14.1. Relaciones filogenéticas

| Relación propuesta | Tratamiento |
|---|---|
| `desciende_de` | Afirmación canónica contextualizada por hipótesis. |
| `ancestro_posible_de` | Afirmación modal, nunca ascendencia definitiva. |
| `grupo_hermano_de` | Derivada de una topología concreta. |
| `diverge_de` | Evento de divergencia. |
| `miembro_de` | Afirmación canónica. |
| `contiene` | Inversa derivada de `miembro_de`. |
| `linaje_troncal_de` | Afirmación o regla de vista, con definición explícita. |
| `grupo_corona_de` | Afirmación sobre definición cladal. |
| `continuacion_cronologica_de` | Afirmación de continuidad, no ascendencia automática. |
| `posible_ancestro_muestreado_de` | Afirmación modal con requisitos temporales. |

## 14.2. Relaciones reticuladas

| Relación propuesta | Tratamiento |
|---|---|
| `hibrida_con` | Evento de hibridación. |
| `recibe_flujo_genico_de` | Derivada de roles de un evento. |
| `introgresion_desde` | Evento o afirmación sobre un evento. |
| `aporta_ancestria_a` | Derivada de un evento y su evidencia. |
| `transfiere_gen_a` | Evento molecular, pospuesto en granularidad fina. |
| `integra_material_viral_de` | Evento molecular, pospuesto. |
| `endosimbiosis_con` | Evento n-ario. |
| `origina_linaje_hibrido_con` | Evento con entidad resultante. |

## 14.3. Relaciones de caracteres

| Relación propuesta | Tratamiento |
|---|---|
| `adquiere_rasgo` | Evento o inferencia filogenética. |
| `pierde_rasgo` | Evento o inferencia. |
| `conserva_rasgo` | Afirmación comparativa. |
| `presenta_evidencia_de` | Observación vinculada a evidencia. |
| `converge_con` | Afirmación comparativa dependiente de rasgo. |
| `hereda_rasgo_de` | Inferencia dentro de una hipótesis. |
| `desarrolla_independientemente` | Afirmación de homoplasia. |

## 14.4. Relaciones ecológicas y culturales

| Relación propuesta | Tratamiento |
|---|---|
| `compite_con` | Afirmación o evento contextual. |
| `depreda_a` | Afirmación o evento contextual. |
| `es_huesped_de` | Afirmación temporal/contextual. |
| `modifica_nicho_de` | Evento o afirmación causal. |
| `transmite_cultura_a` | Evento cultural, pospuesto en detalle. |
| `ejerce_presion_selectiva_sobre` | Hipótesis causal, no hecho automático. |
| `coexiste_con` | Preferentemente derivada; explícita si una fuente la afirma. |
| `reemplaza_parcialmente_a` | Evento poblacional. |

## 14.5. Relaciones epistemológicas

| Relación propuesta | Tratamiento |
|---|---|
| `propuesto_por` | Procedencia de afirmación o hipótesis. |
| `respaldado_por` | Evidencia → afirmación. |
| `cuestionado_por` | Fuente/evidencia → afirmación. |
| `incompatible_con` | Restricción entre afirmaciones o escenarios. |
| `alternativa_a` | Relación entre hipótesis. |
| `sinonimo_propuesto_de` | Afirmación taxonómica contextual. |
| `clasificado_como_por` | Concepto taxonómico dentro de una vista. |
| `requiere_verificacion` | Issue vinculado, no relación biológica. |

---

# 15. Hipótesis, escenarios y compatibilidad

## 15.1. Hipótesis como conjunto

Una hipótesis debe contener:

- afirmaciones incluidas;
- supuestos;
- clasificación utilizada;
- evidencias favorables;
- contraevidencias;
- fuentes favorables;
- fuentes opuestas;
- restricciones;
- grado de aceptación;
- preguntas no resueltas.

## 15.2. Escenarios compatibles

No se mantendrá manualmente una lista exhaustiva de compatibilidad para cada par de aristas. Se utilizarán:

- grupos de conflicto, que son **registros con identificador opaco**
  (`CONFLICT-000001`) y ficha propia en `conflict-groups.jsonl`;
- conjuntos de afirmaciones mutuamente excluyentes;
- requisitos de una hipótesis;
- escenarios o “mundos” compatibles;
- validadores automáticos cuando sea posible.

### 15.2.1. El grupo de conflicto es un registro, no una etiqueta

Un grupo de conflicto tiene nombre, descripción y ámbito, y las hipótesis lo
citan por identificador. La razón es doble.

La primera es de integridad: mientras fueron cadenas libres no había nada que
comprobara que dos hipótesis rivales escribían el mismo texto, y derivaron
solas —los dos únicos fixtures del proyecto llegaron a usar convenciones
distintas para el mismo mecanismo—. Un campo `_ids` sin registro detrás no
tiene integridad referencial, y §7 no admite identificadores sin dueño.

La segunda importa más: **saber que dos hipótesis chocan vale poco si no se
dice en qué**. El registro obliga a escribirlo. Un conflicto sobre dónde cae la
raíz de Eukaryota y uno sobre el orden de la integración mitocondrial exigen
decisiones editoriales distintas, y sin ficha ambos se veían igual.

El validador exige que todo grupo citado exista, y avisa de los grupos con una
sola hipótesis —un conflicto necesita al menos dos que se excluyan— y de los
declarados que nadie cita (`ISSUE-000036`).

## 15.3. Topologías

Una topología es una salida de una hipótesis o análisis. Puede almacenarse como:

- Newick, cuando sea un árbol compatible;
- Extended Newick, cuando haya reticulación;
- lista de clados;
- grafo de eventos;
- conjunto de afirmaciones estructurales.

La elección técnica exacta queda **ABIERTA** hasta la fase de vistas.

## 15.4. Backbone de trabajo

El llamado “consenso principal” será una vista editorial versionada, por ejemplo:

```text
PHYVIEW-WORKING-SYNTHESIS-2026-08-05
```

Debe declarar sus criterios. No se convertirá en verdad absoluta ni sobrescribirá las alternativas.

---

# 16. Persistencia, archivos y versionado

## 16.1. Decisión inicial de almacenamiento

**DECIDIDO:** comenzar con archivos modulares JSON/JSONL versionados en Git.

No se utilizará un único archivo gigantesco como fuente de verdad. Tampoco se adoptará una base de grafos antes de demostrar que el esquema y las consultas lo necesitan.

## 16.2. Estructura recomendada del repositorio

```text
/
├── README.md
├── docs/
│   ├── GUIDE.md
│   ├── ARCHITECTURE.md
│   ├── SCIENTIFIC-METHOD.md
│   ├── INGESTION-PROTOCOL.md
│   ├── VISUALIZATION.md
│   ├── GAME-DESIGN.md
│   ├── ROADMAP.md
│   ├── PRESERVATION-AND-MIGRATION.md
│   ├── GLOSSARY.md
│   ├── campaigns/
│   │   ├── C01-EUKARYA.md
│   │   ├── C02-ANIMALS.md
│   │   └── FUTURE-CAMPAIGNS.md
│   └── adr/
├── knowledge/
│   ├── corpus/
│   │   ├── sections/
│   │   ├── passages/
│   │   └── manifests/
│   ├── records/
│   │   ├── mentions.jsonl
│   │   ├── sources.jsonl
│   │   ├── taxonomic-names.jsonl
│   │   ├── taxon-concepts.jsonl
│   │   ├── clades.jsonl
│   │   ├── lineages.jsonl
│   │   ├── populations.jsonl
│   │   ├── specimens.jsonl
│   │   ├── sites.jsonl
│   │   ├── regions.jsonl
│   │   ├── occurrences.jsonl
│   │   ├── traits.jsonl
│   │   ├── trait-observations.jsonl
│   │   ├── claims.jsonl
│   │   ├── evidence.jsonl
│   │   ├── datasets.jsonl
│   │   ├── analyses.jsonl
│   │   ├── results.jsonl
│   │   ├── events.jsonl
│   │   ├── hypotheses.jsonl
│   │   ├── conflict-groups.jsonl
│   │   ├── issues.jsonl
│   │   └── temporal-expressions.jsonl
│   ├── classifications/
│   ├── views/
│   │   ├── classification-views.jsonl
│   │   ├── phylogenetic-views.jsonl
│   │   └── campaigns/
│   ├── deltas/
│   └── snapshots/
├── game/
│   ├── core/
│   ├── projections/
│   ├── campaigns/
│   │   ├── c01-eukarya/
│   │   │   ├── manifest.json
│   │   │   ├── scientific-scope.json
│   │   │   ├── chapters/
│   │   │   ├── mechanics/
│   │   │   ├── content/
│   │   │   └── tests/
│   │   └── future/
│   ├── mechanics/
│   └── prototypes/
├── schemas/
│   ├── json-schema/
│   └── migrations/
├── scripts/
│   ├── ingest/
│   ├── validate/
│   ├── build-views/
│   ├── build-campaign/
│   └── snapshot/
├── tests/
│   ├── fixtures/
│   │   ├── eukarya-minimal/
│   │   └── future-hominin-regression/
│   ├── schema/
│   ├── validation/
│   ├── views/
│   ├── campaigns/
│   └── simulation/
├── archive/
│   └── guides/
└── generated/
    ├── reports/
    ├── diagrams/
    └── exports/
```

La estructura puede simplificarse al inicio, pero las responsabilidades deben mantenerse separadas. El archivo `archive/guides/` conserva versiones rectoras anteriores; no es un basurero de documentos abandonados, sino parte de la trazabilidad.

## 16.3. Identificadores

Los identificadores serán estables, opacos y permanentes. No deben depender del nombre canónico.

Prefijos consolidados:

| Prefijo | Tipo |
|---|---|
| `SEC-` | sección |
| `PASSAGE-` | pasaje |
| `MENTION-` | mención |
| `SRC-` | fuente |
| `NAME-` | nombre taxonómico |
| `TAXCONCEPT-` | concepto taxonómico |
| `CLADE-` | clado |
| `LINEAGE-` | linaje |
| `POP-` | población |
| `SPECIMEN-` | espécimen |
| `SITE-` | yacimiento |
| `REGION-` | región o ambiente |
| `OCC-` | ocurrencia |
| `TRAIT-` | rasgo |
| `TRAITOBS-` | observación de rasgo |
| `GENE-` | gen |
| `ALLELE-` | alelo |
| `EVENT-` | evento |
| `CLAIM-` | afirmación |
| `EVID-` | evidencia |
| `DATASET-` | conjunto de datos |
| `ANALYSIS-` | análisis |
| `RESULT-` | resultado |
| `HYP-` | hipótesis |
| `TAXVIEW-` | vista taxonómica |
| `PHYVIEW-` | vista filogenética |
| `CAMP-` | campaña |
| `CHAPTER-` | capítulo de campaña |
| `MECH-` | mecánica de juego |
| `GAME-` | proyección de juego |
| `ISSUE-` | cuestión pendiente |
| `TERM-` | término no resuelto |
| `TIME-` | expresión temporal reutilizable |
| `TECH-` | tecnología |
| `ECOSYS-` | estado de ecosistema |
| `METHOD-` | método |
| `RESEARCHER-` | investigador |
| `CONFLICT-` | grupo de conflicto entre hipótesis |

Los cinco últimos se añadieron el 8 de agosto de 2026 al detectar que §6.2 y §15.2 introducen entidades y grupos de conflicto sin prefijo, de modo que no podían tener identificador válido (`ISSUE-000034`, `ISSUE-000036`).

`EDGE-` se reserva para aristas materializadas en una exportación o vista. No será la identidad canónica de una afirmación científica.

Los IDs de campaña no codifican el nombre definitivo ni la posición eterna. `CAMP-000001` puede etiquetarse “Eucaria” aunque el título comercial cambie.

## 16.4. Registro append-only

Cada sección genera operaciones explícitas:

- `ADD_RECORD`;
- `UPDATE_RECORD`;
- `ADD_ALIAS`;
- `ADD_CLAIM`;
- `ADD_EVIDENCE`;
- `ADD_EVENT`;
- `ADD_HYPOTHESIS`;
- `ADD_SOURCE`;
- `ADD_ISSUE`;
- `RESOLVE_ISSUE`;
- `DEPRECATE_RECORD`;
- `SUPERSEDE_RECORD`;
- `MERGE_CONFIRMED_IDENTITIES`;
- `MIGRATE_SCHEMA`;
- `BUILD_VIEW`.

Nunca se elimina o fusiona información sin una operación registrada y reversible.

## 16.5. Versiones

Se distinguen:

```text
schema_version       SemVer del contrato de datos.
dataset_revision     número o ID de la incorporación.
snapshot_id          estado completo reconstruible.
view_version          versión de una vista derivada.
guide_version         versión de esta guía.
commit_id             revisión del repositorio.
```

No se utilizará SemVer para fingir que cada sección es una nueva versión conceptual del universo. La revisión del dataset aumenta por ingestión; el esquema cambia únicamente cuando cambia su contrato.

## 16.6. Checkpoints

Debe existir:

- delta después de cada sección;
- snapshot completo antes de una migración;
- snapshot completo en hitos de desarrollo;
- snapshot antes de transferir el proyecto a otra conversación o herramienta;
- snapshot periódico configurable durante ingestiones largas.

## 16.7. Base de datos futura

**POSPUESTO:** migrar o indexar en PostgreSQL, una base de grafos o RDF.

Se reevalúa cuando ocurra uno o más de estos disparadores:

- las consultas sobre JSONL sean demasiado lentas;
- la integridad referencial resulte difícil de mantener;
- la interfaz requiera edición concurrente;
- las vistas necesiten recorridos de grafo complejos en tiempo real;
- el volumen de datos haga imprácticos los diffs;
- se necesite una API multiusuario.

La migración no reemplazará los IDs ni la semántica. Los archivos versionados pueden continuar como formato de intercambio y respaldo reproducible.

---

# 17. Protocolo de ingestión de una sección

Cada sección de investigación seguirá el mismo flujo.

## Paso 1. Registrar la sección

Crear:

- ID estable `SEC-...`;
- título;
- fecha de ingreso;
- tema;
- período cubierto;
- fuente del texto;
- hash;
- versión original inmutable.

## Paso 2. Segmentar en pasajes

Dividir la sección en pasajes localizables. Cada mención y afirmación debe poder regresar al pasaje exacto que la originó.

## Paso 3. Extraer menciones

Identificar exhaustivamente:

- nombres científicos;
- nombres comunes;
- taxones;
- clados;
- fósiles;
- especímenes;
- yacimientos;
- fechas;
- rangos;
- regiones;
- eventos;
- rasgos;
- genes;
- tecnologías;
- conductas;
- controversias;
- hipótesis;
- fuentes;
- autores;
- métodos;
- términos históricos.

No se omite un elemento porque parezca secundario.

## Paso 4. Normalizar sin borrar el original

Para cada mención:

- conservar texto exacto;
- proponer forma normalizada;
- registrar variantes;
- detectar posibles errores tipográficos;
- distinguir alias de conceptos diferentes;
- evitar correcciones silenciosas.

## Paso 5. Resolver identidad

Decidir si la mención:

- crea una entidad;
- referencia una existente;
- añade un alias;
- refiere a un concepto taxonómico diferente con el mismo nombre;
- permanece no resuelta;
- crea una cuestión pendiente.

La resolución debe ser conservadora. No se fusionan entidades por parecido nominal.

## Paso 6. Extraer afirmaciones

Convertir el contenido en proposiciones atómicas. Separar, por ejemplo:

```text
“X es una especie de Y del período Z y fue propuesta por A”
```

en varias afirmaciones:

- X tiene rango de especie según la clasificación C;
- X pertenece a Y según C;
- X posee rango temporal observado Z;
- A propuso el concepto taxonómico X;
- la fuente S contiene esas afirmaciones.

## Paso 7. Registrar evidencia y análisis

Cuando se mencionen:

- caracteres;
- matrices;
- genes;
- dataciones;
- análisis;
- soporte estadístico;
- figuras;
- resultados;

crear registros separados y vincularlos con las afirmaciones pertinentes.

Cuando estén disponibles deben conservarse autores, año, título, DOI u otro identificador, edición, páginas, figura, tabla y material suplementario. No se inventan referencias ausentes. Una afirmación proporcionada sin fuente se conserva como procedente de la sección y se marca para verificación futura.

## Paso 8. Crear eventos

Promover a evento cualquier proceso que requiera:

- participantes;
- roles;
- tiempo;
- lugar;
- resultado;
- múltiples afirmaciones.

## Paso 9. Integrar hipótesis

Determinar si las nuevas afirmaciones:

- apoyan una hipótesis existente;
- añaden una alternativa;
- contradicen otra;
- obligan a dividir una hipótesis;
- resuelven una cuestión;
- crean un grupo de conflicto.

No se mezclan topologías incompatibles en un único árbol.

## Paso 10. Auditar cobertura

Cada mención debe tener un destino:

| Mención original | Normalización | Tipo | Destino | Acción | Estado |
|---|---|---|---|---|---|

La cobertura completa es una condición de finalización.

## Paso 11. Actualizar vistas

Solo después de registrar afirmaciones e hipótesis se reconstruyen las vistas afectadas.

Una nueva sección puede:

- no modificar el backbone;
- añadir un overlay;
- cambiar una vista histórica;
- crear una topología alternativa;
- invalidar una vista materializada.

## Paso 12. Validar

Ejecutar las once familias de validación obligatorias, definidas en §19.2:

- esquema;
- integridad referencial;
- cobertura;
- identidad;
- tiempo;
- geografía;
- hipótesis y topología;
- evidencia;
- procedencia;
- estado;
- separación de capas.

§19.2 es la lista canónica. §19.3 debe ofrecer un comando por familia.

## Paso 13. Generar delta

El delta debe incluir solo cambios reales:

```json
{
  "section_id": "SEC-000000",
  "schema_version": "1.0.0",
  "dataset_revision_before": "REV-000000",
  "dataset_revision_after": "REV-000001",
  "records_added": [],
  "records_updated": [],
  "claims_added": [],
  "events_added": [],
  "hypotheses_added": [],
  "issues_added": [],
  "issues_resolved": [],
  "records_deprecated": [],
  "views_invalidated": [],
  "views_built": [],
  "validation_results": {}
}
```

## Paso 14. Generar informe humano

El informe no debe repetir todo el JSON. Su especificación completa está en el **Apéndice F.1**, que lo detalla en trece apartados; lo que sigue es su resumen y no debe implementarse en su lugar (`ISSUE-000008`). Debe contener:

1. identificación de la sección;
2. síntesis científica;
3. cambios importantes;
4. controversias;
5. cuestiones pendientes;
6. resultados de validación;
7. visualización local;
8. resumen del delta;
9. estado acumulado compacto.

## Paso 15. Confirmar persistencia

Antes de considerar la sección terminada:

- guardar archivos;
- ejecutar validación final;
- registrar revisión;
- generar snapshot si corresponde;
- comprobar que el estado puede reconstruirse sin la conversación.

---

# 18. Modos de trabajo científico

## 18.1. Modo de ingestión

Objetivo: representar fielmente el material proporcionado.

Reglas:

- no investigar externamente por defecto;
- no completar lagunas;
- no sustituir fuentes;
- no inventar citas;
- no corregir silenciosamente;
- detectar inconsistencias;
- crear issues;
- conservar formulación y procedencia.

## 18.2. Modo de auditoría

Objetivo: contrastar el corpus con literatura científica y bases actuales.

Puede:

- verificar nomenclatura;
- buscar revisiones posteriores;
- comparar clasificaciones;
- evaluar métodos;
- detectar fuentes retractadas o superadas;
- actualizar aceptación científica;
- proponer nuevas afirmaciones con procedencia externa.

Toda incorporación externa debe indicar que proviene de auditoría, no de la sección original.

## 18.3. Modo editorial

Objetivo: construir una síntesis o vista de trabajo.

Debe declarar:

- criterios de selección;
- fecha de corte;
- fuentes priorizadas;
- tratamiento de conflictos;
- simplificaciones;
- nivel de resolución.

## 18.4. Modo de proyección de juego

Objetivo: traducir una vista científica a contenido jugable sin modificar el núcleo.

Debe registrar:

- qué se incluye;
- qué se omite;
- qué se agrupa;
- qué incertidumbre se muestra;
- qué simplificación se introduce;
- por qué sigue siendo científicamente aceptable.

---

# 19. Validación

## 19.1. Niveles de severidad

```text
ERROR    impide aceptar el delta.
WARNING  permite continuar, pero exige issue o justificación.
INFO     observación no bloqueante.
```

## 19.2. Validaciones obligatorias

### Esquema

- campos requeridos;
- tipos;
- enumeraciones;
- versión compatible;
- ausencia de campos no reconocidos cuando corresponda.

### Integridad referencial

- todo ID referenciado existe;
- no hay IDs duplicados;
- las fusiones conservan redirecciones;
- las vistas no apuntan a registros eliminados.

### Cobertura

- toda mención posee destino;
- todo descarte está justificado;
- toda afirmación puede rastrearse a un pasaje o fuente.

### Identidad

- alias no duplicados de manera ambigua;
- homónimos taxonómicos no fusionados;
- nombre y concepto taxonómico diferenciados;
- espécimen y taxón diferenciados.

### Tiempo

- intervalos válidos;
- unidades explícitas;
- observado e inferido separados;
- eventos temporalmente plausibles;
- ausencia de ciclos de ascendencia dentro de una hipótesis.

### Geografía

- yacimiento y región no confundidos;
- ubicaciones inferidas marcadas;
- coexistencia no inferida solo por tiempo si la geografía es incompatible.

### Hipótesis y topología

- afirmaciones incompatibles no seleccionadas en el mismo escenario;
- requisitos satisfechos;
- topología coherente;
- ausencia de ciclos en el subgrafo de ascendencia de cada hipótesis;
- ninguna vista mezcla topologías incompatibles;
- fuentes y contraevidencias vinculadas.

### Evidencia

- soporte cuantitativo con tipo y fuente;
- no hay porcentajes inventados;
- la evidencia respalda la afirmación indicada;
- fuente general y localizador específico cuando estén disponibles.

### Procedencia

Cobertura comprueba que la cadena **exista**; procedencia comprueba que esté **completa**, según los seis requisitos de §4.5.

- toda afirmación enlaza su sección de origen y su mención exacta;
- toda fuente declarada lleva su localizador cuando la fuente lo permita;
- toda afirmación registra la operación que la incorporó y la revisión del conjunto de datos;
- las afirmaciones derivadas declaran su regla y su dependencia, y no se confunden con afirmaciones expresas;
- los registros incorporados en modo auditoría están marcados como externos y no como procedentes de la sección.

### Estado

- registros superados conservados;
- deprecaciones con reemplazo o razón;
- migraciones documentadas;
- dimensiones epistemológicas no mezcladas.

### Separación de capas

- el núcleo científico no contiene costos, bonificaciones o condiciones de victoria;
- la proyección de juego no reescribe afirmaciones científicas;
- las vistas generadas identifican sus simplificaciones.

## 19.3. Comandos previstos

Nombres conceptuales, sujetos al stack elegido:

```text
validate:schema
validate:references
validate:coverage
validate:identity
validate:time
validate:geography
validate:hypotheses
validate:evidence
validate:provenance
validate:state
validate:separation
validate:all
build:classification-view
build:phylogenetic-view
build:local-diagram
snapshot:create
snapshot:verify
ingest:section
```

---

# 20. Visualización

## 20.1. Principio

Una visualización es una vista derivada, no el almacén de conocimiento.

## 20.2. Convenciones iniciales

### Relaciones

- línea continua: backbone seleccionado;
- línea discontinua: hipótesis alternativa;
- línea punteada: relación especulativa;
- flecha lateral etiquetada: flujo génico o transferencia;
- participantes conectados a nodo-evento: hibridación o proceso n-ario;
- borde tenue: clasificación histórica o superada;
- signo de interrogación: posición no resuelta.

### Nodos

Deben distinguirse por forma, etiqueta o patrón:

- taxón;
- concepto taxonómico;
- clado;
- población;
- linaje;
- espécimen;
- evento;
- rasgo;
- hipótesis;
- ancestro no muestreado.

No depender únicamente del color.

## 20.3. Hipótesis incompatibles

Se representarán mediante:

- vistas separadas;
- capas activables;
- pequeños múltiplos;
- overlays claramente etiquetados;
- comparación lado a lado.

No se dibujarán todas las alternativas como si fueran simultáneamente verdaderas.

## 20.4. Herramientas

- Mermaid para diagramas pequeños y documentación;
- Graphviz DOT para relaciones complejas y salidas reproducibles;
- Newick/Extended Newick para intercambio filogenético cuando corresponda;
- una interfaz gráfica interactiva en fases posteriores.

## 20.5. Bandas poblacionales

**RETENIDO para prototipo:** representar poblaciones como bandas temporales cuya anchura pueda expresar:

- tamaño efectivo;
- abundancia relativa;
- diversidad;
- incertidumbre.

Debe elegirse una semántica por vista; el ancho no puede significar cuatro cosas al mismo tiempo.

## 20.6. Accesibilidad

- legible en blanco y negro;
- formas y patrones redundantes;
- etiquetas textuales;
- navegación por teclado en la interfaz futura;
- descripciones alternativas;
- control de densidad;
- zoom semántico.

---

# 21. Diseño del juego consolidado

Esta sección conserva el diseño anterior y lo reorganiza para una producción cronológica por campañas. El cambio afecta prioridades y niveles de implementación, no elimina modos ni sistemas futuros.

## 21.1. Premisa jugable

**DECIDIDO como dirección:** el juego no consiste en “subir” desde un organismo primitivo hasta el humano moderno. Consiste en producir, atravesar, observar y reconstruir historias evolutivas poblacionales.

La secuencia de campañas sigue el corredor hacia la humanidad para dar continuidad pedagógica y productiva, pero ninguna campaña presenta su clado como un paso inferior destinado a generar el siguiente.

## 21.2. Producto campaña por campaña

**DECIDIDO:** cada campaña debe poder lanzarse como una experiencia completa y, al mismo tiempo, ampliar la plataforma común.

Cada lanzamiento contiene:

- campaña jugable;
- Atlas correspondiente;
- red temporal y filogenética;
- lente científica;
- fuentes y procedencia;
- contenido desbloqueable;
- guardado y progresión;
- documentación de simplificaciones;
- compatibilidad con campañas futuras.

No se desarrollará primero una simulación universal para después buscarle contenido. El núcleo compartido se extiende únicamente cuando una campaña introduce un requisito nuevo demostrado.

## 21.3. Capacidades principales

### 21.3.1. Modo Evolución

**DECIDIDO para la Campaña 1 en una forma acotada; RETENIDO para expansiones más complejas.**

El jugador influye indirectamente sobre poblaciones. No selecciona mutaciones concretas ni compra órganos. Las decisiones dependen de la escala.

En Eucaria puede influir en:

- explotación de recursos;
- tolerancia ambiental;
- contacto entre poblaciones;
- asociación simbiótica;
- estabilidad o ruptura de asociaciones;
- ritmo reproductivo abstracto;
- expansión o aislamiento;
- inversión en mantenimiento, crecimiento o reproducción.

En campañas posteriores podrán añadirse:

- movilidad geográfica;
- dieta;
- cuidado parental;
- estructura social;
- aprendizaje;
- transmisión cultural;
- herramientas;
- redes de intercambio.

La variación aparece dentro de límites históricos, funcionales y ambientales. Toda ventaja debe tener costos, dependencias o contextos.

### 21.3.2. Lente científica

**DECIDIDO para el primer lanzamiento.** Es una versión pequeña del futuro modo Reconstrucción.

Permite:

- consultar por qué aparece una relación;
- leer las afirmaciones y fuentes relevantes;
- cambiar entre una síntesis de trabajo y una hipótesis alternativa;
- distinguir observación, inferencia y especulación;
- ver intervalos y nivel de resolución;
- registrar cuestiones abiertas;
- comparar cómo una decisión editorial modifica una vista.

No incluye todavía excavaciones, laboratorios, presupuesto de análisis ni publicación académica simulada.

### 21.3.3. Modo Reconstrucción completo

**RETENIDO y reubicado.** El jugador investiga una historia oculta mediante evidencia incompleta.

Acciones previstas para campañas que dispongan de registros adecuados:

- elegir regiones, yacimientos o colecciones;
- excavar o revisar especímenes;
- datar;
- medir;
- comparar;
- reconstruir;
- analizar ADN o proteínas cuando sea plausible;
- construir hipótesis;
- asignar especímenes;
- definir o revisar taxones;
- publicar;
- responder críticas;
- conservar alternativas.

El sistema debe premiar:

- buen ajuste a datos;
- calibración de incertidumbre;
- reproducibilidad;
- capacidad predictiva;
- parsimonia sin simplificación abusiva;
- reconocimiento de información insuficiente.

El período 400.000–40.000 años continúa siendo el candidato más fuerte para su primer escenario completo.

### 21.3.4. Atlas evolutivo

**DECIDIDO como superficie compartida desde el primer lanzamiento.** Permite navegar entidades, afirmaciones, eventos, hipótesis y vistas.

Cada ficha puede mostrar, cuando corresponda:

- definición;
- rango o función;
- edad observada e inferida;
- distribución o ambiente;
- grupos incluidos;
- ramas hermanas dentro de una vista;
- caracteres;
- señales, fósiles o especímenes;
- nombres alternativos;
- controversias;
- fuentes;
- confianza y aceptación por dimensión;
- historia de cambios;
- campaña en la que se introduce;
- nivel de detalle desbloqueado.

## 21.4. Tres vistas sincronizadas y adaptables

| Vista | Campaña temprana | Campaña tardía |
|---|---|---|
| Entorno | microambientes, recursos, oxígeno, estabilidad, asociaciones | geografía, clima, biomas, barreras, rutas y poblaciones |
| Red | divergencia, endosimbiosis, transferencia, persistencia y extinción | divergencia, migración, flujo génico, absorción y extinción |
| Ciencia | señales comparativas, moleculares y celulares; hipótesis | fósiles, muestras, dataciones, análisis, publicaciones y debates |

La identidad de entidades y afirmaciones es compartida; la interfaz y densidad se adaptan a la escala.

## 21.5. Variables por escala

No existirá una tabla universal de variables obligatorias. Se utilizará un catálogo del que cada campaña selecciona módulos.

| Dimensión | Eucaria | Homininos y campañas tardías |
|---|---|---|
| Demografía | tamaño poblacional abstracto, reproducción, persistencia, deriva | tamaño efectivo, estructura etaria, natalidad, mortalidad, cuellos de botella |
| Ambiente | nutrientes, oxígeno, temperatura, estabilidad | clima, hábitat, estacionalidad, corredores, recursos |
| Ecología | competencia, simbiosis, parasitismo, nicho metabólico | dieta, depredación, patógenos, competencia, construcción de nicho |
| Herencia | variación abstracta, transferencia, integración, recombinación | diversidad, flujo génico, ancestría, carga y loci cuando corresponda |
| Organización | compartimentación, regulación, cooperación intracelular | anatomía, desarrollo, fisiología, conducta social |
| Cultura | no aplicable salvo analogías explícitamente evitadas | herramientas, fuego, aprendizaje, tradición, simbolismo |
| Registro | señales moleculares y comparativas | fosilización, ADN, proteínas, arqueología, sesgo de muestreo |

## 21.6. Bucle universal del modo Evolución

Cada campaña adapta seis fases:

1. **Cambio de condiciones:** el entorno altera posibilidades y costos.
2. **Respuesta poblacional:** el jugador orienta estrategias indirectas.
3. **Variación:** aparecen variantes condicionadas por la historia previa.
4. **Cambio de frecuencias:** selección, deriva, transmisión y azar modifican poblaciones.
5. **Divergencia, contacto o integración:** las poblaciones se separan, interactúan, intercambian material o forman asociaciones.
6. **Registro:** la historia se guarda en el grafo y produce señales observables según la campaña.

La especiación, la integración y las innovaciones no son botones de compra. Emergen de estados, eventos y probabilidades trazables.

## 21.7. Bucle específico de Eucaria

Una ronda o intervalo de la primera campaña puede seguir:

### 1. Ambiente

Cambian:

- recursos;
- disponibilidad de aceptores de electrones;
- oxígeno;
- temperatura;
- estabilidad;
- densidad de competidores;
- oportunidades de asociación.

### 2. Estrategia poblacional

El jugador orienta:

- expansión;
- aislamiento;
- explotación de recursos;
- tolerancia;
- contacto con otros linajes;
- mantenimiento o ruptura de una asociación;
- inversión energética.

### 3. Variación

Surgen variantes:

- metabólicas;
- estructurales;
- regulatorias;
- reproductivas;
- ecológicas.

### 4. Selección y deriva

Las frecuencias cambian según:

- costo energético;
- eficiencia;
- tamaño poblacional;
- estabilidad ambiental;
- conflicto entre participantes;
- azar.

### 5. Integración o conflicto

Una interacción puede conducir a:

- competencia;
- parasitismo;
- cooperación temporal;
- asociación estable;
- transferencia genética abstracta;
- **recombinación por ciclo sexual**, que redistribuye variación dentro de un linaje sin transferirla entre linajes;
- dependencia mutua;
- integración heredable.

### 6. Divergencia y registro

Las poblaciones pueden persistir, separarse, extinguirse o producir nuevos linajes. El Atlas registra los eventos y la lente científica muestra qué parte es consenso, reconstrucción o hipótesis.

## 21.8. Taxonomía dentro del juego

Los rangos sirven para:

- navegación;
- organización;
- comparación;
- explicación histórica;
- objetivos didácticos;
- desbloqueo de herramientas de análisis;
- definición de campañas.

No sirven como:

- niveles de poder;
- etapas de progreso;
- mejoras acumulativas;
- indicador de superioridad.

## 21.9. Condiciones de éxito

**ABIERTO en detalle.** Principios establecidos:

- no existe una única victoria llamada “producir humanos”;
- completar una campaña no significa que su linaje haya sido inevitable;
- la supervivencia no equivale siempre a éxito;
- una extinción puede formar parte de un resultado científicamente significativo;
- mantener diversidad, estabilidad, integración o resiliencia puede ser un objetivo;
- la lente científica premia comprensión y calibración, no memorización;
- cada campaña debe tener condiciones propias y múltiples resultados válidos.

## 21.10. Historia oculta y evidencia generada

**RETENIDO como arquitectura fuerte y desarrollado por etapas:** una partida puede generar:

1. una historia poblacional completa y oculta;
2. un módulo de preservación o señal que decide qué queda observable;
3. un módulo de descubrimiento que decide qué recibe el jugador;
4. un espacio de hipótesis construido a partir de esa evidencia.

En Eucaria se implementará una versión reducida basada en señales y vistas. La tafonomía, los especímenes y la arqueología se activarán en campañas posteriores.

## 21.11. Escenarios de referencia conservados

### Escenario inicial: asociación e integración

Dos poblaciones ancestrales interactúan bajo condiciones ambientales cambiantes. La asociación puede romperse, estabilizarse o profundizarse. El jugador gestiona costos, conflicto y dependencia sin pulsar “crear mitocondria”. El resultado se registra como evento reticulado y no como una bifurcación ordinaria.

### Escenario hominino preservado: África oriental, 2,8 Ma

Se conservan:

- población australopiteca flexible;
- población aislada;
- formas robustas tempranas;
- *Homo* temprano escaso;
- fragmentación ambiental;
- especialización;
- desaparición sin registro;
- dientes como evidencia parcial;
- interpretaciones alternativas de variación, dimorfismo o especies.

Este escenario sigue siendo válido para la campaña final y para el futuro modo Reconstrucción. No forma parte del primer lanzamiento.

## 21.12. Continuidad entre campañas

### Primera etapa

La continuidad se expresa mediante:

- orden narrativo;
- Atlas acumulativo;
- conceptos y herramientas desbloqueados;
- historial de campañas completadas;
- logros de comprensión;
- opciones de visualización adicionales.

### Etapa futura

El `Modo Gran Linaje` podrá evaluar transferencia de estados, rasgos o historias contrafactuales entre campañas. No es requisito del primer lanzamiento ni del segundo.

## 21.13. Contenido mínimo del primer lanzamiento

Debe incluir:

- campaña completa Eukaryota → Holozoa;
- capítulos y tutorial;
- red temporal;
- evento de endosimbiosis;
- divergencias principales;
- Atlas inicial;
- lente científica;
- al menos dos vistas incompatibles o parcialmente incompatibles;
- fuentes consultables;
- guardado;
- accesibilidad básica;
- rejugabilidad limitada pero real;
- final que conecte con la campaña de animales sin afirmar inevitabilidad.

Puede posponer:

- modo Reconstrucción completo;
- fósiles y excavaciones;
- genética molecular de loci;
- geografía continental;
- cultura;
- continuidad biológica literal entre campañas.

## 21.14. Requisitos avanzados preservados para campañas tardías

Los siguientes elementos pertenecían al diseño original centrado en homininos. Se conservan como especificación funcional para Primates, Homininos y cualquier campaña que alcance una complejidad poblacional equivalente.

### 21.14.1. Influencias indirectas disponibles

El jugador podrá influir, según la campaña, en:

- movilidad;
- elección de hábitat;
- dieta;
- estructura social;
- tolerancia o conflicto con otros grupos;
- reproducción;
- cuidado parental;
- aprendizaje;
- transmisión cultural;
- explotación de recursos;
- redes de intercambio.

No elegirá mutaciones concretas. La variación seguirá limitada por anatomía, genética, desarrollo, ambiente e historia previa.

### 21.14.2. Objetivos posibles preservados

- atravesar una crisis climática;
- mantener diversidad genética o cultural;
- colonizar una región;
- sostener varios linajes coexistentes;
- evitar absorción o extinción;
- producir redes culturales extensas;
- persistir mediante una estrategia especializada;
- explorar historias contrafactuales;
- sobrevivir sin desarrollar rasgos asociados popularmente con “progreso”.

### 21.14.3. Variables poblacionales avanzadas

| Dimensión | Variables previstas |
|---|---|
| Demografía | tamaño efectivo, estructura etaria, natalidad, mortalidad, densidad, cuellos de botella |
| Geografía | territorio, movilidad, conectividad, aislamiento, corredores |
| Ecología | dieta, hábitat, estacionalidad, depredación, patógenos, competencia |
| Genética | diversidad, deriva, flujo génico, carga, ancestría |
| Anatomía | locomoción, dentición, manos, termorregulación, desarrollo |
| Conducta | cooperación, conflicto, exploración, cuidado parental |
| Cultura | herramientas, fuego, aprendizaje, tradición, simbolismo |
| Registro futuro | fosilización, preservación, detectabilidad, sesgo de muestreo |

Estas variables no forman una lista obligatoria para todas las campañas. Cada módulo activa únicamente las que necesita.

### 21.14.4. Ambiente y respuesta en campañas tardías

Factores preservados:

- ciclos glaciales;
- aridificación;
- expansión o contracción de bosques;
- cambios costeros;
- erupciones;
- corredores migratorios;
- fauna, competidores y patógenos.

Respuestas posibles:

- permanecer;
- migrar;
- dividirse;
- ampliar o restringir dieta;
- establecer contacto;
- competir;
- intercambiar;
- evitar otros grupos.

El clima modifica posibilidades, no prescribe mutaciones.

### 21.14.5. Compensaciones evolutivas preservadas

- mayor cerebro frente a costo energético y desarrollo prolongado;
- bipedalismo frente a restricciones anatómicas;
- especialización dental frente a flexibilidad;
- cooperación frente a vulnerabilidad a explotación;
- infancia prolongada frente a mayor dependencia.

El catálogo debe ampliarse por campaña y nunca convertirse en una escala universal de superioridad.

### 21.14.6. Mecanismos de cambio de frecuencias

- selección natural;
- selección sexual;
- deriva;
- efecto fundador;
- flujo génico;
- herencia cultural;
- aprendizaje social.

### 21.14.7. Divergencia y reconexión avanzadas

El modelo podrá considerar:

- aislamiento;
- distancia;
- compatibilidad reproductiva;
- contacto;
- diferenciación ecológica;
- tamaño poblacional;
- divergencia cultural;
- duración del aislamiento.

La especiación emerge del proceso. No se activa mediante un botón.

### 21.14.8. Producción de registro en campañas fósiles y humanas

Las poblaciones podrán dejar, con probabilidades desiguales:

- huesos;
- dientes;
- herramientas;
- huellas;
- hogares;
- sedimentos;
- proteínas;
- ADN;
- modificaciones de fauna.

La mayoría del registro se perderá o permanecerá sin descubrir.

### 21.14.9. Bucle completo de Reconstrucción preservado

1. formular una pregunta;
2. asignar recursos;
3. obtener evidencia;
4. evaluar calidad y sesgos;
5. construir una o varias hipótesis;
6. publicar o conservar provisionalmente;
7. recibir revisión y nueva evidencia;
8. revisar, fusionar, dividir o abandonar conceptos.

Este bucle no se reduce a acertar una topología oculta. Debe premiar evidencia, reproducibilidad e incertidumbre calibrada.

---

# 22. Campañas y escalas de juego

## 22.1. Principio general

No se usarán las mismas reglas con idéntica resolución desde los primeros eucariotas hasta *Homo sapiens*. Cada campaña introduce una escala, preguntas y mecánicas nuevas, apoyándose en el núcleo compartido.

## 22.2. Cono de foco operativo

Para cada campaña se documentan:

### A. Corredor principal

Se incluye con resolución suficiente para sostener la experiencia y la continuidad histórica.

### B. Ramas hermanas inmediatas

Se representan para que cada divergencia tenga contexto y no parezca una escalera aislada.

### C. Grupos externos representativos

Se añaden cuando son necesarios para explicar una comparación, hipótesis, rasgo o interacción.

### D. Diversidad diferida

Se conserva en el backlog científico y puede incorporarse al Atlas, pero no bloquea el lanzamiento.

## 22.3. Arquitectura de campañas

```text
PLATAFORMA COMPARTIDA
├── núcleo científico
├── identidad y procedencia
├── afirmaciones y evidencia
├── eventos e hipótesis
├── vistas
├── Atlas
├── red temporal
├── guardado
└── accesibilidad

CAMPAÑA N
├── dossier científico
├── alcance y exclusiones
├── módulo de simulación
├── contenido
├── capítulos
├── interfaz especializada
├── tutorial
├── pruebas
└── criterios de lanzamiento
```

## 22.4. Secuencia prevista y complejidad progresiva

| Orden | Campaña provisional | Corredor principal | Sistemas nuevos dominantes |
|---:|---|---|---|
| 1 | **Eucaria: una célula dentro de otra** | Eukaryota → Holozoa | linajes, poblaciones celulares, selección, deriva, endosimbiosis, integración, hipótesis |
| 2 | **Animales: construir un cuerpo** | Holozoa → Bilateria | multicelularidad, diferenciación, desarrollo, planes corporales, homología |
| 3 | **Cordados: abandonar el agua** | Bilateria → Tetrapoda | anatomía, locomoción, respiración, nichos, transición acuática-terrestre |
| 4 | **Sinápsidos: heredar la noche** | Amniota/Synapsida → Mammalia | reproducción terrestre, termorregulación, dentición, extinciones masivas |
| 5 | **Mamíferos: radiaciones y cuidados** | Mammalia → Primatomorpha | historia de vida, lactancia, cuidado parental, nichos, radiaciones ecológicas |
| 6 | **Primates: manos, ojos y sociedades** | Primates → Hominidae | prensión, visión, locomoción arbórea, dieta, sociabilidad, aprendizaje |
| 7 | **Homininos: humanidades entrelazadas** | Hominini → *Homo sapiens* | poblaciones detalladas, fósiles, herramientas, cultura, migración, arqueología, hibridación e introgresión |

Las fronteras exactas pueden ajustarse mediante ADR sin alterar el orden general.

## 22.5. Campaña 1: Eucaria

### Estado

**DECIDIDA como primer lanzamiento.**

### Título provisional

**Eucaria: una célula dentro de otra.**

### Inicio científico

Un prólogo sobre poblaciones ancestrales y procesos previos a la consolidación de Eukaryota. No se inventará un taxón concreto cuando la identidad sea incierta. Se usarán conceptos como:

- linaje hospedador ancestral reconstruido;
- simbionte bacteriano ancestral;
- poblaciones protoeucariotas;
- ancestro común no muestreado.

### Núcleo

```text
eucariogénesis
→ integración mitocondrial
→ diversificación eucariota temprana
→ Eukaryota
→ Amorphea
→ Obazoa
→ Opisthokonta
→ Holozoa
```

### Final

La campaña termina en Holozoa, preparando la transición a animales sin implementar todavía Metazoa en profundidad.

### Backbone mínimo de contenido

Debe incluir, si el corpus científico seleccionado lo respalda:

- Eukaryota;
- Amorphea;
- Amoebozoa como rama hermana relevante;
- Obazoa;
- Apusomonadida y Breviatea en la resolución necesaria;
- Opisthokonta;
- Holomycota como rama hermana;
- Holozoa;
- Filozoa u otros nodos intermedios únicamente si el dossier científico los requiere para cerrar la campaña;
- poblaciones o linajes ancestrales estructurales;
- evento de endosimbiosis mitocondrial;
- hipótesis alternativas seleccionadas.

La lista no es una licencia para agregar taxones por memoria. Todo contenido canónico entra mediante fuentes y afirmaciones.

### Preguntas científicas jugables

- ¿Qué hace estable una asociación inicialmente conflictiva?
- ¿Cómo cambian los costos y beneficios con el ambiente?
- ¿Cuándo una dependencia se vuelve heredable?
- ¿Qué distingue divergencia, transferencia e integración?
- ¿Cómo puede la misma evidencia apoyar reconstrucciones diferentes?
- ¿Qué rasgos son observados y cuáles inferidos?

### Mecánicas iniciales

- recursos y energía abstractos;
- tamaño y estabilidad poblacional;
- variación y deriva;
- competencia;
- contacto;
- simbiosis;
- conflicto intracelular abstracto;
- integración;
- transferencia genética abstracta;
- divergencia;
- extinción;
- desbloqueo de vistas científicas.

### Capítulos conceptuales

1. **Antes del eucariota:** ambiente, poblaciones y oportunidades de contacto.
2. **La asociación:** cooperación, parasitismo y conflicto.
3. **La integración:** dependencia, herencia y transferencia.
4. **Energía y organización:** costos, regulación y nuevas posibilidades.
5. **Diversificación:** separación de grandes linajes.
6. **Hacia Holozoa:** cierre del corredor y transición a animales.

### Exclusiones explícitas del primer lanzamiento

- todos los supergrupos y taxones eucariotas en resolución exhaustiva;
- origen detallado del núcleo como mecanismo jugable si el corpus no permite una representación responsable;
- genes y proteínas individuales;
- redes metabólicas bioquímicas completas;
- simulación celular físicamente continua;
- multicelularidad animal profunda;
- modo Gran Linaje.

## 22.6. Campaña 2: Animales

**SIGUIENTE CAMPAÑA PREVISTA.** Desde Holozoa y formas unicelulares relacionadas hasta Bilateria.

Mecánicas potenciales:

- multicelularidad;
- adhesión;
- diferenciación celular;
- regulación del desarrollo;
- cooperación y conflicto celular;
- planes corporales;
- reproducción;
- señales ecológicas;
- primeras homologías complejas.

No debe iniciarse hasta que la Campaña 1 se haya lanzado y se haya realizado una revisión postmortem del núcleo.

## 22.7. Campaña 3: Cordados

**PLANIFICADA.** Desde Bilateria hasta Tetrapoda.

Mecánicas potenciales:

- anatomía y módulos corporales;
- locomoción;
- respiración;
- depredación;
- nichos;
- transición acuática-terrestre;
- redes ecológicas;
- registro fósil más explícito.

## 22.8. Campaña 4: Sinápsidos

**PLANIFICADA.** Desde Amniota/Synapsida hasta Mammalia.

Mecánicas potenciales:

- reproducción terrestre;
- termorregulación;
- dentición;
- postura;
- desarrollo;
- nichos nocturnos;
- extinciones masivas;
- continuidad de caracteres mosaico.

## 22.9. Campaña 5: Mamíferos

**PLANIFICADA.** Desde Mammalia hasta Primatomorpha.

Mecánicas potenciales:

- lactancia;
- cuidado parental;
- historia de vida;
- sentidos;
- radiaciones ecológicas;
- dispersión;
- arborealidad;
- competencia tras extinciones.

## 22.10. Campaña 6: Primates

**PLANIFICADA.** Desde primates tempranos hasta Hominidae.

Mecánicas potenciales:

- visión;
- prensión;
- dieta;
- locomoción arbórea;
- sociabilidad;
- aprendizaje;
- historia biogeográfica;
- clasificación por familias, subfamilias, tribus y subtribus.

El inventario detallado del Apéndice B se conserva como especificación científica de esta campaña.

## 22.11. Campaña 7: Homininos

**RETENIDA como campaña culminante.** Integra el trabajo paleoantropológico ya desarrollado.

Capítulos conceptuales conservados:

1. **El último ancestro común**, 8–5 Ma.
2. **El mosaico australopiteco**, 4,5–2,8 Ma.
3. **Tres formas de ser hominino**, 3–1,5 Ma.
4. **La primera expansión**, 2–0,8 Ma.
5. **Humanidades entrelazadas**, 800.000–40.000 años.
6. **Una humanidad superviviente**, 300.000 años–presente.

El capítulo 5 conserva el recorte 400.000–40.000 años como:

- escenario de Reconstrucción completo;
- prueba de introgresión;
- prueba de taxonomía y linajes;
- prueba de fósiles y genomas;
- vertical slice interno de máxima complejidad.

La campaña puede dividirse en dos productos si el volumen lo exige:

```text
Homininos tempranos
Humanidades entrelazadas
```

La decisión se mantiene abierta hasta que las campañas previas permitan estimar costos reales.

## 22.12. Modo Gran Linaje

**POSPUESTO:** una única historia jugable conectada desde Eukaryota hasta homininos.

La primera arquitectura solo garantiza:

- compatibilidad de identidad;
- Atlas acumulativo;
- progresión narrativa;
- desbloqueos;
- posibilidad futura de importar estados resumidos.

El modo continuo se evaluará después de completar al menos tres campañas y conocer qué variables pueden transferirse sin forzar una simulación universal superficial.

# 23. Qué no se hará

## 23.1. Rechazos científicos

**RECHAZADO:**

- una escalera lineal de progreso;
- “pez → anfibio → reptil → mamífero → mono → humano” como secuencia literal;
- presentar la secuencia de campañas como destino biológico;
- chimpancés modernos como antepasados humanos;
- taxones como equivalentes automáticos de clados;
- especies fósiles como ancestros directos por defecto;
- ausencia de fósiles como ausencia biológica;
- razas humanas modernas como ramas taxonómicas discretas;
- categorías históricas presentadas como vigentes;
- convergencia dibujada como ascendencia;
- hibridación confundida con incertidumbre topológica;
- endosimbiosis dibujada como una bifurcación ordinaria;
- inventar un “primer eucariota” nombrado para llenar un hueco;
- tratar la primera evidencia conocida como origen real del rasgo.

## 23.2. Rechazos de diseño

**RECHAZADO:**

- barra universal de inteligencia o complejidad;
- mutaciones, núcleos, mitocondrias u órganos comprados como mejoras lineales;
- especies como personajes rígidos;
- *Homo sapiens* como victoria obligatoria;
- “primitivo” como sinónimo de inferior;
- rangos taxonómicos como niveles;
- un único árbol mostrado como verdad;
- cada fósil como una nueva especie;
- usar complejidad científica solo como decoración;
- exigir que la primera partida continúe literalmente durante miles de millones de años;
- usar exactamente las mismas reglas de simulación en todas las campañas;
- lanzar Eucaria como prólogo técnico incompleto sin arco jugable propio;
- intentar representar todos los eucariotas antes de publicar;
- antropomorfizar células de forma que convierta cooperación, conflicto o herencia en intenciones humanas literales.

## 23.3. Rechazos técnicos

**RECHAZADO:**

- un JSON monolítico;
- un nodo universal con decenas de campos nulos;
- un único `epistemic_status`;
- confianza porcentual inventada;
- almacenar inversas redundantes sin necesidad;
- tratar todas las relaciones como aristas binarias;
- guardar el diseño del juego dentro de cada nodo científico;
- utilizar el chat como almacenamiento principal;
- mezclar ingestión y auditoría externa;
- sobrescribir o eliminar información sin historial;
- dibujar todas las hipótesis incompatibles en una sola topología;
- construir un motor universal antes de tener una campaña concreta;
- acoplar el núcleo científico a las variables particulares de Eucaria;
- eliminar tipos futuros porque la primera campaña no los usa;
- implementar tipos complejos sin fixture ni caso de uso.

# 24. Hoja de ruta de desarrollo

La hoja de ruta sigue dependencias científicas y de producto. El objetivo no es completar una ontología antes de jugar ni improvisar un juego sin datos trazables. Cada fase termina con un artefacto verificable.

## Fase 0. Migración estratégica y constitución del proyecto

### Objetivo

Preservar el trabajo anterior, fijar la estrategia por campañas y crear el marco de trabajo.

### Tareas

1. archivar la guía `1.0.0` con hash;
2. incorporar esta guía `1.1.0` como documento activo;
3. crear ADR-001: afirmaciones como fuente de verdad;
4. crear ADR-002: desarrollo cronológico por campañas;
5. crear ADR-003: núcleo compartido + módulos de campaña;
6. crear registro de decisiones y migraciones;
7. definir convenciones de IDs;
8. elegir lenguaje para tooling inicial;
9. configurar validación, pruebas y CI;
10. definir licencia y política de fuentes;
11. crear el glosario inicial;
12. crear la matriz de preservación del plan hominino.

### Entregables

- repositorio;
- guía activa y archivo histórico;
- ADR-001 a ADR-003;
- estructura de carpetas;
- `README`;
- manifiesto de dataset vacío;
- primer snapshot;
- comando de validación ejecutable;
- registro de decisiones.

### Criterios de aceptación

- los hashes del archivo histórico coinciden con la versión preservada;
- ninguna decisión antigua desaparece;
- el repositorio puede clonarse y validarse;
- no existe dependencia del motor de juego;
- se puede crear una sección y una campaña vacías válidas.

## Fase 1. Dossier de la Campaña 1 y frontera de contenido

### Objetivo

Definir exactamente qué significa Eukaryota → Holozoa antes de cargar datos o programar mecánicas.

### Tareas

1. formular la pregunta central de campaña;
2. fijar inicio, final y capítulos;
3. seleccionar corredor principal;
4. seleccionar ramas hermanas inmediatas;
5. listar grupos externos representativos;
6. crear lista explícita de exclusiones;
7. identificar controversias obligatorias;
8. identificar el evento de endosimbiosis y sus requisitos;
9. seleccionar corpus científico inicial;
10. definir fecha de corte bibliográfico;
11. establecer criterios de aceptación científica;
12. definir presupuesto máximo de entidades, afirmaciones y vistas para el vertical slice;
13. crear `CAMP-000001` y su manifiesto.

### Entregables

- `docs/campaigns/C01-EUKARYA.md`;
- manifiesto de campaña;
- matriz de alcance;
- inventario de fuentes candidatas;
- backlog de diversidad diferida;
- lista de riesgos y cuestiones abiertas.

### Criterios de aceptación

- todo contenido está clasificado como obligatorio, contextual o diferido;
- no hay una exigencia implícita de cubrir todos los eucariotas;
- el final Holozoa está definido;
- el dossier distingue hechos, hipótesis y reconstrucciones;
- existe una explicación de cómo conecta con Campaña 2.

## Fase 2. Corpus, menciones, fuentes y estado reproducible

### Objetivo

Conservar fielmente la investigación incremental y demostrar cobertura exhaustiva.

### Tareas

1. implementar `Section`, `Passage`, `Mention`, `Source`, `Issue`;
2. conservar texto original y hash;
3. registrar localizadores;
4. implementar tabla de cobertura;
5. crear operaciones y deltas;
6. construir validadores de IDs, esquema y cobertura;
7. crear fixture artificial mínimo;
8. implementar snapshots y reconstrucción;
9. separar ingestión de auditoría externa.

### Entregables

- esquemas JSON;
- archivos JSONL;
- CLI de ingestión mínima;
- reporte de cobertura;
- snapshot reproducible.

### Criterios de aceptación

- toda mención del fixture tiene destino;
- una corrección conserva el original;
- el delta puede aplicarse y revertirse;
- el snapshot se reconstruye desde cero;
- ninguna herramienta añade conocimiento externo sin marcarlo.

## Fase 3. Identidad biológica y taxonómica mínima

### Objetivo

Representar nombres, conceptos, clados, linajes y poblaciones sin construir todavía todos los tipos futuros.

### Tareas

1. implementar `TaxonomicName`;
2. implementar `TaxonConcept`;
3. implementar `CladeConcept`;
4. implementar `Lineage`;
5. implementar `Population` con interfaz mínima y especialización por campaña;
6. implementar `Trait`;
7. modelar alias y nombres originales;
8. permitir rangos contextualizados;
9. registrar sinonimias propuestas;
10. implementar fusiones reversibles;
11. validar homónimos y duplicados;
12. crear fixture Eukaryota con dos conceptos o circunscripciones incompatibles;
13. mantener un fixture hominino futuro con dos usos de Hominini.

### Entregables

- esquemas de identidad;
- resolutor asistido;
- informe de duplicados;
- fixtures temprano y futuro.

### Criterios de aceptación

- nombre, concepto, clado y linaje no se confunden;
- un concepto puede cambiar de rango entre vistas;
- una fusión no destruye referencias;
- el modelo poblacional temprano no obliga a usar variables homininas;
- el fixture Hominini continúa siendo representable.

## Fase 4. Afirmaciones, evidencia, tiempo y análisis

### Objetivo

Convertir el corpus en conocimiento trazable y temporalmente explícito.

### Tareas

1. implementar `Claim`;
2. implementar dimensiones epistemológicas;
3. implementar `EvidenceItem`, `Dataset`, `Analysis`, `Result`;
4. vincular afirmaciones a pasajes;
5. almacenar soporte cuantitativo exacto;
6. modelar afirmaciones negativas y conflictos;
7. distinguir afirmaciones expresas de derivadas;
8. implementar tipos de fecha;
9. modelar intervalos e incertidumbre;
10. distinguir evidencia mínima, origen inferido y fecha de divergencia;
11. implementar ambientes o regiones abstractas;
12. crear consultas de procedencia.

### Entregables

- esquemas;
- validador de procedencia;
- informe “por qué aparece esta relación”;
- fixture con fuentes en conflicto;
- primera línea temporal.

### Criterios de aceptación

- toda relación visible puede explicarse;
- una fuente puede apoyar una afirmación y cuestionar otra;
- no existe confianza sin razón;
- observado e inferido no se confunden;
- una fecha profunda puede expresarse como intervalo y método.

## Fase 5. Eventos, reticulación, hipótesis y vistas

### Objetivo

Representar eucariogénesis, divergencias y alternativas como estructuras coherentes.

### Tareas

1. implementar eventos y roles;
2. implementar divergencia;
3. implementar asociación, simbiosis, transferencia e integración;
4. implementar extinción;
5. validar participantes y temporalidad;
6. implementar `Hypothesis`;
7. implementar grupos de conflicto;
8. implementar escenarios compatibles;
9. implementar `ClassificationView` y `PhylogeneticView`;
10. crear backbone fechado;
11. crear vista histórica o de fuente;
12. exportar Graphviz;
13. conservar fixture futuro de introgresión hominina.

### Entregables

- esquema de eventos;
- evento de endosimbiosis completo;
- dos vistas alternativas;
- reporte de diferencias;
- diagrama reproducible.

### Criterios de aceptación

- la endosimbiosis no se representa como padre-hijo simple;
- un evento admite varios participantes y roles;
- ninguna vista mezcla afirmaciones incompatibles;
- cada arista visible tiene procedencia;
- cambiar hipótesis reconstruye la vista sin modificar datos primarios.

## Fase 6. Pipeline de ingestión y validación end-to-end

### Objetivo

Procesar una sección real de principio a fin sin depender del chat como memoria.

### Tareas

1. comando `ingest:section`;
2. extracción asistida de menciones;
3. propuesta de normalización;
4. propuesta de afirmaciones;
5. revisión humana;
6. creación de eventos e hipótesis;
7. delta;
8. validación;
9. informe humano;
10. snapshot;
11. rollback;
12. reconstrucción de vistas afectadas.

### Entregables

- flujo end-to-end;
- interfaz de revisión mínima;
- logs;
- documentación;
- fixtures automatizados.

### Criterios de aceptación

- ninguna propuesta automática se acepta sin trazabilidad;
- las ambigüedades no centrales producen issues y no bloquean todo;
- los errores bloqueantes detienen el commit;
- el estado es reproducible;
- una vista puede reconstruirse desde cero.

## Fase 7. Dataset científico canónico de la Campaña 1

### Objetivo

Construir el conjunto de conocimiento real, acotado y auditado que alimentará el juego.

### Tareas

1. ingresar el corpus seleccionado;
2. normalizar entidades;
3. registrar afirmaciones y evidencia;
4. modelar el evento endosimbiótico;
5. construir el backbone;
6. construir al menos una alternativa;
7. registrar cuestiones abiertas;
8. auditar con fuentes externas cuando el modo lo permita;
9. congelar un snapshot de contenido;
10. generar un informe de cobertura del cono de foco.

### Criterios de aceptación

- el corredor Eukaryota → Holozoa no requiere hacks semánticos;
- la diversidad periférica omitida está documentada;
- todas las relaciones del backbone tienen explicación;
- el evento de integración es temporal y conceptualmente coherente;
- las controversias no se aplanan;
- el snapshot es estable para construir interfaz y juego.

## Fase 8. Atlas y red temporal como vertical slice

### Objetivo

Crear la primera interfaz útil y comprobar que la ciencia es navegable.

### Funciones mínimas

- búsqueda;
- ficha de entidad;
- línea temporal;
- vista de entorno abstracto;
- red filogenética y reticulada;
- selector de hipótesis;
- procedencia;
- historial de conceptos;
- filtros por evidencia y capítulo;
- zoom semántico;
- accesibilidad sin depender solo del color.

### Criterios de aceptación

- el usuario puede explicar por qué un nodo está en una posición;
- puede distinguir divergencia de endosimbiosis;
- puede cambiar de vista sin perder identidad;
- puede acceder a fuentes;
- la densidad es manejable en el alcance del primer lanzamiento.

## Fase 9. Núcleo de simulación de Eucaria

### Objetivo

Implementar un modelo pequeño de poblaciones celulares y asociaciones, no una simulación bioquímica total.

### Variables mínimas

- tamaño poblacional abstracto;
- recursos;
- energía;
- reproducción;
- estabilidad;
- variación abstracta;
- deriva;
- competencia;
- contacto;
- estado de asociación;
- costos y beneficios;
- persistencia/extinción.

### Tareas

1. definir paso temporal abstracto;
2. implementar actualización poblacional;
3. implementar variación y deriva;
4. implementar contacto;
5. implementar asociación y ruptura;
6. implementar conflicto y cooperación;
7. implementar integración como resultado emergente condicionado;
8. implementar divergencia;
9. registrar historia completa;
10. garantizar determinismo por semilla;
11. exportar eventos al grafo.

### Criterios de aceptación

- la misma semilla reproduce la historia;
- no existen tamaños o recursos inválidos;
- la integración no es un botón automático;
- varias estrategias pueden persistir;
- la campaña puede terminar sin una única historia obligatoria;
- los eventos producidos son compatibles con el Atlas.

## Fase 10. Prototipo jugable completo de la Campaña 1

### Objetivo

Unir contenido, simulación, capítulos y objetivos en una experiencia de principio a fin.

### Tareas

1. implementar capítulos;
2. diseñar tutorial;
3. definir objetivos y resultados alternativos;
4. integrar entorno, red y decisiones;
5. crear eventos narrativos científicos;
6. equilibrar costos y compensaciones;
7. implementar guardado;
8. registrar telemetría local de pruebas;
9. crear final y transición a animales.

### Criterios de aceptación

- existe una partida completa;
- el jugador comprende selección, deriva, simbiosis e integración sin menús enciclopédicos obligatorios;
- no hay árbol de mejoras teleológico;
- el final no afirma inevitabilidad;
- las decisiones tienen consecuencias visibles y trazables;
- el prototipo es comprensible sin conocer biología avanzada.

## Fase 11. Integración de la lente científica

### Objetivo

Conectar jugabilidad y conocimiento sin convertir el Atlas en decoración.

### Tareas

- desbloquear fichas desde eventos;
- comparar dos hipótesis;
- mostrar evidencia y procedencia;
- separar historia de partida y conocimiento científico real;
- registrar simplificaciones;
- permitir revisión de decisiones editoriales;
- construir tutorial de incertidumbre.

### Criterios de aceptación

- una mecánica nunca altera una afirmación científica;
- el jugador puede distinguir simulación, evidencia e hipótesis;
- las fuentes son accesibles sin interrumpir obligatoriamente el juego;
- el sistema admite “sin resolver”.

## Fase 12. Producción de contenido, arte, audio y experiencia de usuario

### Objetivo

Transformar el prototipo en un producto publicable.

### Tareas

- arte celular y ambiental;
- lenguaje visual de eventos;
- animaciones;
- audio;
- narrativa y textos;
- localización;
- accesibilidad;
- onboarding;
- rendimiento;
- balance;
- control de densidad científica;
- pruebas con usuarios.

### Criterios de aceptación

- la célula se representa de forma legible sin infantilizar la ciencia;
- la campaña tiene identidad emocional y narrativa;
- el Atlas no requiere leer paredes de texto para jugar;
- la interfaz funciona con teclado y alternativas visuales;
- el rendimiento cumple el objetivo elegido.

## Fase 13. Auditoría, preparación de lanzamiento y publicación

### Objetivo

Lanzar una campaña completa y científicamente defendible.

### Tareas

1. auditoría científica;
2. auditoría de procedencia;
3. auditoría de accesibilidad;
4. pruebas de regresión;
5. revisión de licencias;
6. documentación pública;
7. build reproducible;
8. política de actualizaciones científicas;
9. plan de soporte;
10. publicación.

### Criterios de aceptación

- no quedan errores científicos críticos conocidos;
- las simplificaciones están documentadas;
- el build es reproducible;
- el juego puede completarse;
- las fuentes y créditos son correctos;
- el producto funciona de manera autónoma, no como demostración técnica.

## Fase 14. Revisión post-lanzamiento y estabilización de plataforma

### Objetivo

Aprender del primer lanzamiento antes de ampliar la escala.

### Tareas

- analizar bugs y telemetría;
- revisar comprensión del jugador;
- evaluar deuda del esquema;
- registrar migraciones necesarias;
- clasificar mecánicas reutilizables;
- identificar acoplamientos indebidos a Eucaria;
- actualizar la guía y ADR;
- fijar criterios de inicio de Campaña 2.

### Criterios de aceptación

- existe postmortem;
- los cambios de esquema tienen migraciones;
- el núcleo común está separado del módulo Eucaria;
- el backlog de Campaña 2 tiene alcance controlado.

## Fase 15. Campaña 2: Animales

### Objetivo

Aplicar el mismo ciclo de dossier → datos → prototipo → lanzamiento, agregando solo los sistemas necesarios para multicelularidad, desarrollo y planes corporales.

### Regla

No se comienza por “todos los animales”. Se aplica nuevamente el cono de foco desde Holozoa hasta Bilateria.

## Fase 16. Campañas 3 a 6

Cada campaña repite un ciclo formal:

1. dossier;
2. alcance;
3. corpus;
4. migración de esquema si hace falta;
5. dataset;
6. Atlas;
7. módulo de simulación;
8. prototipo;
9. lente científica;
10. producción;
11. auditoría;
12. lanzamiento;
13. postmortem.

Los sistemas se incorporan cuando aparecen:

- anatomía y fósiles en Cordados;
- extinciones y fisiología en Sinápsidos;
- historia de vida y cuidado parental en Mamíferos;
- sociabilidad y aprendizaje en Primates.

## Fase 17. Campaña de Homininos y sistemas de máxima complejidad

### Objetivo

Implementar la campaña culminante utilizando el trabajo preservado.

### Capacidades que deben activarse o completarse

- especímenes;
- yacimientos;
- ocurrencias fósiles;
- paleogeografía;
- genética de poblaciones;
- migración;
- flujo génico e introgresión;
- taxonomías rivales;
- cultura y tecnologías;
- arqueología;
- tafonomía;
- evidencia generada;
- modo Reconstrucción completo.

### Piloto interno conservado

El período 400.000–40.000 años se utiliza como vertical slice interno antes de producir toda la campaña.

### Criterios de aceptación

- denisovanos pueden existir como linaje sin nombre taxonómico único;
- Hominini puede tener circunscripciones alternativas;
- Harbin u otro caso análogo admite asignaciones incompatibles;
- flujo génico y topología alternativa no se confunden;
- una partida puede producir evidencia parcial para Reconstrucción;
- todos los capítulos conservados tienen un destino.

## Fase 18. Sistemas transversales futuros

Se evalúan después de varias campañas:

- Modo Gran Linaje;
- transferencia de estado entre campañas;
- editor colaborativo;
- razonamiento automático avanzado;
- base de grafos o RDF;
- inferencia probabilística jugable;
- expansión exhaustiva del Atlas fuera del corredor principal.

## 24.1. Matriz de migración de la hoja de ruta `1.0.0`

| Fase anterior | Destino en `1.1.0` | Estado |
|---|---|---|
| Constitución | Fase 0 | Conservada y ampliada con archivado y ADR de campañas. |
| Corpus y menciones | Fase 2 | Conservada. |
| Identidad | Fase 3 | Conservada; implementación inicial reducida al caso actual. |
| Afirmaciones y evidencia | Fase 4 | Conservada. |
| Tiempo, geografía y ocurrencias | Fase 4 y campañas posteriores | Tiempo se implementa ahora; geografía/ocurrencias se especializan por escala. |
| Eventos y reticulación | Fase 5 | Conservada; endosimbiosis reemplaza introgresión como primer fixture real. |
| Hipótesis y vistas | Fase 5 | Conservada. |
| Pipeline completo | Fase 6 | Conservada. |
| Piloto hominino real | Fase 17 | Reubicado; sustituido por dataset Eucaria en Fase 7. |
| Atlas MVP | Fase 8 | Conservado e integrado al primer lanzamiento. |
| Reconstrucción MVP | Fase 11 en forma ligera y Fase 17 en forma completa | Reubicado, no eliminado. |
| Núcleo poblacional | Fase 9 | Conservado y adaptado a poblaciones celulares. |
| Tafonomía y evidencia | Fases 11 y 17 | Señales ligeras primero; tafonomía fósil después. |
| Evolución MVP | Fase 10 | Conservado como campaña Eucaria. |
| Integración de modos | Fase 11 y posteriores | Conservada de forma incremental. |
| Expansión científica | Fases 15–17 | Se invierte el orden: avanza cronológicamente hacia homininos. |

La versión original completa permanece archivada para consultar el detalle histórico de cada fase.

## 24.2. Paquetes avanzados preservados de la hoja de ruta original

Estos paquetes no pertenecen al primer lanzamiento, pero conservan el detalle operativo necesario para campañas posteriores. Deben activarse mediante las fases y disparadores indicados, no reconstruirse de memoria cuando llegue el momento.

### 24.2.1. Tiempo, geografía, sitios y ocurrencias avanzadas

#### Tareas preservadas

- implementar yacimientos;
- implementar regiones y paleorregiones;
- crear ocurrencias vinculadas con entidad, tiempo, lugar y fuente;
- validar coexistencia;
- advertir inversiones aparentes de rangos observados;
- gestionar unidades y conversiones;
- producir líneas temporales y mapas;
- separar localización observada, inferida y aproximada.

#### Criterios de aceptación

- observado e inferido no se confunden;
- una divergencia puede expresarse como intervalo;
- el sistema no rechaza automáticamente una relación por sesgo fósil;
- las ubicaciones inciertas están marcadas;
- la paleogeografía puede versionarse sin cambiar IDs biológicos.

### 24.2.2. Piloto científico hominino preservado

#### Alcance

*Sapiens*, neandertales, denisovanos y humanos asiáticos del Pleistoceno medio y tardío.

#### Tareas

- seleccionar corpus;
- ingresar fuentes y secciones;
- modelar conceptos taxonómicos;
- modelar poblaciones y especímenes;
- registrar eventos de flujo génico;
- construir al menos tres vistas;
- auditar el resultado;
- documentar fallas del esquema.

#### Criterios de aceptación

- denisovanos pueden existir como linaje y coexistir con varios nombres propuestos;
- Harbin u otro caso análogo admite asignaciones alternativas;
- consenso y alternativas son comprensibles;
- la procedencia permite revisión científica;
- el caso no requiere hacks semánticos.

### 24.2.3. Modo Reconstrucción completo

#### Funciones mínimas preservadas

- historia oculta predefinida o simulada;
- conjunto limitado de especímenes;
- presupuesto o turnos;
- selección de análisis;
- construcción de dos o más hipótesis;
- publicación;
- evaluación de ajuste e incertidumbre;
- aparición de nueva evidencia;
- revisión.

#### Criterios de aceptación

- “sin resolver” es un resultado válido;
- no existe una única acción óptima basada en desbloquear tecnología;
- la puntuación separa acierto, evidencia y calibración;
- el escenario es rejugable mediante evidencia parcial.

### 24.2.4. Núcleo poblacional avanzado

#### Variables mínimas preservadas

- tamaño efectivo;
- ubicación;
- movilidad;
- conectividad;
- recursos abstractos;
- diversidad genética abstracta;
- contacto;
- flujo génico;
- persistencia y extinción.

#### Tareas

- modelo temporal por campaña;
- actualización demográfica;
- división;
- migración;
- contacto;
- introgresión;
- cuellos de botella;
- registro de historia completa;
- determinismo por semilla;
- exportación al grafo científico.

#### Criterios de aceptación

- la misma semilla reproduce la historia;
- no aparecen ciclos temporales;
- la especiación no es un botón;
- el modelo produce historias distintas sin violar invariantes;
- los eventos pueden convertirse en evidencia parcial.

### 24.2.5. Tafonomía y producción de evidencia

#### Tareas preservadas

- probabilidad de preservación;
- sesgo por tejido y ambiente;
- destrucción;
- descubrimiento;
- contaminación;
- datación imperfecta;
- muestreo geográfico;
- generación de especímenes y ocurrencias;
- vinculación con historia oculta.

#### Criterios de aceptación

- el registro observable es incompleto y sesgado;
- una historia puede producir varias interpretaciones plausibles;
- el jugador no accede directamente a la verdad simulada;
- los errores y ausencias de evidencia son distinguibles de ausencia biológica.

### 24.2.6. Modo Evolución avanzado

#### Alcance mínimo preservado

- una región o conjunto de regiones;
- varias poblaciones;
- clima abstracto o reconstruido;
- movilidad;
- recursos;
- contacto;
- cultura abstracta cuando corresponda;
- reproducción;
- divergencia;
- mezcla;
- extinción;
- objetivos alternativos.

#### Criterios de aceptación

- no existe árbol de mejoras teleológico;
- toda ventaja tiene costos o contexto;
- múltiples estrategias pueden persistir;
- el jugador influye, no diseña genomas;
- el resultado se registra como historia compatible con el Atlas.

### 24.2.7. Integración completa de modos

#### Objetivo preservado

Usar una partida de Evolución como historia oculta para Reconstrucción y Atlas.

#### Criterios de aceptación

- la historia simulada produce un corpus de evidencia;
- Reconstrucción puede analizarlo;
- Atlas muestra verdad simulada, evidencia e interpretación en capas separadas;
- las proyecciones no contaminan el núcleo científico real;
- una actualización del conocimiento real no altera retrospectivamente la historia simulada sin migración.

# 25. Trabajo pospuesto

Esta sección es parte del plan. Nada de lo siguiente debe desaparecer del proyecto solo porque no entra en el primer lanzamiento.

## 25.1. Granularidad molecular fina

**POSPUESTO:**

- genes individuales;
- alelos;
- haplotipos;
- regiones cromosómicas;
- genomas ancestrales detallados;
- proteínas individuales como sistemas completos;
- virus endógenos específicos;
- transferencia bacteriana concreta;
- duplicaciones génicas detalladas;
- conflictos entre árboles génicos;
- redes metabólicas bioquímicas completas.

### Lo que sí entra en Eucaria

- transferencia genética como evento abstracto cuando sea necesaria;
- integración heredable;
- costos y beneficios funcionales agregados;
- evidencia molecular como categoría y afirmaciones trazables.

### Motivo

La granularidad fina requiere coordenadas, ensamblajes, versiones de referencia, modelos de herencia y validaciones propios.

### Disparador

Retomar cuando una mecánica o afirmación científica no pueda representarse responsablemente mediante abstracción agregada y exista un corpus acotado para validarla.

## 25.2. Cultura detallada

**POSPUESTO:**

- tradiciones;
- tecnologías como linajes culturales;
- transmisión vertical, horizontal y oblicua;
- aprendizaje entre poblaciones;
- redes simbólicas;
- lenguaje;
- sustitución tecnológica detallada.

### Motivo

La cultura necesita identidad, eventos, herencia y relación con poblaciones. Modelarla como atributo simple sería insuficiente.

### Disparador

Retomar durante Primates o Homininos, cuando `Population`, `Event`, tiempo y aprendizaje ya hayan sido probados.

## 25.3. Ecosistemas y paleogeografía dinámica completos

**POSPUESTO:**

- biomas de alta resolución;
- redes tróficas completas;
- paleocostas;
- tectónica;
- cambios de ríos;
- reconstrucción climática espacial continua;
- simulación planetaria;
- todas las especies ecológicas externas.

### Lo que sí entra temprano

Cada campaña puede usar un ambiente abstracto suficiente para sus mecánicas. Eucaria necesita recursos, oxígeno, temperatura y estabilidad; no un planeta entero.

### Disparador

Retomar módulos concretos cuando una campaña necesite corredores, islas, recursos o interacción ecológica no representables mediante ambientes abstractos.

## 25.4. Historia completa de la vida y diversidad periférica

**POSPUESTO como carga exhaustiva de datos, no como capacidad del esquema.**

El desarrollo por campañas incorpora el corredor principal en orden. No obliga a cargar cada taxón conocido de cada rama hermana.

### Disparador

Ampliar una rama periférica cuando exista:

- objetivo científico;
- corpus;
- uso en Atlas o campaña;
- responsable de revisión;
- prueba de visualización;
- presupuesto de mantenimiento.

## 25.5. Exhaustividad preventiva de todos los rangos

**POSPUESTO:** registrar cualquier rango que aparezca, pero no poblar preventivamente cada infraorden, parvorden, cohorte, magnorden, tribu o subtribu del árbol de la vida.

### Disparador

Una fuente, vista o campaña requiere ese rango. La campaña de Primates será el primer gran caso de prueba para tribus, subtribus y subgéneros.

## 25.5.1. Sexo y meiosis en la Campaña 1

**Ya no está pospuesto.** El origen del sexo y de la meiosis entra en la Campaña 1 como contenido del Atlas **y** como mecánica del bucle, por decisión del 8 de agosto de 2026 (`ISSUE-000026`).

Había desaparecido de la `1.1.0` sin figurar entre las exclusiones declaradas ni entre el trabajo pospuesto con disparador, que es lo que §1.1 exige. La omisión no era una decisión: era un hueco.

**Entra:** recombinación, alternancia de ploidía, tipos de apareamiento, y el costo del sexo frente a la reproducción clonal. **No entra:** genética de poblaciones a nivel de locus, que sigue pospuesta en §25.1.

Consecuencia declarada, como exige §0.1: amplía el alcance de la primera campaña frente al riesgo §29.1, y añade variables al módulo de simulación que §21.5 no listaba. Se acepta porque LECA era sexual y omitirlo dejaría un hueco visible en el Atlas justo en el corredor que la campaña recorre.

## 25.6. Compatibilidad automática completa

**POSPUESTO:** razonador que determine compatibilidad lógica entre todas las hipótesis.

### Motivo

La compatibilidad depende de identidad, definición, tiempo, taxonomía y supuestos no siempre formalizados.

### Disparador

Cuando los grupos de conflicto manuales ya no escalen y existan fixtures suficientes para especificar reglas.

## 25.7. Inferencia probabilística jugable

**POSPUESTO:** probabilidades bayesianas internas para hipótesis del jugador o del sistema.

### Motivo

No deben confundirse con soporte publicado ni inventarse priors arbitrarios.

### Disparador

El modo Reconstrucción completo requiere un modelo explícito, validado y separado de la aceptación científica real.

## 25.8. Base de grafos, RDF y ontologías externas

**POSPUESTO:** adoptar Neo4j, RDF/OWL u otra infraestructura especializada.

### Motivo

Primero debe estabilizarse la semántica y probarse con campañas reales.

### Disparador

Necesidades demostradas de consulta, interoperabilidad, razonamiento o edición concurrente.

## 25.9. Editor colaborativo

**POSPUESTO:** interfaz multiusuario con permisos, revisión, comentarios y conflictos.

### Disparador

El proyecto deja de ser individual o la ingestión por Git se vuelve un cuello de botella.

## 25.10. Modo Reconstrucción completo

**POSPUESTO, pero RETENIDO como modo principal futuro.**

La Campaña 1 implementa una lente científica ligera. Excavaciones, especímenes, selección de análisis, publicación y revisión jugable se activarán cuando exista un dominio con evidencia adecuada.

### Disparador

Al menos una campaña con especímenes u observaciones discretas, un módulo de historia oculta y un sistema de evidencia parcial estable. El vertical slice hominino 400.000–40.000 años continúa siendo el candidato principal.

## 25.11. Tafonomía, especímenes y yacimientos completos

**POSPUESTO para la Campaña 1.**

Los tipos pueden existir en el esquema o como interfaces futuras, pero no necesitan implementación productiva hasta campañas con registro fósil relevante.

### Disparador

Cordados, Sinápsidos o una campaña posterior necesitan transformar historia simulada en fósiles y ocurrencias.

## 25.12. Modo Gran Linaje

**POSPUESTO:** una única partida conectada desde Eukaryota hasta *Homo sapiens*.

### Motivo

Las escalas temporales, unidades y mecánicas cambian demasiado. Forzar continuidad temprana produciría una simulación universal superficial.

### Disparador

Al menos tres campañas lanzadas, módulos estabilizados y una especificación explícita de qué estado puede transferirse entre escalas.

## 25.13. Transferencia literal de estado entre campañas

**POSPUESTO:** heredar automáticamente rasgos, poblaciones y resultados completos de una campaña a la siguiente.

### Primera etapa

Solo se transfieren:

- progreso del jugador;
- desbloqueos del Atlas;
- historial narrativo;
- configuraciones;
- logros o marcas de campaña.

### Disparador

El Modo Gran Linaje define un contrato de interoperabilidad entre módulos.

## 25.14. Diversidad eucariota exhaustiva

**POSPUESTO:** incorporar todos los supergrupos, filos, clases y taxones eucariotas en la Campaña 1.

### Motivo

Contradice el cono de foco y bloquearía el lanzamiento.

### Disparador

Expansiones del Atlas o campañas laterales con propósito propio.

## 25.15. Campañas laterales fuera del corredor humano

**POSPUESTO, no rechazado:** campañas centradas en hongos, plantas, artrópodos, dinosaurios, cetáceos u otros linajes.

### Disparador

La plataforma ha demostrado que puede soportar campañas laterales sin desviar el corredor principal ni comprometer mantenimiento.

## 25.16. Todos los sistemas homininos en el núcleo inicial

**POSPUESTO como implementación, RETENIDO como especificación.**

No se implementarán ahora cultura, arqueología, paleogenómica, taxonomía de especímenes y geografía humana detallada. Se mantienen como requisitos futuros y fixtures de regresión.

### Disparador

La hoja de ruta alcance Primates/Homininos o una decisión arquitectónica necesite probar anticipadamente un caso concreto.

# 26. Decisiones todavía abiertas

Las siguientes decisiones no deben resolverse prematuramente. Cada una debe producir un ADR cuando llegue su fase.

| ID | Decisión | Momento adecuado |
|---|---|---|
| `OPEN-001` | Lenguaje principal de tooling | ~~Fase 0~~ · **RESUELTA** por `DEC-051` |
| `OPEN-002` | Formato definitivo de IDs opacos | ~~Fase 0~~ · **RESUELTA** por `DEC-052` |
| `OPEN-003` | Estilo bibliográfico y resolución de DOI | Fases 1–4 |
| `OPEN-004` | Representación de topologías: Newick, listas de clados o ambas | Fase 5 |
| `OPEN-005` | Framework del Atlas | Fase 8 |
| `OPEN-006` | Motor de juego | Antes de Fase 9 |
| `OPEN-007` | Base de datos de producción | Después de Fase 7 o cuando haya métricas reales |
| `OPEN-008` | Semántica exacta del ancho de bandas | Fase 8 y campañas poblacionales posteriores |
| `OPEN-009` | Modelo de puntuación del modo Reconstrucción completo | Fase 17 |
| `OPEN-010` | Modelo poblacional y paso temporal de Eucaria | Fase 9 |
| `OPEN-011` | Criterio de divergencia o especiación emergente por campaña | Fases 9–10 y posteriores |
| `OPEN-012` | Nivel de determinismo y aleatoriedad | Fase 9 |
| `OPEN-013` | Condiciones exactas de éxito de Eucaria | Fase 10 |
| `OPEN-014` | Nombre definitivo del juego y de Campaña 1 | Después del prototipo jugable |
| `OPEN-015` | Licencia de datos, código y contenido | ~~Fases 0–1~~ · **RESUELTA** por `DEC-053` |
| `OPEN-016` | Fecha de corte y corpus científico exacto de Eucaria | Fase 1 |
| `OPEN-017` | Representación visual de célula, ambiente e integración | Fases 8–12 |
| `OPEN-018` | Alcance exacto de Filozoa/Choanozoa dentro del cierre Holozoa | Fases 1 y 7 |
| `OPEN-019` | Qué señales científicas usa la lente de la Campaña 1 | Fases 7–11 |
| `OPEN-020` | Política de actualización del juego ante cambios científicos | Fase 13 |
| `OPEN-021` | Contrato futuro de continuidad entre campañas | Después de tres campañas |
| `OPEN-022` | Si Homininos será una campaña o dos productos | Antes de Fase 17 |
| `OPEN-023` | Qué campaña introduce por primera vez tafonomía completa | Tras definir Cordados |
| `OPEN-024` | Audiencia y nivel de abstracción educativa | Fases 1, 10 y pruebas de usuario |

## 26.1. Criterio general

Una decisión se toma cuando:

- existen dos o más alternativas reales;
- se conocen requisitos;
- puede evaluarse con un prototipo, corpus o benchmark;
- su costo de cambio comienza a crecer;
- la campaña actual realmente la necesita.

No se decide por entusiasmo tecnológico ni para anticipar veinte campañas hipotéticas.

## 26.2. Restricción de decisiones tempranas

Una decisión de Eucaria puede especializar un módulo, pero no debe convertir su necesidad local en una regla universal. Por ejemplo:

- el paso temporal celular no define el paso temporal hominino;
- el ambiente abstracto no elimina la geografía futura;
- la ausencia de especímenes en Campaña 1 no elimina `Specimen` del modelo conceptual;
- la señal molecular temprana no sustituye fósiles o arqueología en campañas posteriores.

# 27. Estrategia de pruebas

## 27.1. Pruebas de esquema

- registros válidos;
- registros inválidos;
- migraciones;
- compatibilidad entre versiones;
- enumeraciones;
- campos obligatorios;
- tipos futuros opcionales sin campos nulos obligatorios;
- manifiestos de campaña.

## 27.2. Pruebas de identidad

- homónimos;
- sinónimos confirmados;
- sinonimias disputadas;
- cambios de nombre;
- cambios de rango;
- conceptos con el mismo nombre y contenido distinto;
- fusiones y deshacer fusiones;
- linajes estructurales sin nombres inventados.

## 27.3. Pruebas de procedencia

- toda afirmación llega a un pasaje;
- toda evidencia llega a una fuente;
- toda vista explica qué afirmaciones utiliza;
- registros externos están marcados como auditoría;
- cada simplificación jugable tiene justificación.

## 27.4. Pruebas temporales

- intervalos solapados;
- intervalos incompatibles;
- rangos observados frente a inferidos;
- eventos imposibles;
- ciclos de ascendencia;
- conversiones de unidades;
- coexistencia de participantes en una asociación;
- límites de campaña.

## 27.5. Pruebas de hipótesis

- escenarios compatibles;
- afirmaciones mutuamente excluyentes;
- topologías alternativas;
- invalidación de vistas;
- reconstrucción determinista;
- backbone fechado;
- una vista no mezcla endosimbiosis con divergencia.

## 27.6. Pruebas de visualización

- snapshots de Graphviz;
- leyendas;
- filtros;
- densidad;
- accesibilidad;
- equivalencia entre vista y afirmaciones seleccionadas;
- zoom semántico;
- legibilidad de eventos reticulados;
- representación sin depender del color.

## 27.7. Pruebas de simulación de Eucaria

- determinismo por semilla;
- conservación de invariantes;
- poblaciones y recursos no negativos;
- reproducción válida;
- deriva;
- contacto temporalmente válido;
- asociación y ruptura;
- integración condicionada;
- extinción terminal;
- múltiples trayectorias;
- **distribución razonable de resultados**: no basta con que existan dos desenlaces distintos; hay que mirar la forma de la distribución, que es donde se detectaría una simulación teleológica (`ISSUE-000027`);
- ausencia de teleología;
- exportación correcta de eventos al grafo.

### 27.7.1. Especificación de la prueba de ausencia de teleología

`ISSUE-000011`. Es la contrapartida ejecutable del riesgo §29.15 y el único que ninguna regla textual puede evitar: la teleología puede colarse por la **dinámica** aunque el vocabulario la prohíba. Una prueba que no se define no se ejecuta, así que se define aquí.

**Diseño.** Se ejecutan N partidas con condiciones iniciales equivalentes y semillas distintas, y se examina la **distribución** de los desenlaces, no su existencia.

**Comprobaciones:**

1. **Ningún desenlace domina por construcción.** La integración endosimbiótica no ocurre en una fracción cercana a 1 de las partidas. Si sale en el 97 % de los casos, no es contingente: es guionizado con ruido.
2. **La extinción es un desenlace real y alcanzable**, con frecuencia no despreciable. §21.9 la admite como resultado científicamente significativo; si nunca ocurre, la simulación tiene un suelo que la protege.
3. **Persistir sin integrarse es viable.** Debe existir una fracción de partidas que llegan al final con poblaciones estables y sin haber completado la integración.
4. **Ninguna variable crece monótonamente con el tiempo por construcción.** Complejidad, tamaño y número de rasgos deben poder bajar. Una magnitud que sólo sube es una escalera con otro nombre.
5. **La ventaja de un rasgo depende del ambiente.** El mismo rasgo debe resultar favorable en unas condiciones y costoso en otras. Si un rasgo es siempre bueno, es una mejora comprable disfrazada (§23.2).
6. **Sensibilidad a la semilla, no al guion.** Dos semillas con el mismo ambiente deben poder producir desenlaces cualitativamente distintos.

**Criterio de fallo.** Cualquier comprobación que no se cumpla es `ERROR` y bloquea el lanzamiento, no advertencia. Los umbrales concretos se fijan en la Fase 9 junto con `OPEN-012`, que decide el nivel de determinismo y aleatoriedad: no pueden fijarse antes porque dependen del modelo poblacional.

**Lo que esta prueba NO comprueba.** Que el contenido sea científicamente correcto. Comprueba que la dinámica no impone un destino. Un sistema puede pasar las seis y seguir contando algo falso; para eso está la revisión humana de §27.12.

## 27.8. Pruebas de campaña

- inicio, capítulos y final alcanzables;
- tutorial;
- guardado y carga;
- objetivos alternativos;
- desbloqueos del Atlas;
- continuidad narrativa;
- contenido obligatorio completo;
- diversidad diferida explícita;
- ninguna dependencia accidental de contenido hominino;
- campaña jugable sin consultar el Atlas de forma obligatoria.

## 27.9. Fixtures de referencia

Mantener conjuntos pequeños y comprensibles:

1. `eukarya-minimal`: corredor y ramas hermanas;
2. `endosymbiosis-event`: evento n-ario con roles;
3. `two-deep-topologies`: dos hipótesis incompatibles;
4. `observed-vs-inferred-time`: primera evidencia frente a origen;
5. `historical-classification`: hipótesis superada;
6. `game-projection-eukarya`: simplificación jugable;
7. `future-hominini-homonym`: dos conceptos llamados Hominini;
8. `future-denisovan-lineage`: linaje sin nombre taxonómico único;
9. `future-introgression`: evento poblacional de flujo génico;
10. `future-specimen-assignment`: fósil con varias asignaciones.

Los fixtures `future-*` no son contenido de Campaña 1. Son pruebas de que la arquitectura conserva el trabajo posterior.

## 27.10. Pruebas de separación entre núcleo y campaña

- eliminar el módulo Eucaria no elimina datos científicos;
- el núcleo no importa clases específicas de la simulación celular;
- una nueva campaña puede declarar variables distintas;
- los IDs científicos sobreviven a cambios de mecánicas;
- un cambio de balance no modifica afirmaciones;
- una actualización científica no reescribe partidas guardadas sin migración.

## 27.11. Pruebas de preservación

- el archivo `1.0.0` conserva su hash;
- **toda decisión cuyo enunciado difiera del de la versión archivada está registrada**, comparando el registro contra el archivo y no contra una lista de identificadores: si cambia su contenido o su alcance, marcada `SUPERSEDIDO` y enlazando su reemplazo; si es reformulación editorial sin cambio de compromiso, anotada en la matriz de preservación con su texto anterior;
- ninguna decisión invierte su contenido conservando identificador y estado;
- capítulos homininos continúan presentes;
- apéndices A–D no pierden contenido;
- cada sistema reubicado tiene una fase o disparador;
- el diff de la guía se revisa antes de aceptar una migración.

## 27.12. Revisión científica humana

La validación automática no determina si una interpretación es correcta. Debe existir revisión humana para:

- identidad dudosa;
- traducción de conceptos;
- calidad de evidencia;
- clasificación de aceptación;
- selección del backbone;
- simplificación jugable;
- selección del cono de foco;
- actualización de controversias.

# 28. Definiciones de terminado

## 28.1. Sección terminada

Una sección está terminada cuando:

- el original está preservado;
- tiene ID y hash;
- las menciones fueron extraídas;
- la cobertura es completa;
- las entidades están resueltas o marcadas;
- las afirmaciones son atómicas;
- la procedencia está vinculada;
- los eventos fueron creados cuando correspondía;
- las hipótesis fueron actualizadas;
- las vistas afectadas están reconstruidas o invalidadas;
- las validaciones pasan;
- existe delta;
- existe informe humano;
- el estado puede reconstruirse sin el chat.

## 28.2. Entidad terminada

Una entidad no necesita estar científicamente “resuelta”. Está correctamente registrada cuando:

- posee identidad estable;
- tiene tipo correcto;
- conserva etiquetas y alias;
- tiene procedencia;
- explicita conflictos;
- no contiene afirmaciones presentadas como atributos incontrovertibles;
- sus cuestiones pendientes están vinculadas.

## 28.3. Vista terminada

- tiene criterios;
- fecha;
- versión;
- hipótesis;
- afirmaciones;
- fuentes;
- exclusiones;
- validación;
- exportación reproducible;
- alcance de campaña o escala declarado.

## 28.4. Mecánica terminada

- tiene objetivo;
- entradas;
- estado;
- reglas;
- salidas;
- costos y compensaciones;
- límites científicos;
- pruebas;
- telemetría de prototipo;
- justificación de simplificaciones;
- no modifica el núcleo científico.

## 28.5. Dossier de campaña terminado

- define pregunta central;
- fija inicio y final;
- enumera corredor principal;
- enumera ramas hermanas;
- define grupos externos;
- contiene exclusiones;
- identifica controversias;
- identifica sistemas nuevos;
- define presupuesto de contenido;
- establece criterios de aceptación;
- declara continuidad con campañas vecinas.

## 28.6. Dataset de campaña terminado

- cubre todo el alcance obligatorio;
- registra contenido contextual y diferido;
- todas las relaciones tienen procedencia;
- las alternativas son coherentes;
- los issues están clasificados;
- existe snapshot congelado;
- pasa auditoría científica;
- puede alimentar vistas sin hacks.

## 28.7. Campaña lista para lanzamiento

- puede completarse de principio a fin;
- tiene tutorial y final;
- no depende de contenido pospuesto;
- Atlas y lente científica funcionan;
- guardado y carga funcionan;
- accesibilidad mínima validada;
- fuentes y licencias son correctas;
- no quedan errores críticos;
- las simplificaciones están documentadas;
- existe plan de actualización;
- funciona como producto completo.

## 28.8. Migración estratégica terminada

- la versión anterior está archivada;
- su hash está registrado;
- las decisiones supersedidas tienen reemplazo;
- todo trabajo reubicado tiene destino;
- los apéndices científicos permanecen;
- la nueva hoja de ruta puede ejecutarse sin depender de memoria conversacional.

# 29. Riesgos y mitigaciones

## 29.1. Expansión ilimitada del alcance

**Riesgo:** interpretar “Eukaryota” como obligación de representar todos los eucariotas antes del lanzamiento.

**Mitigación:** cono de foco, presupuesto de contenido, lista de exclusiones y backlog de diversidad diferida.

## 29.2. Sobreingeniería ontológica

**Riesgo:** pasar años diseñando categorías futuras sin campaña jugable.

**Mitigación:** esquema mínimo por fase, fixtures concretos y prohibición de implementar tipos sin caso de uso o prueba de compatibilidad.

## 29.3. Motor universal prematuro

**Riesgo:** construir una simulación genérica para células, animales y humanos que no represente bien ninguna escala.

**Mitigación:** núcleo compartido pequeño, módulos por campaña e interfaces explícitas.

## 29.4. Mezcla de taxonomía y biología

**Riesgo:** cambios de nombre alteran la historia representada.

**Mitigación:** nombre, concepto, clado, linaje y población separados.

## 29.5. Falsa precisión

**Riesgo:** números de confianza o fechas aparentan más certeza de la disponible.

**Mitigación:** soporte cuantitativo solo desde fuentes, intervalos, categorías cualitativas justificadas y separación observado/inferido.

## 29.6. Alucinación durante ingestión asistida

**Riesgo:** una herramienta agrega taxones, citas o relaciones ausentes.

**Mitigación:** corpus inmutable, pasajes, propuestas revisables, cobertura, procedencia obligatoria y auditoría separada.

## 29.7. Duplicación o fusión excesiva

**Riesgo:** alias, grafías o taxonomías alternativas crean nodos falsos o eliminan diferencias reales.

**Mitigación:** libro de menciones, resolución conservadora, conceptos taxonómicos y fusiones reversibles.

## 29.8. Visualización ilegible

**Riesgo:** la red se vuelve incomprensible incluso en una campaña pequeña.

**Mitigación:** vistas por escala, filtros, zoom semántico, capas, cono de foco y visualizaciones locales.

## 29.9. Acoplamiento con Eucaria

**Riesgo:** el núcleo compartido incorpora supuestos celulares que bloquean campañas posteriores.

**Mitigación:** contratos de módulo, pruebas `future-*`, revisión post-lanzamiento y separación de variables por campaña.

## 29.10. Pérdida del trabajo hominino

**Riesgo:** el nuevo orden se interpreta como descarte de escenarios, inventarios y requisitos anteriores.

**Mitigación:** archivo `1.0.0`, Apéndice J, decisiones supersedidas, fixtures futuros y Fase 17 explícita.

## 29.11. Abstracción visual y baja conexión emocional

**Riesgo:** células y procesos profundos resultan menos intuitivos que animales o humanos.

**Mitigación:** continuidad de linaje, crisis, asociaciones, transformaciones visibles, narrativa de dependencia y conflicto, diseño audiovisual y pruebas de usuario.

## 29.12. Antropomorfización engañosa

**Riesgo:** representar asociaciones celulares como decisiones conscientes humanas.

**Mitigación:** lenguaje de sistemas, probabilidades y presiones; metáforas visuales claramente marcadas; revisión científica del guion.

## 29.13. Evidencia profunda demasiado indirecta

**Riesgo:** el jugador confunde reconstrucción molecular con observación directa.

**Mitigación:** lente científica, capas de evidencia, etiquetas de inferencia y comparación de hipótesis.

## 29.14. Primera campaña convertida en tutorial incompleto

**Riesgo:** Eucaria existe solo para preparar campañas futuras y carece de arco propio.

**Mitigación:** criterios de lanzamiento, capítulos, objetivos alternativos, final y rejugabilidad real.

## 29.15. Simulación teleológica

**Riesgo:** el sistema favorece inevitablemente integración, multicelularidad, cerebros grandes o *Homo sapiens*.

**Mitigación:** costos, resultados alternativos, contingencia, extinciones válidas y ausencia de progreso universal.

## 29.16. Dependencia del chat

**Riesgo:** pérdida de decisiones y estado acumulado.

**Mitigación:** archivos, Git, deltas, snapshots, ADR y guía versionada.

## 29.17. Actualizaciones científicas rompen partidas

**Riesgo:** un cambio taxonómico o filogenético invalida contenido guardado.

**Mitigación:** separar IDs de nombres, versionar vistas y contenido, migrar partidas y conservar la vista científica usada por cada partida.

# 30. Registro consolidado de decisiones

| ID | Estado | Decisión |
|---|---|---|
| `DEC-001` | DECIDIDO | Construir grafo de conocimiento multicapa, no árbol único. |
| `DEC-002` | DECIDIDO | Afirmaciones como unidad epistemológica central. |
| `DEC-003` | DECIDIDO | Las vistas filogenéticas se derivan de hipótesis compatibles. |
| `DEC-004` | DECIDIDO | Separar nombre, concepto taxonómico, clado, linaje y población. |
| `DEC-005` | DECIDIDO | Modelar procesos complejos como eventos. |
| `DEC-006` | DECIDIDO | Separar aceptación, evidencia, resolución, vigencia y estado. |
| `DEC-007` | DECIDIDO | Diferenciar tipos temporales y observado/inferido. |
| `DEC-008` | DECIDIDO | Conservar toda mención, pero no promover toda mención a nodo. |
| `DEC-009` | DECIDIDO | Mantener corpus inmutable y procedencia localizable. |
| `DEC-010` | DECIDIDO | Usar JSON/JSONL modular y Git en la primera etapa. |
| `DEC-011` | DECIDIDO | Mantener deltas, migraciones y snapshots. |
| `DEC-012` | DECIDIDO | La conversación no es fuente de verdad. |
| `DEC-013` | DECIDIDO | Separar ingestión de auditoría externa. |
| `DEC-014` | DECIDIDO | Separar núcleo científico y proyección de juego. |
| `DEC-015` | DECIDIDO | La población es la unidad principal de simulación, especializada por campaña. |
| `DEC-016` | SUPERSEDIDO | Atlas antes que simulación completa. Reemplazado por `DEC-049`. |
| `DEC-017` | SUPERSEDIDO | Reconstrucción como primer modo jugable. Reemplazado por `DEC-050`. |
| `DEC-018` | SUPERSEDIDO | Usar 400.000–40.000 años como primer recorte vertical. Reemplazado por `DEC-034`; contenido preservado por `DEC-035`. |
| `DEC-019` | RETENIDO | Tres vistas sincronizadas: entorno, red y ciencia. |
| `DEC-020` | RETENIDO | Historia oculta → registro parcial → hipótesis del jugador. |
| `DEC-021` | RETENIDO | Bandas poblacionales en la visualización temporal cuando la escala lo permita. |
| `DEC-022` | RECHAZADO | Un único estado epistemológico. |
| `DEC-023` | RECHAZADO | JSON monolítico. |
| `DEC-024` | RECHAZADO | Relaciones reticuladas como flechas binarias sin evento. |
| `DEC-025` | RECHAZADO | Mutaciones u orgánulos comprables y progreso lineal. |
| `DEC-026` | RECHAZADO | *Homo sapiens* como victoria obligatoria. |
| `DEC-027` | POSPUESTO | Base de grafos o RDF. |
| `DEC-028` | POSPUESTO | Genes, alelos y transferencia molecular fina. |
| `DEC-029` | POSPUESTO | Cultura y lenguaje detallados. |
| `DEC-030` | POSPUESTO | Paleogeografía y ecosistemas completos. |
| `DEC-031` | POSPUESTO | Compatibilidad lógica automática exhaustiva. |
| `DEC-032` | SUPERSEDIDO | Posponer campañas anteriores hasta validar homininos. Reemplazado por `DEC-033` y `DEC-034`. |
| `DEC-033` | DECIDIDO | Desarrollar y publicar campañas en orden cronológico general desde Eukaryota hacia homininos. |
| `DEC-034` | DECIDIDO | La primera campaña y primer lanzamiento cubren Eukaryota → Holozoa. |
| `DEC-035` | DECIDIDO | Conservar el trabajo hominino como especificación futura, prueba de estrés y campaña culminante. |
| `DEC-036` | DECIDIDO | Aplicar cono de foco: corredor principal, hermanas inmediatas, externos representativos y diversidad diferida. |
| `DEC-037` | DECIDIDO | Usar núcleo compartido y módulos de simulación por campaña. |
| `DEC-038` | DECIDIDO | La continuidad inicial entre campañas es narrativa, enciclopédica y mediante desbloqueos. |
| `DEC-039` | POSPUESTO | Modo Gran Linaje con una partida continua entre escalas. |
| `DEC-040` | DECIDIDO | La primera campaña usa lente científica ligera; Reconstrucción completa se implementa después. |
| `DEC-041` | DECIDIDO | La Campaña 1 termina en Holozoa y prepara la transición a animales. |
| `DEC-042` | DECIDIDO | La diversidad eucariota exhaustiva no es requisito del primer lanzamiento. |
| `DEC-043` | DECIDIDO | El primer lanzamiento debe ser una campaña completa, no un prólogo técnico. |
| `DEC-044` | DECIDIDO | Eucariogénesis y endosimbiosis serán el primer caso real de reticulación. |
| `DEC-045` | DECIDIDO | Implementar solo tipos y comportamientos necesarios ahora, manteniendo fixtures de compatibilidad futura. |
| `DEC-046` | DECIDIDO | Archivar versiones rectoras y migrar estrategias de forma no destructiva. |
| `DEC-047` | POSPUESTO | Transferencia literal de estado biológico entre campañas. |
| `DEC-048` | RETENIDO | Campaña hominina con seis capítulos; puede dividirse en dos productos si el volumen lo exige. |
| `DEC-049` | DECIDIDO | El Atlas es la primera superficie compartida, integrada desde el primer lanzamiento. Reemplaza a `DEC-016`. |
| `DEC-050` | RETENIDO | Modo Reconstrucción completo, reubicado a campañas con evidencia adecuada. Reemplaza a `DEC-017`. |
| `DEC-051` | DECIDIDO | Python como lenguaje del tooling inicial de ingestión, validación, deltas, snapshots y vistas. Resuelve `OPEN-001`. |
| `DEC-052` | DECIDIDO | Identificadores secuenciales de ancho fijo, seis dígitos, tras el prefijo de §16.3. Resuelve `OPEN-002`. |
| `DEC-053` | DECIDIDO | Código bajo MIT, corpus científico bajo CC BY 4.0, contenido de juego propietario. Resuelve `OPEN-015`. |
| `DEC-054` | DECIDIDO | El eje `acceptance` gana `abandoned` para «ya no la sostiene nadie», en vez de expresarlo con `historical_status: rejected`: son ejes independientes (§10) y acoplarlos habría hecho indistinguible una idea rechazada con defensores de otra sin ellos. Resuelve `ISSUE-000037`. Sube el esquema a 1.1.0. |
| `DEC-055` | DECIDIDO | Los grupos de conflicto pasan a registro propio con identificador opaco (`CONFLICT-000001`, `conflict-groups.jsonl`). Como cadenas libres no tenían integridad referencial y derivaron solas —los dos fixtures usaban convenciones distintas—, y no había dónde decir en qué consiste cada desacuerdo. Resuelve `ISSUE-000036`. Sube el esquema a 1.1.0. |

## 30.1. Relación entre decisiones nuevas y anteriores

Las decisiones `DEC-033` a `DEC-053` no invalidan la arquitectura `DEC-001` a `DEC-031`. Cambian:

- el primer contenido;
- el orden de desarrollo;
- la profundidad inicial de los modos;
- el momento de implementar sistemas paleoantropológicos.

Los principios científicos, la estructura de conocimiento y los inventarios permanecen vigentes.

Cuatro decisiones anteriores están supersedidas: `DEC-018` y `DEC-032` desde la revisión estratégica, y `DEC-016` y `DEC-017` desde la corrección de trazabilidad del 7 de agosto de 2026. Las cuatro conservan su texto original y enlazan su reemplazo.

`DEC-051` a `DEC-053` resuelven las tres decisiones abiertas que bloqueaban la Fase 0. Sus ADR correspondientes se redactan al crear el repositorio, junto a `ADR-001`, `ADR-002` y `ADR-003`.

Sobre `DEC-052`: seis dígitos dan un millón de registros por tipo. Si algún tipo se acercara a ese límite, la ampliación de ancho es una migración de esquema, no un cambio de identidad: los identificadores ya emitidos no se renumeran. El contador es central, lo que basta mientras el proyecto sea individual; el disparador para revisarlo es el del editor colaborativo de §25.9.

# Apéndice A. Inventario científico de partida

## A.1. Condición de este inventario

Este apéndice conserva el conocimiento científico ya discutido y delimita el corpus que el sistema debe poder representar. **No reemplaza la ingestión formal con fuentes y afirmaciones atómicas.** Todos sus elementos deben reingresarse mediante el protocolo normal antes de considerarse datos canónicos.

Las marcas conceptuales previstas son:

- rango formal;
- clado sin rango;
- extinguido;
- posición discutida;
- nombre aproximadamente equivalente;
- crown group;
- stem group;
- total group;
- grado parafilético;
- taxón histórico;
- linaje genético sin nombre formal consensuado.

## A.2. Backbone profundo provisional

```text
Eukaryota
└── Amorphea
    └── Obazoa
        └── Opisthokonta
            └── Holozoa
                └── Filozoa
                    └── Choanozoa sensu stricto / Apoikozoa ⚠ conflicto de circunscripción, no preferencia de autor
                        └── Metazoa = Animalia
                            └── ParaHoxozoa ⚠
                                └── Planulozoa
                                    └── Bilateria
                                        └── Nephrozoa
                                            └── Deuterostomia ⚠ monofilia discutida
                                                └── Chordata
                                                    └── Olfactores
                                                        └── Vertebrata ≈ Craniata
                                                            └── Gnathostomata
                                                                └── Euteleostomi ≈ Osteichthyes crown
                                                                    └── Sarcopterygii
                                                                        └── Rhipidistia ≈ Dipnotetrapodomorpha ⚠ según definición
                                                                            └── Tetrapodomorpha
                                                                                └── Eotetrapodiformes
                                                                                    └── Elpistostegalia
                                                                                        └── Stegocephali
                                                                                            └── Tetrapoda crown
                                                                                                └── Pan-Amniota / Reptiliomorpha sensu lato
                                                                                                    └── Amniota
                                                                                                        └── Synapsida
                                                                                                            └── Eupelycosauria
                                                                                                                └── Sphenacodontia
                                                                                                                    └── Sphenacodontoidea
                                                                                                                        └── Therapsida
                                                                                                                            └── Eutherapsida ⚠ uso no universal
                                                                                                                                └── Neotherapsida
                                                                                                                                    └── Theriodontia
                                                                                                                                        └── Eutheriodontia
                                                                                                                                            └── Cynodontia
                                                                                                                                                └── Epicynodontia
                                                                                                                                                    └── Eucynodontia
                                                                                                                                                        └── Probainognathia
                                                                                                                                                            └── Prozostrodontia
                                                                                                                                                                └── Mammaliamorpha
                                                                                                                                                                    └── Mammaliaformes
                                                                                                                                                                        └── Mammalia
                                                                                                                                                                            └── Theriiformes ⚠ definición variable
                                                                                                                                                                                └── Holotheria ⚠ definición variable
                                                                                                                                                                                    └── Trechnotheria
                                                                                                                                                                                        └── Cladotheria
                                                                                                                                                                                            └── Zatheria
                                                                                                                                                                                                └── Boreosphenida / Tribosphenida ⚠ según definición
                                                                                                                                                                                                    └── Theria
                                                                                                                                                                                                        └── Eutheria
                                                                                                                                                                                                            └── Placentalia
                                                                                                                                                                                                                └── Boreoeutheria
                                                                                                                                                                                                                    └── Euarchontoglires
                                                                                                                                                                                                                        └── Euarchonta ⚠ posición de Scandentia variable
                                                                                                                                                                                                                            └── Primatomorpha
                                                                                                                                                                                                                                └── Primates
                                                                                                                                                                                                                                    └── Haplorhini / Haplorrhini
                                                                                                                                                                                                                                        └── Simiiformes = Anthropoidea aproximadamente
                                                                                                                                                                                                                                            └── Catarrhini
                                                                                                                                                                                                                                                └── Hominoidea
                                                                                                                                                                                                                                                    └── Hominidae
                                                                                                                                                                                                                                                        └── Homininae
                                                                                                                                                                                                                                                            └── Hominini ⚠ circunscripción dependiente de clasificación
                                                                                                                                                                                                                                                                └── Homo
                                                                                                                                                                                                                                                                    └── Homo sapiens
```

La marca `⚠` señala posición, contenido o validez discutidos, y `≈` nombres cuya equivalencia depende de la definición adoptada. Se aplican **nodo a nodo**: una lista de marcas en A.1 sin aplicación concreta no informa de nada (`ISSUE-000018`).

Este backbone es una cadena de nodos y **no una marcha**. Cada nivel tuvo ramas hermanas que persisten hoy, y ninguna divergencia estaba orientada hacia la siguiente. Presentarlo en columna es una comodidad de lectura, no una afirmación sobre la dirección del proceso (§4.2).

## A.3. Ramas hermanas relevantes del backbone

| Nodo | Rama hacia humanos | Rama externa o hermana relevante |
|---|---|---|
| Amorphea | Obazoa | Amoebozoa |
| Obazoa | Opisthokonta | Apusomonadida y Breviatea |
| Opisthokonta | Holozoa | Holomycota |
| Holozoa | Filozoa | Ichthyosporea y Pluriformea |
| Filozoa | Choanozoa s.s. | Filasterea |
| Choanozoa s.s. | Metazoa | Choanoflagellata |
| Planulozoa | Bilateria | Cnidaria |
| Bilateria | Nephrozoa | Xenacoelomorpha |
| Nephrozoa | línea cordada | Protostomia y, según topología, Ambulacraria |
| Chordata | Olfactores | Cephalochordata |
| Olfactores | Vertebrata | Tunicata |
| Vertebrata | Gnathostomata | Cyclostomata: Myxini + Petromyzontida |
| Gnathostomata | Euteleostomi | Chondrichthyes |
| Euteleostomi | Sarcopterygii | Actinopterygii |
| Sarcopterygii | Rhipidistia | Actinistia |
| Rhipidistia | Tetrapodomorpha | Dipnoi |
| Tetrapoda | línea amniota | Lissamphibia |
| Amniota | Synapsida | Sauropsida |
| Neotherapsida | Theriodontia | Anomodontia |
| Theriodontia | Eutheriodontia | Gorgonopsia |
| Eutheriodontia | Cynodontia | Therocephalia |
| Eucynodontia | Probainognathia | Cynognathia |
| Mammalia | Theria | Monotremata |
| Theria | Eutheria | Metatheria |
| Placentalia | Boreoeutheria o rama según raíz | Afrotheria y Xenarthra |
| Boreoeutheria | Euarchontoglires | Laurasiatheria |
| Euarchontoglires | Euarchonta | Glires |
| Primatomorpha | Primates | Dermoptera |
| Primates | Haplorhini | Strepsirrhini |
| Haplorhini | Simiiformes | Tarsiiformes |
| Simiiformes | Catarrhini | Platyrrhini |
| Catarrhini | Hominoidea | Cercopithecoidea |
| Hominoidea | Hominidae | Hylobatidae |
| Hominidae | Homininae | Ponginae |
| Homininae | Hominini | Gorillini |
| Hominini según MDD | Homo | Pan |

## A.4. Grupos troncales relevantes antes de Mammalia

Inventario previsto:

- sinápsidos basales;
- Eupelycosauria;
- Sphenacodontia;
- Sphenacodontidae, incluido *Dimetrodon* como rama lateral;
- Therapsida;
- Biarmosuchia;
- Dinocephalia;
- Anomodontia;
- Gorgonopsia;
- Therocephalia;
- Cynodontia;
- Cynognathia;
- Probainognathia;
- Prozostrodontia;
- Tritylodontidae;
- Morganucodonta;
- Docodonta;
- otros Mammaliaformes.

La secuencia no implica que cada grupo listado sea antepasado directo del siguiente. Muchos representan ramas hermanas, stem groups o grados.

## A.5. Tetrapodomorfos de referencia

El sistema debe poder representar, al menos como casos de prueba:

- †*Eusthenopteron*;
- †*Panderichthys*;
- †*Tiktaalik*;
- †*Elpistostege*;
- †*Acanthostega*;
- †*Ichthyostega*.

Su uso principal será demostrar diferencias entre:

- taxón fósil;
- stem group;
- secuencia de caracteres;
- ancestro directo no demostrado;
- transición representada por varias ramas.

## A.6. Grandes clados placentarios

```text
Placentalia
├── Afrotheria
├── Xenarthra
├── Laurasiatheria
└── Euarchontoglires
```

La raíz entre esos clados debe permitir hipótesis alternativas como:

- Afrotheria basal;
- Xenarthra basal;
- Atlantogenata frente a Boreoeutheria.

## A.7. Euarchontoglires

```text
Euarchontoglires
├── Glires
│   ├── Rodentia
│   └── Lagomorpha
└── Euarchonta
    ├── Scandentia, posición variable
    └── Primatomorpha
        ├── Dermoptera
        └── Primates
```

---

# Apéndice B. Clasificación de primates que el sistema debe poder representar

## B.1. Estructura general

```text
Primates
├── Strepsirrhini
│   ├── Chiromyiformes
│   ├── Lemuriformes
│   └── Lorisiformes
└── Haplorhini
    ├── Tarsiiformes
    └── Simiiformes
        ├── Platyrrhini
        └── Catarrhini
            ├── Cercopithecoidea
            └── Hominoidea
```

Debe poder conservar clasificaciones que:

- incluyan Chiromyiformes dentro de Lemuriformes;
- utilicen superfamilias Daubentonioidea, Lemuroidea, Lorisoidea o Tarsioidea;
- prefieran Anthropoidea a Simiiformes;
- agrupen platirrinos de forma diferente;
- cambien rango de tribu a subtribu.

## B.2. Strepsirrhini

```text
Strepsirrhini
├── Chiromyiformes
│   └── Daubentoniidae
│       └── Daubentonia
├── Lemuriformes
│   ├── Cheirogaleidae
│   │   ├── Allocebus
│   │   ├── Cheirogaleus
│   │   ├── Microcebus
│   │   ├── Mirza
│   │   └── Phaner
│   ├── Lepilemuridae
│   │   └── Lepilemur
│   ├── Lemuridae
│   │   ├── Eulemur
│   │   ├── Hapalemur
│   │   ├── Lemur
│   │   ├── Prolemur
│   │   └── Varecia
│   └── Indriidae
│       ├── Avahi
│       ├── Indri
│       └── Propithecus
└── Lorisiformes
    ├── Lorisidae
    │   ├── Lorisinae
    │   │   ├── Loris
    │   │   ├── Nycticebus
    │   │   └── Xanthonycticebus
    │   └── Perodicticinae
    │       ├── Arctocebus
    │       └── Perodicticus
    └── Galagidae
        └── Galaginae
            ├── Euoticus
            ├── Galago
            ├── Galagoides
            ├── Otolemur
            ├── Paragalago
            └── Sciurocheirus
```

## B.3. Tarsiiformes

```text
Haplorhini
└── Tarsiiformes
    └── Tarsiidae
        ├── Carlito
        ├── Cephalopachus
        └── Tarsius
```

La categoría tradicional “Prosimii” debe registrarse como agrupación histórica o parafilética, no como clado crown válido.

## B.4. Platyrrhini

```text
Platyrrhini
├── Callitrichidae
├── Cebidae
├── Aotidae
├── Pitheciidae
└── Atelidae
```

### Callitrichidae

```text
Callitrichidae
├── Callimico
├── Callithrix
├── Cebuella
├── Leontopithecus
├── Mico
│   ├── Mico, subgénero
│   └── Callibella, subgénero
└── Saguinus
    ├── Saguinus, subgénero
    ├── Leontocebus, subgénero
    ├── Oedipomidas, subgénero
    └── Tamarinus, subgénero
```

### Cebidae

```text
Cebidae
├── Cebinae
│   ├── Cebus
│   └── Sapajus
└── Saimiriinae
    └── Saimiri
```

### Aotidae

```text
Aotidae
└── Aotus
```

### Pitheciidae

```text
Pitheciidae
├── Callicebinae
│   ├── Callicebus
│   ├── Cheracebus
│   ├── Plecturocebus
│   └── †Xenothrix
└── Pitheciinae
    ├── Cacajao
    ├── Chiropotes
    └── Pithecia
```

### Atelidae

```text
Atelidae
├── Alouattinae
│   └── Alouatta
└── Atelinae
    ├── Ateles
    ├── Brachyteles
    └── Lagothrix
```

## B.5. Catarrhini

```text
Catarrhini
├── Cercopithecoidea
│   └── Cercopithecidae
└── Hominoidea
    ├── Hylobatidae
    └── Hominidae
```

## B.6. Cercopithecidae

```text
Cercopithecidae
├── Cercopithecinae
│   ├── Cercopithecini
│   │   ├── Allenopithecus
│   │   ├── Allochrocebus
│   │   ├── Cercopithecus
│   │   ├── Chlorocebus
│   │   ├── Erythrocebus
│   │   └── Miopithecus
│   └── Papionini
│       ├── Cercocebus
│       ├── Lophocebus
│       ├── Macaca
│       ├── Mandrillus
│       ├── Papio
│       ├── Rungwecebus
│       └── Theropithecus
└── Colobinae
    ├── Colobini
    │   ├── Colobus
    │   ├── Piliocolobus
    │   └── Procolobus
    └── Presbytini
        ├── Nasalis
        ├── Presbytis
        ├── Pygathrix
        ├── Rhinopithecus
        ├── Semnopithecus
        ├── Simias
        └── Trachypithecus
```

Clasificaciones alternativas previstas:

```text
Papionini
├── Macacina
│   └── Macaca
└── Papionina
    ├── Cercocebus
    ├── Lophocebus
    ├── Mandrillus
    ├── Papio
    ├── Rungwecebus
    └── Theropithecus
```

Y el cambio de rango entre:

```text
Colobini / Presbytini
```

y:

```text
Colobina / Presbytina
```

según la clasificación.

## B.7. Hominoidea

```text
Hominoidea
├── Hylobatidae
│   ├── Hoolock
│   ├── Hylobates
│   ├── Nomascus
│   └── Symphalangus
└── Hominidae
    ├── Ponginae
    │   └── Pongini
    │       └── Pongo
    └── Homininae
        ├── Gorillini
        │   └── Gorilla
        └── Hominini
            ├── Pan
            └── Homo
```

## B.8. Clasificaciones alternativas de Homininae

### Sistema sin subtribus

```text
Homininae
├── Gorillini
└── Hominini
    ├── Pan
    └── Homo
```

### Sistema con subtribus

```text
Homininae
├── Gorillini
└── Hominini
    ├── Panina
    │   └── Pan
    └── Hominina
        └── linaje humano
```

### Sistema paleoantropológico

```text
Homininae
├── Gorillini
├── Panini
│   └── Pan
└── Hominini
    └── linaje humano posterior a la separación de Pan
```

La posible subdivisión en Australopithecina y Hominina debe mantenerse como clasificación discutida porque “australopitecos” puede constituir un grado parafilético.

---

# Apéndice C. Inventario fósil y paleoantropológico de partida

## C.1. Alrededor del origen de Primates

### Plesiadapiformes y Pan-Primates

Grupos previstos:

- †Purgatoriidae;
- †Plesiadapidae;
- †Carpolestidae;
- †Microsyopidae;
- †Paromomyidae;
- †Saxonellidae;
- †Picrodontidae.

Debe permitirse que “Plesiadapiformes” sea:

- un grupo troncal de Primates;
- un conjunto parafilético;
- una agrupación con algunos miembros próximos a Dermoptera;
- una categoría histórica con circunscripciones diferentes.

### Euprimates tempranos

```text
Primates crown
├── línea estrepsirrina
│   └── †Adapiformes, generalmente stem
└── línea haplorrina
    └── †Omomyiformes, generalmente stem
```

Familias o subgrupos previstos:

- †Notharctidae;
- †Adapidae;
- †Sivaladapidae;
- †Caenopithecidae;
- †Cercamoniinae según clasificación;
- †Omomyidae;
- †Anaptomorphinae;
- †Omomyinae.

No deben etiquetarse simplemente como “lémures primitivos” o “tarseros primitivos”.

## C.2. Stem Simiiformes

Grupos previstos:

- †Eosimiiformes / †Eosimiidae;
- †*Eosimias*;
- †*Phenacopithecus*;
- †*Bahinia*;
- †Amphipithecidae;
- †*Amphipithecus*;
- †*Pondaungia*;
- †*Ganlea*;
- †Parapithecoidea / †Parapithecidae;
- †*Apidium*;
- †*Parapithecus*;
- †*Qatrania*;
- †Proteopithecoidea / †Proteopithecidae;
- †*Proteopithecus*;
- †*Serapia*;
- †Oligopithecidae;
- †*Oligopithecus*;
- †*Catopithecus*.

Las posiciones de Amphipithecidae y otros grupos deben permitir múltiples hipótesis.

## C.3. Stem Catarrhini

Grupos previstos:

- †Propliopithecoidea;
- †Propliopithecidae;
- †*Propliopithecus*;
- †*Aegyptopithecus*;
- †Saadanioidea;
- †Saadaniidae;
- †*Saadanius*;
- †Pliopithecoidea;
- †Pliopithecidae;
- †Crouzeliidae según clasificación;
- †*Pliopithecus*;
- †*Anapithecus*;
- †*Egarapithecus*;
- †*Laccopithecus*;
- †Victoriapithecidae;
- †*Victoriapithecus*;
- †*Prohylobates*;
- †Dendropithecoidea / †Dendropithecidae;
- †Proconsuloidea / †Proconsulidae;
- †Afropithecidae;
- †Nyanzapithecidae.

## C.4. Simios del Mioceno

### África

- †*Proconsul*;
- †*Ekembo*;
- †*Dendropithecus*;
- †*Micropithecus*;
- †*Limnopithecus*;
- †*Morotopithecus*;
- †*Afropithecus*;
- †*Heliopithecus*;
- †*Nacholapithecus*;
- †*Equatorius*;
- †*Kenyapithecus*;
- †*Nakalipithecus*;
- †*Samburupithecus*;
- †*Chororapithecus*;
- †*Masripithecus*, propuesta reciente pendiente de auditoría formal; conservar la fecha de propuesta al ingerir.

### Europa

- †*Griphopithecus*;
- †*Pierolapithecus*;
- †*Anoiapithecus*;
- †*Dryopithecus*;
- †*Hispanopithecus*;
- †*Rudapithecus*;
- †*Danuvius*;
- †*Buronius*;
- †*Ouranopithecus*;
- †*Graecopithecus*;
- †*Oreopithecus*.

### Anatolia y Asia

- †*Anadoluvius*;
- †*Sivapithecus*;
- †*Ankarapithecus*;
- †*Khoratpithecus*;
- †*Lufengpithecus*;
- †*Gigantopithecus*.

### Nombres tribales o agrupaciones

- †Kenyapithecini;
- †Dryopithecini;
- †Sivapithecini;
- †Lufengpithecini;
- †Gigantopithecini.

El sistema debe permitir que su contenido y rango cambien entre autores.

## C.5. Homininos tempranos

### †*Sahelanthropus*

- †*Sahelanthropus tchadensis*;
- candidato a hominino basal;
- postura y posición disputadas;
- no debe fijarse como antepasado directo.

### †*Orrorin*

- †*Orrorin tugenensis*;
- caracteres compatibles con bipedalismo;
- posición exacta incierta.

### †*Ardipithecus*

```text
Ardipithecus
├── †A. kadabba
└── †A. ramidus
```

Debe poder registrarse su mosaico de locomoción terrestre y arbórea.

### Candidatos controvertidos

- †*Graecopithecus freybergi*;
- †*Anadoluvius turkae*.

Su condición de homininos no debe incorporarse al backbone sin una vista dedicada.

## C.6. *Australopithecus*

Inventario previsto:

- †*Australopithecus anamensis*;
- †*Australopithecus afarensis*;
- †*Australopithecus bahrelghazali*;
- †*Australopithecus deyiremeda*;
- †*Australopithecus africanus*;
- †*Australopithecus garhi*;
- †*Australopithecus sediba*;
- †*Australopithecus prometheus*, aceptación reducida o discutida.

El género debe poder aparecer como:

- taxón tradicional;
- grado adaptativo;
- grupo parafilético;
- varios conceptos taxonómicos con circunscripciones distintas.

## C.7. †*Kenyanthropus*

- †*Kenyanthropus platyops*;
- posible deformación del fósil tipo;
- posible inclusión en *Australopithecus afarensis*;
- relación propuesta con *Homo rudolfensis*;
- uso alternativo *Kenyanthropus rudolfensis*.

## C.8. †*Paranthropus*

```text
Paranthropus
├── †P. aethiopicus
├── †P. boisei
└── †P. robustus
```

Nombres o alternativas:

- †*Paranthropus walkeri*, generalmente incluido en *P. aethiopicus*;
- †*Paranthropus crassidens*, generalmente incluido en *P. robustus*;
- †*Zinjanthropus boisei*, nombre original;
- inclusión de estas especies en *Australopithecus*;
- monofilia plausible pero no absoluta.

## C.9. Origen de *Homo*

Preguntas que deben permanecer explícitas:

- qué australopiteco está más próximo al origen;
- si *H. habilis* y *H. rudolfensis* pertenecen al género;
- si el origen fue una única transición o una radiación;
- relación con *Paranthropus*, *A. africanus*, *A. garhi* y *A. sediba*;
- posible coexistencia de varios linajes alrededor de 3–2,5 Ma.

## C.10. Inventario de *Homo*

### Especies reconocidas con regularidad

- †*Homo habilis*;
- †*Homo rudolfensis*;
- †*Homo erectus*;
- †*Homo antecessor*;
- †*Homo naledi*;
- †*Homo floresiensis*;
- †*Homo luzonensis*;
- †*Homo neanderthalensis*;
- *Homo sapiens*.

### Nombres usados con frecuencia pero susceptibles de inclusión en otros taxones

- †*Homo ergaster*;
- †*Homo georgicus*;
- †*Homo heidelbergensis*;
- †*Homo rhodesiensis*.

### Propuestas recientes o no consensuadas

- †*Homo bodoensis*;
- †*Homo longi*;
- †*Homo juluensis*.

### Nombres regionales, históricos o minoritarios

- †*Homo cepranensis*;
- †*Homo daliensis*;
- †*Homo tsaichangensis*;
- †*Homo soloensis*;
- †*Homo pekinensis*;
- †*Homo lantianensis*;
- †*Homo mauritanicus*;
- †*Homo helmei*;
- †*Homo gautengensis*;
- †*Homo altaiensis*;
- propuestas *Homo denisova* o *Homo denisovensis*.

## C.11. *Homo* temprano

### †*Homo habilis*

Debe poder representarse como:

- especie válida;
- conjunto variable;
- material parcialmente fuera de *Homo*;
- posible rama lateral;
- no necesariamente ancestro directo de *H. erectus*.

### †*Homo rudolfensis*

Debe permitir:

- especie separada;
- inclusión en *Kenyanthropus*;
- agrupación con parte de *Homo* temprano;
- variación, dimorfismo o múltiples especies como hipótesis.

## C.12. Complejo *Homo erectus* sensu lato

```text
Homo erectus sensu lato
├── †H. ergaster, África
├── †H. georgicus, Dmanisi
├── †H. erectus sensu stricto, Asia
├── †H. pekinensis, generalmente incluido
├── †H. lantianensis, generalmente incluido
└── †H. soloensis, generalmente incluido
```

Nombres históricos absorbidos:

- †*Pithecanthropus erectus*;
- †*Sinanthropus pekinensis*;
- †*Telanthropus capensis*.

†*Meganthropus* debe permanecer problemático hasta ingresar evidencia específica.

## C.13. Ramas laterales

### †*Homo naledi*

- mosaico de rasgos;
- edad reciente respecto de parte de su anatomía;
- posición basal o lateral dentro de *Homo* según análisis.

### †*Homo floresiensis*

Hipótesis previstas:

- descendencia insular de *H. erectus*;
- descendencia de un *Homo* más basal;
- linaje asiático temprano no documentado en el continente.

### †*Homo luzonensis*

- material limitado;
- combinación de rasgos;
- posición no resuelta.

## C.14. †*Homo antecessor*

Debe poder representarse como:

- próximo al origen de sapiens, neandertales y denisovanos;
- rama lateral próxima;
- población ancestral posible pero no demostrada.

## C.15. Pleistoceno medio

Conceptos y categorías:

- †*Homo heidelbergensis* sensu lato;
- †*Homo heidelbergensis* europeo restringido;
- †*Homo rhodesiensis*;
- †*Homo bodoensis*;
- “*Homo sapiens* arcaico”;
- preneandertales;
- humanos del Pleistoceno medio no asignados.

Debe ser posible que una misma etiqueta histórica agrupe poblaciones de ramas diferentes.

## C.16. Clado sapiens–neandertal–denisovano

Backbone conceptual:

```text
Homo tardío
├── línea de Homo sapiens
└── población neandersovana
    ├── neandertales
    └── denisovanos
```

Debe superponerse con eventos de:

- flujo génico sapiens–neandertal;
- flujo génico sapiens–denisovano;
- flujo neandertal–denisovano;
- contribuciones de poblaciones arcaicas no identificadas;
- estructura interna de cada linaje.

## C.17. Neandertales

Conceptos taxonómicos previstos:

- †*Homo neanderthalensis* como especie;
- †*Homo sapiens neanderthalensis* como subespecie.

El cruzamiento no resuelve por sí solo el rango taxonómico.

## C.18. Denisovanos

Debe distinguirse:

- linaje genético bien respaldado;
- especímenes asignados;
- poblaciones denisovanas internas;
- nombres zoológicos propuestos;
- posibles asociaciones morfológicas;
- ausencia de consenso binomial.

Nombres a registrar como conceptos o propuestas:

- Denisovans / Denisova hominins;
- †*Homo altaiensis*;
- †*Homo denisova*;
- †*Homo denisovensis*;
- inclusión en †*Homo longi*;
- inclusión en †*Homo juluensis*.

## C.19. †*Homo longi*

Debe poder representar:

- concepto basado en el cráneo de Harbin;
- afinidad molecular denisovana del espécimen;
- posibilidad de que el nombre abarque una población, varios fósiles o todo el linaje;
- conflicto entre taxonomía morfológica y linaje genético.

## C.20. †*Homo juluensis*

Agrupación propuesta que puede incluir, según fuente:

- Xujiayao;
- Xuchang;
- Xiahe;
- Penghu;
- Denisova;
- Tam Ngu Hao 2.

Debe permitirse su solapamiento o conflicto con *H. longi* y con conceptos denisovanos.

## C.21. Otros humanos asiáticos

- †*Homo daliensis*;
- †*Homo tsaichangensis*;
- Penghu;
- Maba;
- Narmada;
- Hualongdong;
- Dali;
- Jinniushan;
- Harbin;
- Xujiayao;
- Xuchang;
- Xiahe.

Cada espécimen o conjunto debe mantenerse separado de su asignación taxonómica.

## C.22. *Homo sapiens*

El sistema debe permitir:

- especie viviente sin subespecies universalmente aceptadas;
- uso de *Homo sapiens sapiens* en determinadas clasificaciones;
- propuesta †*Homo sapiens idaltu*;
- origen poblacional estructurado en África;
- múltiples expansiones y contactos;
- haplogrupos como árboles génicos, no taxonomía de la especie;
- nombres históricos y raciales conservados únicamente como sinonimia histórica cuando sea necesario, nunca como ramas biológicas vigentes;
- el inventario previo señaló más de un centenar de nombres y sinónimos históricos asociados a *Homo sapiens* en la base taxonómica consultada; la cifra y cada nombre deben reingresarse desde la fuente antes de usarse como datos canónicos.

---

# Apéndice D. Categorías no cladísticas y advertencias terminológicas

## D.1. “Prosimios”

Agrupa Strepsirrhini y Tarsiiformes, pero resulta parafilético porque los tarseros están más próximos a Simiiformes.

## D.2. “Monos”

Si excluye Hominoidea, es parafilético. Debe conservarse como término común, no como clado restringido sin advertencia.

## D.3. “Australopitecos”

Puede funcionar como grado adaptativo o categoría informal, no necesariamente clado monofilético.

## D.4. “Humanos arcaicos”

Categoría informal que puede abarcar poblaciones muy diferentes. Debe exigir definición contextual.

## D.5. “Eslabón perdido”

No es una categoría científica. Puede registrarse como término histórico o popular, nunca como tipo de entidad filogenética.

## D.6. Hominoideo, homínido, hominine y hominino

El glosario debe distinguir:

- Hominoidea;
- Hominidae;
- Homininae;
- Hominini;
- Hominina;
- Panina;
- Panini;
- uso paleoantropológico de “hominino”.

La traducción entre inglés y español debe guardar el término original porque “hominin” y “hominine” se confunden con facilidad.

---

# Apéndice E. Esquemas conceptuales mínimos

Estos ejemplos no sustituyen los JSON Schema formales. Definen la semántica que los esquemas deben proteger.

**Este apéndice es canónico.** Donde un ejemplo inline del cuerpo de la guía difiera de su esquema aquí, manda el esquema. Las cuatro dimensiones epistemológicas de §10.1 a §10.5 van siempre anidadas bajo `epistemic_dimensions`; `record_status` va siempre en la raíz, porque describe el registro y no la idea.

## E.1. Sección

```json
{
  "id": "SEC-000001",
  "title": "Título descriptivo",
  "received_at": "2026-08-05",
  "original_content_path": "knowledge/corpus/sections/SEC-000001.md",
  "content_hash": "sha256:...",
  "approximate_period": null,
  "topics": [],
  "source_ids": [],
  "schema_version": "1.0.0",
  "dataset_revision": "REV-000001",
  "record_status": "active"
}
```

## E.2. Mención

```json
{
  "id": "MENTION-000001",
  "section_id": "SEC-000001",
  "passage_id": "PASSAGE-000001",
  "original_text": "texto exacto",
  "normalized_form": null,
  "mention_type": "unresolved",
  "character_offsets": {
    "start": 0,
    "end": 11
  },
  "resolution": {
    "status": "pending",
    "target_ids": [],
    "reason": null
  },
  "disposition": null,
  "notes": []
}
```

## E.3. Nombre taxonómico

```json
{
  "id": "NAME-000001",
  "canonical_spelling": "Nombre",
  "original_spellings": [],
  "authorship": null,
  "nomenclatural_status": null,
  "rank_when_established": null,
  "source_ids": [],
  "record_status": "active"
}
```

## E.4. Concepto taxonómico

```json
{
  "id": "TAXCONCEPT-000001",
  "name_id": "NAME-000001",
  "according_to_source_id": "SRC-000001",
  "circumscription": {
    "included_entity_ids": [],
    "excluded_entity_ids": [],
    "definition_text": null
  },
  "rank_assignment": {
    "rank": null,
    "parent_concept_id": null
  },
  "taxonomic_status": null,
  "phylogenetic_interpretation": null,
  "claim_ids": [],
  "first_introduced_in": "SEC-000001",
  "record_status": "active"
}
```

## E.5. Entidad biológica común

```json
{
  "id": "LINEAGE-000001",
  "entity_type": "biological_lineage",
  "preferred_label": "Linaje no nombrado",
  "alias_ids": [],
  "description": null,
  "claim_ids": [],
  "issue_ids": [],
  "first_introduced_in": "SEC-000001",
  "last_modified_in": "SEC-000001",
  "record_status": "active"
}
```

Los datos temporales, geográficos, filogenéticos o epistemológicos no se colocan como verdades planas en este nodo; se expresan mediante ocurrencias y afirmaciones.

## E.6. Afirmación

```json
{
  "id": "CLAIM-000001",
  "claim_type": "relational",
  "subject_id": "SPECIMEN-000001",
  "predicate": "assigned_to",
  "object": {
    "entity_id": "TAXCONCEPT-000001"
  },
  "scope": {
    "hypothesis_ids": [],
    "classification_view_ids": [],
    "temporal_expression_ids": [],
    "region_ids": []
  },
  "provenance": {
    "section_ids": ["SEC-000001"],
    "passage_ids": ["PASSAGE-000001"],
    "source_ids": ["SRC-000001"],
    "operation_id": null,
    "dataset_revision": "REV-000001",
    "origin": "ingestion"
  },
  "epistemic_dimensions": {
    "acceptance": "not_assessed",
    "evidence_strength": "unknown",
    "resolution": "unresolved",
    "historical_status": "current"
  },
  "quantitative_support": [],
  "evidence_ids": [],
  "counterevidence_ids": [],
  "derivation": null,
  "record_status": "active"
}
```

## E.7. Evidencia

```json
{
  "id": "EVID-000001",
  "evidence_type": "morphological",
  "description": "",
  "source_id": "SRC-000001",
  "passage_ids": [],
  "dataset_ids": [],
  "analysis_ids": [],
  "supports_claim_ids": [],
  "challenges_claim_ids": [],
  "limitations": [],
  "quality_notes": [],
  "record_status": "active"
}
```

Tipos previstos:

- morfológica;
- anatómica;
- fósil;
- estratigráfica;
- sedimentológica;
- molecular;
- genómica;
- mitocondrial;
- cromosómica;
- paleoproteómica;
- arqueológica;
- biogeográfica;
- ecológica;
- conductual;
- lingüística;
- cronológica;
- estadística;
- histórica;
- nomenclatural;
- taxonómica.

## E.8. Evento

```json
{
  "id": "EVENT-000001",
  "event_type": "hybridization",
  "participants": [
    {
      "entity_id": "POP-000001",
      "role": "parental_population"
    },
    {
      "entity_id": "POP-000002",
      "role": "parental_population"
    }
  ],
  "result_entity_ids": [],
  "temporal_expression_ids": [],
  "region_ids": [],
  "claim_ids": [],
  "evidence_ids": [],
  "hypothesis_ids": [],
  "record_status": "active"
}
```

## E.9. Hipótesis

```json
{
  "id": "HYP-000001",
  "name": "Nombre descriptivo",
  "description": "",
  "included_claim_ids": [],
  "required_claim_ids": [],
  "excluded_claim_ids": [],
  "assumptions": [],
  "classification_view_ids": [],
  "supporting_evidence_ids": [],
  "counterevidence_ids": [],
  "supporting_source_ids": [],
  "opposing_source_ids": [],
  "conflict_group_ids": [],
  "epistemic_dimensions": {
    "acceptance": "not_assessed",
    "evidence_strength": "unknown",
    "resolution": "unresolved",
    "historical_status": "current"
  },
  "introduced_in": "SEC-000001",
  "record_status": "active"
}
```

## E.10. Vista filogenética

```json
{
  "id": "PHYVIEW-000001",
  "name": "Síntesis de trabajo",
  "cutoff_date": "2026-08-05",
  "hypothesis_ids": [],
  "selected_claim_ids": [],
  "excluded_claim_ids": [],
  "editorial_criteria": [],
  "simplifications": [],
  "scale": "campaign-01-eukarya",
  "generated_artifacts": [],
  "view_version": "1.0.0",
  "built_from_dataset_revision": "REV-000001"
}
```

## E.11. Proyección de juego

```json
{
  "id": "GAME-000001",
  "scientific_reference_ids": [],
  "campaign_id": "CAMP-000001",
  "chapter_id": null,
  "module_id": "c01-eukarya",
  "playable_role": "population",
  "simulation_scale": "cellular-populations",
  "abstraction": "",
  "mechanic_hooks": [],
  "scientific_constraints": [],
  "simplifications": [],
  "continuity_policy": "atlas-and-narrative",
  "future_compatibility_notes": [],
  "justification": "",
  "status": "draft"
}
```

## E.12. Cuestión pendiente

```json
{
  "id": "ISSUE-000001",
  "issue_type": "unresolved_identity",
  "title": "",
  "description": "",
  "severity": "WARNING",
  "raised_in": "SEC-000001",
  "affects": {
    "record_ids": [],
    "claim_ids": [],
    "mention_ids": []
  },
  "evidence_locators": [],
  "proposed_resolution": null,
  "blocks": null,
  "related_issue_ids": [],
  "resolution": {
    "status": "open",
    "resolved_in": null,
    "decision_id": null
  },
  "record_status": "active"
}
```

`issue_type` previstos: `unresolved_identity` · `missing_source` · `conflicting_claims` · `external_knowledge_flagged` · `validation_warning` · `pending_question` · `schema_inconsistency` · `content_gap`.

`severity` usa las tres de §19.1: `ERROR` · `WARNING` · `INFO`. Un `WARNING` de validación que no se justifique debe generar un registro de este tipo, que es lo que hace exigible la regla de §19.1.

`resolution.status`: `open` · `resolved` · `wont_fix`. Una cuestión resuelta **no se elimina**: cambia su estado y enlaza en `resolved_in` la sección o revisión que la cerró, y en `decision_id` la decisión o ADR correspondiente si lo hubo.

`external_knowledge_flagged` es el destino obligatorio del conocimiento general que aparezca durante la ingestión (§4.7) y de toda incorporación de auditoría pendiente de confirmar (§18.2).

---

# Apéndice F. Salida estándar por sección

## F.1. Informe humano

```text
1. Identificación
2. Síntesis científica
3. Cambios relevantes
4. Cobertura y excepciones
5. Entidades nuevas o modificadas
6. Afirmaciones y evidencia
7. Eventos
8. Hipótesis y controversias
9. Cuestiones pendientes
10. Validación
11. Visualización local
12. Resumen del delta
13. Estado acumulado
```

## F.2. Estado acumulado mínimo

- revisión del dataset;
- versión del esquema;
- último snapshot;
- secciones procesadas;
- menciones;
- entidades por tipo;
- afirmaciones;
- eventos;
- hipótesis;
- fuentes;
- issues abiertos;
- vistas válidas;
- vistas pendientes de reconstrucción;
- dominios científicos cubiertos.

## F.3. Preguntas y ambigüedad

Cuando una ambigüedad no impida continuar:

1. no hacer una suposición arbitraria;
2. crear `ISSUE-...`;
3. explicar qué falta;
4. continuar con el resto.

Solo debe formularse una pregunta directa cuando no sea posible representar correctamente una parte central sin la respuesta. En desarrollo automatizado, esa condición produce un estado `blocked` para el registro afectado, no para toda la sección si el resto puede procesarse.

---

# Apéndice G. Inicialización del proyecto

La primera ejecución del sistema debe:

1. crear repositorio vacío;
2. archivar la guía `1.0.0` y registrar su hash;
3. fijar `schema_version` inicial;
4. crear archivos JSONL vacíos válidos;
5. crear manifiesto del dataset;
6. crear `CAMP-000001` en estado `planning`;
7. crear leyenda visual básica;
8. crear glosario mínimo;
9. crear primer snapshot vacío;
10. ejecutar todas las validaciones;
11. no agregar taxones por conocimiento general;
12. crear fixtures artificiales separados del dataset científico;
13. procesar una sección real solo cuando haya sido incorporada como corpus;
14. mantener el fixture futuro hominino fuera del contenido de campaña.

Estado inicial conceptual:

```json
{
  "guide_version": "1.1.0",
  "schema_version": "1.0.0",
  "dataset_revision": "REV-000000",
  "snapshot_id": "SNAP-000000",
  "active_campaign": "CAMP-000001",
  "campaign_status": "planning",
  "counts": {
    "sections": 0,
    "mentions": 0,
    "entities": 0,
    "claims": 0,
    "events": 0,
    "hypotheses": 0,
    "sources": 0,
    "issues": 0,
    "views": 0
  },
  "validation": "passed"
}
```

---

# Apéndice H. Checklist operativo completo

## H.1. Antes de escribir código

- [ ] Archivar guía `1.0.0` y guardar hash.
- [ ] Incorporar guía `1.1.0`.
- [ ] Crear ADR-001 claim-centric.
- [ ] Crear ADR-002 campañas cronológicas.
- [ ] Crear ADR-003 núcleo + módulos.
- [ ] Confirmar estructura de carpetas.
- [ ] Elegir lenguaje de tooling.
- [ ] Definir convención de IDs.
- [ ] Definir licencia.
- [ ] Definir formato de citas.
- [ ] Crear esquema inicial.
- [ ] Crear fixture vacío.
- [ ] Crear CI de validación.

## H.2. Antes de ingresar investigación real

- [ ] Dossier C01 terminado.
- [ ] Fecha de corte definida.
- [ ] Corpus inmutable implementado.
- [ ] Pasajes localizables.
- [ ] Menciones con offsets.
- [ ] Tabla de cobertura.
- [ ] Fuentes y localizadores.
- [ ] Deltas reversibles.
- [ ] Snapshot reconstruible.
- [ ] Issues.
- [ ] Validadores de identidad.
- [ ] Separación entre ingestión y auditoría documentada.

## H.3. Antes de construir una filogenia

- [ ] Nombres separados de conceptos.
- [ ] Clados separados de taxones.
- [ ] Linajes y poblaciones disponibles.
- [ ] Afirmaciones atómicas.
- [ ] Evidencia vinculada.
- [ ] Hipótesis implementadas.
- [ ] Grupos de conflicto.
- [ ] Tiempo observado/inferido.
- [ ] Validación de ciclos.
- [ ] Criterios de vista.
- [ ] Alcance de campaña declarado.

## H.4. Antes de modelar endosimbiosis

- [ ] Participantes identificados o marcados como reconstruidos.
- [ ] Evento y roles implementados.
- [ ] Compatibilidad temporal.
- [ ] Contexto ambiental.
- [ ] Evidencia vinculada.
- [ ] Distinción entre asociación, transferencia e integración.
- [ ] Relaciones derivadas.
- [ ] Hipótesis alternativas.
- [ ] Prueba de que no se dibuja como bifurcación simple.

## H.5. Antes del Atlas de Eucaria

- [ ] Dataset real validado.
- [ ] Vistas reproducibles.
- [ ] Procedencia navegable.
- [ ] Comparación de hipótesis.
- [ ] Leyenda accesible.
- [ ] Zoom semántico definido.
- [ ] Historial taxonómico.
- [ ] Filtros por capítulo.
- [ ] Rendimiento medido.

## H.6. Antes del prototipo de Evolución de Eucaria

- [ ] Modelo poblacional mínimo estable.
- [ ] Tiempo determinista por semilla.
- [ ] Ambiente abstracto.
- [ ] Recursos y energía.
- [ ] Variación y deriva.
- [ ] Contacto.
- [ ] Asociación y ruptura.
- [ ] Integración condicionada.
- [ ] Divergencia.
- [ ] Extinción.
- [ ] Costos y compensaciones.
- [ ] Registro completo de eventos.
- [ ] Exportación al Atlas.
- [ ] Pruebas de teleología.

## H.7. Antes del lanzamiento de Campaña 1

- [ ] Campaña completa jugable.
- [ ] Tutorial.
- [ ] Guardado y carga.
- [ ] Atlas integrado.
- [ ] Lente científica.
- [ ] Fuentes y licencias.
- [ ] Accesibilidad.
- [ ] Rendimiento.
- [ ] Auditoría científica.
- [ ] Simplificaciones documentadas.
- [ ] Final y transición a Animales.
- [ ] Plan de actualización.
- [ ] Postmortem programado.

## H.8. Antes del modo Reconstrucción completo

- [ ] Historia oculta definida.
- [ ] Evidencia separada.
- [ ] Especímenes u observaciones discretas.
- [ ] Métodos y costos abstractos.
- [ ] Hipótesis construibles.
- [ ] Incertidumbre puntuable sin falsa probabilidad.
- [ ] Nueva evidencia y revisión.
- [ ] Final “sin resolver” válido.
- [ ] Escenario probado con usuarios.

## H.9. Antes de una campaña nueva

- [ ] Postmortem de campaña anterior.
- [ ] Pregunta central.
- [ ] Escala temporal.
- [ ] Escala espacial o ambiental.
- [ ] Corredor principal.
- [ ] Ramas hermanas.
- [ ] Grupos externos.
- [ ] Diversidad diferida.
- [ ] Corpus.
- [ ] Mecánicas nuevas.
- [ ] Mecánicas reutilizables.
- [ ] Migraciones de esquema.
- [ ] Simplificaciones.
- [ ] Riesgos científicos.
- [ ] Criterios de éxito.
- [ ] Presupuesto de contenido.
- [ ] Prueba vertical.

## H.10. Antes de modificar trabajo preservado

- [ ] Consultar guía histórica.
- [ ] Identificar decisión afectada.
- [ ] Crear ADR o decisión nueva.
- [ ] Marcar `SUPERSEDIDO`, no borrar.
- [ ] Actualizar matriz de preservación.
- [ ] Mantener fixtures futuros.
- [ ] Verificar apéndices científicos.
- [ ] Guardar snapshot previo.

---

# Apéndice I. Próximo orden de trabajo recomendado

La siguiente secuencia puede ejecutarse sin depender de decisiones lejanas:

1. crear el repositorio;
2. copiar `Guia_Maestra_Red_Evolutiva_v1.0.0_ARCHIVO.md` al archivo histórico;
3. incorporar esta guía como `docs/GUIDE.md`;
4. registrar hashes;
5. crear ADR-001, ADR-002 y ADR-003;
6. crear `CAMP-000001` y el dossier C01-EUKARYA;
7. decidir fecha de corte y corpus inicial;
8. fijar corredor, hermanas, externos y exclusiones;
9. implementar `Section`, `Passage`, `Mention`, `Source` e `Issue`;
10. implementar IDs, deltas y snapshots;
11. demostrar cobertura con fixture artificial;
12. implementar `TaxonomicName`, `TaxonConcept`, `CladeConcept`, `Lineage`, `Population` y `Trait`;
13. crear fixture `eukarya-minimal`;
14. conservar fixture `future-hominini-homonym`;
15. implementar `Claim`, `EvidenceItem`, `Analysis` y dimensiones epistemológicas;
16. implementar tiempo e incertidumbre;
17. implementar `Event` con endosimbiosis;
18. implementar `Hypothesis`, grupos de conflicto y dos vistas alternativas;
19. generar Graphviz reproducible;
20. completar el pipeline de ingestión;
21. procesar el corpus real de Eucaria;
22. congelar snapshot del dataset C01;
23. construir el Atlas vertical slice;
24. implementar simulación de poblaciones celulares;
25. implementar asociación, conflicto e integración;
26. construir los capítulos jugables;
27. integrar la lente científica;
28. probar con usuarios;
29. producir arte, audio, textos y accesibilidad;
30. auditar y lanzar Campaña 1;
31. realizar postmortem;
32. comenzar dossier de Campaña 2.

La primera meta tangible es poder representar con procedencia un evento de endosimbiosis, dos topologías alternativas y un corredor Eukaryota → Holozoa, y luego convertir ese conjunto en una experiencia jugable completa. El caso hominino permanece como fixture de futuro y no bloquea este objetivo.

---

# Apéndice J. Matriz de preservación y migración del plan anterior

## J.1. Objetivo

Este apéndice demuestra que el cambio de orden de desarrollo no elimina el trabajo previo. Cada bloque de la guía `1.0.0` tiene un destino explícito.

## J.2. Artefactos preservados

| Artefacto o bloque previo | Estado en `1.1.0` | Destino |
|---|---|---|
| Arquitectura corpus → entidades → claims → evidencia → eventos → hipótesis → vistas → juego | Vigente | Núcleo compartido, secciones 6–20. |
| Separación de nombre, concepto taxonómico, clado, linaje y población | Vigente | Secciones 7–9; requerida desde Campaña 1. |
| Modelo epistemológico multidimensional | Vigente | Sección 10. |
| Tiempo observado/inferido | Vigente | Sección 11 y Fase 4. |
| Eventos n-arios y reticulación | Vigente | Sección 13; primer caso real: endosimbiosis. |
| Hipótesis y vistas incompatibles | Vigente | Sección 15; se implementan antes del primer lanzamiento. |
| JSON/JSONL, Git, deltas y snapshots | Vigente | Sección 16. |
| Protocolo de ingestión | Vigente | Secciones 17–19. |
| Atlas | Vigente y adelantado | Parte del primer lanzamiento. |
| Modo Evolución | Vigente | Primera implementación acotada a Eucaria; se amplía por campaña. |
| Modo Reconstrucción | Retenido y reubicado | Lente ligera primero; modo completo en campañas posteriores. |
| Tres vistas mundo/red/ciencia | Vigente | Adaptadas a entorno/red/ciencia por escala. |
| Historia oculta → registro → hipótesis | Retenida | Versión ligera en Eucaria; completa con tafonomía después. |
| Población como unidad | Vigente y generalizada | Poblaciones celulares primero; humanas después. |
| Campañas Simbiosis, Cuerpos, Sinápsidos y Primates | Activadas | Reordenadas como Campañas 1–6. |
| Campaña Homininos | Preservada | Campaña 7 o dos productos finales. |
| Capítulos homininos 1–6 | Preservados | Sección 22.11 y Fase 17. |
| Recorte 400.000–40.000 años | Reubicado | Capítulo Humanidades entrelazadas, fixture complejo y primer Reconstrucción completo. |
| Escenario África oriental 2,8 Ma | Preservado | Referencia de campaña hominina y reconstrucción. |
| Inventario Eukaryota → *Homo sapiens* | Preservado | Apéndice A. |
| Clasificación detallada de primates | Preservada | Apéndice B y Campaña 6. |
| Inventario fósil y paleoantropológico | Preservado | Apéndice C y Campaña 7. |
| Advertencias terminológicas | Preservadas | Apéndice D. |
| Esquemas conceptuales | Preservados y ampliados | Apéndice E. |
| Checklist, DoD y riesgos | Actualizados sin pérdida | Secciones 27–29 y Apéndice H. |

## J.3. Decisiones supersedidas, no borradas

### DEC-018

Proponía 400.000–40.000 años como primer recorte. Se conserva en el registro como `SUPERSEDIDO`. `DEC-034` establece Eukaryota → Holozoa como primer lanzamiento; `DEC-035` conserva el contenido hominino.

### DEC-032

Posponía campañas profundas hasta validar homininos. Se conserva como `SUPERSEDIDO`. `DEC-033` invierte el orden y activa el desarrollo cronológico.

### DEC-016

Establecía «Atlas antes que simulación completa», es decir, el Atlas como etapa previa a la jugabilidad. La `1.1.0` lo integra en el primer lanzamiento (§2.6). Se conserva como `SUPERSEDIDO` y `DEC-049` lo reemplaza.

Esta decisión se había reescrito en el sitio conservando su identificador y su estado, sin marcarse. Corregido el 7 de agosto de 2026 mediante el procedimiento del Apéndice H.10.

### DEC-017

Proponía el modo Reconstrucción como primer modo jugable. La `1.1.0` lo reubica a campañas con evidencia adecuada y adelanta una lente científica ligera (§2.6, §21.3.2). Se conserva como `SUPERSEDIDO` y `DEC-050` lo reemplaza.

Misma corrección de trazabilidad y misma fecha que `DEC-016`.

## J.3.1. Reformulaciones editoriales sin cambio de compromiso

Detectadas el 7 de agosto de 2026 al comparar el registro contra el archivo. **No son supersesiones**: adaptan el enunciado a la estructura por campañas sin invertir ni recortar la decisión. Se anotan aquí para que ningún cambio quede silencioso.

| ID | Texto en `1.0.0` | Texto en `1.1.0` | Naturaleza |
|---|---|---|---|
| `DEC-015` | «La población es la unidad principal de simulación y juego.» | «…de simulación, especializada por campaña.» | Precisa el alcance; el compromiso con el juego permanece en §2.4 y §21.3.1. |
| `DEC-019` | «Tres vistas sincronizadas: mundo, red y ciencia.» | «…entorno, red y ciencia.» | Renombra una vista; §3.4 usa «Mundo o entorno» para la misma. |
| `DEC-021` | «Bandas poblacionales en la visualización temporal.» | «…cuando la escala lo permita.» | Añade condición de aplicabilidad, coherente con §20.5 y `OPEN-008`. |
| `DEC-025` | «Mutaciones comprables y progreso lineal.» | «Mutaciones **u orgánulos** comprables y progreso lineal.» | **Amplía** el rechazo para cubrir el contenido de la Campaña 1. |

## J.4. Capacidades protegidas mediante fixtures futuros

Aunque no se implementen en Campaña 1, el esquema debe seguir pasando estos casos:

- dos conceptos taxonómicos llamados Hominini;
- un linaje denisovano sin nombre específico estable;
- un espécimen con asignaciones alternativas;
- un evento de introgresión entre poblaciones;
- una taxonomía histórica superada;
- un rango fósil observado distinto del rango inferido;
- una vista de consenso y varias alternativas.

## J.5. Regla para futuras revisiones

Toda revisión estratégica debe incluir:

1. archivo de la versión anterior;
2. hash;
3. decisiones nuevas;
4. decisiones supersedidas;
5. matriz de migración;
6. actualización de fases;
7. actualización del trabajo pospuesto;
8. pruebas de preservación;
9. explicación de qué no cambió.

---

# Conclusión

La forma activa del proyecto es:

> **Una base de conocimiento científico versionada y centrada en afirmaciones, capaz de generar múltiples redes evolutivas coherentes y de proyectarlas hacia un juego poblacional desarrollado cronológicamente por campañas.**

El núcleo acepta incertidumbre, taxonomías rivales, evidencia parcial y procesos reticulados sin colapsarlos en un árbol único. El juego utiliza esa complejidad para producir decisiones, descubrimiento y narrativas emergentes, no para decorar una escalera de progreso.

El desarrollo comienza con una campaña completa entre Eukaryota y Holozoa. Esa campaña implementa el mínimo núcleo científico, el Atlas, la red temporal, una lente de evidencia y un bucle de evolución centrado en poblaciones celulares, simbiosis e integración. Después, cada campaña añade únicamente los sistemas necesarios para su escala.

El trabajo sobre homininos no se descarta ni se reduce. Permanece como especificación de destino, conjunto de pruebas, inventario científico y campaña culminante. Cuando el proyecto llegue allí, la plataforma ya habrá validado identidad, eventos, hipótesis, visualización, simulación, producción y lanzamiento en varias escalas anteriores.

El nuevo orden no reduce la ambición. La convierte en una secuencia ejecutable y verificable.
