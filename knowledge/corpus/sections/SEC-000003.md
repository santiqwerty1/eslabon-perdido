# 4. La raíz eucariota y la forma de Amorphea

Recursos y convenciones operativas de esta sección: [C-684–C-689]

- La clasificación de Adl et al. 2019 normaliza los nombres y circunscripciones de las tablas nodales. [C-684; S01 clasificación]
- EukProt sirve como referencia auxiliar para evaluar la disponibilidad de proteomas predichos en el muestreo eucariota. [C-685; S03 título y resumen]
- PR2 sirve como referencia auxiliar para contrastar rótulos SSU y taxonomía asociada en las tablas. [C-686; S04 título y resumen]
- UniEuk se aplica como marco auxiliar para armonizar conceptos taxonómicos. [C-687; S05 título y resumen]
- Las edades se expresan por defecto en Ma antes del presente y la Tabla Cronoestratigráfica Internacional 2026/06 se usa como estándar cronoestratigráfico. [C-688; S02 metadatos y encabezado de versión]
- Las marcas ⚠, ≈, [F] y [H] conservan, respectivamente, los significados declarados de posición discutida, equivalencia dependiente, clado filogenómico y nodo dependiente de hipótesis. [C-689]

## 4.1. Por qué la raíz es difícil

La raíz del árbol eucariota identifica el nodo correspondiente a la población LECA reconstruida y condiciona la polaridad de los caracteres eucariotas. [C-431; S102 resumen; S56 tesis general]

No existe un grupo externo celular próximo a Eukaryota que conserve suficientes caracteres homólogos y una distancia evolutiva corta para enraizarlo directamente. [C-432; S102 resumen; S137 §Rooting]

Las divergencias profundas del árbol eucariota acumulan sustituciones múltiples y saturación. [C-433; S102 resumen; S137 §Phylogenomic artefacts]

La atracción de ramas largas puede agrupar linajes de evolución rápida por artefacto. [C-434; S102 resumen; S104 tesis general]

La heterogeneidad composicional y la heterogeneidad de tasas entre sitios pueden cambiar la topología recuperada. [C-435; S102 figs. 1–2; S104 tesis general]

La selección de ortólogos, los datos ausentes y las secuencias atípicas pueden alterar la raíz inferida. [C-436; S104 tesis general; S126 figs. 2 y 5]

Una probabilidad posterior, un bootstrap y una prueba AU no son medidas intercambiables y se transcriben sin convertirlas a una escala común. [C-437; n/a; convención documental]

## 4.2. Hipótesis de raíz que no deben fundirse

### 4.2.1. División histórica unikonta–bikonta

```text
Eukaryota [H] ⚠ [C-438]
├─ Unikonta sensu histórico ⚠ [C-438–C-439]
└─ Bikonta sensu histórico ⚠ [C-438; C-440]
```

La división histórica unikonta–bikonta situó la raíz entre un conjunto que incluía Amoebozoa y Opisthokonta y otro conjunto de eucariotas ancestrales supuestamente biciliados. [C-438; S116 tesis general; S118 tesis general; S89 clasificación]

La denominación Unikonta suponía un estado ancestral con un solo cinetosoma o sistema flagelar. [C-439; S89 §Unikonta; S138 discusión]

La denominación Bikonta suponía un estado ancestral con dos cinetosomas o sistemas flagelares. [C-440; S116 tesis general; S138 discusión]

La división unikonta–bikonta no coincide exactamente con Amorphea frente a Diaphoretickes ni con Opimoda frente a Diphoda. [C-441; S105 discusión; S124 definición; S137 revisión]

### 4.2.2. Raíz entre Amorphea y Diaphoretickes: una abreviación condicionada

Brown et al. organizaron el árbol eucariota no en dos, sino en tres ensamblajes de orden superior: Amorphea, Diaphoretickes y Excavata. [C-690; S108 Introduction]

Al resumir la propuesta de Derelle et al., Brown et al. escribieron que la raíz quedaba “somewhere between Amorphea and the other two listed lineages”. [C-691; S108 Introduction]

La expresión «raíz entre Amorphea y Diaphoretickes» corresponde por tanto a una abreviación de árboles simplificados, no a una bipartición inequívoca cuando Excavata y los linajes profundos no asignados se representan por separado. [C-692; S108 Introduction; Results]

Esta abreviación no es sinónima de la raíz Opimoda–Diphoda: Opimoda contiene más que Amorphea y Diphoda contiene más que Diaphoretickes bajo la circunscripción de Derelle et al. [C-693; S105 fig. 1; S108 Introduction]

### 4.2.3. Raíz Opimoda–Diphoda

```text
Eukaryota [H] ⚠ [C-442]
├─ Opimoda ⚠ [C-443]
└─ Diphoda ⚠ [C-444]
```

Derelle et al. propusieron una raíz entre Opimoda y Diphoda mediante proteínas eucariotas de origen bacteriano. [C-442; S105 título; figs. 1–3]

Opimoda incluyó a Amorphea y linajes profundos asociados según la circunscripción de Derelle et al. [C-443; S105 fig. 1; definición]

Diphoda incluyó a Diaphoretickes y varios linajes excavados según la circunscripción de Derelle et al. [C-444; S105 fig. 1; definición]

El análisis de Derelle et al. recuperó la raíz Opimoda–Diphoda con PP = 0.95 bajo CAT-GTR y PP = 0.97 bajo CAT en los análisis citados. [C-445; S105 resultados; figs. 2–3]

### 4.2.4. Raíz Discoba

```text
Eukaryota [H] ⚠ [C-446]
├─ Discoba ⚠ [C-446]
└─ restantes eucariotas activamente mitocondriados del muestreo [C-446–C-447]
```

He et al. propusieron una raíz con Discoba como rama hermana del resto de los eucariotas activamente mitocondriados incluidos. [C-446; S106 título; fig. 1]

La raíz Discoba de He et al. no prueba la monofilia de una Excavata amplia. [C-447; S106 discusión; S137 revisión]

### 4.2.5. Raíz excavada con divergencias sucesivas

```text
Eukaryota [H] ⚠ [C-449]
├─ linaje excavado 1 del análisis [C-449]
└─┬─ linaje excavado 2 del análisis [C-449]
  └─┬─ linaje excavado 3 del análisis [C-449]
    └─┬─ linaje excavado 4 del análisis [C-449]
      └─ restantes eucariotas muestreados [C-449–C-450]
```

Al Jewari y Baldauf analizaron 183 proteínas eucariotas de ascendencia arqueana para evaluar la raíz. [C-448; S103 resumen; Methods]

Al Jewari y Baldauf recuperaron cuatro linajes excavados que se separan sucesivamente antes del resto de Eukaryota. [C-449; S103 resumen; figs. 1–3]

La hipótesis de raíz excavada sucesiva no identifica a Excavata como un único clado hermano del resto. [C-450; S103 resumen; fig. 3]

Al Jewari y Baldauf atribuyeron parte del conflicto con otras raíces a secuencias atípicas, mosaicos y sensibilidad a datos ausentes en modelos CAT. [C-451; S104 tesis general; S103 discusión]

### 4.2.6. Raíz Opisthokonta

```text
Eukaryota [H] ⚠ [C-453]
├─ Opisthokonta [C-453]
└─ restantes eucariotas [C-453–C-454]
```

Cerón-Romero et al. analizaron 2.786 familias génicas de 158 linajes mediante reconciliación de árboles génicos y árbol de especies. [C-452; S107 título; Methods]

Cerón-Romero et al. favorecieron una raíz entre Opisthokonta y todos los demás linajes eucariotas. [C-453; S107 título; resultados]

La raíz Opisthokonta es incompatible en su posición exacta con Opimoda–Diphoda y con raíces excavadas. [C-454; S105; S103; S107]

### 4.2.7. Raíz Opimoda+–Diphoda+ de Williamson et al.

```text
Eukaryota [H] ⚠ [C-459]
├─ Opimoda+ ⚠ [C-459–C-460]
└─ Diphoda+ ⚠ [C-459–C-460]
```

Williamson et al. analizaron 100 taxones y 93 proteínas relacionadas con la mitocondria. [C-455; S102 Methods; fig. 1]

Williamson et al. incluyeron todos los supergrupos eucariotas reconocidos por su clasificación de trabajo. [C-456; S102 resumen; Supplementary table 7]

Williamson et al. compararon modelos sitio-homogéneos, mezclas de perfiles y modelos sitio-heterogéneos. [C-457; S102 figs. 1–2; Methods]

Williamson et al. aplicaron retirada de sitios rápidos, taxones rápidos y genes divergentes como pruebas de artefacto. [C-458; S102 Methods; Extended Data]

Williamson et al. recuperaron consistentemente una raíz entre Opimoda+ y Diphoda+. [C-459; S102 resumen; figs. 1–2]

Opimoda+ y Diphoda+ amplían o modifican las circunscripciones de Opimoda y Diphoda usadas en 2015. [C-460; S102 fig. 1; S105 definición]

La raíz de Williamson et al. es una inferencia filogenómica y no una observación directa de LECA. [C-461; n/a; clasificación de evidencia basada en S102]

### 4.2.8. Comparación de las raíces

<!-- TABLE:table-15-4-2-8-comparacion-de-las-raices -->

No existe una posición de raíz eucariota aceptada como consenso universal. [C-462; S102 resumen; S137 §Rooting]

## 4.3. Caracteres moleculares raros y su peso actual

### 4.3.1. Fusión DHFR–TS

Stechmann y Cavalier-Smith propusieron la fusión DHFR–TS como sinapomorfía derivada de Bikonta. [C-463; S116 tesis general]

DHFR y TS aparecen fusionadas en numerosos eucariotas y separadas en otros. [C-464; S117 fig. 2; Results]

Se han documentado pérdidas de DHFR, TS o del locus fusionado en varios subgrupos. [C-465; S117 Results; fig. 2]

La fisión de genes y la pérdida diferencial hacen que DHFR–TS sea un carácter no fiable para polarizar por sí solo la raíz. [C-466; S117 líneas sobre DHFR–TS; Discussion]

La fusión DHFR–TS conserva valor como carácter histórico local, pero no como prueba decisiva de una raíz unikonta–bikonta. [C-467; S117 Discussion; S120 tesis general]

### 4.3.2. Repertorios de miosina

Richards y Cavalier-Smith clasificaron 37 combinaciones de dominios de miosina en el muestreo disponible en 2005. [C-468; S118 Abstract]

Richards y Cavalier-Smith atribuyeron tres tipos de miosina a LECA en su reconstrucción. [C-469; S118 Results; S119 introducción]

Sebé-Pedrós et al. incorporaron representantes de todos los supergrupos eucariotas principales de su clasificación de trabajo. [C-470; S119 introducción; Methods]

Sebé-Pedrós et al. declararon que no pretendían inferir el árbol eucariota a partir del contenido de miosinas. [C-471; S119 introducción: “We do not aim to infer...”]

La reconstrucción de repertorios de miosina de C-469 puede alterarse por duplicación, pérdida, convergencia, fisión y transferencia horizontal. [C-472; S119 introducción; Discussion]

Los repertorios de miosina tienen peso actual como evidencia de historia de familias génicas, no como polarizador único de la raíz. [C-473; S119 Discussion; S102 introducción]

### 4.3.3. Inserciones y deleciones conservadas

Baldauf y Palmer identificaron cuatro inserciones o deleciones compartidas por animales y hongos frente al muestreo externo de 1993. [C-474; S122 resumen; Results]

Una inserción de 12 aminoácidos en eEF1A fue uno de los caracteres usados para asociar animales y hongos. [C-475; S122 resumen; fig. 1]

Tres hendiduras pequeñas en enolasa fueron usadas como caracteres adicionales de la relación animales–hongos. [C-476; S122 resumen; Results]

Los indels de eEF1A y enolasa registrados en C-475 y C-476 pueden presentar homoplasia, errores de alineamiento y pérdidas secundarias. [C-477; S123 tesis general; S120 Discussion]

Los indels históricos respaldan Opisthokonta, pero no determinan por sí solos la raíz de Eukaryota. [C-478; S122; S123]

### 4.3.4. Posiciones de intrones

Rogozin et al. documentaron conservación de posiciones de intrones entre reinos eucariotas. [C-479; S121 título; Results]

Rogozin et al. documentaron ganancias y pérdidas masivas de intrones específicas de linaje. [C-480; S121 título; Results]

La conservación de intrones puede sostener homología profunda, pero la pérdida diferencial dificulta usarla como marcador de raíz único. [C-481; S121 Discussion; S120 Discussion]

### 4.3.5. Evaluación conjunta

Rogozin et al. analizaron cambios genómicos raros y no recuperaron apoyo para la filogenia unikonta–bikonta. [C-482; S120 título; Results]

Ningún carácter molecular raro localizado en esta sesión resuelve por sí solo la raíz eucariota. [C-483; S117; S119, S120, S121, S122, S123]

## 4.4. Amorphea y los linajes que orbitan su base

### 4.4.1. Amorphea

Adl et al. definieron Amorphea como el clado menos inclusivo que contiene Homo sapiens, Neurospora crassa y Dictyostelium discoideum. [C-484; S124 definición de Amorphea; S01 clasificación]

Amorphea incluye Amoebozoa y Obazoa en la clasificación adoptada. [C-485; S01 clasificación; S108 fig. 1; S109 árbol]

Amoebozoa es el grupo hermano de Obazoa dentro de Amorphea en la topología de trabajo. [C-486; S01 clasificación; S109 árbol; S112 fig. 3]

La definición de nodo de Amorphea no depende de un estado ameboide o pseudopodial universal. [C-487; S124 definición y etimología de Amorphea]


```text
CRuMs [F] ── grupo hermano de ── Amorphea [F] [C-491; C-520]
                                      ├─ Amoebozoa [F] [C-485; C-519; C-486]
                                      └─ Obazoa [F] [C-485; C-519; C-486]
```

### 4.4.2. CRuMs

Brown et al. analizaron 351 proteínas, 61 o 64 taxones y 97.002 posiciones de aminoácidos. [C-488; S108 Methods: Data Set Construction]

Brown et al. usaron LG+C60+F+Γ-PMSF y CAT-GTR+Γ como modelos sitio-heterogéneos. [C-489; S108 Methods: Tree Inference]

Brown et al. recuperaron Collodictyonida, Rigifilida y Mantamonas como un clado denominado provisionalmente CRuMs. [C-490; S108 resumen; fig. 1]

Brown et al. recuperaron CRuMs como grupo hermano de Amorphea con soporte máximo. [C-491; S108 Results: fig. 1; líneas sobre maximal support]

Brown et al. declararon que CRuMs era un rótulo provisional y no un taxón formal. [C-492; S108 Discussion: “place-holding moniker”]

### 4.4.3. Ancyromonadida y Malawimonadida

Brown et al. situaron Ancyromonadida fuera de Amorphea y más lejos de Amorphea que CRuMs. [C-493; S108 resumen; Results]

En el análisis de máxima verosimilitud de Brown et al., Ancyromonadida y Malawimonadida formaron un clado con BS = 77 %. [C-494; S108 Results; fig. 1]

Las cadenas bayesianas convergentes de Brown et al. situaron Malawimonadida con CRuMs+Amorphea y excluyeron Ancyromonadida con PP = 1. [C-495; S108 Results; suppl. figs. S2–S3]

Brown et al. trataron las dos posiciones de Ancyromonadida y Malawimonadida como hipótesis candidatas. [C-496; S108 Results: “candidate hypotheses requiring further investigation”]

Torruella et al. 2025 recuperaron una asociación entre Ancyromonadida y Malawimonadida en parte de sus análisis, sin eliminar toda sensibilidad profunda. [C-497; S109 resultados; fig. 2; sin localizar]

## 4.5. Historia nomenclatural: nombres solapados, no una bolsa de sinónimos

### 4.5.1. Unikonta y Amorphea

En Cavalier-Smith 2002, Unikonta se circunscribió mediante una reconstrucción ancestral uniciliada y caracteres moleculares asociados. [C-498; S89 clasificación]

Unikonta fue abandonado en la clasificación de Adl et al. porque el nombre y su diagnóstico sugerían una ancestralidad flagelar no sostenida. [C-499; S124 introducción y definición de Amorphea]

Amorphea sustituyó a Unikonta mediante una definición filogenética de nodo que no depende de contar cilios. [C-500; S124 definición; S01 clasificación]

### 4.5.2. Podiata

Cavalier-Smith empleó “podiates” para eucariotas con pseudópodos o descendientes de formas pseudopodiales dentro de su sistema. [C-501; S125 clasificación; S145 tesis general]

El uso de Podiata en filogenómicas recientes puede designar Amorphea+CRuMs. [C-502; S109 árbol; S108 relación hermana; sin localizar]

Podiata sensu Cavalier-Smith y Podiata sensu filogenómico reciente son circunscripciones rivales y no sinónimos automáticos. [C-503; S125; S109]

### 4.5.3. Sulcozoa

Cavalier-Smith propuso Sulcozoa para Apusozoa y Varisulca en su clasificación de 2013. [C-504; S125 resumen y clasificación]

Sulcozoa fue concebido como un conjunto que podía ser parafilético respecto de Opisthokonta y Amoebozoa. [C-505; S125 discusión clasificatoria]

Sulcozoa no es un nombre alternativo moderno de Obazoa. [C-506; S125; S111 definición de Obazoa]

### 4.5.4. Varisulca

Varisulca reunió Diphyllatea, Planomonadida, Discocelida, Mantamonadida y Rigifilida en la clasificación de Cavalier-Smith. [C-507; S125 clasificación; sin localizar]

Varisulca no equivale a CRuMs porque incluye linajes distintos y excluye Collodictyonida en la circunscripción citada. [C-508; S125; S108 definición de CRuMs]

### 4.5.5. Estado de Amorphea

Amorphea permanece en uso en Adl et al. 2019. [C-509; S01 clasificación]

La disponibilidad nomenclatural, la aceptación en una clasificación y el soporte filogenético son propiedades distintas. [C-510; n/a; convención documental]

## 4.6. Corredor filogenético y tablas por nodo

El árbol siguiente es una vista parcial del corredor. Las ramas eucariotas externas no se despliegan como catálogo. Dentro de Holozoa, la lista de ramas profundas no representa un orden de divergencia; las tres topologías incompatibles se muestran por separado en 4.7.

```text
Eukaryota [F]  [vista parcial] [C-683]
├─ ⋯ ramas externas al corredor no desplegadas [C-683]
└─ Amorphea [F]  [C-683; C-485]
   ├─ Amoebozoa [F] [C-485; C-519; C-486]
   └─ Obazoa [F] [C-485; C-519; C-486]
      ├─ Breviatea [F] ⚠ [C-535; C-553]
      └─┬─ Apusomonadida [F] ⚠ [C-535; C-544]
        └─ Opisthokonta [F] [C-544; C-561]
           ├─ Holomycota [F] [C-560; C-569]
           └─ Holozoa [F] [C-560; C-569]
              │  [orden de las ramas siguientes no representado; véase 4.7] [C-666]
              ├─ Pluriformea [F] ⚠ [C-576; C-592]
              │  ├─ Corallochytrea [F] [C-592; C-600; C-601]
              │  └─ Syssomonas y linajes incluidos según circunscripción [C-592; C-601]
              ├─ Ichthyosporea [F] ⚠ [C-576; C-584]
              └─ Filozoa [F] [C-576; C-616]
                 ├─ Filasterea [F] [C-609; C-616; C-608]
                 └─ Choanozoa sensu stricto ≈ Apoikozoa [F] [C-609; C-616; C-624]
                    ├─ Choanoflagellata [F] [C-624; C-632]
                    └─ Metazoa [F]  [terminal] [C-014; C-624; C-633]
```

La inclusión de Amorphea en Eukaryota, la incertidumbre sobre la raíz interna de Holozoa y la circunscripción de Pluriformea están registradas respectivamente en C-683, C-666 y C-673–C-676.

### 4.6.1. Eukaryota

<!-- TABLE:table-16-4-6-1-eukaryota -->

### 4.6.2. Amorphea

Sandin et al. compararon 32 árboles con 77 calibraciones y 100 réplicas de TreePL. [C-787; C-788; C-789] Para Amorphea publicaron una mediana de 1.773 Ma y un máximo/mínimo de medianas de 1.934/1.703 Ma. [C-791] Estos valores constituyen un estudio paralelo a S126: no reemplazan su intervalo ni se combinan con él mediante promedios o amplitudes propias. [C-786–C-791; S548 métodos; resultados]

<!-- TABLE:table-17-4-6-2-amorphea -->

### 4.6.3. Amoebozoa

<!-- TABLE:table-18-4-6-3-amoebozoa -->

### 4.6.4. Obazoa

<!-- TABLE:table-19-4-6-4-obazoa -->

### 4.6.5. Apusomonadida

<!-- TABLE:table-20-4-6-5-apusomonadida -->

### 4.6.6. Breviatea

<!-- TABLE:table-21-4-6-6-breviatea -->

### 4.6.7. Opisthokonta

<!-- TABLE:table-22-4-6-7-opisthokonta -->

### 4.6.8. Holomycota

<!-- TABLE:table-23-4-6-8-holomycota -->

### 4.6.9. Holozoa

<!-- TABLE:table-24-4-6-9-holozoa -->

### 4.6.10. Ichthyosporea

<!-- TABLE:table-25-4-6-10-ichthyosporea -->

### 4.6.11. Pluriformea sensu Hehenberger et al. 2017

<!-- TABLE:table-26-4-6-11-pluriformea-sensu-hehenberger-et-al-2017 -->

### 4.6.12. Corallochytrea

<!-- TABLE:table-27-4-6-12-corallochytrea -->

### 4.6.13. Filasterea

<!-- TABLE:table-28-4-6-13-filasterea -->

### 4.6.14. Filozoa

<!-- TABLE:table-29-4-6-14-filozoa -->

### 4.6.15. Choanozoa sensu stricto ≈ Apoikozoa

<!-- TABLE:table-30-4-6-15-choanozoa-sensu-stricto-apoikozoa -->

### 4.6.16. Choanoflagellata

<!-- TABLE:table-31-4-6-16-choanoflagellata -->

### 4.6.17. Metazoa

<!-- TABLE:table-32-4-6-17-metazoa -->

## 4.7. Tres raíces incompatibles dentro de Holozoa unicelular

```text
H32 Pluriformea-sister:      (Pluriformea, (Ichthyosporea, Filozoa)) [C-656]
H33 Teretosporea-sister:     ((Pluriformea, Ichthyosporea), Filozoa) [C-657]
H34 Ichthyosporea-sister:    (Ichthyosporea, (Pluriformea, Filozoa)) [C-659; C-660]
```

Liu et al. reunieron 348 taxones pertenecientes a 33 linajes principales de Opisthokonta. [C-648; S126 Results; S3 table]

La matriz BUSCO de Liu et al. contiene 228 genes. [C-649; S126 tabla 1; Methods]

La matriz OrthoFinder de Liu et al. contiene 440 genes. [C-650; S126 tabla 1; Methods]

La matriz Tikhonenkov_2020 de Liu et al. contiene 201 genes. [C-651; S126 tabla 1; Methods]

Liu et al. generaron 18 árboles mediante tres matrices, dos versiones de taxones y tres esquemas de modelos. [C-652; S126 Methods; fig. 2]

Aproximadamente 85 % de las ramas internas fueron congruentes entre los 18 árboles. [C-653; S126 Results]

Los análisis con el mismo conjunto de ortólogos mostraron 97–98 % de congruencia. [C-654; S126 Results]

Los análisis con conjuntos de ortólogos diferentes mostraron 87–91 % de congruencia. [C-655; S126 Results]

BUSCO y Tikhonenkov_2020 recuperaron Pluriformea como grupo hermano del resto de Holozoa. [C-656; S126 Results; fig. 4]

OrthoFinder recuperó Pluriformea+Ichthyosporea como Teretosporea, hermana de Filozoa. [C-657; S126 Results; fig. 4]

Una ejecución BUSCO bajo GTR+CAT apoyó débilmente Teretosporea-sister con UFB = 23. [C-658; S126 Results; S1 Data]

La hipótesis Ichthyosporea-sister no fue recuperada en los análisis principales de Liu et al. [C-659; S126 Results]

La reducción de la matriz Tikhonenkov_2020 a 60 taxones cambió el resultado a Ichthyosporea-sister. [C-660; S126 fig. 5C; Results]

El aumento del muestreo a 180, 240 y 347 taxones favoreció Pluriformea-sister en los análisis citados. [C-661; S126 fig. 5C; Results]

La hipótesis Teretosporea-sister obtuvo UFB = 98 con OrthoFinder#2 bajo un modelo sitio-homogéneo. [C-662; S126 fig. 5E; Results]

Solo 0,7 % de los loci, 3 de 426, apoyaron Teretosporea-sister en el cálculo de gCF citado. [C-663; S126 fig. 5E; Results]

El 98,6 % de los árboles génicos, 420 de 426, apoyó topologías distintas de las tres candidatas en el análisis citado. [C-664; S126 fig. 5E; Results]

Los apoyos de sitios para las tres topologías fueron 34,04/32,98/32,98. [C-665; S126 fig. 5E; S112 table]

En S126, el alto soporte de concatenación para raíces internas alternativas de Holozoa coexiste con baja concordancia génica y de sitios. [C-666; S126 Results; fig. 5]

## 4.8. Circunscripciones rivales en el extremo del corredor

### 4.8.1. Choanozoa sensu histórico, Choanozoa sensu stricto y Apoikozoa

La Choanozoa histórica de Cavalier-Smith reunió protistas opisthokontos y excluyó animales, por lo que era parafilética respecto de Metazoa. [C-667; S125 clasificación; S130 introducción]

Brunet y King emplearon Choanozoa para el clado Choanoflagellata+Metazoa. [C-668; S134 glosario; definición]

Budd y Jensen propusieron Apoikozoa para el clado Metazoa+Choanoflagellata. [C-669; S135 resumen]

Adl et al. 2019 prefirieron Choanozoa y consideraron inadecuada la etimología de Apoikozoa. [C-670; S01 nota de Choanozoa]

Choanozoa sensu histórico no tiene la misma circunscripción que Choanozoa sensu stricto ≈ Apoikozoa. [C-671; S01; S134; S135]

### 4.8.2. Pluriformea, Corallochytrea y Corallochytrium

Corallochytrium es miembro de Corallochytrea según la clasificación adoptada. [C-672] Corallochytrium es un género y Corallochytrea un linaje; esas categorías no son intercambiables. [C-672; S01 clasificación; S129 fig. 1]

Hehenberger et al. introdujeron el nombre Pluriformea para el clado de su muestreo que reunía Syssomonas y Corallochytrium. [C-673; S129 resumen; fig. 1]

Corallochytrea es miembro de Pluriformea sensu Hehenberger et al. 2017. [C-674] Puesto que Pluriformea añade al menos Syssomonas a la rama de Corallochytrium, no se trata aquí como sinónimo automático de Corallochytrea. [C-674; S129 fig. 1; S01 clasificación]

Liu et al. emplearon “Pluriformea/Corallochytrea” y después “Pluriformea” como una abreviación operacional de su muestreo. [C-675; S126 Methods; fig. 2; sin localizar]

Pluriformea, Corallochytrea y Corallochytrium deben conservarse como entidades separadas en el corpus. [C-676; n/a; derivación documental de C-672–C-675]

## 4.9. Qué permanece sin resolver

La posición exacta de la raíz eucariota permanece discutida entre raíces Opimoda(+)-Diphoda(+), excavadas y Opisthokonta. [C-677; S102; S103; S104; S105; S106; S107]

La relación exacta de Ancyromonadida y Malawimonadida con CRuMs y Amorphea permanece sensible al método. [C-678; S108; S109; S115]

El orden interno temprano de Obazoa ha cambiado con la incorporación de nuevos taxones. [C-679; S111 árbol; S109 árbol]

La raíz interna de Holozoa unicelular permanece sin resolver. [C-680; S126 fig. 5]

Las edades nodales de S126 proceden de MCMCTree con diez calibraciones fósiles, un análisis con raíz de 1,5 Ga y una sensibilidad con raíz de 1,9 Ga. [C-682] Se transcriben los intervalos publicados sin calcular puntos medios. [C-682; C-525; C-526; C-533; C-534; C-541; C-542; C-550; C-558; C-559; C-566; C-574; C-582; C-590; C-591; C-598; C-599; C-614; C-615; C-622; C-623]

## 4.10. Registro de afirmaciones de la sección 4

<!-- TABLE:claims-04 -->

---
