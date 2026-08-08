# Fixtures de las familias de validación

Datos artificiales para probar `scripts/validate/families/`. **No son corpus**:
ningún registro de aquí es dato canónico ni entra en `knowledge/records/`. Su
único propósito es que cada comprobación de §19.2 se pueda ejercitar en las dos
direcciones —lo que debe fallar y lo que debe pasar—, porque un validador que
sólo se prueba contra datos correctos no distingue "correcto" de "no comprobado".

Los fixtures de referencia de §27.9 (`eukarya-minimal`, `historical-classification`,
`game-projection-eukarya`…) viven en sus propias carpetas y sirven de caso
positivo adicional: las pruebas los recorren enteros y exigen cero errores.

## Estructura

Una carpeta por familia y sentido:

```text
validation-families/
├── <familia>-ok/           registros correctos; la familia no debe decir nada
└── <familia>-bad/          registros mal a propósito
```

Las familias `state` y `separation` parten el lado malo en un caso por carpeta,
porque cada uno necesita su propio snapshot y su propia cadena de deltas y
algunos se contradicen entre sí:

```text
├── state-ok/
├── state-bad/
│   ├── record-status-as-synonym/       §10.5 y §10.6 usados como sinónimos
│   ├── deprecation-without-reason/     cerrar un registro sin decir hacia dónde
│   ├── evidence-strength-without-reason/
│   ├── collapsed-axes/                 un campo que resume varios ejes
│   ├── lost-record/                    algo que estaba en el snapshot y ya no está
│   └── undocumented-migration/
├── separation-ok/
└── separation-bad/
    ├── core-with-mechanics/            costes y victoria en el núcleo científico
    ├── core-points-to-projection/      la referencia en el sentido prohibido
    ├── projection-rewrites-claim/      la capa 8 redactando ciencia
    ├── view-without-simplifications/
    └── hypothesis-as-fact/
```

Dentro de cada caso:

| Carpeta | Contenido | Constante que la apunta |
|---|---|---|
| raíz | `*.jsonl` del núcleo científico | el `data` que recibe `check` |
| `snapshots/` | snapshots previos | `state.SNAPSHOTS_DIR` |
| `deltas/` | deltas de §17 paso 13 | `state.DELTAS_DIR` |
| `migrations/` | documentos de migración | `state.MIGRATIONS_DIR` |
| `views/` | vistas construidas | `separation.SCIENCE_DIRS` |
| `projections/` | capa 8 | `separation.PROJECTION_DIRS` |

Las rutas son constantes de módulo precisamente para esto: la prueba las
reapunta aquí y el dataset real no se toca.

Los identificadores usan el rango `NNN-0009xx` y `NNN-0008xx` para no chocar con
los fixtures de referencia. Los nombres científicos que aparecen son reales
cuando el caso lo exige, pero ninguna afirmación de aquí está ingerida ni
verificada.
