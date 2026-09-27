# corredor-mini-v2

La versión siguiente de `corredor-mini`, para probar la absorción de una versión
nueva (DEC-059, `tests/ingest/test_absorber.py`). Cada cambio es uno de los casos
que `absorber.py informe` tiene que clasificar. Este README no entra en la
huella: está fuera de la capa canónica.

| Fila | Qué le pasa | Cómo la ve el diff |
|---|---|---|
| C-001 | Cambian la fuerza y el motivo; el enunciado es el mismo | modificada (por el texto de la afirmación) |
| C-002 | Nada | sin cambios |
| C-003 | Se retira por no ser atómica. Su número queda como fila de registro (glosa, `tiene_estado*`, vigencia superada) y sus dos proposiciones pasan a C-007 y C-008, declaradas en `data/auditoria/sucesiones_afirmaciones.csv` | modificada (por posición) |
| C-004 | Nada | sin cambios |
| C-005 | Se retira sin sucesoras | retirada |
| C-006 → C-010 | Se renumera sin cambiar, en la sección 1 | sólo renumeración |
| C-007, C-008 | Las sucesoras de C-003 | nuevas |
| C-009 | Una fila nueva sin relación con las demás | nueva |

Además:

- **A_fuentes:** S01 corrige su título.
- **B_entidades:**
  - FIX-Omega, cuya primera fila era C-003, se retira;
  - FIX-Zeta pasa a citar C-010.
- **Prosa de la sección 0:**
  - el párrafo de C-002–C-003 se reescribe en dos, uno de C-002 y otro de C-007–C-008;
  - se añade uno de C-009;
  - lo que viene detrás se desplaza.
- **Prosa de la sección 1:** sólo cambia su cita, de C-006 a C-010.

Las sucesoras llevan números nuevos, por encima de los que ya existían, como hace
el corredor. Con números intercalados, el emparejamiento por posición dejaría de
cuadrar y la fila de registro saldría como retirada más nueva.
