# Aviso para aplicar desde ya · corredor Eukaryota → Holozoa

Versión corta y pegable del encargo de seguimiento, con **sólo lo que conviene
aplicar mientras la investigación sigue abierta**. El documento completo, con
las pasadas de cierre, es `C01-ENCARGO-SEGUIMIENTO.md`.

---

Tres cosas para escribir distinto de aquí en adelante. **Ninguna pide volver
atrás sobre lo ya entregado**: eso se hará en una pasada de cierre. Basta con que
lo nuevo salga ya con la forma buena, que es enormemente más barato que
retocarlo después sobre mil novecientas filas.

## 1. Cita siempre el apartado, y la línea además — no en su lugar

Se descargó el texto completo de 286 de tus fuentes y se midió, sobre 1 149
localizadores, cuáles permiten recortar automáticamente el pasaje citado. El
resultado es contraintuitivo:

| Forma del localizador | Resuelve |
|---|---:|
| nombre de apartado: «resumen», «resultados», «discusión» | **89 %** |
| puntero semántico: «clasificación», «filogenia» | **78 %** |
| **número de línea** | **0 %** |
| **página** | **0 %** |
| **figura o tabla** | **0 %** |
| **sólo la clave, sin nada más** | **0 %** |

Los localizadores que parecen más precisos son los que menos sirven para
verificar. El texto completo llega en XML JATS y **el XML no conserva la
maquetación impresa**: no hay líneas ni páginas que contar.

Eso no quita valor a la línea, que sigue siendo la forma más exacta de señalar
para quien lee con el PDF delante. Sólo significa que **no debe ir sola**.

- ✅ `S56 discusión, líneas 318–321` — se verifica sola y sigue siendo exacta.
- ❌ `S56 líneas 318–321` — obliga a abrir el PDF a mano cada vez.
- ❌ `S56` a secas — no dice dónde mirar. Hay 232 así.

Las figuras son un caso legítimo aparte: si una afirmación descansa en una
figura, ningún texto la sostiene y siempre hará falta un ojo humano. Cuando el
texto **también** lo diga, cita además el apartado.

## 2. A igualdad de calidad científica, prefiere la fuente accesible

De tus 523 fuentes, **237 no tienen texto completo accesible**. Eso deja **501
afirmaciones de 1 813 (27 %) sin ninguna fuente consultable**, y **409 de ellas
dependen además de una sola fuente cerrada**: hoy son inverificables por
cualquiera, ni por ti ni por un revisor futuro.

**Esto es una regla de desempate, no un cambio de criterio.** Cuando dos fuentes
sostengan lo mismo con calidad equivalente, cita la accesible. Cuando **no** sean
equivalentes, **manda la ciencia**: una fuente cerrada y buena vale más que una
abierta y mediocre, y esto no autoriza a rebajar calidad por comodidad.

Donde una afirmación quede con una sola fuente cerrada, añadir **una segunda
accesible que la corrobore** evita que sea un callejón sin salida para quien
quiera comprobarla. No sustituye a la primera.

## 3. Define cada predicado nuevo en el momento de inventarlo

Los predicados marcados con asterisco —`no_equivale_a*`, `definido_como*`— ya son
**308**. Cada uno necesita una línea que diga qué significa y qué relación
expresa, y hacerlo al inventarlo cuesta segundos; reconstruirlo después, sobre
308, es una tarea entera.

Basta con una línea por predicado nuevo: nombre, qué relación expresa, y un
ejemplo de la afirmación donde lo usaste.

---

## Lo que sigue igual y no quiero que cambies

- **Las búsquedas negativas etiquetadas `NO LOCALIZADO EN ESTA SESIÓN` son un
  resultado, no una tarea pendiente.** No las rellenes. Un hueco declarado sirve;
  una respuesta rellenada estropea lo que se construya encima.
- **El eje de aceptación en «no evaluado»** cuando no puedes nombrar quién
  discrepa. Es lo correcto.
- **Las dos capas**, prosa y registro. Funciona.
