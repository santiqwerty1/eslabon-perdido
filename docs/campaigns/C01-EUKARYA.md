# Campaña 1 · Eucaria: una célula dentro de otra

**Estado:** `planning` · **ID:** `CAMP-000001` · **Fase actual:** pendiente de Fase 1

> Este dossier está **vacío por diseño**. La Fase 1 lo completa, y no antes: fijar el alcance exige tener el corpus, y el corpus está pendiente de ingestión.

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
| Controversias obligatorias | tres candidatas identificadas, sin ingerir |
| Evento de endosimbiosis y sus requisitos | pendiente |
| Corpus científico inicial | pendiente de ingestión |
| Fecha de corte bibliográfico | pendiente (`OPEN-016`) |
| Criterios de aceptación científica | pendiente |
| **Presupuesto máximo** de entidades, afirmaciones y vistas | pendiente |

## Material disponible, no ingerido

`knowledge/corpus/inbox/` contiene material recibido que **todavía no es corpus**. Nada de ahí es dato canónico hasta pasar por el protocolo de §17.

- **`Filogenia.md`** — investigación sobre filogenia humana, corte bibliográfico 4 de agosto de 2026, 34 referencias. Cubre el corredor topológicamente pero de paso: sólo dos citas lo sostienen, y no aporta datos temporales, de caracteres ni ecológicos para estos nodos.
- **Investigación específica de Eucaria** — encargada con el prompt de `C01-PROMPT-INVESTIGACION.md`, en curso. Es la que debe cerrar los huecos.

## Huecos conocidos

Registrados en `docs/ISSUES.md`:

- `ISSUE-000010` — no hay catálogo terminológico eucariota («protista», «protozoo», «algas»). La fuente actual tampoco lo trae: exige investigación nueva.
- `ISSUE-000021` — falta contenido científico del corredor: Archaea y Bacteria no aparecen nunca, pese a ser el arranque; se perdió el sinónimo Corallochytrea; no hay definiciones por contenido.
- ~~`ISSUE-000026`~~ — **resuelta el 8 de agosto de 2026**: el sexo y la meiosis **entran** en la Campaña 1, como contenido del Atlas y como mecánica. Ver §25.5.1 de la guía.
- `ISSUE-000013` — `OPEN-016` tiene respuesta de facto y sigue abierta.

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
