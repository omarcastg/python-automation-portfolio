#!/usr/bin/env python3
"""csv2json: Convierte un CSV (nombre, edad, ciudad) a JSON.

Caracteristicas:
  - Detecta si el CSV tiene cabecera o no.
  - Ignora filas malformadas y reporta cuantas se ignoraron.
  - Guarda el JSON con indentacion.

Uso:
    python3 csv2json.py entrada.csv salida.json
    python3 csv2json.py entrada.csv salida.json --no-header
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

# Columnas esperadas por defecto.
DEFAULT_FIELDS = ["nombre", "edad", "ciudad"]

# Nombres que, si aparecen en la primera fila, indican que hay cabecera.
HEADER_HINTS = {"nombre", "name", "edad", "age", "ciudad", "city"}


def looks_like_header(row: list[str]) -> bool:
    """Heuristica: la fila parece cabecera si sus celdas coinciden con nombres conocidos."""
    if not row:
        return False
    normalized = {cell.strip().lower() for cell in row}
    return bool(normalized & HEADER_HINTS)


def is_valid_row(row: list[str]) -> bool:
    """Una fila es valida si tiene exactamente 3 campos no vacios."""
    if len(row) != 3:
        return False
    return all(cell.strip() != "" for cell in row)


def convert(
    input_path: str | Path,
    output_path: str | Path,
    has_header: bool | None = None,
) -> dict[str, Any]:
    """Convierte el CSV a JSON.

    Args:
        input_path: ruta del CSV de entrada.
        output_path: ruta del JSON de salida.
        has_header: True/False para forzar; None para autodetectar.

    Returns:
        dict con 'records', 'ignored' y 'total'.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    records: list[dict[str, str]] = []
    ignored = 0
    total = 0

    with input_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        rows = list(reader)

    if not rows:
        # CSV vacio: nada que procesar.
        result = {"records": [], "ignored": 0, "total": 0}
        _write_json(output_path, result["records"])
        return result

    # Determinar cabecera.
    if has_header is None:
        has_header = looks_like_header(rows[0])

    if has_header:
        header = [c.strip().lower() for c in rows[0]]
        data_rows = rows[1:]
    else:
        header = DEFAULT_FIELDS
        data_rows = rows

    for row in data_rows:
        total += 1
        if not is_valid_row(row):
            ignored += 1
            continue
        record = {header[i]: row[i].strip() for i in range(3)}
        records.append(record)

    _write_json(output_path, records)
    return {"records": records, "ignored": ignored, "total": total}


def _write_json(output_path: Path, records: list[dict[str, str]]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(records, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Convierte CSV a JSON.")
    parser.add_argument("input", help="Archivo CSV de entrada")
    parser.add_argument("output", help="Archivo JSON de salida")
    parser.add_argument(
        "--no-header",
        action="store_true",
        help="Forzar que el CSV NO tiene cabecera",
    )
    parser.add_argument(
        "--header",
        action="store_true",
        help="Forzar que el CSV SI tiene cabecera",
    )
    args = parser.parse_args(argv)

    has_header: bool | None = None
    if args.no_header:
        has_header = False
    elif args.header:
        has_header = True

    result = convert(args.input, args.output, has_header=has_header)
    print(
        f"OK: {len(result['records'])} registros escritos, "
        f"{result['ignored']} filas ignoradas de {result['total']}."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
