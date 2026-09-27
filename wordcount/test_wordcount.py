#!/usr/bin/env python3
"""Tests unitarios para wordcount.py (unittest)."""

import os
import tempfile
import unittest

from wordcount import (
    count_words,
    format_report,
    main,
    read_text,
    tokenize,
    top_words,
)


class TestTokenize(unittest.TestCase):
    def test_basico(self):
        self.assertEqual(tokenize("Hola mundo hola"), ["hola", "mundo", "hola"])

    def test_minusculas(self):
        self.assertEqual(tokenize("PYTHON Python python"), ["python", "python", "python"])

    def test_acentos_y_enie(self):
        self.assertEqual(tokenize("canción niño"), ["canción", "niño"])

    def test_ignora_puntuacion(self):
        self.assertEqual(tokenize("hola, mundo! ¿qué?"), ["hola", "mundo", "qué"])

    def test_min_length(self):
        self.assertEqual(tokenize("a bb ccc dddd", min_length=3), ["ccc", "dddd"])

    def test_numeros(self):
        self.assertEqual(tokenize("año 2024"), ["año", "2024"])


class TestCountWords(unittest.TestCase):
    def test_frecuencias(self):
        c = count_words("uno dos uno tres uno")
        self.assertEqual(c["uno"], 3)
        self.assertEqual(c["dos"], 1)
        self.assertEqual(c["tres"], 1)

    def test_texto_vacio(self):
        self.assertEqual(count_words(""), {})


class TestTopWords(unittest.TestCase):
    def test_orden_por_frecuencia(self):
        text = "b b b a a c"
        self.assertEqual(top_words(text, top=3), [("b", 3), ("a", 2), ("c", 1)])

    def test_limite_top(self):
        text = "a b c d e"
        self.assertEqual(len(top_words(text, top=2)), 2)

    def test_desempate_alfabetico(self):
        # misma frecuencia -> orden alfabetico
        text = "zeta alfa beta"
        self.assertEqual(
            top_words(text, top=3),
            [("alfa", 1), ("beta", 1), ("zeta", 1)],
        )

    def test_min_length(self):
        text = "a bb bb ccc ccc ccc"
        self.assertEqual(top_words(text, top=2, min_length=2), [("ccc", 3), ("bb", 2)])


class TestReadText(unittest.TestCase):
    def test_lee_utf8(self):
        with tempfile.NamedTemporaryFile(
            "w", suffix=".txt", delete=False, encoding="utf-8"
        ) as fh:
            fh.write("canción niño")
            path = fh.name
        try:
            self.assertEqual(read_text(path), "canción niño")
        finally:
            os.unlink(path)

    def test_archivo_inexistente(self):
        with self.assertRaises(FileNotFoundError):
            read_text("/ruta/que/no/existe_12345.txt")


class TestFormatReport(unittest.TestCase):
    def test_contiene_palabras(self):
        report = format_report([("hola", 3), ("mundo", 1)], 4)
        self.assertIn("hola", report)
        self.assertIn("mundo", report)
        self.assertIn("4", report)


class TestMain(unittest.TestCase):
    def test_main_ok(self):
        with tempfile.NamedTemporaryFile(
            "w", suffix=".txt", delete=False, encoding="utf-8"
        ) as fh:
            fh.write("uno dos uno tres uno")
            path = fh.name
        try:
            rc = main([path, "--top", "2"])
            self.assertEqual(rc, 0)
        finally:
            os.unlink(path)

    def test_main_archivo_inexistente(self):
        rc = main(["/ruta/que/no/existe_99999.txt"])
        self.assertEqual(rc, 1)


class TestArchivosEspeciales(unittest.TestCase):
    def _escribir_temporal(self, contenido):
        with tempfile.NamedTemporaryFile(
            "w", suffix=".txt", delete=False, encoding="utf-8"
        ) as fh:
            fh.write(contenido)
            return fh.name

    def test_archivo_vacio(self):
        path = self._escribir_temporal("")
        try:
            text = read_text(path)
            self.assertEqual(len(tokenize(text)), 0)
            self.assertEqual(count_words(text), {})
            self.assertEqual(top_words(text, top=10), [])
        finally:
            os.unlink(path)

    def test_archivo_solo_espacios(self):
        path = self._escribir_temporal("   \n\t  \n\n   \t ")
        try:
            text = read_text(path)
            self.assertEqual(len(tokenize(text)), 0)
            self.assertEqual(count_words(text), {})
            self.assertEqual(top_words(text, top=10), [])
        finally:
            os.unlink(path)

    def test_palabras_repetidas(self):
        path = self._escribir_temporal("sol luna sol estrella sol luna")
        try:
            text = read_text(path)
            c = count_words(text)
            self.assertEqual(c["sol"], 3)
            self.assertEqual(c["luna"], 2)
            self.assertEqual(c["estrella"], 1)
            self.assertEqual(
                top_words(text, top=3),
                [("sol", 3), ("luna", 2), ("estrella", 1)],
            )
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
