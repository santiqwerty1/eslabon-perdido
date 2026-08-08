# eslabón perdido

Una **base de conocimiento científico versionada y centrada en afirmaciones**, capaz de generar múltiples redes evolutivas coherentes y de proyectarlas hacia un juego poblacional desarrollado cronológicamente por campañas.

**Estado:** Fase 0 completada. Sin corpus ingerido todavía.

---

## Qué es esto

Dos sistemas relacionados pero separados:

1. Un **núcleo científico** que organiza corpus, entidades, afirmaciones, evidencia, eventos, hipótesis y vistas.
2. Una **capa de juego** que selecciona y transforma partes del núcleo en campañas jugables.

El núcleo no depende del motor de juego. La capa de juego referencia entidades por identificador estable y **nunca modifica sus relaciones para favorecer la jugabilidad**.

La primera campaña cubre **Eukaryota → Holozoa**. La última, **Hominini → *Homo sapiens***. El orden cronológico es de exposición y producción, **no una escalera de progreso**.

## Empezar por aquí

| Documento | Para qué |
|---|---|
| [`docs/GUIDE.md`](docs/GUIDE.md) | El documento rector. Todo lo demás se deriva de él. |
| [`docs/GLOSSARY.md`](docs/GLOSSARY.md) | Vocabulario mínimo: estados de decisión, ejes epistemológicos, identidad. |
| [`docs/ISSUES.md`](docs/ISSUES.md) | Cuestiones pendientes. 28 registradas, 9 resueltas. |
| [`docs/adr/`](docs/adr/) | Decisiones arquitectónicas con su razón y sus alternativas rechazadas. |
| [`docs/campaigns/C01-EUKARYA.md`](docs/campaigns/C01-EUKARYA.md) | Dossier de la Campaña 1. Vacío por diseño hasta la Fase 1. |

## Estructura

```text
docs/           guía activa, ADR, glosario, dossiers de campaña
knowledge/      el núcleo científico
  corpus/       secciones, pasajes, manifiestos · inbox/ = recibido, sin ingerir
  records/      21 JSONL: menciones, fuentes, entidades, afirmaciones, evidencia…
  views/        vistas derivadas
  deltas/       un delta por sección ingerida, aplicable y reversible
  snapshots/    estados completos reconstruibles
game/           núcleo de juego y módulos por campaña
schemas/        JSON Schema y migraciones
scripts/        tooling en Python
tests/          fixtures, esquema, validación, vistas, campañas, simulación
archive/        versiones rectoras anteriores — trazabilidad, no basurero
```

## Uso

```bash
pip install -r requirements.txt
python scripts/validate/validate.py all
python scripts/snapshot/snapshot.py verify
```

`validate.py` implementa las once familias obligatorias. Las que dependen de tipos aún no implementados se declaran **pendientes con su fase** en vez de pasar en verde por vacuidad.

> **Entorno:** el Python del sistema de desarrollo no trae `pip`, así que la validación de esquema completa se ejecuta en CI. Registrado como `ISSUE-000029`.

## Reglas que no se negocian

- **No se inventa nada.** Ni nombres, ni fechas, ni relaciones, ni fuentes. Lo que no está en el material se registra como `Issue`, nunca como dato silencioso.
- **Nada de certeza falsa.** Sin porcentajes de confianza arbitrarios. Los valores cuantitativos sólo entran si la fuente los da.
- **Nada de teleología.** Ningún linaje es superior, más evolucionado ni está destinado a producir humanos.
- **Procedencia obligatoria.** Toda afirmación se rastrea hasta su sección, su mención exacta, su fuente, la operación que la incorporó y la revisión del dataset.
- **La conversación no es fuente de verdad.** El estado vive en archivos versionados y reconstruibles.
- **No se borra historia.** Las decisiones reemplazadas se marcan `SUPERSEDIDO` y enlazan su reemplazo. Las sinonimias disputadas se modelan como afirmación, no como borrado.

## Licencias

| Capa | Licencia |
|---|---|
| Código (`scripts/`, `schemas/`, `tests/`) | [MIT](LICENSE) |
| Corpus y datos (`knowledge/`) | [CC BY 4.0](LICENSE-DATA) |
| Contenido de juego (`game/`) | [Propietario](LICENSE-CONTENT) |

La frontera de licencia coincide con la frontera arquitectónica. Ver [ADR-006](docs/adr/ADR-006-licencias.md).
