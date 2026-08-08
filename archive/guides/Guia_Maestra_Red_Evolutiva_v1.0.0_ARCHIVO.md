# Guía maestra de desarrollo
## Red evolutiva humana, base de conocimiento científico y juego

**Estado:** documento rector inicial  
**Fecha de consolidación:** 5 de agosto de 2026  
**Versión de la guía:** 1.0.0  
**Alcance:** arquitectura científica, modelo de datos, flujo de investigación, visualización, validación, hoja de ruta y diseño preliminar del juego.

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

---

# 0. Propósito de esta guía

Esta guía consolida todo lo discutido hasta ahora sobre el proyecto y organiza las decisiones en un orden que pueda implementarse. No es un prompt operativo ni una especificación cerrada de producto. Es el documento rector que explica:

1. qué se está construyendo;
2. qué problemas debe resolver;
3. qué decisiones ya se adoptaron;
4. qué propuestas se conservan como dirección de diseño;
5. qué alternativas se rechazaron;
6. qué trabajo se pospuso;
7. qué decisiones siguen abiertas;
8. en qué orden debe desarrollarse el sistema;
9. cómo comprobar que cada etapa está terminada;
10. cómo conectar la base científica con el juego sin deformar ninguna de las dos.

La guía debe mantenerse versionada. Cualquier cambio importante en identidad de entidades, semántica de campos, tratamiento de hipótesis, persistencia, visualización o mecánicas debe registrarse mediante una decisión arquitectónica explícita y no mediante una modificación silenciosa.

---

# 1. Cómo interpretar el estado de una decisión

Cada decisión de esta guía utiliza uno de estos estados:

| Estado | Significado |
|---|---|
| **DECIDIDO** | Forma parte de la arquitectura actual y debe implementarse salvo que una decisión posterior la reemplace. |
| **RETENIDO** | Es una propuesta de diseño valiosa que se conserva, pero debe validarse mediante prototipo antes de tratarla como definitiva. |
| **POSPUESTO** | Está contemplado por la arquitectura, pero no debe implementarse todavía. Incluye el criterio que habilitará retomarlo. |
| **RECHAZADO** | No debe utilizarse porque contradice los objetivos científicos, técnicos o de diseño. |
| **ABIERTO** | Hace falta decidirlo en una fase posterior, cuando existan datos suficientes. |

Una idea puede ser científicamente válida y, aun así, estar pospuesta por costo o falta de dependencias. Posponer no equivale a descartar. Ese matiz evita que el backlog se convierta en un cementerio donde todas las ideas figuran como “quizá algún día”, la forma corporativa de la vida después de la muerte.

---

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

## 2.4. La población será la unidad principal del juego

**DECIDIDO para la dirección de diseño:** el jugador no controlará especies como unidades rígidas ni comprará mutaciones en un árbol de habilidades. Controlará, observará o reconstruirá **poblaciones**.

Las especies, taxones y clados serán:

- entidades científicas;
- agrupaciones interpretativas;
- resultados emergentes de procesos poblacionales;
- unidades de navegación o presentación;
- nunca niveles de poder.

## 2.5. Tres niveles de realidad

**RETENIDO como principio central del juego:** el sistema distinguirá:

```text
HISTORIA BIOLÓGICA OCURRIDA
        ↓ deja restos parciales
REGISTRO FÓSIL, ARQUEOLÓGICO Y GENÉTICO
        ↓ es interpretado
HIPÓTESIS DEL JUGADOR O DE LA COMUNIDAD CIENTÍFICA
```

Esta separación permite que una misma infraestructura alimente una simulación evolutiva, un modo de reconstrucción científica y un atlas educativo.

## 2.6. Estrategia de implementación

**DECIDIDO:** se desarrollará primero el núcleo científico y sus herramientas de validación. Después se construirán, en este orden recomendado:

1. un explorador o Atlas;
2. un prototipo de Reconstrucción;
3. el núcleo de simulación poblacional;
4. el modo Evolución completo;
5. campañas de escala profunda.

El orden reduce el riesgo de desarrollar una simulación gigantesca sobre datos sin identidad estable. La humanidad ya ha producido suficientes sistemas complejos cuya base es “por ahora funciona”.

## 2.7. Primer recorte vertical

**RETENIDO y recomendado:** utilizar como piloto el período aproximado entre **400.000 y 40.000 años**, centrado en:

- *Homo sapiens*;
- neandertales;
- denisovanos;
- poblaciones arcaicas no identificadas;
- *Homo floresiensis*;
- *Homo luzonensis*;
- fósiles asiáticos de asignación discutida;
- migración, aislamiento, introgresión, extinción, absorción y evidencia incompleta.

Este recorte contiene casi todos los problemas difíciles del proyecto sin exigir simular cuatro mil millones de años en la primera versión.

---

# 3. Visión del producto

## 3.1. Nombre provisional

**RAMAS: Una historia de la humanidad** es el título provisional. No está adoptado como nombre comercial y puede cambiar.

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

**RETENIDO:** tres vistas sincronizadas:

1. **Mundo:** geografía, clima, biomas, recursos, barreras, migraciones y poblaciones.
2. **Red evolutiva:** divergencias, persistencias, extinciones, reticulaciones y cambios de interpretación.
3. **Tablero científico:** especímenes, fuentes, dataciones, caracteres, análisis, hipótesis y controversias.

Cada modo podrá priorizar una vista, pero las tres deben compartir la misma identidad de entidades.

---

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

---

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

La primera versión no debe intentar representar exhaustivamente todos esos niveles. Debe demostrar que el modelo funciona con un caso que incluya:

- conceptos taxonómicos alternativos;
- poblaciones;
- especímenes;
- fechas inciertas;
- flujo génico;
- varias fuentes;
- dos o más hipótesis incompatibles;
- una vista de consenso;
- una vista histórica;
- una proyección simple de juego.

---

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

## 6.8. Capa 8: proyección de juego

La proyección de juego referencia entidades, afirmaciones, eventos y vistas científicas, pero mantiene sus propios datos:

- rol jugable;
- abstracción utilizada;
- requisitos de campaña;
- variables de simulación;
- mecánicas;
- efectos;
- condiciones de aparición;
- simplificaciones;
- advertencias científicas;
- justificación de diseño.

No se almacenará dentro de cada nodo científico.

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

| Tipo | Responsabilidad | Fase mínima |
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
  "object": { "entity_id": "TAXCONCEPT-B" },
  "context_ids": ["HYP-000003"],
  "asserted_by": ["SRC-000017"],
  "passage_ids": ["PASSAGE-000991"],
  "acceptance": "mixed",
  "evidence_strength": "medium",
  "resolution": "partially_resolved",
  "historical_status": "current",
  "record_status": "active",
  "quantitative_support": null,
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
not_assessed
```

Describe la recepción general, no la fuerza lógica interna de una hipótesis.

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
superseded
archived
```

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
  "participant_roles": [
    { "entity_id": "POP-A", "role": "donor" },
    { "entity_id": "POP-B", "role": "recipient" }
  ],
  "temporal_expression_id": "TIME-000030",
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

- grupos de conflicto;
- conjuntos de afirmaciones mutuamente excluyentes;
- requisitos de una hipótesis;
- escenarios o “mundos” compatibles;
- validadores automáticos cuando sea posible.

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
│   ├── GLOSSARY.md
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
│   │   └── issues.jsonl
│   ├── classifications/
│   ├── views/
│   ├── deltas/
│   └── snapshots/
├── game/
│   ├── projections/
│   ├── campaigns/
│   ├── mechanics/
│   └── prototypes/
├── schemas/
│   ├── json-schema/
│   └── migrations/
├── scripts/
│   ├── ingest/
│   ├── validate/
│   ├── build-views/
│   └── snapshot/
├── tests/
│   ├── fixtures/
│   ├── schema/
│   ├── validation/
│   ├── views/
│   └── simulation/
└── generated/
    ├── reports/
    ├── diagrams/
    └── exports/
```

La estructura puede simplificarse al inicio, pero las responsabilidades deben mantenerse separadas.

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
| `REGION-` | región |
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
| `GAME-` | proyección de juego |
| `ISSUE-` | cuestión pendiente |
| `TERM-` | término no resuelto |
| `TIME-` | expresión temporal reutilizable |

`EDGE-` se reserva para aristas materializadas en una exportación o vista. No será la identidad canónica de una afirmación científica.

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

Ejecutar validaciones de:

- esquema;
- referencias;
- cobertura;
- identidad;
- tiempo;
- geografía;
- hipótesis;
- topología;
- procedencia;
- estado;
- separación ciencia-juego.

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

El informe no debe repetir todo el JSON. Debe contener:

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

### Hipótesis

- afirmaciones incompatibles no seleccionadas en el mismo escenario;
- requisitos satisfechos;
- topología coherente;
- fuentes y contraevidencias vinculadas.

### Evidencia

- soporte cuantitativo con tipo y fuente;
- no hay porcentajes inventados;
- la evidencia respalda la afirmación indicada;
- fuente general y localizador específico cuando estén disponibles.

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
validate:provenance
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

Esta sección conserva todo lo propuesto hasta ahora, indicando qué está decidido y qué necesita prototipo.

## 21.1. Premisa jugable

**DECIDIDO como dirección:** el juego no consiste en “subir” desde un organismo primitivo hasta el humano moderno. Consiste en producir, atravesar y reconstruir historias evolutivas poblacionales.

## 21.2. Modos principales

### Modo Evolución

**RETENIDO.** El jugador guía poblaciones mediante decisiones ecológicas, geográficas, sociales y culturales indirectas.

Puede influir en:

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

No elige directamente mutaciones concretas. La variación aparece dentro de límites históricos, anatómicos, genéticos y ambientales.

Posibles objetivos:

- atravesar una crisis climática;
- mantener diversidad;
- colonizar una región;
- sostener varios linajes coexistentes;
- evitar absorción o extinción;
- producir redes culturales;
- persistir con una estrategia especializada;
- explorar historias contrafactuales.

No existe obligación de producir *Homo sapiens*.

### Modo Reconstrucción

**RETENIDO y prioritario para el primer prototipo jugable.** El jugador investiga una historia oculta mediante evidencia incompleta.

Acciones previstas:

- elegir regiones o colecciones;
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

No debe premiar únicamente acertar el árbol oculto.

### Atlas evolutivo

**DECIDIDO como primer producto visible.** Permite navegar entidades, afirmaciones, eventos, hipótesis y vistas.

Cada nodo puede mostrar:

- definición;
- rango o función;
- edad observada e inferida;
- distribución;
- grupos incluidos;
- ramas hermanas dentro de una vista;
- caracteres;
- fósiles;
- nombres alternativos;
- controversias;
- fuentes;
- confianza y aceptación por dimensión;
- historia de cambios.

## 21.3. Tres vistas sincronizadas

| Vista | Contenido |
|---|---|
| Mundo | clima, regiones, biomas, barreras, recursos, rutas y poblaciones |
| Red | divergencia, persistencia, extinción, reticulación, eventos y vistas alternativas |
| Ciencia | fósiles, muestras, dataciones, análisis, publicaciones, hipótesis y debates |

## 21.4. Variables poblacionales previstas

| Dimensión | Variables posibles |
|---|---|
| Demografía | tamaño efectivo, edad, natalidad, mortalidad, densidad, cuellos de botella |
| Geografía | territorio, movilidad, conectividad, aislamiento, corredores |
| Ecología | dieta, hábitat, estacionalidad, depredación, patógenos, competencia |
| Genética | diversidad, deriva, flujo génico, carga, ancestría |
| Anatomía | locomoción, dentición, manos, termorregulación, desarrollo |
| Conducta | cooperación, conflicto, exploración, cuidado parental |
| Cultura | herramientas, fuego, aprendizaje, tradición, simbolismo |
| Registro futuro | fosilización, preservación, detectabilidad, sesgo de muestreo |

No todas se implementarán en la primera simulación.

## 21.5. Bucle del modo Evolución

### 1. Cambio ambiental

Posibles factores:

- ciclos glaciales;
- aridificación;
- expansión o contracción de bosques;
- cambios costeros;
- erupciones;
- corredores migratorios;
- fauna, competidores y patógenos.

El clima modifica posibilidades, no prescribe mutaciones.

### 2. Respuesta poblacional

La población puede:

- permanecer;
- migrar;
- dividirse;
- ampliar o restringir dieta;
- establecer contacto;
- competir;
- intercambiar;
- evitar otros grupos.

### 3. Variación

Las variantes tienen beneficios y costos. Ejemplos de compensaciones:

- mayor cerebro frente a costo energético y desarrollo prolongado;
- bipedalismo frente a restricciones anatómicas;
- especialización dental frente a flexibilidad;
- cooperación frente a vulnerabilidad a explotación;
- infancia prolongada frente a mayor dependencia.

### 4. Cambio de frecuencias

Mecanismos:

- selección natural;
- selección sexual;
- deriva;
- efecto fundador;
- flujo génico;
- herencia cultural;
- aprendizaje social.

### 5. Divergencia y reconexión

Se evalúan:

- aislamiento;
- distancia;
- compatibilidad;
- contacto;
- diferenciación ecológica;
- tamaño;
- cultura;
- duración.

La especiación emerge; no se activa con un botón.

### 6. Producción de registro

Las poblaciones dejan rastros con probabilidad desigual:

- huesos;
- dientes;
- herramientas;
- huellas;
- hogares;
- sedimentos;
- proteínas;
- ADN;
- modificaciones de fauna.

La mayoría se pierde.

## 21.6. Bucle del modo Reconstrucción

1. formular una pregunta;
2. asignar recursos;
3. obtener evidencia;
4. evaluar calidad y sesgos;
5. construir una o varias hipótesis;
6. publicar o conservar provisionalmente;
7. recibir revisión y nueva evidencia;
8. revisar, fusionar, dividir o abandonar conceptos.

## 21.7. Taxonomía dentro del juego

Los rangos sirven para:

- navegación;
- organización;
- comparación;
- herencia histórica de restricciones;
- objetivos didácticos;
- desbloqueo de herramientas de análisis;
- definición de campañas.

No sirven como:

- niveles de poder;
- etapas de progreso;
- mejoras acumulativas;
- indicador de superioridad.

## 21.8. Condiciones de éxito

**ABIERTO en detalle.** Principios ya establecidos:

- no debe existir una única victoria llamada “producir humanos”;
- la supervivencia no equivale siempre a éxito;
- una extinción puede formar parte de una campaña científicamente significativa;
- la reconstrucción debe premiar incertidumbre bien calibrada;
- el modo Evolución puede evaluar persistencia, diversidad, expansión, resiliencia o historia producida.

## 21.9. Historia oculta y evidencia generada

**RETENIDO como arquitectura fuerte del juego:** una partida puede generar:

1. una historia poblacional completa y oculta;
2. un módulo tafonómico que decide qué rastros sobreviven;
3. un módulo de descubrimiento que decide qué evidencia encuentra el jugador;
4. un espacio de hipótesis construido a partir de esa evidencia.

Esto convierte la base científica en parte del diseño, no en una enciclopedia pegada al menú.

## 21.10. Ejemplo de escenario de diseño

África oriental, alrededor de 2,8 millones de años:

- población australopiteca flexible;
- población aislada;
- formas robustas tempranas;
- *Homo* temprano escaso.

Una aridificación fragmenta hábitats. Algunas poblaciones intercambian genes, otras se especializan, una desaparece sin registro y otra deja solo dientes. En el modo Reconstrucción, el jugador debe evaluar si los restos representan variación, dimorfismo, varias especies o información insuficiente.

Este escenario es una referencia conceptual, no el primer recorte técnico obligatorio.

---

# 22. Campañas y escalas de juego

No se usarán las mismas reglas con idéntica resolución desde los primeros eucariotas hasta *Homo sapiens*.

## Campaña I. Simbiosis

**POSPUESTA.** Desde la evolución eucariota hasta la multicelularidad.

Mecánicas potenciales:

- endosimbiosis;
- transferencia horizontal;
- cooperación celular;
- conflicto intracelular;
- diferenciación;
- reproducción sexual.

## Campaña II. Cuerpos

**POSPUESTA.** Desde Metazoa hasta Tetrapoda.

Mecánicas potenciales:

- planes corporales;
- desarrollo;
- locomoción;
- respiración;
- transición acuática-terrestre;
- redes ecológicas;
- extinciones masivas.

## Campaña III. Herencia sinápsida

**POSPUESTA.** Desde Synapsida hasta los primeros primates.

Mecánicas potenciales:

- termorregulación;
- dentición;
- reproducción;
- desarrollo;
- nichos nocturnos;
- radiación mamaliana;
- vida arbórea.

## Campaña IV. Primates

**POSPUESTA.** Desde primates tempranos hasta Hominoidea.

Mecánicas potenciales:

- visión;
- prensión;
- dieta;
- locomoción arbórea;
- sociabilidad;
- biogeografía.

## Campaña V. Homininos

**RETENIDA como campaña principal futura.** Capítulos conceptuales:

1. **El último ancestro común**, 8–5 Ma.
2. **El mosaico australopiteco**, 4,5–2,8 Ma.
3. **Tres formas de ser hominino**, 3–1,5 Ma.
4. **La primera expansión**, 2–0,8 Ma.
5. **Humanidades entrelazadas**, 800.000–40.000 años.
6. **Una humanidad superviviente**, 300.000 años–presente.

El capítulo 5 es el candidato recomendado para el primer recorte jugable.

---

# 23. Qué no se hará

## 23.1. Rechazos científicos

**RECHAZADO:**

- una escalera lineal de progreso;
- “pez → anfibio → reptil → mamífero → mono → humano” como secuencia literal;
- chimpancés modernos como antepasados humanos;
- taxones como equivalentes automáticos de clados;
- especies fósiles como ancestros directos por defecto;
- ausencia de fósiles como ausencia biológica;
- razas humanas modernas como ramas taxonómicas discretas;
- categorías históricas presentadas como vigentes;
- convergencia dibujada como ascendencia;
- hibridación confundida con incertidumbre topológica.

## 23.2. Rechazos de diseño

**RECHAZADO:**

- barra universal de inteligencia;
- mutaciones compradas como mejoras lineales;
- especies como personajes rígidos;
- *Homo sapiens* como victoria obligatoria;
- “primitivo” como sinónimo de inferior;
- rangos taxonómicos como niveles;
- un único árbol mostrado como verdad;
- cada fósil como una nueva especie;
- usar complejidad científica solo como decoración.

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
- dibujar todas las hipótesis incompatibles en una sola topología.

---

# 24. Hoja de ruta de desarrollo

La hoja de ruta está organizada por dependencias. No debe saltarse una fase solo porque la interfaz posterior resulte más entretenida.

## Fase 0. Constitución del proyecto

### Objetivo

Crear el marco de trabajo y fijar el vocabulario mínimo.

### Tareas

1. crear repositorio;
2. incorporar esta guía;
3. crear registro de decisiones arquitectónicas;
4. definir convenciones de IDs;
5. definir formato de secciones y fuentes;
6. elegir lenguaje para herramientas iniciales;
7. configurar validación y pruebas básicas;
8. crear un glosario inicial;
9. definir política de contribución y revisión científica.

### Entregables

- estructura de carpetas;
- `README`;
- guía versionada;
- ADR inicial;
- plantilla de sección;
- plantilla de fuente;
- esquema mínimo de IDs;
- comando de validación vacío pero ejecutable.

### Criterios de aceptación

- el repositorio puede clonarse y validarse;
- las decisiones abiertas están registradas;
- no existe dependencia del motor de juego;
- se puede crear una sección vacía válida.

### No incluye

- taxonomía real;
- interfaz;
- base de datos;
- simulación.

## Fase 1. Corpus y menciones

### Objetivo

Conservar fielmente investigación incremental y demostrar cobertura exhaustiva.

### Tareas

1. implementar `Section`, `Passage`, `Mention`, `Source`, `Issue`;
2. conservar texto original y hash;
3. registrar localizadores;
4. implementar tabla de cobertura;
5. crear operaciones y deltas;
6. construir validadores de IDs, esquema y cobertura;
7. crear primer fixture artificial.

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
- el snapshot se reconstruye desde cero.

## Fase 2. Identidad biológica y taxonómica

### Objetivo

Resolver la separación entre nombres, conceptos, clados, linajes, poblaciones y especímenes.

### Tareas

1. implementar tipos de entidad;
2. implementar alias y nombres originales;
3. modelar conceptos taxonómicos según fuente;
4. permitir rangos contextualizados;
5. registrar sinonimias propuestas;
6. implementar fusiones reversibles;
7. crear validadores de homónimos y duplicados;
8. crear una pequeña clasificación de prueba con dos usos incompatibles del mismo nombre.

### Entregables

- esquemas de entidades;
- resolutor de identidad asistido;
- informe de posibles duplicados;
- fixture de taxonomías alternativas.

### Criterios de aceptación

- un mismo nombre puede referir a dos conceptos;
- un concepto puede cambiar de rango entre vistas;
- una fusión no destruye referencias;
- un espécimen no puede convertirse accidentalmente en taxón.

## Fase 3. Afirmaciones, evidencia y análisis

### Objetivo

Convertir el sistema en una base de conocimiento trazable.

### Tareas

1. implementar `Claim`;
2. implementar dimensiones epistemológicas;
3. implementar evidencia, datasets, análisis y resultados;
4. vincular afirmaciones a pasajes;
5. almacenar soporte cuantitativo exacto;
6. modelar afirmaciones negativas y conflictos;
7. distinguir afirmaciones expresas de derivadas;
8. crear consultas de procedencia.

### Entregables

- esquemas;
- validador de procedencia;
- informe “por qué aparece esta relación”;
- fixture con dos fuentes en conflicto.

### Criterios de aceptación

- toda relación visible puede explicarse mediante afirmaciones;
- una fuente puede apoyar una afirmación y cuestionar otra;
- no existe confianza sin razón;
- un cambio de aceptación no altera la identidad de la entidad.

## Fase 4. Tiempo, geografía y ocurrencias

### Objetivo

Representar presencia, rangos y compatibilidad temporal sin confundir evidencia y origen.

### Tareas

1. implementar tipos de fecha;
2. intervalos e incertidumbre;
3. ocurrencias;
4. yacimientos y regiones;
5. validación de coexistencia;
6. advertencias por inversión de rangos observados;
7. unidades y conversiones;
8. primera línea temporal generada.

### Entregables

- esquema temporal;
- esquema geográfico mínimo;
- validadores;
- visualización temporal.

### Criterios de aceptación

- observado e inferido no se confunden;
- una divergencia puede ser intervalo;
- el sistema no rechaza automáticamente un ancestro por sesgo fósil;
- las ubicaciones inciertas están marcadas.

## Fase 5. Eventos y reticulación

### Objetivo

Representar procesos n-arios y no arbóreos.

### Tareas

1. implementar eventos y roles;
2. divergencia;
3. migración;
4. hibridación e introgresión;
5. extinción y absorción;
6. relaciones derivadas;
7. validación de participantes, tiempo y lugar;
8. exportación visual de eventos.

### Entregables

- esquema de eventos;
- fixture de introgresión;
- diagrama reticulado;
- validador temporal.

### Criterios de aceptación

- un evento admite varios participantes;
- roles producen relaciones derivadas coherentes;
- el evento puede estar disputado sin duplicar entidades;
- una hibridación no se confunde con una topología alternativa.

## Fase 6. Hipótesis y vistas

### Objetivo

Construir topologías y clasificaciones coherentes a partir de afirmaciones.

### Tareas

1. implementar `Hypothesis`;
2. grupos de conflicto;
3. escenarios compatibles;
4. `ClassificationView`;
5. `PhylogeneticView`;
6. backbone fechado;
7. vistas históricas;
8. invalidación y reconstrucción de vistas;
9. exportación Graphviz y formatos filogenéticos.

### Entregables

- dos topologías incompatibles del mismo fixture;
- vista de trabajo;
- vista histórica;
- reporte de diferencias.

### Criterios de aceptación

- ninguna vista mezcla afirmaciones incompatibles;
- cada arista visible puede rastrearse;
- cambiar una hipótesis reconstruye la vista sin modificar datos primarios;
- el backbone declara criterios y fecha.

## Fase 7. Pipeline de ingestión completo

### Objetivo

Automatizar el protocolo de sección sin entregar decisiones científicas delicadas a una caja negra.

### Tareas

1. comando `ingest:section`;
2. extracción asistida de menciones;
3. propuesta de normalización;
4. propuesta de afirmaciones;
5. revisión humana;
6. delta;
7. validación;
8. informe humano;
9. snapshot;
10. rollback.

### Entregables

- flujo end-to-end;
- interfaz de revisión mínima;
- logs;
- documentación.

### Criterios de aceptación

- ninguna propuesta automática se acepta sin trazabilidad;
- el sistema puede continuar ante ambigüedades no centrales;
- los errores bloqueantes detienen el commit;
- el estado es reproducible.

## Fase 8. Piloto científico real

### Objetivo

Probar el sistema con un dominio acotado pero científicamente difícil.

### Recorte recomendado

Sapiens, neandertales, denisovanos y humanos asiáticos del Pleistoceno medio/tardío.

### Tareas

1. seleccionar corpus;
2. ingresar fuentes y secciones;
3. modelar conceptos taxonómicos;
4. modelar poblaciones y especímenes;
5. registrar eventos de flujo génico;
6. construir al menos tres vistas;
7. auditar el resultado;
8. documentar fallas del esquema.

### Criterios de aceptación

- el caso completo no requiere hacks semánticos;
- pueden coexistir denisovanos como linaje y varios nombres taxonómicos propuestos;
- Harbin u otro caso análogo puede tener asignaciones alternativas;
- la vista de consenso y las alternativas son comprensibles;
- la procedencia es suficiente para revisión científica.

## Fase 9. Atlas MVP

### Objetivo

Crear la primera interfaz útil para navegar el conocimiento.

### Funciones mínimas

- búsqueda;
- ficha de entidad;
- línea temporal;
- mapa básico;
- vista filogenética;
- selector de hipótesis;
- historial taxonómico;
- procedencia;
- comparación entre vistas;
- filtros por escala y evidencia.

### Criterios de aceptación

- el usuario puede responder por qué una entidad aparece en determinada posición;
- puede cambiar de clasificación sin perder identidad;
- puede distinguir hecho, inferencia, hipótesis y estado histórico;
- la interfaz no depende solo del color.

## Fase 10. Reconstrucción MVP

### Objetivo

Transformar el núcleo científico en una experiencia jugable de inferencia.

### Funciones mínimas

- historia oculta predefinida;
- conjunto limitado de especímenes;
- presupuesto o turnos;
- selección de análisis;
- construcción de dos o más hipótesis;
- publicación;
- evaluación de ajuste e incertidumbre;
- aparición de nueva evidencia;
- revisión.

### Criterios de aceptación

- el jugador puede conservar “sin resolver” como resultado válido;
- no existe una única acción óptima basada en desbloquear tecnología;
- la puntuación separa acierto, evidencia y calibración;
- el escenario es rejugable mediante evidencia parcial.

## Fase 11. Núcleo de simulación poblacional

### Objetivo

Simular poblaciones antes de construir un modo Evolución completo.

### Variables mínimas recomendadas

- tamaño efectivo;
- ubicación;
- movilidad;
- conectividad;
- recursos abstractos;
- diversidad genética abstracta;
- contacto;
- flujo génico;
- persistencia/extinción.

### Tareas

1. modelo de tiempo;
2. actualización demográfica;
3. división;
4. migración;
5. contacto;
6. introgresión;
7. cuellos de botella;
8. registro de historia completa;
9. determinismo por semilla;
10. exportación al grafo científico.

### Criterios de aceptación

- la misma semilla reproduce la historia;
- no aparecen ciclos temporales;
- la especiación no es un botón;
- el modelo produce historias diferentes sin violar invariantes;
- los eventos pueden convertirse en evidencia parcial.

## Fase 12. Tafonomía y producción de evidencia

### Objetivo

Separar historia ocurrida de historia observable.

### Tareas

- probabilidad de preservación;
- sesgo por tejido y ambiente;
- destrucción;
- descubrimiento;
- contaminación;
- datación imperfecta;
- muestreo geográfico;
- generación de especímenes y ocurrencias;
- vinculación con historia oculta.

### Criterios de aceptación

- el registro observable es incompleto y sesgado;
- una historia puede producir varias interpretaciones plausibles;
- el jugador no accede directamente a la verdad simulada.

## Fase 13. Modo Evolución MVP

### Objetivo

Permitir intervención indirecta sobre poblaciones.

### Alcance mínimo

- una región;
- varias poblaciones;
- clima abstracto;
- movilidad;
- recursos;
- contacto;
- cultura abstracta;
- reproducción;
- divergencia;
- mezcla;
- extinción;
- objetivos alternativos.

### Criterios de aceptación

- no existe árbol de mejoras teleológico;
- toda ventaja tiene costos o contexto;
- múltiples estrategias pueden persistir;
- el jugador influye, no diseña genomas;
- el resultado se registra como historia compatible con el Atlas.

## Fase 14. Integración de modos

### Objetivo

Usar una partida de Evolución como historia oculta para Reconstrucción y Atlas.

### Criterios de aceptación

- la historia simulada produce corpus de evidencia;
- Reconstrucción puede analizarlo;
- Atlas muestra verdad, evidencia e interpretación en capas separadas;
- las proyecciones no contaminan el núcleo científico real.

## Fase 15. Expansión científica y campañas

### Objetivo

Extender escalas y mecánicas solo después de validar el núcleo.

Orden sugerido:

1. homininos;
2. hominoideos;
3. primates;
4. mamíferos y sinápsidos;
5. tetrápodos y vertebrados;
6. animales;
7. eucariogénesis y simbiosis.

Cada expansión puede requerir un módulo de simulación distinto.

---

# 25. Trabajo pospuesto

Esta sección es parte del plan. Nada de lo siguiente debe desaparecer del proyecto solo porque no entra en el MVP.

## 25.1. Granularidad molecular fina

**POSPUESTO:**

- genes individuales;
- alelos;
- haplotipos;
- regiones cromosómicas;
- genomas ancestrales;
- virus endógenos;
- transferencia bacteriana concreta;
- duplicaciones génicas detalladas;
- conflictos entre árboles génicos.

### Motivo

Requiere identidad molecular, coordenadas, ensamblajes, versiones de referencia y modelos de herencia propios.

### Disparador

Retomar cuando el piloto poblacional necesite explicar introgresión por regiones genómicas o una campaña de eucariogénesis.

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

La cultura necesita su propia identidad, eventos, herencia y relación con poblaciones. Modelarla como un atributo simple sería insuficiente.

### Disparador

Retomar después de que `Population`, `Event` y tiempo funcionen en el modo Evolución básico.

## 25.3. Ecosistemas y paleogeografía dinámica

**POSPUESTO:**

- biomas detallados;
- redes tróficas;
- paleocostas;
- tectónica;
- cambios de ríos;
- reconstrucción climática espacial;
- especies ecológicas no directamente vinculadas con la filogenia humana.

### Motivo

Aumenta enormemente el estado de simulación y puede desviar el proyecto hacia un simulador planetario antes de validar poblaciones.

### Disparador

Retomar cuando una campaña concreta necesite corredores, islas, recursos o interacción ecológica no representables mediante regiones abstractas.

## 25.4. Historia completa de la vida

**POSPUESTO como carga de datos, no como capacidad del esquema.**

El esquema debe soportarla desde el diseño, pero la ingestión se hará por dominios. No se cargará cada taxón conocido antes del primer prototipo.

### Disparador

Completar una escala solo cuando exista:

- objetivo científico;
- campaña;
- corpus;
- responsable de revisión;
- prueba de que la interfaz puede mostrarla.

## 25.5. Exhaustividad de todos los rangos

**POSPUESTO en ingestión inicial:** registrar desde el principio cualquier rango que aparezca, pero no poblar preventivamente cada infraorden, parvorden, cohorte, magnorden, tribu o subtribu del árbol de la vida.

### Disparador

Una fuente, vista o campaña requiere ese rango.

## 25.6. Compatibilidad automática completa

**POSPUESTO:** razonador que determine compatibilidad lógica entre todas las hipótesis.

### Motivo

La compatibilidad puede depender de identidad, definición, tiempo, taxonomía y supuestos no formalizados.

### Disparador

Cuando los grupos de conflicto manuales ya no escalen y existan suficientes fixtures para especificar reglas.

## 25.7. Inferencia probabilística

**POSPUESTO:** probabilidades bayesianas internas para hipótesis del juego o del sistema científico.

### Motivo

No deben confundirse con soporte publicado ni inventarse priors arbitrarios.

### Disparador

Una mecánica de Reconstrucción requiere un modelo explícito y validado, separado de la aceptación científica real.

## 25.8. Base de grafos, RDF y ontologías externas

**POSPUESTO:** adoptar Neo4j, RDF/OWL u otra infraestructura especializada.

### Motivo

Primero debe estabilizarse la semántica. Una base sofisticada no rescata un concepto taxonómico mal identificado; solo permite consultarlo con mucha velocidad.

### Disparador

Necesidades reales de consulta, interoperabilidad o razonamiento.

## 25.9. Editor colaborativo

**POSPUESTO:** interfaz multiusuario con permisos, revisión, comentarios y conflictos.

### Disparador

El proyecto deja de ser individual o la ingestión manual por Git se vuelve un cuello de botella.

## 25.10. Campañas de simbiosis, cuerpos, sinápsidos y primates

**POSPUESTAS** hasta validar el ciclo completo con homininos.

---

# 26. Decisiones todavía abiertas

Las siguientes decisiones no deben resolverse prematuramente. Cada una debe producir un ADR cuando llegue su fase.

| ID | Decisión | Momento adecuado |
|---|---|---|
| `OPEN-001` | Lenguaje principal de tooling | Fase 0 |
| `OPEN-002` | Formato definitivo de IDs opacos | Fase 0 |
| `OPEN-003` | Estilo bibliográfico y resolución de DOI | Fase 1–3 |
| `OPEN-004` | Representación de topologías: Newick, listas de clados o ambas | Fase 6 |
| `OPEN-005` | Framework del Atlas | Fase 9 |
| `OPEN-006` | Motor de juego | Antes de Fase 10–11 |
| `OPEN-007` | Base de datos de producción | Tras piloto real |
| `OPEN-008` | Semántica exacta del ancho de bandas | Fase 9 |
| `OPEN-009` | Sistema de puntuación de Reconstrucción | Fase 10 |
| `OPEN-010` | Modelo demográfico y paso temporal | Fase 11 |
| `OPEN-011` | Modelo de especie emergente | Fase 11–13 |
| `OPEN-012` | Nivel de determinismo y aleatoriedad | Fase 11 |
| `OPEN-013` | Condiciones de victoria | Fase 13 |
| `OPEN-014` | Nombre definitivo del juego | Después del prototipo |
| `OPEN-015` | Licencia de datos, código y contenido | Fase 0–1 |

## 26.1. Criterio general

Una decisión se toma cuando:

- existen dos o más alternativas reales;
- se conocen requisitos;
- puede evaluarse con un prototipo o benchmark;
- su costo de cambio comienza a crecer.

No se decide por entusiasmo tecnológico ni por la majestuosidad del logo de una base de datos.

---

# 27. Estrategia de pruebas

## 27.1. Pruebas de esquema

- registros válidos;
- registros inválidos;
- migraciones;
- compatibilidad entre versiones;
- enumeraciones;
- campos obligatorios.

## 27.2. Pruebas de identidad

- homónimos;
- sinónimos confirmados;
- sinonimias disputadas;
- cambios de nombre;
- cambios de rango;
- conceptos con el mismo nombre y contenido distinto;
- fusiones y deshacer fusiones.

## 27.3. Pruebas de procedencia

- toda afirmación llega a un pasaje;
- toda evidencia llega a una fuente;
- toda vista explica qué afirmaciones utiliza;
- registros externos están marcados como auditoría.

## 27.4. Pruebas temporales

- intervalos solapados;
- intervalos incompatibles;
- rangos observados frente a inferidos;
- eventos imposibles;
- ciclos de ascendencia;
- conversiones de unidades.

## 27.5. Pruebas de hipótesis

- escenarios compatibles;
- afirmaciones mutuamente excluyentes;
- topologías alternativas;
- invalidación de vistas;
- reconstrucción determinista.

## 27.6. Pruebas de visualización

- snapshots de Graphviz;
- leyendas;
- filtros;
- densidad;
- accesibilidad;
- equivalencia entre vista y afirmaciones seleccionadas.

## 27.7. Pruebas de simulación

- determinismo por semilla;
- conservación de invariantes;
- ausencia de tamaños negativos;
- migración temporalmente válida;
- introgresión con coexistencia;
- extinción terminal;
- reproducibilidad;
- distribución razonable de resultados.

## 27.8. Fixtures de referencia

Mantener conjuntos pequeños y comprensibles:

1. taxonomía con homónimo conceptual;
2. árbol con dos topologías incompatibles;
3. evento de introgresión;
4. fósil con varias asignaciones;
5. rango observado posterior al origen inferido;
6. hipótesis histórica superada;
7. proyección de juego simplificada.

## 27.9. Revisión científica humana

La validación automática no determina si una interpretación paleontológica es correcta. Debe existir revisión humana para:

- identidad dudosa;
- traducción de conceptos;
- calidad de evidencia;
- clasificación de aceptación;
- selección del backbone;
- simplificación jugable.

---

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
- tipo correcto;
- etiquetas y alias;
- procedencia;
- conflictos explícitos;
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
- exportación reproducible.

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
- justificación de simplificaciones.

---

# 29. Riesgos y mitigaciones

## 29.1. Expansión ilimitada del alcance

**Riesgo:** intentar cargar toda la evolución antes de validar una sección.

**Mitigación:** recorte vertical, fases, criterios de aceptación y backlog pospuesto explícito.

## 29.2. Sobreingeniería ontológica

**Riesgo:** pasar años diseñando categorías sin usuarios ni prototipo.

**Mitigación:** esquema mínimo por fase, fixtures concretos y prohibición de implementar tipos sin caso de uso.

## 29.3. Mezcla de taxonomía y biología

**Riesgo:** cambios de nombre alteran la historia representada.

**Mitigación:** nombre, concepto, clado, linaje y población separados.

## 29.4. Falsa precisión

**Riesgo:** números de confianza o fechas aparentan más certeza de la disponible.

**Mitigación:** soporte cuantitativo solo desde fuentes, intervalos, categorías cualitativas justificadas y separación observado/inferido.

## 29.5. Alucinación durante ingestión asistida

**Riesgo:** una herramienta agrega taxones, citas o relaciones ausentes.

**Mitigación:** corpus inmutable, pasajes, propuestas revisables, cobertura, procedencia obligatoria y auditoría separada.

## 29.6. Duplicación de entidades

**Riesgo:** alias, grafías o taxonomías alternativas crean nodos falsamente distintos.

**Mitigación:** libro de menciones, resolución conservadora, conceptos taxonómicos y fusiones reversibles.

## 29.7. Fusión excesiva

**Riesgo:** nombres parecidos o sinonimias propuestas eliminan diferencias reales.

**Mitigación:** conservar ambos conceptos mientras exista disputa; la sinonimia es una afirmación, no una orden automática.

## 29.8. Visualización ilegible

**Riesgo:** la red completa se vuelve un mapa extraterrestre de transporte público.

**Mitigación:** vistas por escala, filtros, pequeños múltiplos, zoom semántico, capas y visualizaciones locales.

## 29.9. Acoplamiento con el juego

**Riesgo:** modificar ciencia para encajar en mecánicas.

**Mitigación:** proyección externa, IDs, registro de simplificaciones y pruebas de separación.

## 29.10. Simulación teleológica

**Riesgo:** el sistema favorece inevitablemente cerebros grandes, cultura humana o supervivencia de *H. sapiens*.

**Mitigación:** compensaciones, objetivos múltiples, contingencia, costos energéticos, escenarios contrafactuales y ausencia de progreso universal.

## 29.11. Dependencia del chat

**Riesgo:** pérdida de decisiones y estado acumulado.

**Mitigación:** archivos, Git, deltas, snapshots y guía versionada.

---

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
| `DEC-015` | DECIDIDO | La población es la unidad principal de simulación y juego. |
| `DEC-016` | DECIDIDO | Atlas antes que simulación completa. |
| `DEC-017` | RETENIDO | Reconstrucción como primer modo jugable. |
| `DEC-018` | RETENIDO | Período 400.000–40.000 años como recorte vertical. |
| `DEC-019` | RETENIDO | Tres vistas sincronizadas: mundo, red y ciencia. |
| `DEC-020` | RETENIDO | Historia oculta → registro parcial → hipótesis del jugador. |
| `DEC-021` | RETENIDO | Bandas poblacionales en la visualización temporal. |
| `DEC-022` | RECHAZADO | Un único estado epistemológico. |
| `DEC-023` | RECHAZADO | JSON monolítico. |
| `DEC-024` | RECHAZADO | Relaciones reticuladas como flechas binarias sin evento. |
| `DEC-025` | RECHAZADO | Mutaciones comprables y progreso lineal. |
| `DEC-026` | RECHAZADO | *Homo sapiens* como victoria obligatoria. |
| `DEC-027` | POSPUESTO | Base de grafos o RDF. |
| `DEC-028` | POSPUESTO | Genes, alelos y transferencia molecular fina. |
| `DEC-029` | POSPUESTO | Cultura y lenguaje detallados. |
| `DEC-030` | POSPUESTO | Paleogeografía y ecosistemas completos. |
| `DEC-031` | POSPUESTO | Compatibilidad lógica automática exhaustiva. |
| `DEC-032` | POSPUESTO | Campañas anteriores a los homininos. |

---

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
                    └── Choanozoa sensu stricto / Apoikozoa según uso
                        └── Metazoa = Animalia
                            └── ParaHoxozoa
                                └── Planulozoa
                                    └── Bilateria
                                        └── Nephrozoa
                                            └── Deuterostomia, monofilia discutida
                                                └── Chordata
                                                    └── Olfactores
                                                        └── Vertebrata ≈ Craniata
                                                            └── Gnathostomata
                                                                └── Euteleostomi ≈ Osteichthyes crown
                                                                    └── Sarcopterygii
                                                                        └── Rhipidistia ≈ Dipnotetrapodomorpha según definición
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
                                                                                                                            └── Eutherapsida, uso no universal
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
                                                                                                                                                                            └── Theriiformes, definición variable
                                                                                                                                                                                └── Holotheria, definición variable
                                                                                                                                                                                    └── Trechnotheria
                                                                                                                                                                                        └── Cladotheria
                                                                                                                                                                                            └── Zatheria
                                                                                                                                                                                                └── Boreosphenida / Tribosphenida según definición
                                                                                                                                                                                                    └── Theria
                                                                                                                                                                                                        └── Eutheria
                                                                                                                                                                                                            └── Placentalia
                                                                                                                                                                                                                └── Boreoeutheria
                                                                                                                                                                                                                    └── Euarchontoglires
                                                                                                                                                                                                                        └── Euarchonta, posición de Scandentia variable
                                                                                                                                                                                                                            └── Primatomorpha
                                                                                                                                                                                                                                └── Primates
                                                                                                                                                                                                                                    └── Haplorhini / Haplorrhini
                                                                                                                                                                                                                                        └── Simiiformes = Anthropoidea aproximadamente
                                                                                                                                                                                                                                            └── Catarrhini
                                                                                                                                                                                                                                                └── Hominoidea
                                                                                                                                                                                                                                                    └── Hominidae
                                                                                                                                                                                                                                                        └── Homininae
                                                                                                                                                                                                                                                            └── Hominini, circunscripción dependiente de clasificación
                                                                                                                                                                                                                                                                └── Homo
                                                                                                                                                                                                                                                                    └── Homo sapiens
```

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
- †*Masripithecus*, propuesta reciente que requiere auditoría formal.

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
    "source_ids": ["SRC-000001"]
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
  "acceptance": "not_assessed",
  "evidence_strength": "unknown",
  "resolution": "unresolved",
  "historical_status": "current",
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
  "scale": "hominins",
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
  "campaign_id": null,
  "playable_role": null,
  "abstraction": "",
  "mechanic_hooks": [],
  "scientific_constraints": [],
  "simplifications": [],
  "justification": "",
  "status": "draft"
}
```

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
2. fijar `schema_version` inicial;
3. crear archivos JSONL vacíos válidos;
4. crear manifiesto del dataset;
5. crear leyenda visual básica;
6. crear glosario mínimo;
7. crear primer snapshot vacío;
8. ejecutar todas las validaciones;
9. no agregar taxones por conocimiento general;
10. procesar inmediatamente una sección solo cuando haya sido entregada como corpus.

Estado inicial conceptual:

```json
{
  "schema_version": "1.0.0",
  "dataset_revision": "REV-000000",
  "snapshot_id": "SNAP-000000",
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

- [ ] Incorporar esta guía al repositorio.
- [ ] Crear ADR-001 con la arquitectura claim-centric.
- [ ] Confirmar estructura de carpetas.
- [ ] Elegir lenguaje de tooling.
- [ ] Definir convención de IDs.
- [ ] Definir licencia.
- [ ] Definir formato de citas.
- [ ] Crear esquema inicial.
- [ ] Crear fixture vacío.
- [ ] Crear CI de validación.

## H.2. Antes de ingresar investigación real

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

## H.4. Antes de modelar flujo génico

- [ ] Poblaciones identificadas.
- [ ] Eventos y roles.
- [ ] Coexistencia temporal.
- [ ] Contexto geográfico.
- [ ] Evidencia.
- [ ] Dirección o bidireccionalidad.
- [ ] Distinción entre evento y señal genética.
- [ ] Relaciones derivadas.

## H.5. Antes del Atlas

- [ ] Piloto científico real validado.
- [ ] Vistas reproducibles.
- [ ] Procedencia navegable.
- [ ] Comparación de hipótesis.
- [ ] Leyenda accesible.
- [ ] Zoom semántico definido.
- [ ] Historial taxonómico.
- [ ] Rendimiento medido.

## H.6. Antes de Reconstrucción

- [ ] Historia oculta definida.
- [ ] Evidencia separada.
- [ ] Métodos y costos abstractos.
- [ ] Hipótesis construibles.
- [ ] Incertidumbre puntuable sin falsa probabilidad.
- [ ] Nueva evidencia y revisión.
- [ ] Final “sin resolver” válido.
- [ ] Escenario probado con usuarios.

## H.7. Antes de Evolución

- [ ] Modelo poblacional estable.
- [ ] Tiempo determinista.
- [ ] Geografía mínima.
- [ ] Demografía.
- [ ] Migración.
- [ ] Contacto y flujo génico.
- [ ] Extinción.
- [ ] Costos y compensaciones.
- [ ] Registro completo de eventos.
- [ ] Exportación a evidencia.
- [ ] Pruebas de teleología.

## H.8. Antes de una campaña nueva

- [ ] Pregunta central.
- [ ] escala temporal;
- [ ] escala geográfica;
- [ ] corpus;
- [ ] mecánicas necesarias;
- [ ] mecánicas reutilizables;
- [ ] simplificaciones;
- [ ] riesgos científicos;
- [ ] criterios de éxito;
- [ ] recorte de contenido;
- [ ] prueba vertical.

---

# Apéndice I. Próximo orden de trabajo recomendado

La siguiente secuencia puede ejecutarse sin depender de decisiones lejanas:

1. crear el repositorio y guardar esta guía;
2. redactar ADR-001: “las afirmaciones son la fuente de verdad”;
3. implementar `Section`, `Passage`, `Mention`, `Source` e `Issue`;
4. implementar IDs, deltas y snapshots;
5. crear fixture artificial con cinco menciones;
6. demostrar cobertura completa;
7. implementar `TaxonomicName`, `TaxonConcept`, `CladeConcept`, `Lineage`, `Population` y `Specimen`;
8. crear fixture con dos conceptos llamados Hominini;
9. implementar `Claim`, `EvidenceItem`, `Analysis` y dimensiones epistemológicas;
10. crear dos fuentes ficticias en conflicto;
11. implementar tiempo, ocurrencias y regiones;
12. implementar `Event` con un caso de introgresión;
13. implementar `Hypothesis`, grupos de conflicto y dos vistas alternativas;
14. generar Graphviz reproducible;
15. completar el pipeline de ingestión;
16. seleccionar el corpus real del piloto;
17. procesar el piloto;
18. corregir el esquema solo mediante migraciones;
19. construir el Atlas MVP;
20. diseñar y probar Reconstrucción;
21. construir el núcleo poblacional;
22. generar evidencia desde simulación;
23. integrar los modos;
24. ampliar la filogenia por escalas.

La primera meta tangible no es “tener todo el árbol humano”. Es poder tomar una sección pequeña, conservar cada mención, representar dos interpretaciones incompatibles, explicar toda relación mostrada y reconstruir el estado desde archivos. Una vez que eso funciona, el proyecto tiene cimientos. Antes de eso, solo tiene entusiasmo con sangría jerárquica.

---

# Conclusión

La forma definitiva del proyecto es:

> **Una base de conocimiento científico versionada y centrada en afirmaciones, capaz de generar múltiples redes evolutivas coherentes y de proyectarlas hacia un juego poblacional de evolución y reconstrucción.**

El núcleo debe aceptar incertidumbre, taxonomías rivales, evidencia parcial y procesos reticulados sin colapsarlos en un árbol único. El juego debe utilizar esa complejidad para producir decisiones, descubrimiento y narrativas emergentes, no para decorar una escalera de progreso.

El desarrollo comienza por identidad, procedencia y validación; continúa con hipótesis, eventos y vistas; produce primero un Atlas y un modo de Reconstrucción; y solo después aborda una simulación evolutiva completa. Todo lo pospuesto permanece contemplado por el esquema, pero no interfiere con el primer recorte vertical.
