# csv2json

## Descripción

`csv2json.py` convierte un archivo **CSV** con columnas `nombre, edad, ciudad` a un archivo
**JSON** indentado. Cada fila válida del CSV se transforma en un objeto JSON cuyas claves son
los nombres de columna y cuyos valores son cadenas de texto (los valores no se convierten a
números).

## Requisitos

- Python 3.8 o superior.
- Solo biblioteca estándar (no requiere dependencias externas).

## Uso

```bash
python3 csv2json.py entrada.csv salida.json
```

Flags opcionales:

- `--no-header`: fuerza a tratar el CSV como **sin** cabecera.
- `--header`: fuerza a tratar el CSV como **con** cabecera.

```bash
# Forzar que el CSV no tiene cabecera
python3 csv2json.py entrada.csv salida.json --no-header

# Forzar que el CSV sí tiene cabecera
python3 csv2json.py entrada.csv salida.json --header
```

## Ejemplo

### CSV de entrada (`entrada.csv`)

```csv
nombre,edad,ciudad
Ana,30,Madrid
Luis,25,Bogota
```

### JSON de salida (`salida.json`)

```json
[
  {
    "nombre": "Ana",
    "edad": "30",
    "ciudad": "Madrid"
  },
  {
    "nombre": "Luis",
    "edad": "25",
    "ciudad": "Bogota"
  }
]
```

## Comportamiento

- **Autodetección de cabecera**: si no se pasa `--header` ni `--no-header`, se inspecciona la
  primera fila. Si alguna de sus celdas coincide con un nombre conocido
  (`nombre`, `name`, `edad`, `age`, `ciudad`, `city`), se considera que hay cabecera y se usa
  como claves del JSON (en minúsculas). En caso contrario, se asume que no hay cabecera y se
  usan las claves por defecto `nombre`, `edad`, `ciudad`.
- **Filas malformadas ignoradas**: una fila se considera válida solo si tiene exactamente
  3 campos y ninguno está vacío. Las filas inválidas se descartan y se cuentan.
- **Conteo reportado**: al finalizar, el script imprime un resumen, por ejemplo:

  ```text
  OK: 2 registros escritos, 1 filas ignoradas de 3.
  ```

- **Formato de salida**: JSON con indentación de 2 espacios, codificación UTF-8 y caracteres
  no ASCII preservados (`ensure_ascii=False`). Se crea el directorio de salida si no existe.

## Tests

```bash
python3 -m unittest test_csv2json -v
```

## Estructura de archivos

```text
csv2json/
├── csv2json.py       # Script principal (conversión CSV -> JSON)
├── test_csv2json.py  # Pruebas unitarias
└── README.md         # Este documento
```
