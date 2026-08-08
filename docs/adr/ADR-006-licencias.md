# ADR-006 · Licencias de código, datos y contenido

**Estado:** aceptado · **Fecha:** 7 de agosto de 2026 · **Resuelve:** `OPEN-015` · **Decisión de registro:** `DEC-053`

## Contexto

El proyecto tiene tres capas con naturalezas distintas: tooling, un corpus científico con procedencia trazable, y el contenido de un juego. Licenciarlas igual sería un error en las tres direcciones.

## Decisión

| Capa | Licencia | Fichero |
|---|---|---|
| Código | MIT | `LICENSE` |
| Corpus científico y datos | CC BY 4.0 | `LICENSE-DATA` |
| Contenido de juego | Propietario, todos los derechos reservados | `LICENSE-CONTENT` |

## Razones

- Encaja con la separación núcleo/juego de §2.1: la base de conocimiento se comporta como recurso científico citable y el producto se puede publicar comercialmente.
- Es el patrón de las bases taxonómicas de referencia, que es el papel que el Atlas aspira a cumplir.
- CC BY exige atribución, coherente con un proyecto cuyo principio central es la procedencia obligatoria (§4.5).

## Consecuencias

- Cualquiera puede reutilizar el corpus citando la fuente, incluida su reincorporación a bases externas.
- El contenido de campaña —textos, arte, audio, capítulos— queda fuera de esa reutilización.
- Al ingerir material de terceros hay que comprobar que su licencia permite la redistribución bajo CC BY, o registrar la restricción en el `Source`.

## Alternativas consideradas

Copyleft en los datos (CC BY-SA) protegería mejor el trabajo de procedencia, pero contamina el contenido derivado y complica la publicación comercial. Todo permisivo facilitaría que se republique la campaña con otro nombre, y el trabajo de fuentes es lo más caro de reproducir del proyecto.
