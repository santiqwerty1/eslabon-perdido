# ADR-002 · Desarrollo y publicación por campañas cronológicas

**Estado:** aceptado · **Fecha:** 7 de agosto de 2026 · **Decisión de registro:** `DEC-033`, `DEC-034`, `DEC-035`

## Contexto

La versión `1.0.0` de la guía planteaba empezar por un piloto hominino de 400.000–40.000 años, el caso de máxima complejidad del proyecto: taxonomías incompatibles, paleogenómica, introgresión, especímenes con asignaciones rivales. Construir primero lo más difícil obliga a implementar todos los sistemas antes de tener nada jugable.

## Decisión

El juego se desarrolla y publica siguiendo el corredor evolutivo en orden cronológico general, campaña por campaña, desde Eukaryota hasta homininos. La primera campaña cubre **Eukaryota → Holozoa**.

Cada campaña debe ser simultáneamente experiencia jugable completa, ampliación del Atlas, prueba de una escala evolutiva nueva y extensión controlada del núcleo compartido.

## Consecuencias

- La plataforma crece con el contenido; el núcleo se extiende **sólo** cuando una campaña introduce un requisito demostrado.
- El trabajo hominino no se descarta: pasa a Campaña 7, a fixtures de regresión y a especificación de destino (`DEC-035`).
- El orden cronológico **no** implica progreso teleológico. Es orden de exposición y producción, no jerarquía de organismos.
- Se llega al caso más complejo con identidad, eventos, hipótesis, visualización y producción ya validados en escalas anteriores.

## Alternativas supersedidas

`DEC-018` (400.000–40.000 años como primer recorte) y `DEC-032` (posponer campañas profundas hasta validar homininos). Ambas se conservan en el registro con enlace a su reemplazo.
