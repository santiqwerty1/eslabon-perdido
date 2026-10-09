---
tipo: inicio
titulo: 'eslabon-perdido'
area: proyecto
estado: vigente
actualizado: '2026-10-08'
origen:
  - posta init
revisar: false
---

# eslabon-perdido

Bóveda del proyecto: el estado vivo está acá, no en las conversaciones. Si algo no coincide con
`git log` o con GitHub, mandan los comandos.

## Hoy

- [Para revisar](Trabajo.base#Para%20revisar) · [Avance](Seguimiento/Avance.md) · última bitácora: [2026-10-08](Bitacora/2026-10-08.md)

![[Trabajo.base#Para revisar]]

<!-- posta:recuentos -->
_Recuentos: los escribe `posta generar`._
<!-- /posta:recuentos -->

## Fichas

- **Preguntas** (`P-NNN`): `Seguimiento/Preguntas/` · estados pendiente · parcial · respondida · cerrada
- **Supuestos** (`S-NNN`): `Seguimiento/Supuestos/` · estados por_validar · verificado · refutado
- **Decisiones** (`D-NNN`): `Seguimiento/Decisiones/` · estados propuesta · vigente · sustituida · descartada
- **Riesgos** (`R-NNN`): `Seguimiento/Riesgos/` · estados abierto · resuelto · descartado · por_revalidar
- **Hallazgos** (`H-NNN`): `Seguimiento/Hallazgos/` · estados abierto · resuelto · descartado · por_revalidar · sin_revisar_por_cuota
- **Tareas** (`T-NNN`): `Seguimiento/Tareas/` · estados pendiente · preparado · en_curso · bloqueado · parcial · hecho

Plantillas en `Plantillas/`; vistas en `Trabajo.base`. Cada ficha lleva `tipo`, `codigo`, `titulo`,
`area`, `estado`, `actualizado`, `origen` y `revisar`; la prioridad (1–5) exige `prioridad_origen`.

## Cómo trabajamos

- Al abrir: `posta relevo abrir` (qué cambió desde la última foto, qué espera).
- Al cerrar: `posta relevo cerrar --siguiente "acción exacta"`; la foto queda en `Sesiones/`.
- Antes de un PR: `posta check` sin errores. Los agentes proponen (`posta accion proponer`); la persona aprueba.
