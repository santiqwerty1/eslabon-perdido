#!/usr/bin/env python3
"""Pruebas de scripts/build_views/red.py (la red por hipótesis, DEC-061).

Los casos van sobre un libro mayor mínimo escrito aquí, con un ejemplo de cada
regla: la bipartición con complemento, el re-enraizado que rompe clados, la
raíz sin lado declarado, la hipótesis que no trae raíz, las composiciones, la
clasificación, las históricas, las derivadas, el tronco y las poblaciones.
Sobre el libro mayor real sólo se comprueban invariantes: cada afirmación de
topología queda seleccionada o excluida, y lo seleccionado se cumple.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "build_views"))
sys.path.insert(0, str(ROOT / "scripts" / "validate"))

import red  # noqa: E402

E, A, A1, A2, A2A, A2B, D, X = (f"CLADE-{n:06d}" for n in (901, 902, 903, 904, 905, 906, 907, 908))
R1, R2, OPI, DIP, K = (f"CLADE-{n:06d}" for n in (909, 910, 911, 912, 913))
P, I, F, T = (f"CLADE-{n:06d}" for n in (921, 922, 923, 924))
CONCEPTO, LECA, TALLO, ASGARD = "TAXCONCEPT-000901", "POP-000901", "LINEAGE-000901", "LINEAGE-000902"
RAIZ, HOLO = "CONFLICT-000901", "CONFLICT-000902"


def dims(historico="current"):
    return {"acceptance": "not_assessed", "evidence_strength": "medium", "resolution": "resolved",
            "historical_status": historico}


def af(n, s, pred, o, hyp=(), historico="current", derivada=False):
    return {"id": f"CLAIM-{n:06d}", "claim_type": "relational", "subject_id": s, "predicate": pred,
            "object": {"entity_id": o} if o.split("-")[0] in ("CLADE", "TAXCONCEPT", "LINEAGE", "POP")
            else {"category": o, "vocabulary": None},
            "scope": {"hypothesis_ids": list(hyp)} if hyp else None,
            "derivation": {"rule": "prueba", "depends_on_ids": []} if derivada else None,
            "epistemic_dimensions": dims(historico), "notes": [], "record_status": "active",
            "provenance": {"section_ids": ["SEC-000001"], "passage_ids": [], "source_ids": []}}


def hip(n, nombre, incluidas, grupos, corto):
    return {"id": f"HYP-{n:06d}", "name": nombre, "description": f"{nombre}. ({corto} del corredor)",
            "included_claim_ids": incluidas, "excluded_claim_ids": [], "conflict_group_ids": grupos,
            "alternative_hypothesis_ids": [], "record_status": "active"}


# Tronco: E contiene A y D; A = (A1, K); K = (A2a, A2b) por composición; A2a contiene P, I, F.
TRONCO = [
    af(1, A, "member_of", E), af(2, D, "member_of", E), af(3, A1, "member_of", A), af(4, A2A, "member_of", A),
    af(5, A2B, "member_of", A), af(6, A2A, "sister_group_of", A2B), af(7, A1, "sister_group_of", K),
    af(8, P, "member_of", A2A), af(9, I, "member_of", A2A), af(10, F, "member_of", A2A),
    af(11, LECA, "member_of", E), af(12, TALLO, "stem_lineage_of", E), af(13, E, "sister_group_of", ASGARD),
    af(14, A1, "member_of", CONCEPTO), af(15, D, "member_of", A, historico="historical"),
    af(16, A2B, "member_of", A2A, derivada=True),
]
HIPOTESIS_AF = [
    af(21, X, "sister_group_of", R1, hyp=["HYP-000901"]),
    af(22, A2A, "sister_group_of", R2, hyp=["HYP-000902"]),
    af(23, OPI, "sister_group_of", DIP, hyp=["HYP-000903"]),
    af(24, A, "member_of", OPI, hyp=["HYP-000903"]),
    af(25, X, "classified_as_by", "linajes sucesivos", hyp=["HYP-000904"]),
    af(26, I, "sister_group_of", F, hyp=["HYP-000905"]),
    af(27, P, "sister_group_of", I, hyp=["HYP-000906"]),
    af(28, T, "sister_group_of", F, hyp=["HYP-000906"]),
]
HIPOTESIS = [
    hip(901, "Raíz X", ["CLAIM-000021"], [RAIZ], "H1"),
    hip(902, "Raíz A2a", ["CLAIM-000022"], [RAIZ], "H2"),
    hip(903, "Raíz Opi–Dip", ["CLAIM-000023", "CLAIM-000024"], [RAIZ], "H3"),
    hip(904, "Raíz excavada", ["CLAIM-000025"], [RAIZ], "H4"),
    hip(905, "P hermana del resto", ["CLAIM-000026"], [HOLO], "H5"),
    hip(906, "T hermana de F", ["CLAIM-000027", "CLAIM-000028"], [HOLO], "H6"),
]
CLADOS = {E: "Euk", A: "Amor", A1: "A1", A2: "A2", A2A: "Opis", A2B: "Apus", D: "Diaph", X: "Disc",
          R1: "resto sin Disc", R2: "resto sin Opis", OPI: "Opi", DIP: "Dip", K: "Apus+Opis",
          P: "Pluri", I: "Ichthyo", F: "Filo", T: "Tereto"}
ESPEC = {
    "nombre": "prueba", "decision": "DEC-000", "escala": "prueba", "raiz": E,
    "anclas": {RAIZ: {"nodo": E, "lectura": "primera_divergencia", "motivo": "chocan en la primera divergencia"}},
    "complementos": {R1: {"de": X, "dentro_de": E, "motivo": "el resto sin Disc"},
                     R2: {"de": A2A, "dentro_de": E, "motivo": "el resto sin Opis"}},
    "composiciones": {K: {"miembros": [A2A, A2B], "motivo": "Apus+Opis"},
                      T: {"miembros": [P, I], "motivo": "Pluri+Ichthyo"}},
    "vistas": [{"hipotesis": []}] + [{"hipotesis": [f"HYP-{n:06d}"]} for n in range(901, 907)],
}


def jsonl(path: Path, filas: list[dict]) -> None:
    path.write_text("".join(json.dumps(f, ensure_ascii=False) + "\n" for f in filas), encoding="utf-8")


class LibroMinimo:
    def __init__(self, raiz: Path, extra: list[dict] = ()):
        self.raiz = raiz
        self.base = raiz / "knowledge" / "records"
        self.base.mkdir(parents=True)
        man = raiz / "knowledge" / "corpus" / "manifests"
        man.mkdir(parents=True)
        (man / "dataset.json").write_text(json.dumps({
            "dataset_revision": "REV-000007", "snapshot_id": "SNAP-000003",
            "corpus_freeze": {"path": "knowledge/corpus/manifests/corredor.json", "commit": "abcdef0123",
                              "version": "0.1", "decision": "DEC-000"}}), encoding="utf-8")
        (man / "corredor.json").write_text(json.dumps({"cutoff": "2026-08-08", "version": "0.1"}),
                                           encoding="utf-8")
        jsonl(self.base / "claims.jsonl", TRONCO + HIPOTESIS_AF + list(extra))
        jsonl(self.base / "hypotheses.jsonl", HIPOTESIS)
        jsonl(self.base / "clades.jsonl", [{"id": k, "preferred_label": v, "record_status": "active"}
                                           for k, v in CLADOS.items()])
        jsonl(self.base / "lineages.jsonl", [
            {"id": TALLO, "preferred_label": "biota troncal", "record_status": "active"},
            {"id": ASGARD, "preferred_label": "asgard", "record_status": "active"}])
        jsonl(self.base / "populations.jsonl", [{"id": LECA, "preferred_label": "LECA", "record_status": "active"}])
        jsonl(self.base / "taxonomic-names.jsonl", [{"id": "NAME-000901", "canonical_spelling": "Sulco",
                                                     "record_status": "active"}])
        jsonl(self.base / "taxon-concepts.jsonl", [{"id": CONCEPTO, "name_id": "NAME-000901",
                                                    "according_to_source_id": None, "record_status": "active"}])
        jsonl(self.base / "conflict-groups.jsonl", [
            {"id": RAIZ, "name": "Raíz", "description": "raíz", "scope": "topology", "record_status": "active"},
            {"id": HOLO, "name": "Holo", "description": "holo", "scope": "topology", "record_status": "active"}])
        self.espec = raiz / "espec.json"
        self.espec.write_text(json.dumps(ESPEC), encoding="utf-8")
        self.vistas = raiz / "knowledge" / "views" / "phylogenetic-views.jsonl"
        self.vistas.parent.mkdir(parents=True)

    def construir(self, espec: dict | None = None) -> dict:
        if espec is not None:
            self.espec.write_text(json.dumps(espec), encoding="utf-8")
        return red.construir(self.base, self.raiz, self.espec, self.vistas)

    def escribir(self, d: dict) -> str:
        texto = red.jsonl(d["registros"])
        self.vistas.write_text(texto, encoding="utf-8")
        return texto


def vista(d: dict, hyp: str | None) -> tuple[dict, dict]:
    for rec, v in d["vistas"]:
        if (rec["hypothesis_ids"] or [None]) == [hyp]:
            return rec, v
    raise KeyError(hyp)


def hijos(v: dict, n: str) -> set[str]:
    return set(v["arbol"].hijos.get(n, []))


def nombrados(v: dict, n: str) -> set[str]:
    """Los nodos con nombre bajo n, atravesando los que no lo tienen."""
    out = set()
    for h in v["arbol"].hijos.get(n, []):
        out |= nombrados(v, h) if h.startswith("~") else {h}
    return out


class TestRedMinima(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.libro = LibroMinimo(Path(self.tmp.name))
        self.d = self.libro.construir()

    def tearDown(self):
        self.tmp.cleanup()

    def test_tronco_contiene_compone_y_anota(self):
        rec, v = vista(self.d, None)
        self.assertEqual(hijos(v, E), {A, D})
        self.assertEqual(hijos(v, A), {A1, K}, "la composición de K junta a sus miembros")
        self.assertEqual(hijos(v, K), {A2A, A2B})
        self.assertEqual(v["arbol"].anotaciones[E], [LECA], "una población se anota, no es rama")
        tallo = v["arbol"].padre[E]
        self.assertEqual(v["arbol"].tipo[tallo], "tronco")
        self.assertEqual(hijos(v, tallo), {E, TALLO})
        self.assertEqual(hijos(v, v["principal"]), {tallo, ASGARD})
        self.assertEqual(rec["hypothesis_ids"], [])
        self.assertIn("CLAIM-000007", rec["selected_claim_ids"], "A1 hermana de K se cumple tras componer K")

    def test_motivos_de_entrada(self):
        _, v = vista(self.d, None)
        self.assertEqual(v["fuera"]["CLAIM-000014"][0], "clasificacion")
        self.assertEqual(v["fuera"]["CLAIM-000015"][0], "historica")
        self.assertEqual(v["fuera"]["CLAIM-000016"][0], "derivada")
        self.assertEqual(v["fuera"]["CLAIM-000021"][0], "otra_hipotesis")
        _, v5 = vista(self.d, "HYP-000905")
        self.assertEqual(v5["fuera"]["CLAIM-000027"][0], "rival")
        self.assertEqual(v5["fuera"]["CLAIM-000021"][0], "otra_hipotesis")
        self.assertNotIn("CLAIM-000025", v5["fuera"], "lo que no es topología no entra en la vista")

    def test_biparticion_con_complemento(self):
        rec, v = vista(self.d, "HYP-000901")
        self.assertEqual(hijos(v, E), {X, R1})
        self.assertEqual(hijos(v, R1), {A, D}, "el complemento recibe el resto de Euk")
        self.assertIn("CLAIM-000021", rec["selected_claim_ids"])
        self.assertEqual(v["rotos"], [])
        self.assertTrue(any("el resto sin Disc" in c for c in rec["editorial_criteria"]))

    def test_reenraizado_rompe_los_clados_del_camino(self):
        rec, v = vista(self.d, "HYP-000902")
        self.assertEqual(hijos(v, E), {A2A, R2})
        self.assertEqual(v["rotos"], sorted([A, K]), "A y K contenían la raíz nueva")
        self.assertEqual(nombrados(v, R2), {D, A1, A2B}, "el resto re-enraizado: D, y A1 con Apus")
        for cid in ("CLAIM-000001", "CLAIM-000003", "CLAIM-000004", "CLAIM-000005", "CLAIM-000006",
                    "CLAIM-000007"):
            self.assertEqual(v["fuera"][cid][0], "contradicha", cid)
        self.assertIn("CLAIM-000022", rec["selected_claim_ids"])
        self.assertIn("CLAIM-000008", rec["selected_claim_ids"], "lo que está dentro de Opis sigue en pie")
        self.assertTrue(any("no declara en excluded_claim_ids" in n for n in rec["notes"]))
        self.assertTrue(any("dejan de ser clados" in n for n in rec["notes"]))

    def test_raiz_sin_lado_declarado(self):
        rec, v = vista(self.d, "HYP-000903")
        self.assertEqual(hijos(v, E), {OPI, DIP, D})
        self.assertIn("sin_lado", v["arbol"].marcas[D])
        self.assertEqual(v["arbol"].padre[A], OPI, "el padre más interno manda: Opi dentro de Euk")
        self.assertIn("CLAIM-000023", rec["selected_claim_ids"], "la raíz se cumple fuera de lo que no tiene lado")
        self.assertTrue(any("Sin lado declarado" in s and D in s for s in rec["simplifications"]))

    def test_hipotesis_que_no_trae_raiz(self):
        rec, v = vista(self.d, "HYP-000904")
        self.assertEqual(v["sin_raiz"], [RAIZ])
        self.assertTrue(any("no trae afirmación hermana" in n for n in rec["notes"]))
        self.assertTrue(any(RAIZ in s for s in rec["simplifications"] if s.startswith("Conflictos")))

    def test_hermanos_y_composicion_en_holo(self):
        _, v5 = vista(self.d, "HYP-000905")
        (grupo,) = [h for h in hijos(v5, A2A) if h.startswith("~")]
        self.assertEqual(hijos(v5, grupo), {I, F})
        self.assertIn("hipotesis", v5["arbol"].marcas[I])
        rec6, v6 = vista(self.d, "HYP-000906")
        self.assertEqual(hijos(v6, A2A), {T, F})
        self.assertEqual(hijos(v6, T), {P, I}, "la composición de T nombra el grupo de P e I")
        self.assertIn("CLAIM-000028", rec6["selected_claim_ids"])

    def test_toda_afirmacion_de_red_queda_seleccionada_o_excluida(self):
        de_red = {c["id"] for c in TRONCO + HIPOTESIS_AF if c["predicate"] in red.DE_RED}
        for rec, _ in self.d["vistas"]:
            sel, exc = set(rec["selected_claim_ids"]), set(rec["excluded_claim_ids"])
            self.assertFalse(sel & exc, rec["id"])
            self.assertEqual(sel | exc, de_red, rec["id"])

    def test_identificadores_estables_y_version_por_contenido(self):
        texto = self.libro.escribir(self.d)
        segunda = self.libro.escribir(self.libro.construir())
        self.assertEqual(texto, segunda, "dos ejecuciones dan los mismos bytes")
        ids = {tuple(r["hypothesis_ids"]): r["id"] for r in self.d["registros"]}
        self.assertEqual(ids[()], "PHYVIEW-000001")
        # Una afirmación nueva del tronco cambia todas las vistas; se reconstruyen con versión nueva.
        extra = af(40, ASGARD, "diverges_from", TALLO)
        claims = self.libro.base / "claims.jsonl"
        claims.write_text(claims.read_text(encoding="utf-8") + json.dumps(extra) + "\n", encoding="utf-8")
        d2 = self.libro.construir()
        for rec in d2["registros"]:
            self.assertEqual(rec["id"], ids[tuple(rec["hypothesis_ids"])])
            self.assertEqual(rec["view_version"], "1.1.0")
        self.libro.escribir(d2)
        # Una vista que la especificación ya no pide se retira, no se borra.
        espec = dict(ESPEC, vistas=ESPEC["vistas"][:-1])
        d3 = self.libro.construir(espec)
        retirada = next(r for r in d3["registros"] if r["hypothesis_ids"] == ["HYP-000906"])
        self.assertEqual(retirada["record_status"], "deprecated")

    def test_los_registros_cumplen_su_esquema(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("jsonschema no instalado")
        schemas = {p.name: json.loads(p.read_text(encoding="utf-8"))
                   for p in (ROOT / "schemas" / "json-schema").glob("*.json")}
        esquema = schemas["phylogenetic-view.json"]
        try:
            from referencing import Registry, Resource
            registro = Registry().with_resources([(n, Resource.from_contents(s)) for n, s in schemas.items()]).crawl()
            val = Draft202012Validator(esquema, registry=registro)
        except ImportError:
            from jsonschema import RefResolver
            val = Draft202012Validator(esquema, resolver=RefResolver.from_schema(esquema, store={
                s["$id"]: s for s in schemas.values() if "$id" in s}))
        for rec in self.d["registros"]:
            errores = [e.message for e in val.iter_errors(rec)]
            self.assertEqual(errores, [], rec["id"])

    def test_el_validador_acepta_las_vistas(self):
        import validate
        jsonl(self.libro.base / "phylogenetic-views.jsonl", self.d["registros"])
        rep = validate.run(["hypotheses", "separation"], self.libro.base)
        self.assertEqual([e for e in rep.errors if "PHYVIEW" in e], [])
        self.assertEqual([w for w in rep.warnings if "PHYVIEW" in w], [])

    def test_pagina_documento_y_fragmento(self):
        datos = red.datos_pagina(self.d)
        doc, frag = red.pagina(datos), red.pagina(datos, documento=False)
        self.assertTrue(doc.startswith("<!doctype html>"))
        self.assertFalse(frag.lstrip().startswith("<!doctype"))
        self.assertIn("<title>La red por hipótesis</title>", frag[:8192])
        carga = doc.split('id="datos">', 1)[1].split("</script>", 1)[0]
        self.assertEqual(json.loads(carga)["tronco"], "PHYVIEW-000001")
        grupos = {g["id"]: g for g in datos["grupos"]}
        self.assertEqual(grupos[RAIZ]["foco"], E, "el grupo anclado se centra en su nodo")
        self.assertEqual(grupos[HOLO]["foco"], A2A, "el otro, en el ancestro común de lo que disputan")


class TestRedReal(unittest.TestCase):
    """Invariantes sobre el libro mayor real, que no dependen de cuántas secciones haya."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.d = red.construir(vistas_path=Path(cls.tmp.name) / "vistas.jsonl")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_toda_afirmacion_de_red_queda_en_un_solo_sitio(self):
        de_red = {c for c, x in self.d["libro"].r.claims.items() if x["predicate"] in red.DE_RED}
        for rec, _ in self.d["vistas"]:
            sel, exc = set(rec["selected_claim_ids"]), set(rec["excluded_claim_ids"])
            self.assertFalse(sel & exc, rec["id"])
            self.assertEqual(sel | exc, de_red, rec["id"])

    def test_lo_seleccionado_se_cumple(self):
        libro = self.d["libro"]
        for rec, v in self.d["vistas"]:
            for cid in rec["selected_claim_ids"]:
                ok, _, detalle = red.cumple(v["arbol"], libro, libro.r.claims[cid], set(v["rotos"]))
                self.assertTrue(ok, f"{rec['id']} {cid}: {detalle}")

    def test_ninguna_vista_mezcla_rivales(self):
        libro = self.d["libro"]
        for rec, _ in self.d["vistas"]:
            rivales = libro.rivales(rec["hypothesis_ids"])
            for cid in rec["selected_claim_ids"]:
                alcance = set((libro.r.claims[cid].get("scope") or {}).get("hypothesis_ids") or [])
                self.assertFalse(alcance & rivales, f"{rec['id']} {cid}")

    def test_la_pagina_sale_igual_dos_veces(self):
        a = red.pagina(red.datos_pagina(self.d))
        b = red.pagina(red.datos_pagina(red.construir(vistas_path=Path(self.tmp.name) / "vistas.jsonl")))
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
