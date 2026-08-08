"""Familias de validación de §19.2.

Cada familia vive en su propio módulo y expone:

    NAME: str          identificador del comando (validate:<NAME>)
    PHASE: str | None  fase que la habilita, o None si ya es ejecutable
    def check(data: dict[str, list[dict]], rep) -> None

`data` mapea nombre de fichero JSONL a lista de registros. `rep` expone
`error`, `warn` e `info`. Una familia que aún no puede comprobarse declara su
fase en PHASE y deja `check` vacío: es la diferencia entre "correcto" y "no
comprobado".
"""
