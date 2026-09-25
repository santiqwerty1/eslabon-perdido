# Fixture `corpus-versions`

**Qué es:** dos versiones de un corpus en miniatura con la forma del corredor
—`data/afirmaciones/`, `data/apendices/`, `docs/secciones/`—, para comprobar
que `scripts/ingest/freeze.py diff` distingue lo que cambió de verdad de lo que
sólo se desplazó por renumeración.

`v2` es `v1` después de una pasada de auditoría que hace, a propósito, una cosa
de cada clase:

| Qué pasa en `v2` | Qué debe decir el diff |
|---|---|
| `C-001` no cambia | sin cambios |
| se inserta una afirmación nueva tras `C-001` y todo lo demás se desplaza | `C-002` nueva |
| `C-002` pasa a `C-003` y su fuente gana apartado: `S02` → `S02 discusión` | modificada, emparejada por el texto de la afirmación |
| `C-003` pasa a `C-004` y su síntesis cita los números nuevos | sólo renumeración |
| `C-004` pasa a `C-005` y se reescribe el texto | modificada, emparejada por posición |
| `C-005` pasa a `C-006` y su síntesis cita el número nuevo | sólo renumeración |
| `C-006` se retira | retirada |
| la entidad `afirmación C-003` pasa a `afirmación C-004` | sólo renumeración, aunque cambie la clave |
| se añade la entidad `FIX-Beta` | nueva |
| `001-arranque.md` sólo cambia las citas `C-…` | sólo renumeración |
| `002-final.md` cambia el texto | cambiado |

`tests/run_tests.py` ejecuta el diff y exige exactamente esos recuentos, y
comprueba además que `create` congela `v1` y que `verify` la reconoce y rechaza
`v2`.

**Qué NO es:** corpus. Las etiquetas llevan el prefijo `FIX-` y las fuentes son
ficticias. §4.7 prohíbe inventar contenido científico; esto no lo es.
