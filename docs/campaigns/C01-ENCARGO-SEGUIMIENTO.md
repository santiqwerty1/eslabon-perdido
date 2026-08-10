# Encargo de seguimiento sobre el corredor Eukaryota → Holozoa

Ejecuta lo que sigue sobre el corpus que ya entregaste. **No es una revisión ni una reescritura**: son cuatro adiciones acotadas. Todo lo que ya está entregado se queda como está, salvo donde digo lo contrario.

Antes de nada, dos cosas que hiciste bien y que **no** quiero que cambies:

- **Las búsquedas negativas etiquetadas `NO LOCALIZADO EN ESTA SESIÓN` son un resultado, no una tarea pendiente.** No las rellenes. Un hueco declarado me sirve; una respuesta rellenada me estropea lo que construya encima.
- **El eje de aceptación en «no evaluado»**. Aplicaste la regla al pie de la letra —si no puedes nombrar quién discrepa, no etiquetes— y es lo correcto. El punto 4 lo matiza, pero no lo revierte.

---

## 1. Regenerar el manifiesto y el apéndice H

Los dos autoinformes van por detrás de los datos:

| | Declarado | En los CSV |
|---|---:|---:|
| filas del registro | 1.937 | **1.952** |
| fuentes distintas | 517 | **523** |
| entidades | 1.491 | **1.500** |
| fechas | 212 | **215** |
| magnitudes | 553 | **562** |

Es mecánico, pero importa más de lo que parece: el contraste entre lo que el corpus declara y lo que contiene es lo único que puede detener una ingestión sin que nadie tenga que leerse 1.952 filas. Con los recuentos desfasados, esa comprobación falla desde el primer minuto y deja de servir.

Regenera `manifest.json` y `H_recuento_control.csv` desde los datos, no a mano.

## 2. Siete filas del apéndice G que deberían tener sección propia

**Esto es un fallo de mi encargo, no tuyo.** Las aparcaste en «material no encajado» porque el prompt no les dio dónde vivir, y tenías razón en no forzarlas dentro de una sección que no les correspondía. Pero son contenido central del corredor y las necesito desarrolladas.

**Desarrolla como sección nueva, con el mismo formato de registro que el resto:**

- **sexo, ciclos de ploidía y apareamiento**
- **anisogamia y origen de tipos sexuales**
- **costes moleculares de roturas y reparación meiótica**
- **modelo de expansión genómica y sexo**
- **edad del origen mitocondrial**
- **reducción genómica mitocondrial, transferencia al núcleo e importación TOM/TIM**
- **conflicto mitonuclear**

Las cuatro primeras van juntas: el origen del sexo entra en el proyecto como contenido consultable **y como mecánica jugable**, así que necesito el mecanismo y sus costes, no solo la topología. Las tres últimas son el núcleo del evento reticulado que vertebra todo el corredor.

Mismas exigencias de siempre: cita por afirmación con localizador, atribución `expresa`/`sintesis`/`glosa`, fuerza con motivo escrito, y los huecos etiquetados en vez de rellenados.

**Y lo que NO quiero que desarrolles.** «Topología interna de Metazoa» está correctamente fuera de alcance: el encargo pedía Metazoa solo como nombre terminal. Déjala donde está. Lo mismo con cualquier otra fila del apéndice G que no esté en la lista de arriba: si la dejaste fuera, fue por una razón, y no la estoy discutiendo.

## 3. Una línea por cada predicado que inventaste

Usaste **308 predicados nuevos marcados con asterisco**, que son el 42 % de todos los usos. Hiciste bien: el vocabulario que te di se quedaba corto y `no_equivale_a*`, `no_demuestra*` o `se_distingue_de*` son distinciones reales que no tenía.

El problema es mío al otro lado. Mi sistema no guarda los predicados como etiquetas: a cada uno le asigna **cómo se almacena** —si es una afirmación directa, algo que se deriva de otra cosa, un evento con participantes, o una relación modal del tipo «podría ser»—. Con 308 sin definir, tengo que adivinar 308 veces.

Te adjunto `C01-PREDICADOS-NUEVOS.csv` con los 308, su número de usos y una fila de ejemplo de cada uno. **Rellena tres columnas:**

- **qué relación afirma** — una frase. «A no es lo mismo que B según la fuente», «A tiene el estado B en el momento C».
- **simétrico** — sí o no. ¿`A no_equivale_a B` implica `B no_equivale_a A`?
- deja el resto como está.

Si alguno lo inventaste sobre la marcha y hoy lo escribirías distinto, dilo en la columna: prefiero saberlo ahora.

Empieza por los más usados, que concentran el grueso: `no_equivale_a*` (53), `tiene_estado*` (48), `compatible_con*` (36), `no_demuestra*` (24), `contiene*` (22), `se_distingue_de*` (21).

## 4. Un repaso acotado del eje de aceptación

El 92 % de las afirmaciones está en «no evaluado». Repito que es correcto y que no quiero que lo aflojes.

Lo que sí quiero: **revisa solo aquellas donde la literatura permite nombrar a la vez quién lo sostiene y quién discrepa**, y sube únicamente ésas. El criterio no cambia; lo que pido es que lo apliques en la dirección contraria una vez, buscando activamente los casos donde sí se puede.

Sospecho que están concentradas en las controversias con nombre propio —las hipótesis rivales de eucariogénesis, la raíz eucariota, Choanozoa frente a Apoikozoa— donde la discrepancia está publicada y es citable.

**Si el resultado es que casi ninguna sube, dilo con esas palabras.** Eso también es información, y es una que necesito: significaría que el eje de aceptación llega vacío y que la decisión de qué hacer con él es mía y no tuya.

---

## 5. Localizadores: completar los dos tipos, sin sustituir ninguno

Los localizadores de la columna `Fuente` vienen de dos clases distintas, y cada
una dice algo que la otra no:

- **Posicional** — «S56 líneas 318–321», «S57 p. 296», «S38 resumen y fig. 5».
  Dice **dónde** está la evidencia. Permite recortar el pasaje exacto.
- **Semántico** — «S01 clasificación», «S109 filogenia», «S124 definición de
  Amorphea», «S05 tesis general». Dice **qué papel** juega la fuente en esa
  afirmación. No se puede deducir de un rango de líneas.

Contadas las 1 885 afirmaciones con localizador:

| | Afirmaciones |
|---|---:|
| sólo posicional o de sección | 914 |
| **posicional + semántico** | **523** |
| sólo semántico | 193 |

La convención buena ya la usas en 523 filas. Lo que se pide es extenderla, y
**nunca sustituir un tipo por el otro**: convertir «S01 clasificación» en un
rango de líneas perdería el papel de la fuente, y al revés perdería el sitio.
Se quieren los dos.

**5.a — Prioritario: 193 afirmaciones sólo con puntero semántico.**
Añadirles el localizador posicional. Estas bloquean: la ingestión exige una capa
de pasajes (§17) donde cada afirmación apunta al fragmento que la sostiene, y un
puntero semántico no se puede recortar mecánicamente. Sin esto, esas 193 entran
sin pasaje o entran como cuestión abierta.

**5.b — Deseable, no bloqueante: 914 afirmaciones sólo con localizador
posicional.** Añadirles el puntero semántico. Nada se rompe sin ellos —el pasaje
ya se recorta—, pero con ellos el corpus dice, de cada cita, no sólo dónde
mirar sino por qué esa fuente sostiene esa afirmación. Es información editorial
que hoy sólo vive en 523 filas y que ningún proceso puede reconstruir después.

Si hay que elegir por tiempo, 5.a primero y 5.b como pasada posterior.

---

## 6. Dos discrepancias que aparecieron al contar

Ninguna es grave, pero conviene resolverlas antes de dar el corpus por cerrado.

**El recuento de fuente única no cuadra por uno.** El apéndice H declara **1 196**
afirmaciones que dependen de una sola fuente. Contando sobre
`exports/afirmaciones.csv` —claves `S` de dos o tres dígitos, que es la regla del
apéndice A— salen **1 195**. Una fila de diferencia, sin identificar. O el
control arrastra un valor viejo, o hay una fila que se cuenta distinto.

**191 citas no dicen dónde mirar.** Dan la clave de la fuente y nada más
—«S123» a secas—, sin sección, línea ni descripción. Con el texto completo
descargado se puede recortar el pasaje que sostiene cada afirmación, pero sólo
cuando la cita señala un sitio; en éstas no hay nada que localizar. Completarlas
con un puntero, del tipo que sea, es lo mismo que pide el punto 5.

**Diez fuentes del apéndice A no las cita ninguna afirmación.** De las 523, sólo
513 aparecen en la columna `Fuente` de alguna fila. ¿Sobran del apéndice, o
falta citarlas en las afirmaciones que las usaron?

---

## Formato

El mismo de siempre: CSV canónico en `data/`, columnas en el orden fijado, vocabularios cerrados, `exports/` regenerado. La sección nueva del punto 2 entra como fichero de sección más filas en los apéndices que le correspondan.

Y como el corpus ya no es pequeño: **dime qué cambió y qué no**. Un resumen de qué ficheros tocaste y cuántas filas añadiste vale más que releerlo entero.
