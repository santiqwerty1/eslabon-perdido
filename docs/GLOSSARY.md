# Glosario

Vocabulario mínimo del proyecto. Se amplía por campaña.

Los términos marcados **[pendiente de ingestión]** son definiciones científicas tomadas de material todavía no ingerido: **no son dato canónico** hasta pasar por el protocolo de §17. Se incluyen aquí porque el modelo las usa como marcas conceptuales y sin ellas la marca queda vacía.

---

## Estados de decisión

| Estado | Significado |
|---|---|
| `DECIDIDO` | Forma parte de la arquitectura actual; se implementa salvo reemplazo. |
| `RETENIDO` | Propuesta valiosa; exige prototipo antes de tratarse como definitiva. |
| `POSPUESTO` | Contemplado pero no implementado aún. **Debe llevar disparador explícito.** |
| `RECHAZADO` | Contradice los objetivos. Sólo se reabre con un ADR que explique qué premisa cambió. |
| `ABIERTO` | Falta decidirlo en una fase posterior. |
| `SUPERSEDIDO` | Válido antes; una decisión posterior reemplazó su prioridad, alcance u orden. Conserva su texto y **enlaza su reemplazo**. |

Nunca se elimina una fila histórica para que el registro parezca más ordenado.

## Ejes epistemológicos

Son **independientes**: no se promedian, no se derivan unos de otros y no se convierten en un porcentaje. Que algo tenga consenso amplio y evidencia débil a la vez es información, no una contradicción.

| Eje | Valores | Qué mide |
|---|---|---|
| Aceptación científica | `broad_consensus` · `majority_acceptance` · `mixed_acceptance` · `minority_position` · `not_assessed` | La recepción, no la fuerza lógica interna. |
| Fuerza de evidencia | `high` · `medium` · `low` · `unknown` | Requiere **razón escrita**. |
| Resolución | `resolved` · `partially_resolved` · `unresolved` · `insufficient_information` | `unresolved` es «hay disputa»; `insufficient_information` es «no hay datos para decidir». |
| Vigencia histórica | `current` · `historical` · `superseded` · `rejected` | Estado de la **idea**. |
| Estado del registro | `active` · `deprecated` · `merged` · `superseded` · `archived` | Ciclo de vida del **dato**. |
| Papel en una vista | `selected_backbone` · `selected_overlay` · `alternative` · `excluded` · `not_evaluated` | Propiedad de la relación vista↔afirmación, no de la afirmación. |

⚠️ `superseded` aparece en dos ejes con significados distintos: idea reemplazada frente a registro reemplazado.

## Identidad

Las distinciones que el sistema nunca debe confundir:

- **Nombre taxonómico** — una denominación, su grafía y su autoría. **No contiene por sí solo una circunscripción**: un mismo nombre pudo usarse para conceptos distintos.
- **Concepto taxonómico** — el uso de un nombre con una circunscripción concreta **según una fuente**. Dos conceptos pueden ser congruentes, estar incluidos, superponerse, ser incompatibles o ser homónimos.
- **Clado** — grupo definido por ascendencia. Conserva **su tipo de definición**. No se infiere que todo taxón formal sea monofilético.
- **Grado evolutivo** — agrupación por nivel de organización, no por ascendencia. Suele ser parafilética.
- **Linaje** — continuidad biológica inferida. **Puede existir sin nombre formal.**
- **Población** — unidad localizada en tiempo y espacio. Entidad principal de migración, flujo génico, deriva, selección y simulación.
- **Espécimen** — objeto físico individual. **No se convierte automáticamente en taxón, especie, población ni ancestro.**
- **Ocurrencia** — presencia documentada o inferida en un lugar e intervalo. Separa la identidad de la evidencia de su presencia.
- **Rasgo** frente a **observación de rasgo** — el carácter abstracto se distingue de su observación concreta, que es lo que permite conservar incertidumbre y homología discutida.

## Grupos corona, troncales y totales · **[pendiente de ingestión]**

- **Crown group** (grupo corona) — el último ancestro común de los representantes vivientes y todos sus descendientes.
- **Stem group** (grupo troncal) — los linajes extinguidos más próximos al grupo corona que a cualquier grupo viviente externo.
- **Total group** (grupo total) — la unión de ambos: el grupo corona más su grupo troncal.

La distinción no es una sutileza nomenclatural. Es la bisagra del desacuerdo entre las estimaciones de reloj molecular y el registro fósil: buena parte del registro antiguo puede ser grupo troncal y no corona.

*Procedencia: `knowledge/corpus/inbox/Filogenia.md`, sección de convenciones. Debe reingresarse por el protocolo de §17 antes de considerarse canónico.*

## Producción

- **Corredor principal** — la cadena de nodos que una campaña modela con la máxima resolución.
- **Cono de foco** — los cuatro anillos que acotan una campaña: corredor, ramas hermanas inmediatas, grupos externos representativos y diversidad diferida. Exhaustividad significa no omitir nada **dentro del alcance declarado**.
- **Campaña** — experiencia jugable completa que además amplía el Atlas, prueba una escala evolutiva nueva y extiende el núcleo compartido.
- **Vista** — producto derivado de un conjunto de afirmaciones. Declara fecha de corte, criterios editoriales, simplificaciones y **lo que excluye**.
- **Proyección de juego** — traducción de una vista a contenido jugable. Referencia entidades científicas por identificador y **no las modifica**.
- **Lente científica** — versión reducida del modo Reconstrucción presente desde el primer lanzamiento: consultar evidencia, comparar hipótesis y cambiar de vista.
- **Delta** — el conjunto de cambios reales que produce la ingestión de una sección. Debe poder aplicarse **y revertirse**.
- **Fixture `future-*`** — caso de prueba que no es contenido de ninguna campaña actual. Comprueba que el esquema no bloquee capacidades futuras.

## Etiquetas para lo no identificado

No se inventan nombres. Cuando hace falta representar estructura sin identidad conocida:

`ancestro común no identificado` · `linaje ancestral no muestreado` · `linaje fantasma` · `posición pendiente` · `nodo estructural provisional` · `taxón flotante`

Y cuando algo no puede ubicarse con seguridad:

`incertae_sedis` · `ubicación no resuelta` · `afinidad incierta` · `posible miembro de` · `posible grupo hermano de` · `posible ancestro` · `posición dependiente de hipótesis`

Ninguna de estas etiquetas recibe nombre científico inventado. La ausencia de ubicación es información válida.
