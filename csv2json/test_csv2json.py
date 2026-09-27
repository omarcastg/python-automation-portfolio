#!/usr/bin/env python3
"""Tests unitarios para csv2json.py.

Cubre: cabecera, autodeteccion, --no-header, filas malformadas,
CSV vacio, indentacion/UTF-8 del JSON y persistencia.

Ejecutar:
    cd /home/omar/OMAR-AI/workspaces/csv2json && python3 -m unittest test_csv2json -v
"""

from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

# Asegura que el modulo bajo test sea importable desde este directorio.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from csv2json import DEFAULT_FIELDS, convert, main  # noqa: E402


class TestCsv2Json(unittest.TestCase):
    """Tests para csv2json.convert y csv2json.main."""

    def setUp(self) -> None:
        # Directorio temporal aislado por test.
        self._tmp = tempfile.TemporaryDirectory()
        self.tmpdir = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    # --- helpers ---------------------------------------------------------
    def write_csv(self, content: str, name: str = "in.csv") -> Path:
        path = self.tmpdir / name
        path.write_text(content, encoding="utf-8")
        return path

    def out_path(self, name: str = "out.json") -> Path:
        return self.tmpdir / name

    # --- 1. CSV con cabecera --------------------------------------------
    def test_with_header_three_records(self) -> None:
        csv_text = (
            "nombre,edad,ciudad\n"
            "Ana,30,Madrid\n"
            "Luis,25,Bogota\n"
            "Marta,40,Lima\n"
        )
        in_path = self.write_csv(csv_text)
        out = self.out_path()

        result = convert(in_path, out)

        self.assertEqual(result["total"], 3)
        self.assertEqual(result["ignored"], 0)
        self.assertEqual(len(result["records"]), 3)
        self.assertEqual(
            result["records"][0],
            {"nombre": "Ana", "edad": "30", "ciudad": "Madrid"},
        )
        self.assertEqual(
            result["records"][1],
            {"nombre": "Luis", "edad": "25", "ciudad": "Bogota"},
        )
        self.assertEqual(
            result["records"][2],
            {"nombre": "Marta", "edad": "40", "ciudad": "Lima"},
        )
        # Claves exactas en cada registro.
        for rec in result["records"]:
            self.assertEqual(set(rec.keys()), {"nombre", "edad", "ciudad"})

    # --- 2. CSV sin cabecera (autodeteccion) ----------------------------
    def test_no_header_autodetection_uses_default_fields(self) -> None:
        csv_text = (
            "Ana,30,Madrid\n"
            "Luis,25,Bogota\n"
            "Marta,40,Lima\n"
        )
        in_path = self.write_csv(csv_text)
        out = self.out_path()

        result = convert(in_path, out)  # has_header=None -> autodetecta

        self.assertEqual(result["total"], 3)
        self.assertEqual(result["ignored"], 0)
        self.assertEqual(len(result["records"]), 3)
        # La primera fila NO es cabecera: se trata como dato.
        self.assertEqual(
            result["records"][0],
            {"nombre": "Ana", "edad": "30", "ciudad": "Madrid"},
        )
        self.assertEqual(
            result["records"][2],
            {"nombre": "Marta", "edad": "40", "ciudad": "Lima"},
        )
        # Las claves coinciden con DEFAULT_FIELDS.
        for rec in result["records"]:
            self.assertEqual(list(rec.keys()), DEFAULT_FIELDS)

    # --- 3. Forzar has_header=False -------------------------------------
    def test_force_no_header_treats_all_rows_as_data(self) -> None:
        # Primera fila parece cabecera, pero forzamos que NO lo es.
        csv_text = (
            "nombre,edad,ciudad\n"
            "Ana,30,Madrid\n"
        )
        in_path = self.write_csv(csv_text)
        out = self.out_path()

        result = convert(in_path, out, has_header=False)

        # Ambas filas son datos; la "cabecera" se convierte en un registro.
        self.assertEqual(result["total"], 2)
        self.assertEqual(result["ignored"], 0)
        self.assertEqual(len(result["records"]), 2)
        self.assertEqual(
            result["records"][0],
            {"nombre": "nombre", "edad": "edad", "ciudad": "ciudad"},
        )
        self.assertEqual(
            result["records"][1],
            {"nombre": "Ana", "edad": "30", "ciudad": "Madrid"},
        )

    # --- 4. Filas malformadas ignoradas y contadas ----------------------
    def test_malformed_rows_are_ignored_and_counted(self) -> None:
        csv_text = (
            "nombre,edad,ciudad\n"
            "Ana,30,Madrid\n"       # valida
            "SoloDos,25\n"          # malformada (2 campos)
            "Luis,25,Bogota,Extra\n"  # malformada (4 campos)
            ",40,Lima\n"            # malformada (campo vacio)
            "Marta,40,Lima\n"       # valida
        )
        in_path = self.write_csv(csv_text)
        out = self.out_path()

        result = convert(in_path, out)

        self.assertEqual(result["total"], 5)   # 5 filas de datos
        self.assertEqual(result["ignored"], 3)  # 3 malformadas
        self.assertEqual(len(result["records"]), 2)
        self.assertEqual(
            result["records"][0],
            {"nombre": "Ana", "edad": "30", "ciudad": "Madrid"},
        )
        self.assertEqual(
            result["records"][1],
            {"nombre": "Marta", "edad": "40", "ciudad": "Lima"},
        )

    # --- 5. CSV vacio ----------------------------------------------------
    def test_empty_csv_produces_empty_json(self) -> None:
        in_path = self.write_csv("")
        out = self.out_path()

        result = convert(in_path, out)

        self.assertEqual(result["total"], 0)
        self.assertEqual(result["ignored"], 0)
        self.assertEqual(result["records"], [])
        # El JSON de salida debe existir y ser una lista vacia.
        self.assertTrue(out.exists())
        self.assertEqual(json.loads(out.read_text(encoding="utf-8")), [])

    # --- 6. Indentacion y UTF-8 del JSON --------------------------------
    def test_json_output_is_indented_and_utf8(self) -> None:
        csv_text = (
            "nombre,edad,ciudad\n"
            "Jose,30,Malaga\n"
            "Nuria,28,Leon\n"
        )
        in_path = self.write_csv(csv_text)
        out = self.out_path()

        convert(in_path, out)

        raw = out.read_text(encoding="utf-8")
        # Indentacion de 2 espacios: la primera clave va en una linea con sangria.
        self.assertIn('\n  {\n    "nombre": "Jose"', raw)
        # Caracteres no ASCII preservados (ensure_ascii=False).
        self.assertIn("Malaga", raw)
        # El contenido es JSON valido y coincide con lo esperado.
        data = json.loads(raw)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["ciudad"], "Malaga")

    # --- 7. Persistencia via main() -------------------------------------
    def test_main_writes_file_and_prints_summary(self) -> None:
        csv_text = (
            "nombre,edad,ciudad\n"
            "Ana,30,Madrid\n"
            "Luis,25,Bogota\n"
        )
        in_path = self.write_csv(csv_text)
        out = self.out_path()

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main([str(in_path), str(out)])

        self.assertEqual(rc, 0)
        self.assertTrue(out.exists())
        data = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(len(data), 2)
        self.assertEqual(data[1]["nombre"], "Luis")
        # El resumen se imprime en stdout.
        self.assertIn("2", buf.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
