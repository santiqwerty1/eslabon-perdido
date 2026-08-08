# ADR-003 · Núcleo compartido y módulos de campaña

**Estado:** aceptado · **Fecha:** 7 de agosto de 2026 · **Decisión de registro:** `DEC-037`, `DEC-014`

## Contexto

Siete campañas que van de poblaciones celulares a poblaciones humanas no pueden compartir el mismo modelo demográfico. Pero tampoco pueden ser siete proyectos distintos: la identidad de las entidades, la procedencia y el Atlas tienen que ser continuos.

## Decisión

Un **núcleo compartido** gestiona identidad, afirmaciones, evidencia, eventos, tiempo, hipótesis, vistas, Atlas, versionado, guardado y procedencia. Cada **módulo de campaña** define su escala temporal, su unidad poblacional concreta, sus variables de simulación, ambiente, rasgos, eventos, interfaz, objetivos y simplificaciones.

El núcleo científico **no depende del motor de juego**. La capa de juego referencia entidades por identificadores estables y no modifica sus relaciones para favorecer la jugabilidad.

## Consecuencias

- `Population` es una **interfaz conceptual común**, no un simulador universal idéntico de células a homininos.
- Una campaña puede usar sólo parte del modelo científico: esa selección se registra **como proyección, no como eliminación**.
- El diseño de juego nunca se guarda dentro de un nodo científico.
- Se rechaza construir un motor universal antes de tener una campaña concreta.

## Verificación

La familia `separation` de §19.2 comprueba que el núcleo no contenga costos, bonificaciones ni condiciones de victoria, y que la proyección de juego no reescriba afirmaciones.
