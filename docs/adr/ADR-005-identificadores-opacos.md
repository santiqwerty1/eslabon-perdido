# ADR-005 · Formato de los identificadores opacos

**Estado:** aceptado · **Fecha:** 7 de agosto de 2026 · **Resuelve:** `OPEN-002` · **Decisión de registro:** `DEC-052`

## Contexto

§16.3 fija 33 prefijos y exige que los identificadores sean estables, opacos y permanentes, y que **no dependan del nombre canónico**. Esa exigencia es consecuencia directa de §7.2: si un mismo nombre puede designar conceptos distintos, el nombre no puede ser clave.

Quedaba por decidir el formato de la parte que va detrás del prefijo.

## Decisión

**Secuencial con ancho fijo de seis dígitos**: `CLAIM-000001`, `SEC-000042`, `ISSUE-000029`.

## Razones

- Es el formato de todos los ejemplos de la guía y del Apéndice E, así que no obliga a reescribir nada.
- Legible en conversación y en informes, y limpio en los diffs de Git, que es el almacenamiento decidido en `DEC-010`.
- Ordenable sin trabajo adicional.

## Consecuencias

- Requiere un **contador central** por tipo. Basta mientras el proyecto sea individual; el disparador para revisarlo es el del editor colaborativo de §25.9.
- Seis dígitos dan un millón de registros por tipo. `MENTION-` es el candidato natural a agotarlo primero.
- Si un tipo se acercara al límite, **ampliar el ancho es una migración de esquema, no un cambio de identidad**: los identificadores ya emitidos no se renumeran.
- La reserva de rangos se anota en el manifiesto del dataset. Actualmente `ISSUE-000001` a `ISSUE-000028` están reservados para migrar `docs/ISSUES.md` en la Fase 2.

## Alternativas consideradas

ULID o UUIDv7 resolverían la concurrencia desde el día uno, pero son ilegibles, rompen los ejemplos de la guía y hacen penosos los diffs. Un sufijo aleatorio sobre el secuencial no resuelve del todo ninguno de los dos problemas.
