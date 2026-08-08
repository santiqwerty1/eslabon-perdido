#!/usr/bin/env python3
"""Runner de los fixtures de referencia (§27.9).

Tres clases de caso, y la tercera es la que importa:

- **fixtures de referencia** (`tests/fixtures/<nombre>/`): datasets completos que
  deben validar sin errores. Prueban que la arquitectura representa lo que dice
  representar.
- **`validation-families/<familia>-ok/`**: casos correctos de una familia
  concreta. Deben pasar.
- **`validation-families/<familia>-bad/`**: casos que contienen el defecto que
  esa familia existe para detectar. **Deben fallar, y fallar en su familia.**
  Un validador que sólo se prueba contra datos correctos no demuestra nada:
  pasaría igual si no comprobara nada en absoluto.

Sin dependencias externas. Si falta `jsonschema`, la familia `schema` avisa y el
resto sigue funcionando.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
sys.path.insert(0, str(ROOT / "scripts" / "validate"))

import validate  # noqa: E402


GREEN, RED, YELLOW, DIM, RESET = "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[0m"


def has_records(d: Path) -> bool:
    return any(d.glob("*.jsonl"))


def run_one(d: Path, families: list[str]) -> validate.Report:
    return validate.run(families, records_dir=d)


def main() -> int:
    ordinarios: list[Path] = []
    ok_cases: list[tuple[str, Path]] = []
    bad_cases: list[tuple[str, Path]] = []

    for d in sorted(FIXTURES.iterdir()):
        if not d.is_dir():
            continue
        if d.name == "validation-families":
            for sub in sorted(d.iterdir()):
                if not sub.is_dir():
                    continue
                fam, _, kind = sub.name.rpartition("-")
                destino = ok_cases if kind == "ok" else bad_cases
                if has_records(sub):
                    destino.append((fam, sub))
                    continue
                # Algunas familias aíslan un defecto por subdirectorio, que es
                # mejor: así un caso no enmascara a otro.
                for caso in sorted(sub.iterdir()):
                    if caso.is_dir() and has_records(caso):
                        destino.append((fam, caso))
        elif has_records(d):
            ordinarios.append(d)

    fallos: list[str] = []
    avisos = 0

    print(f"{DIM}fixtures de referencia — deben validar sin errores{RESET}")
    for d in ordinarios:
        rep = run_one(d, validate.FAMILY_ORDER)
        avisos += len(rep.warnings)
        marca = f"{GREEN}PASA{RESET}" if rep.ok else f"{RED}FALLA{RESET}"
        extra = f"  {YELLOW}{len(rep.warnings)} avisos{RESET}" if rep.warnings else ""
        print(f"  {marca}  {d.name}{extra}")
        if not rep.ok:
            fallos.append(d.name)
            for e in rep.errors[:4]:
                print(f"        {RED}{e}{RESET}")

    if ok_cases:
        print(f"\n{DIM}casos correctos por familia — deben pasar{RESET}")
        for fam, d in ok_cases:
            rep = run_one(d, [fam] if fam in validate.FAMILY_ORDER else validate.FAMILY_ORDER)
            avisos += len(rep.warnings)
            marca = f"{GREEN}PASA{RESET}" if rep.ok else f"{RED}FALLA{RESET}"
            print(f"  {marca}  {fam}/{d.name}")
            if not rep.ok:
                fallos.append(d.name)
                for e in rep.errors[:3]:
                    print(f"        {RED}{e}{RESET}")

    if bad_cases:
        print(f"\n{DIM}casos defectuosos por familia — deben fallar en su familia{RESET}")
        for fam, d in bad_cases:
            if fam not in validate.FAMILY_ORDER:
                print(f"  {YELLOW}OMITIDO{RESET}  {d.name}: '{fam}' no es una familia de §19.2")
                continue
            rep = run_one(d, [fam])
            # Detectado = la familia produjo al menos un error o una advertencia.
            # Una advertencia cuenta: §19.1 la admite como deteccion siempre que
            # exija issue o justificacion, y hay defectos que no bloquean el delta.
            detectado = bool(rep.errors or rep.warnings)
            marca = f"{GREEN}DETECTA{RESET}" if detectado else f"{RED}NO DETECTA{RESET}"
            n = len(rep.errors) + len(rep.warnings)
            print(f"  {marca}  {fam}/{d.name}  {DIM}({n} hallazgos){RESET}")
            if not detectado:
                fallos.append(f"{d.name} (el defecto pasó desapercibido)")

    total = len(ordinarios) + len(ok_cases) + len(bad_cases)
    print(f"\n{total} casos · {len(fallos)} fallos · {avisos} advertencias acumuladas")
    if fallos:
        print(f"{RED}FALLOS:{RESET} " + ", ".join(fallos))
        return 1
    print(f"{GREEN}TODOS LOS FIXTURES CORRECTOS{RESET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
