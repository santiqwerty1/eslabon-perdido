# Campaña 1 · Eucaria: una célula dentro de otra

**Estado:** `planning` · **ID:** `CAMP-000001` · **Fase actual:** Fase 1, con el corpus congelado

> Este dossier sigue **vacío por diseño**, pero ya no por falta de corpus. Fijar el alcance exigía tener el corpus, y desde el 25 de septiembre de 2026 hay una versión congelada (`DEC-056`). La Fase 1 lo completa sobre ella.

## Corredor

```text
prólogo de eucariogénesis
→ Eukaryota
→ Amorphea
→ Obazoa
→ Opisthokonta
→ Holozoa
```

Termina en Holozoa, en el umbral de la historia animal. **No** pretende poblar exhaustivamente los eucariotas conocidos.

## Qué falta decidir en la Fase 1

| Tarea | Estado |
|---|---|
| Pregunta central de campaña | pendiente |
| Inicio, final y capítulos | pendiente |
| Corredor principal detallado | esbozado en `scientific-scope.json` |
| Ramas hermanas inmediatas | esbozadas |
| Grupos externos representativos | esbozados |
| **Lista explícita de exclusiones** | pendiente |
| Controversias obligatorias | en el corpus congelado —81 hipótesis, con sus incompatibilidades declaradas en el apéndice E—; falta elegir cuáles son obligatorias |
| Evento de endosimbiosis y sus requisitos | pendiente |
| Corpus científico inicial | **congelado**: corredor `0.6.0-research-audit` en `af7e799` (`DEC-056`). Ingerida y convertida la sección 6 (`SEC-000001`, `DEC-057`); el resto, pendiente |
| Fecha de corte bibliográfico | **8 de agosto de 2026**, la de la versión congelada (`DEC-056`) |
| Criterios de aceptación científica | pendiente |
| **Presupuesto máximo** de entidades, afirmaciones y vistas | pendiente |

## Corpus de la campaña

El material de partida es el corpus del repositorio `corredor-eukaryota-holozoa`,
encargado con [`C01-PROMPT-INVESTIGACION.md`](C01-PROMPT-INVESTIGACION.md).

| | |
|---|---|
| Versión congelada | `0.6.0-research-audit`, commit `af7e799` |
| Registro | [`knowledge/corpus/manifests/corredor-v0.6.0-research-audit-af7e799.json`](../../knowledge/corpus/manifests/corredor-v0.6.0-research-audit-af7e799.json) |
| Huella de la capa canónica | `sha256:b53f15ad613451387591f519d7ec8d4144a774aed83fbaaabd5e5207a18aa415` |
| Contenido | 1.952 afirmaciones · 523 fuentes · 1.500 entidades · 109 eventos · 215 fechas · 81 hipótesis · 562 magnitudes · 68 búsquedas negativas |
| Conformidad con el prompt | 0 errores de `parse_research.py` |

**No es un corpus cerrado.** Su auditoría sigue abierta y el encargo de
seguimiento está sin empezar, así que llegarán versiones nuevas. Cada una se
congela aparte, se compara con la anterior y sólo reingiere las secciones que
cambiaron: [`INGESTION-C01.md`](../INGESTION-C01.md) explica cómo.

Lo que sigue pendiente del lado del corpus está en
[`C01-ENCARGO-SEGUIMIENTO.md`](C01-ENCARGO-SEGUIMIENTO.md). Lo que más pesa en
la campaña es su punto 2, sexo, anisogamia y mitocondria, porque el sexo entra
como mecánica (§25.5.1). Antes de insistir en él conviene contrastarlo con lo
que ya hay: la sección 11 del corpus trata costes del sexo (11.5) y tipos de
apareamiento, ciclos de ploidía y anisogamia (11.6), la 9 trata cooperación y
conflicto entre genomas (9.9), y la columna «sección propuesta» del apéndice G
remite las siete filas a secciones existentes. Puede que el punto 2 pida
profundidad y no una sección que falte.

`knowledge/corpus/inbox/Filogenia.md` **no** es material de esta campaña: cubre el
linaje humano y se reserva para la del clado tardío (`ISSUE-000014`).

## Huecos conocidos

Registrados en `docs/ISSUES.md`:

- ~~`ISSUE-000010`~~ — **resuelta el 10 de agosto de 2026** por el corpus: la sección 14, «Nomenclatura», trata «protista», «protozoo», «alga» e «invertebrado». Queda decidir al ingerir si se proyecta como apéndice `D.7`.
- ~~`ISSUE-000021`~~ — **resuelta el 10 de agosto de 2026** por el corpus: Archaea, Bacteria, Corallochytrea y el resto del contenido del corredor están con fuente.
- ~~`ISSUE-000026`~~ — **resuelta el 8 de agosto de 2026**: el sexo y la meiosis **entran** en la Campaña 1, como contenido del Atlas y como mecánica. Ver §25.5.1 de la guía.
- ~~`ISSUE-000013`~~ — **resuelta el 25 de septiembre de 2026** por `DEC-056`: corpus y fecha de corte los fija la versión congelada.

## Requisitos que el dataset debe demostrar

De §5.3, como banco de pruebas de la arquitectura:

- poblaciones ancestrales reconstruidas **sin nombres inventados**;
- origen e integración mitocondrial como **evento reticulado con participantes y roles**;
- cooperación y conflicto intracelular;
- al menos **dos controversias o hipótesis alternativas reales**;
- rasgos, costos, evidencia y procedencia;
- intervalos temporales con incertidumbre;
- **dos o más hipótesis realmente incompatibles**; la incompatibilidad parcial no basta (`ISSUE-000028`);
- una vista de trabajo fechada y una vista histórica o de fuente.

## Conexión con la Campaña 2

La campaña termina en Holozoa y prepara la transición a *Animales: construir un cuerpo* (Holozoa → Bilateria), **sin afirmar inevitabilidad**. La Campaña 2 no se inicia hasta que ésta se haya lanzado y se haya hecho el postmortem del núcleo.
