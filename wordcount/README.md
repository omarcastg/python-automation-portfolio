# wordcount

Script en Python que cuenta las palabras de un archivo de texto y muestra
las **10 más frecuentes** (configurable).

## Requisitos

- Python 3.7+ (solo librería estándar, sin dependencias).

## Uso

```bash
python3 wordcount.py archivo.txt
```

### Opciones

| Opción | Descripción | Default |
|---|---|---|
| `--top N` | Número de palabras más frecuentes a mostrar | `10` |
| `--min-length N` | Longitud mínima de palabra para contarla | `1` |

### Ejemplos

```bash
# Top 10 por defecto
python3 wordcount.py libro.txt

# Top 5
python3 wordcount.py libro.txt --top 5

# Ignorar palabras de menos de 4 letras
python3 wordcount.py libro.txt --min-length 4
```

### Salida de ejemplo

```
Archivo: libro.txt
Total de palabras: 1234
Palabras unicas: 456

  #  PALABRA                  FREC
---------------------------------
  1  que                       87
  2  la                        76
  3  de                        65
```

## Comportamiento

- Las palabras se normalizan a **minúsculas**.
- Se soportan **acentos y ñ** (`canción`, `niño`).
- Se ignoran signos de puntuación.
- El orden es por **frecuencia descendente**; a igual frecuencia, orden **alfabético** (resultado determinista).

## Tests

Los tests unitarios usan `unittest` (solo librería estándar) y cubren:

- **Tokenización**: caso básico, normalización a minúsculas, acentos y `ñ`,
  ignorar puntuación, `--min-length` y números.
- **Conteo de palabras**: frecuencias correctas, **archivo vacío** y
  **texto con solo espacios** (sin palabras que contar).
- **Top de palabras**: orden por frecuencia, límite de `--top`,
  desempate alfabético, `--min-length` y **palabras repetidas**.
- **Lectura de archivos**: UTF-8 y archivo inexistente (`FileNotFoundError`).
- **Formato del informe**: incluye palabras y totales.
- **CLI (`main`)**: ejecución correcta y archivo inexistente (código de salida 1).

### Casos de borde cubiertos

Estos tres casos verifican que el script maneja correctamente entradas sin
contenido útil y el conteo de palabras repetidas:

- **Archivo vacío**: un archivo sin contenido produce `0` palabras, un
  diccionario de conteo vacío y una lista de top vacía.
- **Solo espacios**: un archivo con únicamente espacios, tabuladores y saltos
  de línea se trata igual que un archivo vacío (sin palabras que contar).
- **Palabras repetidas**: las frecuencias se acumulan correctamente y el top
  respeta el orden por frecuencia descendente.

Para ejecutarlos:

```bash
python3 -m unittest test_wordcount -v
```

## Estructura

```
wordcount/
├── wordcount.py        # Script principal
├── test_wordcount.py   # Tests unitarios (unittest)
└── README.md
```
