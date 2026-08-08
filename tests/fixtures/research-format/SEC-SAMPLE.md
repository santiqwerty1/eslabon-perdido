*Documento sintético. No es ciencia: es un molde del formato que exige `docs/campaigns/C01-PROMPT-INVESTIGACION.md`, para probar el parser antes de que llegue la investigación real.*

# Encargo de investigación: molde de formato

**Fecha de corte bibliográfico: 2026-08-04.**

## 3. Sección de ejemplo

Este párrafo es capa narrativa. Puede tener el tono que quiera y no se procesa como dato: sirve de contexto y de argumento.

El clado sintético FIX-Alfa reúne a FIX-Beta y FIX-Gamma ([S01 §2.1]). La posición de FIX-Gamma depende del modelo de sustitución empleado, y se recupera fuera del clado bajo modelos sitio-heterogéneos ([S02 fig. 3]).

### Registro de afirmaciones

| # | Afirmación | Sujeto | Predicado | Objeto | Atribución | Fuente | Aceptación | Fuerza | Motivo | Resolución | Vigencia |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C-001 | FIX-Beta pertenece a FIX-Alfa | FIX-Beta | miembro_de | FIX-Alfa | expresa | S01 §2.1 | consenso amplio | alta | replicado en tres filogenómicas independientes | resuelta | vigente |
| C-002 | FIX-Gamma pertenece a FIX-Alfa | FIX-Gamma | miembro_de | FIX-Alfa | expresa | S02 fig. 3 | aceptación mixta | media | topología sensible al modelo de heterogeneidad composicional | sin resolver | vigente |
| C-003 | FIX-Gamma es grupo hermano de FIX-Delta | FIX-Gamma | grupo_hermano_de | FIX-Delta | expresa | S02 fig. 3 | posición minoritaria | baja | un solo análisis, sin réplica | sin resolver | vigente |
| C-004 | La posición de FIX-Gamma es incompatible entre C-002 y C-003 | C-002 | incompatible_con | C-003 | sintesis(C-002, C-003) | S02 fig. 3 | no evaluado | desconocida | derivada de dos filas del propio registro | sin resolver | vigente |
| C-005 | El nombre FIX-Alfa se ha usado con dos circunscripciones | FIX-Alfa | sinonimo_propuesto_de | FIX-AlfaHistorico | expresa | S03 p. 44 | aceptación mayoritaria | media | discutido en la revisión, sin datos nuevos | parcialmente resuelta | histórica |
| C-006 | Llamar «primitivo» a FIX-Beta induce a error | FIX-Beta | requiere_verificacion | n/a | glosa | n/a | no evaluado | desconocida | comentario del autor, sin fuente detrás | información insuficiente | vigente |

## 17. Apéndices

**A. Fuentes.**

| clave | autores | año | título | publicación o repositorio | DOI | tipo | notas de calidad | fecha de consulta |
|---|---|---|---|---|---|---|---|---|
| S01 | Sintética, A.; Molde, B. | 2024 | Un trabajo sintético sobre FIX-Alfa | Revista Inexistente | https://doi.org/10.0000/sintetico.001 | investigación primaria | n/a | 2026-08-04 |
| S02 | Prueba, C. | 2025 | Modelos sitio-heterogéneos y FIX-Gamma | Otra Revista Inexistente | https://doi.org/10.0000/sintetico.002 | investigación primaria | única fuente que sostiene C-003 | 2026-08-04 |
| S03 | Revisión, D. | 2023 | Historia nomenclatural de FIX-Alfa | Anales Ficticios | DOI no verificado | revisión | síntesis secundaria sin datos propios | 2026-08-04 |

**B. Entidades.**

| etiqueta preferida | tipo | sinónimos y grafías alternativas | marcas | # |
|---|---|---|---|---|
| FIX-Alfa | clado sin rango | FIX-AlfaHistorico | ⚠ ≈ | C-001 |
| FIX-Beta | clado sin rango | n/a | n/a | C-001 |
| FIX-Gamma | clado sin rango | n/a | ⚠ [H] | C-002 |
| FIX-Delta | clado sin rango | n/a | n/a | C-003 |

**H. Recuento de control.**

| magnitud | valor |
|---|---|
| fuentes distintas | 3 |
| oraciones marcadas `[SIN FUENTE]` | 0 |
| filas del registro | 6 |
| afirmaciones que dependen de una sola fuente | 4 |
| celdas con `SIN CIFRA PUBLICADA LOCALIZADA` | 0 |
