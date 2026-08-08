# Encargo de investigación: el corredor Eukaryota → Holozoa

Ejecuta lo que sigue y devuélveme el documento resultante. No evalúes, no reformules ni comentes este encargo, y no incluyas preámbulo sobre tu método salvo en la sección de búsquedas negativas que te pido al final.

Quiero que investigues en profundidad el corredor evolutivo que va desde el origen de los eucariotas hasta el nodo que reúne coanoflagelados y animales. Con la misma exhaustividad que aplicarías a una filogenia completa, pero con un foco distinto: **esta vez el objeto no es solo la topología, sino la ecología, los mecanismos y las magnitudes**. Quiero saber quién comía a quién, quién vivía dentro de quién, qué costaba cada cosa, cuánto duraba y qué evidencia sostiene cada afirmación.

Declara al principio del documento la **fecha de corte bibliográfico**.

## 0. Restricciones no negociables

- **Nada de teleología.** No describas ningún linaje como superior, inferior, primitivo, avanzado, más evolucionado, destinado a producir animales, un intento fallido o un paso obligatorio hacia otra cosa. No escribas que un rasgo apareció «para» algo ni que un linaje «todavía no había desarrollado» algo. No trates a los unicelulares vivientes como versiones antiguas o detenidas de nada: tienen exactamente la misma profundidad de historia que nosotros y han cambiado durante todo ese tiempo. Usa en su lugar: adaptación, especialización, persistencia, divergencia, extinción, contingencia, restricción histórica, cambio de nicho. El encuadre «hasta el umbral de los animales» describe qué tramo del árbol me interesa, no una dirección del proceso: nada en este corredor estaba orientado hacia Holozoa, y cada nodo tuvo ramas hermanas que persisten hoy. Aplica esto también a los títulos, a los pies de tabla y a las frases de cierre.
- **No inventes nada.** Ni nombres, ni fechas, ni taxones, ni relaciones, ni cifras. Si te pido una magnitud y no está publicada, la respuesta correcta es «no hay valor publicado» y, si puedes, por qué no lo hay. No estimes, no interpoles, no redondees y no des un orden de magnitud «razonable». Un hueco declarado lo puedo usar; una cifra verosímil sin fuente me estropea todo lo que construya encima de ella.
- **No cites de memoria.** Cita únicamente trabajos que hayas recuperado en esta sesión. No reconstruyas un DOI a partir del patrón habitual de la revista: si no lo tienes verificado, escribe `DOI no verificado` y da la URL que sí recuperaste. Si recuerdas un trabajo relevante y no consigues recuperarlo, no lo cites: menciónalo en la sección de huecos como trabajo conocido no recuperado. Prefiero una laguna declarada a una referencia que no resuelve.
- **No diseñes el juego.** Este material alimentará una base de conocimiento y, más adelante, una simulación. No te pido que la diseñes. No propongas variables, mecánicas, reglas, parámetros ni escalas, no adaptes nada para hacerlo jugable y no simplifiques por anticipado pensando en que alguien tendrá que implementarlo.
- **Separa los registros.** La prosa puede tener el tono que quieras: viva, con transiciones y comentarios. Las filas del registro de afirmaciones y las celdas de tabla, no: son declarativas, planas, sin ironía, sin metáfora y sin adjetivo valorativo. Si una fila necesita ironía para funcionar, no es una afirmación.
- **Conserva el término original.** Escribo en español y la literatura está en inglés. La primera vez que traduzcas un concepto, un método o una categoría, deja el término inglés entre paréntesis. Si yo uso en este encargo un término español que no corresponde a ninguno establecido, dímelo y usa el correcto.

## 1. Alcance

**Corredor principal**, con la máxima resolución:

```
tallo de Eukaryota (el intervalo entre FECA y LECA)
→ Eukaryota (grupo corona)
→ Amorphea
→ Obazoa
→ Opisthokonta
→ Holozoa
→ Filozoa
→ Choanozoa sensu stricto ≈ Apoikozoa
```

El corredor termina en el nodo que reúne coanoflagelados y animales. **Choanoflagellata entra con la misma resolución que el resto del corredor**: ecología, alimentación, colonias y rosetas, señales inductoras. **Metazoa entra solo como nombre terminal**: no desarrolles el origen ni la diversificación de los animales ni la topología interna de Metazoa. Ese material corresponde a otro trabajo.

**Ramas hermanas inmediatas**, con tratamiento propio cada una y no como mención en una tabla: Amoebozoa (frente a Obazoa), Apusomonadida y Breviatea (frente a Opisthokonta), Holomycota incluidos Fungi y sus parientes unicelulares (frente a Holozoa), e Ichthyosporea, Pluriformea, Corallochytrea y Filasterea dentro de Holozoa.

**Participantes del evento fundacional, con la misma profundidad que el corredor**: las arqueas Asgard —Asgardarchaeota en conjunto, sus divisiones nombradas, los linajes conocidos solo por genomas ensamblados a partir de metagenomas y los que proceden de cultivo— y las alfaproteobacterias. No son contexto: son actores. Quiero su diversidad interna, su ecología, su metabolismo y su posición filogenética con el mismo detalle que pido para Obazoa.

**Fuera de alcance como catálogo taxonómico**: no desarrolles la composición interna de SAR, Archaeplastida, Discoba, Metamonada, Haptista, Cryptista, CRuMs ni los demás supergrupos. No los describas como ramas.

**Pero sí los quiero como comparandos, sin timidez**, siempre que documenten un mecanismo del corredor. Espero encontrar, entre otros: *Monocercomonoides exilis*, *Giardia*, *Trichomonas vaginalis*, *Nyctotherus ovalis*, *Blastocystis*, *Entamoeba*, *Pelomyxa*, *Paulinella chromatophora*, *Hatena arenicola*, *Braarudosphaera bigelowii*, y los eucariotas con plastos secundarios y nucleomorfo. La regla es: **si el linaje externo documenta un resultado posible del mismo proceso que estoy modelando, lo quiero; si solo añade taxones a una lista, no.** La exclusión es de diversidad, no de mecanismo. Cualquier otro linaje entra solo si explica un rasgo, un evento o una hipótesis mencionados explícitamente en este documento, en un párrafo que empiece diciendo qué mecanismo del corredor ilustra.

## 2. El punto de partida: dos dominios o tres

Antes de nada, el encuadre. Es la pregunta que decide qué es Eukaryota como entidad y no quiero que se dé por cerrada.

- **La forma del árbol de la vida**: árbol de tres dominios frente a hipótesis del eocito y dos dominios primarios. ¿Los eucariotas son grupo hermano de las arqueas o se ramifican **dentro** de ellas? Da el soporte cuantitativo tal cual y di qué análisis, con qué modelo y con qué muestreo sostiene cada resultado. Explica la consecuencia nomenclatural: si Eukaryota está dentro de Asgard, «Archaea» en su uso corriente designa un grupo parafilético; quiero saber cómo tratan ese problema los autores que lo discuten. Incluye la posición minoritaria: la hipótesis neomurana y quién la sostiene hoy, si alguien.
- **El estado de partida procariota**: caracteriza Bacteria y Archaea como los dos dominios de los que arranca todo. Incluye la **divisoria lipídica** —éteres isoprenoides sobre glicerol-1-fosfato frente a ésteres de ácidos grasos sobre glicerol-3-fosfato— y el problema que plantea: los eucariotas tienen lípidos de tipo bacteriano pese a un hospedador arqueano. Qué soluciones se han propuesto, qué muestran los experimentos de membranas heteroquirales y por qué sigue sin resolverse. Añade la **naturaleza quimérica del genoma eucariota**: genes informacionales de afinidad arqueana frente a genes operacionales de afinidad bacteriana, con las proporciones que dé la literatura.
- **El linaje hospedador**: qué grupo asgard se propone hoy como el más próximo a los eucariotas y con qué evidencia. Cultivos y observaciones directas: *Candidatus* Prometheoarchaeum syntrophicum y el modelo E3, *Lokiarchaeum ossiferum* y lo que la criotomografía muestra de su citoesqueleto y sus protrusiones. **Proteínas de firma eucariota (ESP)**: actina, profilina, gelsolina, ESCRT-III, ubiquitina, GTPasas pequeñas, tubulina — cuáles se han caracterizado funcionalmente y cuáles solo se han detectado en secuencia. Distingue en cada afirmación si procede de cultivo o de genoma ensamblado a partir de metagenomas: no es la misma clase de evidencia.
- **El simbionte**: la evidencia del origen alfaproteobacteriano de la mitocondria y qué grupo concreto es hoy el candidato más próximo.

## 3. Eucariogénesis

Trátala con detalle y sin resolverla artificialmente.

- **Poblaciones ancestrales con etiqueta establecida**: usa y define **FECA**, **LECA**, **LACA**, **LBCA** y **LUCA**. Son etiquetas publicadas, no invenciones, y son exactamente lo que necesito para nombrar poblaciones reconstruidas sin acuñar taxones. Di quién introdujo cada término. Sé explícito en que LECA es el ancestro común de todos los eucariotas vivientes y **no** «el primer eucariota». Explica qué separa a FECA de LECA y por qué el tallo eucariota es donde ocurre casi todo lo interesante y donde no hay descendientes vivos que muestrear. Qué se ha propuesto sobre su duración y su diversidad, y qué linajes se han sugerido como ramas troncales.
- **Reconstrucción de LECA**: qué caracteres se le atribuyen y con qué criterio. Como mínimo: mitocondria con crestas, envoltura nuclear y poro, retículo y Golgi, endomembranas con familias de Rab y SNARE, actina y tubulina, cilio con transporte intraflagelar y cuerpo basal, peroxisomas, mitosis, meiosis y ciclo sexual, intrones espliceosomales y espliceosoma. Para cada carácter: si la inferencia procede de presencia a ambos lados de la raíz eucariota, de reconstrucción de estado ancestral con un método concreto, o de otra cosa. **Declara el método en cada caso**: es la afirmación más inferida de todo el documento y no quiero que llegue sin procedencia.
- **El orden de los eventos**: mitocondria temprana frente a mitocondria tardía. ¿Precedió la fagotrofia a la mitocondria o al revés? Los dos lados con su evidencia.
- **Los modelos rivales con nombre propio**: hipótesis del hidrógeno, sintrofía, inside-out, modelos autógenos frente a simbiogénicos, y como máximo tres más que consideres vigentes, con una frase que justifique por qué los incluyes. Para cada uno: qué predice, qué evidencia lo apoya, qué lo compromete, y además **su montaje inicial** — qué organismos supone presentes, qué intercambio metabólico postula y en qué dirección, qué condiciones ambientales requiere (anoxia, hidrógeno, sulfuro, proximidad física), qué geometría propone y qué papel asigna a cada participante antes de la integración.
- **El origen del núcleo, tratado aparte del origen de la célula eucariota.** Son dos preguntas distintas y no las fundas. Modelos: **invasión de intrones** —los intrones de grupo II del endosimbionte se convierten en espliceosomales, el empalme es más lento que la traducción y la envoltura nuclear separa ambos procesos—; **eucariogénesis viral**; **origen autógeno por invaginación**; **inside-out**. Qué predice cada uno, qué lo apoya, qué lo compromete.
- **La hipótesis del protocoatómero**: COPI, COPII, clatrina y el complejo del poro nuclear comparten un plegamiento ancestral, y el sistema endomembranoso se derivaría por duplicación y divergencia de una maquinaria única de curvatura de membrana. Con el mismo detalle que los modelos de eucariogénesis.
- **Matriz de compatibilidad.** Cierra la sección con una tabla de pares: para cada par de modelos, si son mutuamente excluyentes, parcialmente compatibles o compatibles, y qué observación concreta los distinguiría. Cuando la incompatibilidad sea parcial, di **qué parte** choca; «ambos aceptan el origen alfaproteobacteriano y difieren solo en el orden de adquisición de la fagotrofia» me sirve mucho más que «son rivales». Si dos modelos se presentan habitualmente como rivales pero responden a preguntas distintas —uno al orden de los eventos y otro al mecanismo de la asociación—, dilo: es información, no un empate. No fundas topologías incompatibles en una sola figura: un esquema por hipótesis, cada uno con su fuente. Lo que falsaría cada modelo por separado va en el apéndice E, no aquí.
- **Qué es lo que realmente no se sabe.**

## 4. La raíz eucariota y la forma de Amorphea

No des el corredor por descontado. Antes de recorrerlo quiero saber cuánto se sostiene.

- **Dónde se enraíza el árbol eucariota**: las propuestas con nombre —raíz entre Opimoda y Diphoda, raíz excavada, raíz entre Amorphea y Diaphoretickes, la vieja división unikonta/bikonta— con la evidencia de cada una y por qué el problema es duro (ausencia de grupo externo cercano, divergencias antiguas, atracción de ramas largas).
- **Caracteres moleculares raros** usados para enraizar o para sostener el corredor: la fusión dihidrofolato reductasa–timidilato sintasa, los repertorios de miosinas, inserciones y deleciones conservadas, posiciones de intrones. Para cada uno: qué nodo sostiene, qué excepciones o reversiones se han encontrado, qué peso se le da hoy.
- **Qué contiene realmente Amorphea**, y qué linajes se le han asociado o disociado: Amoebozoa, Obazoa y los orfanatos que orbitan el nodo — **CRuMs** (Collodictyonida, Rigifilida, Mantamonas), **Ancyromonadida**, **Malawimonadida**. Dónde caen hoy y con qué soporte.
- **Nombres rivales del mismo nodo o de nodos solapados**: Unikonta, Podiata, Sulcozoa, Varisulca, Amorphea. Quién propuso cada uno, con qué contenido, con qué carácter diagnóstico, si sigue en uso y por qué se abandonó si se abandonó. Es el caso de historia nomenclatural que más me interesa después de Choanozoa/Apoikozoa, y no lo tengo.

## 5. El registro material: fósiles y biomarcadores

Este apartado es el ancladero observacional de todo lo demás. Quiero saber **qué se ha visto en la roca**: qué formación, qué edad, qué datación la sostiene.

- **Microfósiles de pared orgánica (acritarcos)**: qué caracteres se usan para atribuir una vesícula a Eukaryota —ornamentación, procesos, aberturas de excistamiento, pared multicapa, química de la pared— y qué fuerza tiene cada uno. Trata *Valeria lophostriata*, *Tappania plana*, *Dictyosphaera*, *Shuiyousphaeridium*, la biota del Grupo Ruyang y la Formación Roper.
- **Candidatos antiguos y discutidos**: *Grypania spiralis*, *Qingshania magnifica*, *Rafatazmia chitrakootensis* y los fósiles vindhyanos. Qué se argumenta a favor y en contra de la atribución eucariota, y si el candidato es grupo corona o grupo tronco.
- **Microfósiles con forma de vasija (*vase-shaped microfossils*, VSM)** del Grupo Chuar y equivalentes: qué son —amebas testadas, es decir Amoebozoa, la rama hermana de Obazoa— y las **perforaciones interpretadas como depredación por perforación**. Es la evidencia directa de depredación entre protistas que necesito: el trabajo concreto, el tamaño de las perforaciones, y las interpretaciones alternativas (diagénesis, daño post mortem, artefacto de preparación).
- **Fósiles con relevancia directa para el corredor**: *Bangiomorpha pubescens* (Formación Hunting) como testimonio de multicelularidad diferenciada y de reproducción sexual, y como **calibración dominante de los relojes eucariotas** —qué edad tiene, con qué método, y qué pasa con las estimaciones si esa calibración se mueve—; *Ourasphaira giraldae* como candidato a hongo más antiguo; *Bicellum brasieri* como candidato a holozoo con multicelularidad diferenciada.
- **El umbral final del corredor**: la Formación Doushantuo y los llamados embriones ediacáricos (*Tianzhushania*, *Megasphaera*, *Caveasphaera*, *Helicoforamina*), con la controversia sobre si son embriones animales o protistas holozoos enquistantes de tipo ictiospóreo. Los dos lados. Cierra exactamente donde termina mi corredor.
- **Biomarcadores**: esteranos y su interpretación; el **caso de los esteranos arcaicos** y su reinterpretación como contaminación, con la referencia del trabajo que lo demostró; la **biota de protosteroides** y qué implica para el «aburrido millardo» y para la distinción tronco/corona; el 24-isopropilcolestano y su disputa. Por qué la biosíntesis de esteroles exige oxígeno molecular y qué ata eso a la sección 7.

Para cada ítem: qué se observa, qué se infiere, con qué método se dató, con qué incertidumbre, quién discute la atribución y con qué argumento. Y para cada nodo del corredor: cuál es el fósil más antiguo que se le puede asignar con alguna confianza, o que no hay ninguno.

## 6. Tiempo: relojes moleculares y su desacuerdo con las rocas

- **Estimaciones publicadas** de la edad de LECA y de cada nodo del corredor, con el intervalo tal como lo da cada trabajo. Varios estudios, no uno, y cuánto se solapan.
- **Cómo se obtuvo cada estimación**: modelo de reloj (estricto, relajado log-normal, autocorrelado), calibraciones y qué tipo de acotación aporta cada una (mínima, máxima, uniforme), muestreo génico y taxonómico, datación por nodos o de evidencia total.
- **El peso desproporcionado de unas pocas calibraciones**, en especial *Bangiomorpha*.
- **El desacuerdo**: los fósiles inequívocos de eucariotas corona son bastante más jóvenes que muchas estimaciones de reloj. Expón la explicación de conciliación —que buena parte del registro antiguo es grupo tronco y no corona— y la posición minoritaria que defiende un origen eucariota tardío. Etiquétalo como controversia y no lo cierres.
- **Por qué los relojes son frágiles aquí**: divergencias antiguas, saturación, heterotaquia, ausencia de fósiles diagnósticos, dependencia del prior de calibración.

Cuando varios trabajos den estimaciones incompatibles de la misma magnitud, **no promedies, no elijas la más citada y no des un valor de consenso**. Enuméralas una a una con su rango, método, calibración, muestreo y fuente, y explica por qué difieren si los autores lo discuten. Si el rango total abarca un orden de magnitud, escríbelo con esas palabras. Si no existe estimación de consenso, la frase correcta es «no existe una estimación de consenso», no una cifra intermedia.

## 7. Ambiente

Quiero la cronología **y la magnitud**: qué valor alcanzó cada factor, en qué unidad, con qué proxy y con qué dispersión entre estudios. No homogeneices unidades entre trabajos.

- **Oxígeno**: Gran Oxidación, excursión de Lomagundi-Jatuli y su posible sobreimpulso, la caída posterior, el intervalo mesoproterozoico de baja pO₂, la oxigenación neoproterozoica. Cifras estimadas de oxígeno atmosférico y oceánico para el Paleoproterozoico, Mesoproterozoico y Neoproterozoico, cada una con su proxy (cromo, hierro, tierras raras, isótopos de azufre) y con la **discrepancia entre estimaciones bajas y altas**, que es una controversia cuantitativa abierta. Qué habilita el oxígeno (respiración aerobia, biosíntesis de esteroles, colágeno) y qué cuesta (especies reactivas, catalasa, superóxido dismutasa). **Umbrales fisiológicos publicados**: el umbral de Pasteur y sus revisiones, y los umbrales propuestos para procesos concretos como la síntesis de esteroles. Valor publicado y quién lo publicó; no lo redondees ni lo conviertas.
- **Química redox del océano**: el modelo de océano euxínico de aguas medias, la alternativa ferruginosa y el estado del debate. Qué fracción y qué profundidades se reconstruyen como óxicas, anóxicas ferruginosas o euxínicas, y cómo cambia a lo largo del intervalo. Qué **aceptores de electrones** hay en cada escenario y en qué orden de rendimiento energético.
- **Metales traza y nutrientes**: disponibilidad de Mo, Fe, Cu, Zn, Ni y Co a lo largo del Proterozoico y su relación con la fijación de nitrógeno; limitación por nitrógeno y por fósforo, incluidas las propuestas sobre secuestro de P por óxidos de hierro.
- **El «aburrido millardo»**: qué se afirma que fue estable y qué no, y las reinterpretaciones recientes, incluida la basada en biomarcadores de protosteroides.
- **Episodios globales con nombre**: glaciación huroniana; glaciaciones criogénicas Sturtiana y Marinoana con sus edades e incertidumbres; excursiones isotópicas de carbono relevantes. Temperatura y estabilidad del intervalo.
- **El hábitat de origen**: ¿surgió la célula eucariota en un entorno óxico o en uno anóxico y sulfídico? Las dos posiciones; la hipótesis del hidrógeno es anaerobia por construcción y eso tiene consecuencias.
- **Hábitat y estructura espacial**: qué ambientes concretos ocupan los linajes del corredor y sus parientes actuales —bentónico o planctónico, marino, salobre o dulceacuícola, sedimento, tapetes microbianos, interior de otro organismo— y qué reconstrucciones existen del ambiente ancestral de cada nodo. Qué transiciones de hábitat se han inferido y con qué evidencia. Qué se sabe de dispersión y aislamiento en poblaciones de eucariotas microbianos: hasta qué punto están estructuradas geográficamente y qué escalas de distancia se manejan.
- **Densidad de vida**: si existe alguna estimación publicada de abundancias o densidades celulares en comunidades microbianas del intervalo, dámela. Si no existe ninguna, dilo explícitamente: necesito saberlo.

Para cada factor: qué es dato medido y qué es reconstrucción, con qué proxy y con qué supuestos.

## 8. Ecología y trofismo

Esta es la parte que más me interesa y la que menos suele desarrollarse.

- **Modos de alimentación** en el corredor y sus ramas hermanas: fagotrofia, osmotrofia, parasitismo, comensalismo, filtración. Qué modo tiene cada nodo y cuándo aparece o se pierde.
- **Depredación como observación**: qué evidencia hay de depredación entre eucariotas tempranos y quién depredaba a quién. Evidencia indirecta: perforaciones y hendiduras en VSM y en acritarcos, ornamentaciones y envolturas interpretadas como defensivas, distribuciones de tamaño. Para cada caso, formación, yacimiento, edad con método, quién interpreta la marca como depredación y qué alternativas discute la literatura.
- **Depredación como hipótesis causal**, que no es lo mismo: el principio de recorte, la fagotrofia como carácter que define y habilita el estilo de vida eucariota, la escalada depredador-presa proterozoica y su relación con el tamaño celular y el blindaje. Para cada propuesta: qué predice sobre el registro fósil, qué la apoya y qué observación la falsaría.
- **Magnitudes de la interacción trófica**: rangos de tamaño celular en procariotas y eucariotas unicelulares, en las unidades en que se publiquen; relaciones de tamaño entre depredador y presa documentadas en protistas fagotróficos actuales; tasas de ingestión o de aclaramiento publicadas; restricciones físicas propuestas sobre qué puede fagocitar una célula de un tamaño dado y qué cuesta mantener ese tamaño. Si hay estimaciones de tamaño para microfósiles del intervalo, dámelas con su margen de error.
- **Virus y elementos móviles como actores.** Lisis viral como mortalidad y como reciclado de materia —el bucle viral—; virus gigantes (Nucleocytoviricota: mimivirus, pandoravirus, medusavirus, pitovirus) y qué aportan al debate sobre el origen del núcleo y sobre el tamaño de los genomas; virus de Asgard; **elementos genéticos móviles** —intrones de grupo II, retroelementos, transposones— y su relación con el origen de la telomerasa, los telómeros y los cromosomas lineales; y el origen de la inmunidad innata eucariota (cGAS-STING, viperinas, argonautas, ARN de interferencia) a partir de sistemas de defensa antivirales procariotas. Qué está documentado como homología y qué es analogía.
- **Qué es respuesta y qué es cambio heredable.** En los organismos comparables documentados, qué respuestas se producen dentro de la vida de una célula o en pocas generaciones y son reversibles —enquistamiento, cambio de modo de alimentación, agregación, formación de rosetas, transición entre formas del ciclo vital, latencia— y qué caracteres exigen cambio genético fijado. Para cada caso: qué señal lo dispara, cuánto tarda en manifestarse, si revierte al retirar la señal, cuánto cuesta y en qué linaje está documentado. Y cuáles son los límites conocidos de la plasticidad en estos linajes.
- **Los organismos concretos, con nombre.** Para cada uno: ecología documentada, modo de alimentación, hospedador si lo tiene, ciclo de vida, y qué aporta al corredor.
  - **Coanoflagelados**: *Monosiga brevicollis*, *Salpingoeca rosetta*, *Choanoeca flexa* (inversión de láminas celulares regulada por luz). En *S. rosetta*, los dos casos de inducción bacteriana: el sulfonolípido de *Algoriphagus machipongonensis* que induce rosetas y la condroitinasa de *Vibrio fischeri* que induce apareamiento. Molécula, bacteria, efecto, dosis si se publicó.
  - **Filasterea**: *Capsaspora owczarzaki* (relación con *Biomphalaria glabrata*, ciclo de tres estadios, agregación) y *Ministeria vibrans*, incluido lo que se descubrió sobre su supuesto pedúnculo.
  - **Ichthyosporea**: *Sphaeroforma arctica*, *Creolimax fragrantissima*, *Ichthyophonus hoferi*, *Abeoforma*, *Pirum*. Qué son respecto de sus hospedadores: parásitos, comensales, saprótrofos, o depende del estadio.
  - **Pluriformea y Corallochytrea**: *Corallochytrium limacisporum*, *Syssomonas multiformis*, *Pigoraptor*. Detalla *Syssomonas*: fusión celular parcial, agregación y alimentación conjunta sobre presas mayores que la propia célula.
  - **Otros holozoos unicelulares depredadores**: *Tunicaraptor unikontum* y su posición.
  - **Obazoa fuera de Opisthokonta**: *Thecamonas trahens*; *Breviata anathema*, *Pygsuia biforma* (con su ruta de rodoquinona adquirida por transferencia lateral) y *Lenisia limosa* con sus epibiontes *Arcobacter*. *Lenisia* me interesa mucho: es el análogo vivo más directo de la hipótesis sintrófica y está en una rama hermana del corredor.
  - **Holomycota**: *Fonticula alba*, *Nuclearia*, *Rozella allomycis* y Cryptomycota, Microsporidia (reducción genómica extrema, mitosomas, parasitismo obligado), quítridos flagelados.
  - **Amoebozoa**: *Dictyostelium discoideum* (agregación, cuerpos fructíferos, tramposos y castigo), *Entamoeba*, *Pelomyxa* con sus metanógenos endosimbióticos, *Mastigamoeba*.

  Si de alguno solo hay descripción morfológica y no genoma ni cultivo, dilo.

## 9. Asociación: el catálogo de desenlaces

- **Tipología cerrada y numerada** de resultados posibles de una asociación entre linajes, con al menos un caso documentado real por tipo, su fuente, y qué mantiene la asociación en ese estado: (1) contacto sin consecuencia; (2) depredación o consumo; (3) parasitismo; (4) asociación transitoria facultativa; (5) asociación estable no heredable; (6) endosimbiosis con transmisión vertical; (7) dependencia mutua obligada; (8) integración con transferencia de genes al genoma del hospedador; (9) reducción extrema u orgánulo derivado; (10) degradación o pérdida de la asociación; (11) ruptura con recuperación de vida libre, si existe algún caso. Si algún tipo no tiene caso documentado, dilo: es un dato.
- **Los casos, ordenados por grado de integración**, un párrafo cada uno y empezando por qué mecanismo del corredor ilustran:
  - **Asociación externa y sintrofía**: *Lenisia limosa* con epibiontes *Arcobacter*; consorcios de arqueas metanógenas y bacterias sulfatorreductoras.
  - **Endosimbiontes procariotas en protistas**: metanógenos en *Pelomyxa* y en ciliados anaerobios; endosimbiontes betaproteobacterianos en tripanosomátidos; *Perkinsela* en *Paramoeba*.
  - **Endosimbiosis en curso o reciente**: *Paulinella chromatophora*; el nitroplasto UCYN-A en *Braarudosphaera bigelowii*; *Hatena arenicola* y su división asimétrica con reparto desigual del simbionte; cuerpos esferoidales de *Rhopalodia* y *Epithemia*.
  - **Robo temporal de orgánulos (cleptoplastia)**: *Mesodinium*, *Dinophysis*, *Elysia*.
  - **Endosimbiosis secundaria y terciaria**, y el **nucleomorfo** de criptófitos y clorarachniófitos como reducción genómica sorprendida a medio camino.
  - **Endosimbiosis anidadas y reducción extrema**: *Tremblaya* y *Moranella*; *Buchnera*; *Wolbachia*.

  Para cada caso: quién es hospedador y quién simbionte, qué aporta cada uno, antigüedad estimada del inicio de la asociación, **modo de transmisión (vertical, horizontal o mixto)**, tamaño del genoma del simbionte comparado con el de sus parientes de vida libre, si hay transferencia de genes al núcleo, si hay importación de proteínas de vuelta, y si la asociación es obligada, facultativa o reversible.
- **Qué condiciones asocia la literatura a cada desenlace.** Qué se ha propuesto, y con qué evidencia, sobre lo que empuja una asociación hacia la dependencia obligada —transmisión vertical, cuellos de botella en la transmisión, pérdida de genes de reparación, deriva en poblaciones simbiontes pequeñas, restricción a un solo hospedador— y sobre lo que la mantiene facultativa o la rompe —transmisión horizontal, disponibilidad ambiental de la función que aporta el simbionte, cambio de hospedador, coste neto para el hospedador, competencia entre simbiontes dentro de la misma célula. No propongas un criterio ni construyas un modelo: quiero los correlatos empíricos y las hipótesis publicadas, con quién los sostiene, sobre qué casos y con qué apoyo.
- **Pérdida y degradación de la mitocondria, como gradiente ordenado**, con sus organismos: mitocondria aerobia completa → mitocondria anaerobia con cadena ramificada → orgánulo con genoma propio y metabolismo de hidrógeno (*Nyctotherus ovalis*, el intermedio que demuestra que el gradiente es real) → hidrogenosoma sin genoma (*Trichomonas vaginalis*) → mitosoma reducido al ensamblaje de agrupaciones hierro-azufre (*Giardia*, *Entamoeba*, Microsporidia) → **ausencia total de orgánulo derivado de la mitocondria** (*Monocercomonoides exilis*, con el sistema SUF adquirido por transferencia lateral) → **pérdida del genoma mitocondrial conservando el orgánulo** (*Henneguya salminicola*). Para cada estadio: qué funciones se conservan, cuáles se pierden, qué rendimiento energético queda y en qué ambiente vive el organismo. La integración no es irreversible ni es un solo estado, y esto es lo que lo demuestra.
- **Cooperación y conflicto entre los dos genomas**, como sistema con tensión permanente y no como episodio superado:
  - **Por qué la mitocondria conserva un genoma**: la hipótesis de colocalización para regulación redox y sus alternativas (hidrofobicidad de los productos, código genético divergente), con lo que las apoya y lo que las compromete.
  - **Transferencia endosimbiótica de genes al núcleo**: cuántos genes, en qué dirección, y cómo se resuelve el retorno de las proteínas al orgánulo (secuencias de destino, maquinaria de importación TOM/TIM). Qué se ha propuesto sobre por qué unos genes se transfieren y otros no.
  - **Reducción genómica del simbionte** y **trinquete de Muller** en poblaciones endosimbióticas pequeñas y asexuales. Trayectorias documentadas de pérdida de genes: cuántos, en cuánto tiempo, con qué forma de curva.
  - **Elementos mitocondriales egoístas**: mutantes con ventaja de replicación pese a ser deletéreos para la célula. Y elementos genéticos egoístas nucleares, con su peso en linajes de este corredor.
  - **Mecanismos de resolución del conflicto**: herencia uniparental, cuello de botella germinal, heteroplasmia, selección purificadora sobre el ADN mitocondrial. Qué evidencia hay de que operen como supresión de conflicto, en qué linajes, y cuáles son las excepciones conocidas.
  - **Consecuencias del conflicto**: la propuesta de que la anisogamia y los dos sexos derivan de la necesidad de controlar el conflicto citoplasmático; incompatibilidades mitonucleares; la «maldición de la madre».
- **Transferencia génica horizontal hacia y dentro de eucariotas.** Mecanismos reales (conjugación, transducción, transformación, elementos móviles, vectores virales) y cuáles se aplican a eucariotas y cuáles no. La **posición de que existe una barrera natural** a la transferencia de procariotas a eucariotas y la posición contraria, con las cifras de cada una y con el método por el que se atribuye origen bacteriano a un gen eucariota. La hipótesis del **trinquete «eres lo que comes»**. Casos aceptados dentro o cerca del corredor: la rodoquinona de *Pygsuia*, el sistema SUF de *Monocercomonoides*. Y al menos un **caso de transferencia reclamada y después atribuida a contaminación** —el episodio de los tardígrados es el más documentado—, porque necesito el patrón de error, no solo los aciertos.

## 10. Rasgos con costo

Reparto con la sección 9, para que nada aparezca dos veces con dos redacciones: **el mecanismo y su evidencia van en la 9; el balance de costes y beneficios con cifras va aquí**. Cada afirmación aparece una sola vez, con referencia cruzada desde la otra sección.

Para cada innovación del corredor, **qué cuesta**: núcleo y envoltura nuclear, endomembranas, citoesqueleto de actina y tubulina, fagocitosis, peroxisomas, mitosis (cerrada, abierta y semiabierta, con la distribución de esos estados en el corredor y su entorno), mitocondria y fosforilación oxidativa, cilio, adhesión celular, señalización.

Preséntalo como tabla con columnas: rasgo · qué habilita · dependencias previas que exige · cifra de coste publicada · unidad exacta · organismo, condición experimental o modelo del que procede · si es medida o estimada por los autores · fuente y localizador · compensación documentada. **Si no existe cifra publicada, escribe literalmente `SIN CIFRA PUBLICADA LOCALIZADA` en las columnas de cifra y unidad**; no dejes la celda vacía, no la rellenes con un orden de magnitud, una analogía, una regla general de bioenergética ni una estimación propia. Anticipo que muchas filas llevarán ese marcador: eso es un resultado correcto, no un fallo tuyo.

**La controversia energética, tratada como controversia.** Hay una disputa publicada, cuantitativa y sin resolver sobre si la mitocondria fue una precondición energética de la complejidad genómica. Quiero los dos lados con sus cifras y sus supuestos, no una síntesis:

- La posición de que la endosimbiosis elevó la energía disponible por gen en varios órdenes de magnitud y levantó una barrera que los procariotas no pueden superar: de dónde sale la cifra, qué se normaliza por qué (por gen, por genoma, por volumen celular, por superficie de membrana bioenergética) y qué predice.
- La posición contraria, que sostiene que el coste de un gen es una fracción minúscula del presupuesto celular y que **no existe barrera energética alguna**: qué mide, sobre qué organismos, y por qué llega a un resultado incompatible.
- Las réplicas y contrarréplicas publicadas entre ambas.
- **El marco poblacional como alternativa**: la **hipótesis de la barrera de deriva** y el papel del **tamaño efectivo de población (Ne)** en la complejidad genómica —intrones espliceosomales, expansión de familias génicas, regiones intergénicas, redundancia— sin recurrir a la energía. Da valores de Ne publicados para procariotas, protistas unicelulares y eucariotas multicelulares, con su método de estimación, y qué magnitudes de coeficiente de selección se consideran efectivas frente a la deriva a esos tamaños.

Deja explícito qué parte de la discrepancia es empírica y qué parte es una elección de denominador, y **no la resuelvas**. Di además qué rasgos del corredor se explican mejor como adaptación con beneficio neto y cuáles se han propuesto como productos de deriva sin beneficio: el corpus necesita poder decir «esto no hizo falta que fuera ventajoso».

## 11. Sexo, meiosis y ciclo vital

> **Sección obligatoria y de primer orden.** El origen del sexo entra en la Campaña 1 como contenido del Atlas y como mecánica jugable, así que este apartado alimenta directamente el diseño. No lo trates como contexto.

- **¿Era sexual LECA?** El estado de la cuestión y su evidencia: presencia del kit génico meiótico (SPO11, DMC1, MSH4, MSH5, HOP1, MND1, REC8 y los que la literatura añada) en linajes que se creían asexuales, y qué grado de aceptación tiene la conclusión de que el sexo es ancestral y universal en eucariotas. Distingue meiosis de sexo, y ambos de recombinación.
- **De dónde sale la meiosis**: relación con la mitosis y con la maquinaria bacteriana de reparación por recombinación homóloga (RecA/Rad51). Qué se propone como función original: reparación, purga de mutaciones, generación de variación, resolución de ploidía. Y separa las hipótesis sobre el **origen** de las hipótesis sobre el **mantenimiento**: no son lo mismo.
- **Qué cuesta el sexo en un protista**: el coste doble clásico y por qué no se aplica igual en linajes isógamos; coste de encontrar pareja, de la fusión, del ciclo de ploidía y del tiempo.
- **Tipos de apareamiento, singamia, cariogamia, ciclos haplonte, diplonte y haplodiplonte** en el corredor y su entorno; origen de la anisogamia.
- **Sexo críptico y parasexualidad** en linajes tenidos por asexuales: cómo se detecta (firmas de recombinación en poblaciones) frente a cómo se observa.
- **Evidencia fósil de sexo**: qué caracteres de *Bangiomorpha* se interpretan como esporas diferenciadas y qué fuerza tiene esa interpretación.
- **Apareamiento inducido por señales externas**: el caso documentado en coanoflagelados.

## 12. Multicelularidad y el repertorio preanimal

Trata la multicelularidad como un problema con varias soluciones documentadas, no como un rasgo único.

- **Vía clonal por división sin separación**: colonias y rosetas de coanoflagelados; qué las induce y qué cuesta mantenerlas.
- **Vía cenocítica con celularización**: crecimiento a núcleos múltiples seguido de compartimentación, documentado en Ichthyosporea (*Sphaeroforma arctica*, *Creolimax fragrantissima*). Descríbela con detalle; es la ruta que me falta por completo y está en una rama hermana del corredor.
- **Vía agregativa**: células que se juntan tras crecer por separado — *Capsaspora owczarzaki*, *Fonticula alba*, *Dictyostelium discoideum*. Tres orígenes independientes en tres ramas del entorno inmediato.
- **La consecuencia teórica de la diferencia**: qué relación de parentesco genera cada ruta entre las células del agregado, por qué la vía agregativa admite tramposos y la clonal mucho menos, y qué evidencia empírica de conflicto y de mecanismos antitramposo existe. Los trabajos concretos.
- **Evidencia experimental de costes**: experimentos de evolución de multicelularidad en levadura y sus continuaciones a escala macroscópica — qué se midió, en cuántas generaciones, con qué compensaciones.
- **El repertorio ancestral: qué de «animal» ya estaba antes de los animales.** Con genoma y cifras —tamaño, número de genes, densidad de intrones— para *Monosiga brevicollis*, *Salpingoeca rosetta*, *Capsaspora owczarzaki*, *Ministeria vibrans*, *Sphaeroforma arctica*, *Creolimax fragrantissima*, *Corallochytrium limacisporum*, *Thecamonas trahens*. Y para cada familia funcional, en qué linaje aparece y en cuál falta: adhesión (integrinas y adhesoma, cadherinas, dominios de matriz extracelular, colágeno); señalización (tirosina quinasas y fosfatasas, receptores acoplados a proteína G, componentes de Notch y Hedgehog); regulación (Brachyury, Runx, p53/p63/p73, Myc, familias de homeodominio).
- **La hipótesis de la transición de temporal a espacial**: el mismo repertorio regulatorio desplegado en estadios sucesivos de un ciclo vital unicelular y después en tipos celulares coexistentes, con la expresión diferencial a lo largo del ciclo de *Capsaspora* como caso documentado. Qué la apoya y qué queda sin explicar.

## 13. Escalas, tasas y recuentos

Necesito poder ordenar los procesos en el tiempo, no solo fecharlos. Para cada punto: qué duración o qué tasa da la literatura, en qué unidad y con qué fuente. **Si no hay cifra publicada, dilo, y da en su lugar la ordenación relativa que la literatura sí sostenga, indicando quién la sostiene.**

- Duración estimada del tallo eucariota, es decir cuánto separa a FECA de LECA.
- Tiempos de generación y tasas de división de eucariotas unicelulares de vida libre comparables a los del corredor —amebas, coanoflagelados, ictiospóreos, apusomonádidos—, con las condiciones de cultivo en que se midieron.
- Tasas de mutación por generación y por sitio publicadas para procariotas y para eucariotas unicelulares.
- Duración de los episodios ambientales: cuánto duran las glaciaciones globales, cuánto tarda en cambiar el estado redox de una cuenca oceánica, qué duración se asigna al «aburrido millardo» y con qué límites.
- En cada caso de endosimbiosis documentado, cuánto tiempo ha transcurrido desde el inicio estimado de la asociación hasta el grado de integración que se observa hoy.
- Cuántos genes conserva un genoma mitocondrial y cuál es el rango entre eucariotas.
- **Rapidez relativa entre procesos**: qué es rápido y qué es lento en esta historia, y respecto a qué.

Y los recuentos, porque necesito distinguir lo que ocurrió una sola vez de lo que ocurre con regularidad y no quiero deducirlo del silencio del texto. Para cada proceso, cuántas veces se ha originado de forma independiente según la literatura, quién hace el recuento y con qué criterio:

- endosimbiosis primaria que produce un orgánulo con transferencia de genes al núcleo: qué casos se reconocen como independientes, y cuál es concretamente la evidencia de que la mitocondria tiene un origen único y no varios;
- pérdida, reducción o degradación de la mitocondria: en cuántos linajes y con qué independencia entre ellos;
- fagotrofia: orígenes y pérdidas reconocidos a lo largo de los eucariotas;
- multicelularidad clonal, cenocítica y agregativa: cuántos orígenes independientes se cuentan;
- parasitismo intracelular y simbiosis obligada: si existe alguna estimación de con qué frecuencia aparecen.

Cuando un recuento sea disputado, dame el rango y quién sostiene cada extremo.

## 14. Nombres y nomenclatura

- **No inventes nombres.** Cuando haya que referirse a una población o linaje sin nombre formal, usa una etiqueta descriptiva. **Y decláralas antes de la sección 1, en una lista cerrada**, del tipo «linaje hospedador arqueano no identificado» o «simbionte alfaproteobacteriano ancestral no muestreado». A partir de ahí **úsalas siempre con esa redacción literal**, en la prosa y en las tablas: no las abrevies, no las parafrasees, no introduzcas variantes sobre la marcha. Si necesitas una etiqueta nueva, añádela a la lista. Si el mismo objeto aparece como «el hospedador arqueano», «el linaje hospedador» y «la población hospedadora ancestral», mi sistema creará tres entidades donde hay una.
- **Marcado.** Declara **una sola vez** que prácticamente todo este corredor son clados sin rango formal, y lista las excepciones que tengan rango con el código que lo regula. No marques `[R]`/`[C]` nodo por nodo: es una columna constante que no informa. Reserva el marcado nodo a nodo para lo que sí discrimina: `⚠` posición, contenido o validez discutidos · `≈` nombres cuya equivalencia depende de la definición adoptada · `[F]` clado recuperado por filogenómica sin sinapomorfía morfológica publicada · `[H]` nodo cuya composición depende de la hipótesis adoptada, indicando cuál. Usa `†` **solo** para taxones con registro fósil propio: un linaje troncal o una población ancestral reconstruida no lleva `†`, lleva su etiqueta de linaje no muestreado.
- **Define operativamente *crown group*, *stem group* y *total group*, y después aplícalos.** Para cada fósil proterozoico que menciones, di si se interpreta como grupo corona de Eukaryota, grupo tronco, o de posición indeterminada, y con qué carácter se argumenta. Para cada nodo del corredor, qué distingue el clado corona del clado total y si hay algún fósil o linaje asignado al tallo. Explica por qué esta distinción es la bisagra del desacuerdo entre relojes y rocas: no es una sutileza nomenclatural, es la propuesta de conciliación.
- **Distingue tres cosas que suelen mezclarse**: nombre nomenclaturalmente disponible, taxón aceptado por una comunidad o base de datos, y clado filogenéticamente respaldado.
- **Conserva la historia nomenclatural**: sinónimos, grafías alternativas y circunscripciones rivales. Cuando dos nombres compitan por el mismo nodo, explica **por qué** compiten: sinonimia plena, preferencia de autor o conflicto real de contenido. Los casos que me interesan: Choanozoa *sensu stricto* frente a Apoikozoa, y los nombres rivales del nodo Amorphea de la sección 4. Aclara además con fuente la relación entre **Pluriformea**, **Corallochytrea** y *Corallochytrium*: si un nombre está anidado en el otro, si son sinónimos, o si la circunscripción varía según autor. En general: cualquier par de nombres que yo haya escrito con barra o con `≈` en este encargo es una conjetura de trabajo, no un dato; si me equivoco, dilo explícitamente.
- **Códigos aplicables.** Explica qué gobierna el ICZN, qué el ICN, qué el ICNP y **qué el PhyloCode**, cuyo volumen *Phylonyms* contiene definiciones filogenéticas formales para varios clados de este corredor. No digas que estos nodos «no tienen código»: di cuál se les aplica, cuál no, y cuáles tienen definición filogenética publicada frente a cuáles son uso convencional.
- **Advertencias terminológicas.** Dedica una sección a los términos de uso común que no son clados en este ámbito. Como mínimo, más los que encuentres: «protista» y reino Protista · «protozoo» · «alga», incluido su uso para cianobacterias · «invertebrado» · «procariota», definición negativa y el argumento de que debería abandonarse como categoría taxonómica · «acritarco», taxón de forma artificial y categoría principal del registro fósil de esta campaña · «reino» aplicado a eucariotas (cinco reinos, seis, siete) · **Archezoa**, hipótesis de eucariotas primitivamente sin mitocondria, **refutada**: quiero el caso completo, porque es el mejor ejemplo documentado de hipótesis abandonada en este ámbito · **Excavata** · **Chromalveolata** · **Unikonta / bikonta** · «hongo» aplicado a oomicetos y a mohos mucilaginosos, que son estramenópilos y Amoebozoa · «flagelo», que designa dos estructuras no homólogas en bacterias y en eucariotas · «simbiosis» usada como sinónimo de mutualismo cuando incluye el parasitismo · «endosimbiosis seriada» y qué partes de la propuesta original se aceptan hoy · «eucariota primitivo» · «organismo simple» · «fósil viviente» · «eslabón perdido» · **«basal» aplicado a un linaje viviente**, con especial cuidado: explica por qué un linaje viviente no puede ser basal respecto de otro viviente y qué se quiere decir realmente cuando se usa.

  Para cada término: qué agrupa o agrupaba, quién lo introdujo y cuándo, por qué es parafilético, polifilético, artificial, informal o refutado, qué evidencia lo desmontó si la hubo, con qué se sustituye hoy, y si conserva algún uso legítimo acotado —ecológico, funcional, didáctico— y cuál exactamente. «Protista» y «alga» no están en la misma situación que «invertebrado», y necesito la diferencia.

  Esta sección es la que más riesgo tiene de salirte de memoria, porque son cosas que todo el mundo sabe. Precisamente por eso: **cada término necesita al menos una fuente que documente el problema**, no solo tu explicación. Que «protista» sea parafilético es de manual, pero necesito el manual. Si para alguno no encuentras nada citable, escríbelo igual y márcalo como `glosa`.

  Es material que necesito y que no tengo, y quiero que esta sección esté entre las más largas del documento.

## 15. Lo que no se sabe, y cómo lo sabemos

- **El mapa del terreno probatorio.** Para cada clase de evidencia disponible en este intervalo —relojes moleculares, filogenómica comparada, microfósiles y sus tipos, biomarcadores, proxies geoquímicos, genómica y biología celular de organismos actuales, experimentos de laboratorio con simbiosis— dime: qué tipo de pregunta puede responder y cuál no, qué resolución temporal y taxonómica alcanza, y cuáles son sus modos de fallo conocidos.
- **Evidencia retirada.** Qué casos hay de evidencia que se aceptó ampliamente y después se reinterpretó o se retiró. El de los esteranos precámbricos y la contaminación es el que conozco; quiero saber si hay otros y qué se aprendió de cada uno. Es el mejor material que existe para mostrar cómo funciona la ciencia.
- **Nodos con soporte débil**: cuáles y por qué (divergencias antiguas, ramas internas cortas, sensibilidad al muestreo o al modelo, atracción de ramas largas, heterogeneidad composicional), qué fechas son especulativas, qué relaciones cambiarían con mejor muestreo, y qué preguntas siguen abiertas.
- **Búsquedas negativas.** Qué buscaste explícitamente y no encontraste, con los términos exactos que usaste. Marca cada hueco del documento con una de estas tres etiquetas: `LA LITERATURA DECLARA QUE NO SE SABE` (con la cita que lo declara) · `NO LOCALIZADO EN ESTA SESIÓN` (con los términos buscados) · `NO BUSCADO` (con el motivo). Un hueco sin etiqueta no me sirve, porque no puedo saber si volver a buscarlo.

**Un hueco declarado me sirve más que una respuesta rellenada.**

## 16. Cómo quiero las afirmaciones

Este material alimenta una base de conocimiento donde la unidad es la afirmación con evidencia, no el árbol. Por eso el documento tendrá **dos capas**:

- **capa narrativa**: prosa, árboles, explicaciones, contexto. Escríbela como quieras; es la que se lee.
- **capa de registro**: filas numeradas. Es la que se procesa.

**Ninguna afirmación puede existir solo en la capa narrativa.** Si algo se afirma en la prosa y no aparece como fila del registro, se pierde. La prosa es el argumento; el registro es el dato. Toda relación que aparezca en un bloque de árbol tiene que aparecer también como fila.

Al final de cada sección numerada, su **registro de afirmaciones**: una tabla donde **cada fila es una sola proposición**. Si un párrafo contiene cuatro proposiciones, produce cuatro filas. La prueba es simple: si una fila puede ser verdadera en una mitad y falsa en la otra, todavía no es una fila.

Columnas, en este orden exacto:

`#` · `Afirmación` · `Sujeto` · `Predicado` · `Objeto` · `Atribución` · `Fuente` · `Aceptación` · `Fuerza` · `Motivo` · `Resolución` · `Vigencia`

- **`#`** — identificador local correlativo para todo el documento: `C-001`, `C-002`… Nunca lo reinicies por sección.
- **`Afirmación`** — una frase declarativa, plana, que pueda ser verdadera o falsa por sí sola.
- **`Sujeto` / `Predicado` / `Objeto`** — la misma proposición descompuesta. Para el predicado usa esta lista cuando encaje: `miembro_de`, `grupo_hermano_de`, `desciende_de`, `diverge_de`, `grupo_corona_de`, `linaje_troncal_de`, `posee_rasgo`, `adquiere_rasgo`, `pierde_rasgo`, `converge_con`, `depreda_a`, `es_huesped_de`, `compite_con`, `endosimbiosis_con`, `transfiere_gen_a`, `sinonimo_propuesto_de`, `clasificado_como_por`, `tiene_edad_estimada`, `tiene_valor_medido`, `propuesto_por`, `respaldado_por`, `cuestionado_por`, `incompatible_con`. Si ninguno encaja, inventa el tuyo y márcalo con asterisco: prefiero un predicado nuevo declarado a una proposición forzada dentro de uno que no le corresponde.
- **`Atribución`** — exactamente uno de tres valores. **`expresa`**: la fuente afirma eso, en esos términos; es el caso normal y debería ser la mayoría del documento. **`sintesis`**: lo concluyes tú combinando fuentes o extendiendo una fuente a un caso que no trata; indica de qué filas sale, `sintesis(C-012, C-031)`; si no puedes nombrar las filas de origen, no es una síntesis, es una glosa. **`glosa`**: explicación, analogía o comentario tuyo sin fuente detrás; es legítimo y no quiero que lo evites, quiero que esté marcado. Voy a tratar las tres de forma distinta, y el error que quiero evitar tiene nombre: una conclusión tuya perfectamente razonable que dentro de seis meses aparece en mi base de datos con un DOI al lado, respaldada por un artículo que en realidad no dice eso.
- **`Fuente`** — clave del apéndice A **más el sitio exacto**: `S07 §3.2` · `S07 fig. 4` · `S07 tabla 1` · `S07 supl. fig. S3` · `S07 p. 1142`. Una clave sin localizador solo vale cuando la afirmación **es** la tesis general del trabajo. Siempre que haya de por medio una cifra, un intervalo, un valor de soporte o un carácter concreto, quiero el localizador. Si no puedes ubicar el pasaje, escribe `sin localizar`: un `sin localizar` honesto me cuesta una comprobación, un localizador inventado me cuesta la confianza en todos los demás.
- **`Aceptación`** — `consenso amplio` · `aceptación mayoritaria` · `aceptación mixta` · `posición minoritaria` · `no evaluado`. Toda etiqueta distinta de «no evaluado» debe poder justificarse nombrando al menos una fuente que la sostiene y, si no es consenso amplio, al menos una que discrepe. Si no puedes nombrar la discrepancia, la etiqueta correcta es «no evaluado».
- **`Fuerza`** — `alta` · `media` · `baja` · `desconocida`.
- **`Motivo`** — una línea que justifique la fuerza, obligatoria: «replicado en tres filogenómicas independientes», «un solo genoma», «inferido de un único carácter», «topología sensible al modelo de heterogeneidad composicional», «medido en un organismo modelo y extrapolado». Sin motivo, la etiqueta de fuerza no vale nada y no la voy a usar.
- **`Resolución`** — `resuelta` · `parcialmente resuelta` · `sin resolver` · `información insuficiente`. Distingue con cuidado «hay disputa» de «no hay datos para decidir»: son estados distintos del mundo.
- **`Vigencia`** — `vigente` · `histórica` · `superada` · `rechazada`. Se aplica también a nombres y a hipótesis. Una circunscripción abandonada hace veinte años es `histórica`, no es un error: la quiero conservada y etiquetada, porque los nombres viejos aparecen en la literatura vieja y necesito poder leerla.

Los cuatro ejes últimos son **independientes**: una afirmación puede tener consenso amplio y evidencia débil a la vez, simplemente porque nadie la ha puesto a prueba. Esa combinación es información, no una contradicción. No los mezcles, no los promedies y no conviertas ninguno en un porcentaje.

Tres reglas más:

- **Los rechazos son afirmaciones y ocupan su propia fila.** Cuando una fuente contradiga a otra, no basta con exponer las dos posiciones en párrafos consecutivos: escribe una fila más, con predicado `cuestionado_por`, que enlace explícitamente a la fila cuestionada. La fila cuestionada se conserva intacta: no la corrijas ni la suavices. Lo mismo con las contraevidencias que debilitan una afirmación sin negarla.
- **Cuando la formulación cargue epistémicamente, cítala literal.** Si una fuente dice «is consistent with», no escribas «demuestra»; si dice «cannot be ruled out», no escribas «es posible que». En esas filas añade entre comillas el fragmento original **en su idioma**, junto al localizador. Aplícalo siempre en tres sitios: verbos que distinguen sugerir, apoyar y demostrar; negaciones y dobles negaciones; y cualquier frase que acote el alcance («under this model», «in these taxa», «when compositional heterogeneity is accounted for»). Prefiero una fila con una cita en inglés a una fila en español elegante que ya no puedo auditar.
- **Cada topología, con su método.** Cuando cites una relación filogenética, di con qué se obtuvo: matriz (número de genes y de posiciones, criterio de ortología), muestreo taxonómico, modelo de sustitución —y en particular si es sitio-homogéneo o **sitio-heterogéneo** (CAT, CAT-GTR, mezclas de perfiles)—, si hubo **recodificación de aminoácidos** (Dayhoff, SR4), eliminación de sitios rápidos o de taxones de rama larga, y si se hizo coalescencia de árboles génicos frente a concatenación. Indica qué pruebas de artefacto se aplicaron. Si dos estudios discrepan, di si discrepan en los datos o solo en el modelo.

**Cuando una fuente dé soporte cuantitativo** —bootstrap, probabilidad posterior, intervalo, margen de error— transcríbelo tal cual. No conviertas medidas distintas a una escala común ni inventes porcentajes de confianza.

**Regla de densidad.** Toda oración de la prosa que contenga una fecha, una cifra, un nombre de taxón atribuido a un autor, una relación de parentesco, un carácter diagnóstico, un mecanismo propuesto o una atribución de hipótesis debe llevar al menos un localizador de fuente. Si una oración de ese tipo no lo lleva, no la borres: precédela del marcador literal `[SIN FUENTE]` y explica en la misma línea por qué la incluyes.

**Cuando no haya cifra, quiero la ordenación.** Si la literatura no da un valor absoluto pero sí permite ordenar dos procesos por magnitud, duración o rapidez, dame esa ordenación y quién la sostiene, marcándola expresamente como comparación cualitativa y no como medida. Una comparación con fuente me sirve; una cifra plausible sin fuente no me sirve para nada.

## 17. Apéndices

Todos en tablas Markdown con las columnas en el orden que indico y sin columnas añadidas: se leen a máquina. Usa **solo claves locales de este documento** (`C-001`, `S01`, `E01`, `H01`). No generes identificadores con prefijos tipo `CLAIM-`, `SRC-`, `ENTITY-`, `EVENT-` ni `HYP-`: esos los asigna mi pipeline y los tuyos colisionarían. Si un campo no aplica, escribe `n/a`; no lo dejes en blanco.

**A. Fuentes.** Es la bibliografía; no hagas otra aparte. Columnas: clave (`S01`…) · autores · año · título · publicación o repositorio · DOI en forma `https://doi.org/10.xxxx/...` o URL resoluble si no hay DOI · tipo · notas de calidad · fecha de consulta.
El **tipo** es de esta lista cerrada: `investigación primaria` · `revisión` · `base de datos taxonómica` · `preprint` · `capítulo o libro` · `tesis` · `divulgación o blog` · `otro`. No lo deduzcas del prestigio de la revista: una revisión en *Nature* es una revisión.
En **notas de calidad**, cuando aplique: si es un preprint sin revisión por pares, si el trabajo ha sido corregido o retractado, si es una síntesis secundaria sin datos propios, o si es la única fuente que sostiene algo en todo el documento. No te pido que descartes fuentes débiles: te pido que las etiquetes, porque después tengo que decidir qué verificar primero. Y no apoyes en un preprint o en un recurso no revisado ninguna afirmación que presentes como consenso amplio.
Una URL suelta no me sirve como referencia. El precedente de este encargo acabó con treinta y cuatro URLs desnudas sin autor, año ni título, y fue inutilizable.

**B. Entidades.** Una fila por cada cosa nombrada: clado, nombre taxonómico, concepto taxonómico, linaje, población reconstruida, rasgo, gen, orgánulo, método, magnitud ambiental, término histórico. Columnas: etiqueta preferida · tipo · sinónimos y grafías alternativas · marcas (`⚠`, `≈`, `†`, `[F]`, `[H]`) como atributos de la fila · `#` de la fila del registro donde aparece por primera vez.
Cuando un nombre tenga circunscripciones rivales, **una fila por circunscripción, con su fuente**. Choanozoa *sensu stricto* según un autor y Choanozoa en su uso histórico son dos filas, no una fila con una nota. Toda marca `≈` obliga a esas filas.

**C. Eventos.** Una fila por episodio con participantes. Columnas: clave (`E01`…) · tipo · participantes **con su papel** · entidad resultante si la hay · intervalo temporal · `#` de las filas que lo sostienen · qué fuente lo describe como evento.
**Tipo**: `endosimbiosis` · `transferencia horizontal` · `transferencia génica endosimbiótica` · `divergencia` · `radiación` · `extinción` · `adquisición de rasgo` · `pérdida de rasgo` · `reducción genómica` · `depredación` · `competencia` · `relación huésped-patógeno` · `asociación no heredable`.
**Papeles**: `hospedador` · `endosimbionte` · `simbionte extracelular` · `donante` · `receptor` · `población parental` · `linaje resultante` · `depredador` · `presa` · `huésped` · `parásito` · `competidor`. Un participante sin papel no me sirve: «la mitocondria y la arquea hospedadora participaron en la endosimbiosis» no dice quién entró en quién.
**La integración mitocondrial no es un evento, son varios**: adquisición, reducción genómica del simbionte, transferencia de genes al núcleo, aparición de la importación de proteínas. Si la literatura los separa, sepáralos en filas distintas, con su orden relativo y con qué evidencia lo sostiene. Si no puede ordenarlos, dilo.
**Los casos comparables llevan ficha igual**: toda endosimbiosis, asociación, dependencia o pérdida que traigas de fuera del corredor va aquí con sus participantes y papeles.
Añade una columna de **desenlace**: `transitoria` · `dependencia` · `integración heredable` · `degradación` · `pérdida` · `no determinado`.

**D. Fechas.** Una fila por dato temporal, incluidas las que aparecen en la prosa y en los árboles. Columnas: a qué se aplica · límite más antiguo · límite más reciente · **unidad explícita** · incertidumbre tal como la da la fuente · tipo (`edad de ocurrencia` · `rango observado` · `rango inferido de linaje` · `estimación de divergencia` · `intervalo de evento` · `evidencia de rasgo` · `publicación`) · método y calibración · `observado` o `inferido` · fuente con localizador · `#` de la fila que la sostiene.
Declara al principio del documento qué unidad usas por defecto y usa además las unidades con nombre de la tabla cronoestratigráfica internacional (Paleoproterozoico, Mesoproterozoico, Neoproterozoico; Statheriense, Calymmiense, Ectasiense, Steniense, Toniense, Criogénico, Ediacárico), no solo cifras en Ga. Si conviertes una cifra de unidad, conserva también el valor original. **Un intervalo sin unidad explícita no me sirve, aunque sea obvio por el contexto**, y con edades entre 1,5 y 2,5 Ga la ambigüedad Ma/Ga es real. Si un campo no consta en la fuente, escribe `no consta en la fuente`.

**E. Hipótesis.** Una fila por hipótesis con nombre propio. Columnas: clave (`H01`…) · qué sostiene en una frase · supuestos que da por buenos · `#` de las filas que la componen · fuentes a favor · fuentes en contra · **con qué otras hipótesis es incompatible y en qué punto exacto** · qué observación la falsaría. Distingue incompatibilidad real de rivalidad aparente.

**F. Magnitudes.** Todas las cifras del documento reunidas en una sola tabla. Columnas: magnitud · valor tal como lo publica la fuente · unidad original · organismo, nodo o intervalo al que se aplica · método o proxy · incertidumbre publicada · `observado` o `inferido` · fuente con localizador · `#`.
**Sin conversiones, sin unificar unidades y sin promediar entre estudios discordantes.** Si dos fuentes dan valores distintos para lo mismo, quiero las dos filas y quiero saber en qué difieren sus métodos.

**G. Material no encajado.** Lo que encuentres y sea relevante pero no encaje en ninguna sección va aquí, con la misma exigencia de fuente por afirmación y con una nota de a qué sección crees que pertenece. No lo omitas, pero no lo dejes suelto en la prosa.

**H. Recuento de control.** Al final: número total de fuentes distintas · número de oraciones marcadas `[SIN FUENTE]` · número de filas del registro · número de afirmaciones que dependen de una sola fuente · número de celdas con `SIN CIFRA PUBLICADA LOCALIZADA`. Prefiero saberlo a descubrirlo contando.

## 18. Formato, esfuerzo y entrega

Documento en Markdown, en español.

- **Numera todos los encabezados de forma jerárquica y estable** (`3.`, `3.2.`, `3.2.1.`) y mantén los párrafos cortos, de una idea cada uno. Cada afirmación tiene que poder localizarse en un pasaje concreto y citable; un párrafo de veinte líneas con seis proposiciones no es un pasaje, es un problema.
- **No pongas información sustantiva solo** en un pie de tabla, en un paréntesis largo, en una nota al margen o en el pie de una figura.
- **Árboles** en bloques de texto, con las marcas de la sección 14.
- **Una tabla por cada nodo del corredor y por cada rama hermana inmediata**, con columnas: nodo · qué linajes quedan dentro · qué linaje queda fuera (grupo hermano) · caracteres morfológicos o ultraestructurales propuestos como sinapomorfía, con fuente · caracteres moleculares o genómicos propuestos (fusiones génicas, inserciones y deleciones raras, sintenia, dominios proteicos), con fuente · tipo de evidencia que sostiene el nodo · soporte cuantitativo transcrito literalmente · edad estimada con intervalo · método de la estimación · `#` de la fila del registro que sostiene cada celda sustantiva.
  Esta tabla es una **vista de resumen**: no debe contener nada que no esté ya en el registro.
  Advertencia que asumo de antemano: varios nodos de este corredor se recuperaron por filogenómica y es probable que no tengan ninguna sinapomorfía morfológica publicada. Si no localizas una para ese nodo concreto, escribe literalmente `SIN SINAPOMORFÍA MORFOLÓGICA PUBLICADA LOCALIZADA`. No rellenes la celda con caracteres generales del grupo, ni con rasgos heredados de un nodo superior, ni con una inferencia tuya. **Rellenar esa celda con un carácter no publicado para ese nodo es el peor error que puedes cometer en este documento**, y prefiero veinte celdas con ese marcador a una sola inventada.
- **Autoridades de referencia, declaradas al principio y no condicionalmente.** Para clasificación de eucariotas, la revisión de clasificación, nomenclatura y diversidad de eucariotas de la Sociedad Internacional de Protistólogos (Adl et al.), con la edición exacta; si te apartas de ella en algún nodo, dilo y justifícalo. Para recursos de secuencia y muestreo, indica cuáles usas (EukProt, PR2, UniEuk o los que correspondan). Para el tiempo geológico, la versión de la tabla cronoestratigráfica internacional de la ICS.
- **Reparto del esfuerzo.** La ecología, los mecanismos y las magnitudes (secciones 5 a 13) deben ocupar **al menos tanto** como la eucariogénesis y la nomenclatura juntas. Cada rama hermana de la sección 1 debe tener tratamiento propio. Las secciones glamurosas y bien publicadas tienden a absorber todo el presupuesto: no dejes que pase.
- **Extensión.** Como referencia de escala: un encargo anterior mío sobre la filogenia humana completa produjo unas 2.000 líneas con 34 fuentes. Este cubre un tramo del árbol mucho más corto y exige densidad mucho mayor. **Espero bastantes más de 80 fuentes distintas**; si te quedas por debajo, dilo en la primera línea y explica qué no conseguiste recuperar. Ninguna sección de nivel 2 puede sostenerse sobre una sola fuente.
- **Si no cabe en una entrega, no comprimas el final ni recortes uniformemente.** Entrega por partes y dime en la primera qué falta y en qué orden llegará. Orden de prioridad si algo tiene que ceder: (1) nombres, nomenclatura y advertencias terminológicas; (2) el punto de partida, la eucariogénesis y las hipótesis rivales; (3) lo que no se sabe, controversias y búsquedas negativas; (4) asociación y desenlaces; (5) rasgos con costo; (6) ecología y trofismo; (7) registro material y tiempo; (8) ambiente; (9) el resto.

Por último, un cierre breve: **este corpus tiene que permitir responder, con material citado, a estas seis preguntas.** Añade un apartado final que remita a las secciones donde está el material de cada una, o que diga que la literatura no permite responderla.

1. ¿Qué hace estable una asociación inicialmente conflictiva?
2. ¿Cómo cambian los costos y beneficios con el ambiente?
3. ¿Cuándo una dependencia se vuelve heredable?
4. ¿Qué distingue divergencia, transferencia e integración?
5. ¿Cómo puede la misma evidencia apoyar reconstrucciones diferentes?
6. ¿Qué rasgos están observados y cuáles inferidos?