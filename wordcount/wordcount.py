#!/usr/bin/env python3
"""wordcount.py - Cuenta palabras de un archivo de texto y muestra las 10 mas frecuentes.

Uso:
    python3 wordcount.py archivo.txt
    python3 wordcount.py archivo.txt --top 5
    python3 wordcount.py archivo.txt --min-length 3
"""

import argparse
import re
import sys
from collections import Counter

# Palabra = secuencia de letras (incluye acentos y ñ) y numeros.
WORD_RE = re.compile(r"[^\W\d_]+|\d+", re.UNICODE)


def tokenize(text, min_length=1):
    """Devuelve la lista de palabras normalizadas (minusculas) del texto.

    min_length: longitud minima de palabra para ser contada.
    """
    words = WORD_RE.findall(text.lower())
    return [w for w in words if len(w) >= min_length]


def count_words(text, min_length=1):
    """Devuelve un Counter con la frecuencia de cada palabra."""
    return Counter(tokenize(text, min_length=min_length))


def top_words(text, top=10, min_length=1):
    """Devuelve una lista de tuplas (palabra, frecuencia) ordenada desc.

    El desempate es alfabetico para que el resultado sea determinista.
    """
    counter = count_words(text, min_length=min_length)
    # Orden: por frecuencia desc, luego palabra asc.
    return sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))[:top]


def read_text(path):
    """Lee un archivo de texto en UTF-8."""
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def format_report(pairs, total_words):
    """Formatea el reporte de las palabras mas frecuentes."""
    lines = []
    lines.append(f"Total de palabras: {total_words}")
    lines.append(f"Palabras unicas: {len(pairs) if False else ''}".rstrip())
    lines.append("")
    lines.append(f"{'#':>3}  {'PALABRA':<20} {'FREC':>6}")
    lines.append("-" * 33)
    for i, (word, freq) in enumerate(pairs, start=1):
        lines.append(f"{i:>3}  {word:<20} {freq:>6}")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Cuenta palabras de un archivo de texto y muestra las mas frecuentes."
    )
    parser.add_argument("archivo", help="Ruta del archivo de texto a analizar")
    parser.add_argument(
        "--top", type=int, default=10,
        help="Numero de palabras mas frecuentes a mostrar (default: 10)",
    )
    parser.add_argument(
        "--min-length", type=int, default=1,
        help="Longitud minima de palabra para contarla (default: 1)",
    )
    args = parser.parse_args(argv)

    try:
        text = read_text(args.archivo)
    except FileNotFoundError:
        print(f"Error: no se encontro el archivo '{args.archivo}'", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"Error al leer el archivo: {exc}", file=sys.stderr)
        return 1

    total = len(tokenize(text, min_length=args.min_length))
    pairs = top_words(text, top=args.top, min_length=args.min_length)

    print(f"Archivo: {args.archivo}")
    print(f"Total de palabras: {total}")
    print(f"Palabras unicas: {len(count_words(text, min_length=args.min_length))}")
    print()
    print(f"{'#':>3}  {'PALABRA':<20} {'FREC':>6}")
    print("-" * 33)
    for i, (word, freq) in enumerate(pairs, start=1):
        print(f"{i:>3}  {word:<20} {freq:>6}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
