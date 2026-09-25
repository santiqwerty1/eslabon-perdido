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

    # --- conformidad del formato de investigación --------------------------
    fmt = FIXTURES / "research-format"
    if fmt.is_dir():
        import subprocess
        print(f"\n{DIM}formato de la investigación — el correcto pasa, el defectuoso falla{RESET}")
        for doc, debe_pasar in ((fmt / "SEC-SAMPLE.md", True), (fmt / "SEC-SAMPLE-BAD.md", False)):
            if not doc.exists():
                continue
            r = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "ingest" / "parse_research.py"), str(doc)],
                capture_output=True, text=True)
            paso = r.returncode == 0
            bien = paso == debe_pasar
            marca = f"{GREEN}{'PASA' if paso else 'DETECTA'}{RESET}" if bien else f"{RED}INESPERADO{RESET}"
            n_err = r.stdout.count("ERROR")
            print(f"  {marca}  {doc.name}  {DIM}({n_err} errores de conformidad){RESET}")
            if not bien:
                fallos.append(f"{doc.name} (conformidad inesperada)")
        total_fmt = 2
    else:
        total_fmt = 0

    # --- versiones del corpus ------------------------------------------------
    # El diff tiene que separar la corrección de la renumeración: si confunde
    # una con otra, la ingestión de cada pasada de auditoría reingeriría el
    # corpus entero o, peor, daría por igual una afirmación que cambió.
    ver = FIXTURES / "corpus-versions"
    total_ver = 0
    if ver.is_dir():
        import json
        import subprocess
        import tempfile
        print(f"\n{DIM}versiones del corpus — el diff separa corrección de renumeración{RESET}")
        freeze = [sys.executable, str(ROOT / "scripts" / "ingest" / "freeze.py")]
        esperado = {"sin_cambios": 1, "solo_renumeracion": 2, "modificadas": 2, "nuevas": 1, "retiradas": 1}
        with tempfile.TemporaryDirectory() as tmp:
            informe, congelada = Path(tmp) / "diff.json", Path(tmp) / "v1.json"
            subprocess.run([*freeze, "diff", str(ver / "v1"), str(ver / "v2"), "--json", str(informe)],
                           capture_output=True, text=True)
            obtenido = {}
            if informe.exists():
                inf = json.loads(informe.read_text(encoding="utf-8"))
                af = inf["afirmaciones"]
                obtenido = {k: (v if isinstance(v, int) else len(v)) for k, v in af.items() if k in esperado}
                ent = inf["registros"].get("data/apendices/B_entidades.csv", {})
                obtenido["entidad nueva"] = len(ent.get("nuevas", []))
                obtenido["entidad renumerada"] = len(ent.get("solo_renumeracion", []))
                obtenido["prosa cambiada"] = sum(1 for x in inf["prosa"] if x["estado"] == "cambiado")
            esperado_todo = {**esperado, "entidad nueva": 1, "entidad renumerada": 2, "prosa cambiada": 1}
            bien = obtenido == esperado_todo
            marca = f"{GREEN}PASA{RESET}" if bien else f"{RED}FALLA{RESET}"
            print(f"  {marca}  diff v1 → v2  {DIM}({', '.join(f'{k} {v}' for k, v in obtenido.items())}){RESET}")
            if not bien:
                fallos.append("corpus-versions: diff")
                print(f"        {RED}esperado {esperado_todo}{RESET}")

            subprocess.run([*freeze, "create", str(ver / "v1"), "--salida", str(congelada),
                            "--fecha", "2026-09-25"], capture_output=True, text=True)
            propia = subprocess.run([*freeze, "verify", str(ver / "v1"), str(congelada)],
                                    capture_output=True, text=True).returncode == 0
            ajena = subprocess.run([*freeze, "verify", str(ver / "v2"), str(congelada)],
                                   capture_output=True, text=True).returncode != 0
            bien = propia and ajena
            marca = f"{GREEN}PASA{RESET}" if bien else f"{RED}FALLA{RESET}"
            print(f"  {marca}  congelar v1: verify la reconoce y rechaza v2")
            if not bien:
                fallos.append("corpus-versions: create/verify")

        total_ver = 2

    # --- pruebas de la ingestión ---------------------------------------------
    # Los bordes del diff —filas que un diff equivocado haría desaparecer sin
    # aviso— y la ingestión de una sección del corredor sobre corredor-mini.
    pruebas = sorted((ROOT / "tests" / "ingest").glob("test_*.py"))
    if pruebas:
        import subprocess
        print(f"\n{DIM}ingestión — congelación, diff y secciones del corredor{RESET}")
        for prueba in pruebas:
            r = subprocess.run([sys.executable, str(prueba)], capture_output=True, text=True)
            resumen = (r.stderr.strip().splitlines() or ["?"])[-1]
            marca = f"{GREEN}PASA{RESET}" if r.returncode == 0 else f"{RED}FALLA{RESET}"
            print(f"  {marca}  {prueba.name}  {DIM}({resumen}){RESET}")
            if r.returncode != 0:
                fallos.append(f"ingest/{prueba.name}")
                print(r.stderr[-3000:])
        total_ver += len(pruebas)

    total = len(ordinarios) + len(ok_cases) + len(bad_cases) + total_fmt + total_ver
    print(f"\n{total} casos · {len(fallos)} fallos · {avisos} advertencias acumuladas")
    if fallos:
        print(f"{RED}FALLOS:{RESET} " + ", ".join(fallos))
        return 1
    print(f"{GREEN}TODOS LOS FIXTURES CORRECTOS{RESET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
