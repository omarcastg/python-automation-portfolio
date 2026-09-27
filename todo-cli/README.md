# todo-cli

Gestor simple de tareas pendientes desde la línea de comandos, con persistencia
en un archivo JSON. Sin dependencias externas: solo la biblioteca estándar de Python.

## Requisitos

- Python 3.8 o superior.

## Instalación / uso

No requiere instalación. Clona o copia el directorio y ejecuta `todo.py` con Python:

```bash
cd todo-cli
python3 todo.py --help
```

Las tareas se guardan por defecto en `tasks.json`, junto al script.

## Comandos

| Comando | Descripción | Ejemplo |
| --- | --- | --- |
| `add <texto>` | Añade una tarea nueva con id autoincremental. | `python3 todo.py add "Comprar pan"` |
| `list` | Lista todas las tareas con `[ ]` (pendiente) o `[x]` (hecha). | `python3 todo.py list` |
| `done <id>` | Marca como completada la tarea con ese id. | `python3 todo.py done 1` |
| `rm <id>` | Borra la tarea con ese id. | `python3 todo.py rm 1` |
| `--db <ruta>` | Opción global: usa otro archivo JSON en lugar de `tasks.json`. | `python3 todo.py --db otra.json list` |

> Nota: `--db` es una opción global y debe colocarse **antes** del subcomando
> (`add`, `list`, `done`, `rm`).

### Ejemplos

```bash
# Añadir tareas
python3 todo.py add "Comprar pan"
# Anadida tarea 1: Comprar pan

python3 todo.py add "Escribir informe"
# Anadida tarea 2: Escribir informe

# Listar
python3 todo.py list
# [ ] 1. Comprar pan
# [ ] 2. Escribir informe

# Completar la primera
python3 todo.py done 1
# Tarea 1 completada.

python3 todo.py list
# [x] 1. Comprar pan
# [ ] 2. Escribir informe

# Borrar la segunda
python3 todo.py rm 2
# Tarea 2 borrada.

# Usar otra base de datos
python3 todo.py --db /tmp/mi_lista.json add "Tarea en otro archivo"
python3 todo.py --db /tmp/mi_lista.json list
```

Si no hay tareas, `list` muestra un aviso:

```bash
python3 todo.py list
# No hay tareas.
```

Si el id indicado en `done` o `rm` no existe, el programa avisa y devuelve
código de salida `1`:

```bash
python3 todo.py done 99
# No existe la tarea 99.
```

## Formato del almacenamiento

El archivo JSON (por defecto `tasks.json`) contiene una **lista de objetos**, cada
uno con las claves `id` (entero), `text` (cadena) y `done` (booleano):

```json
[
  {
    "id": 1,
    "text": "Comprar pan",
    "done": true
  },
  {
    "id": 2,
    "text": "Escribir informe",
    "done": false
  }
]
```

- `id`: identificador único y autoincremental (se calcula como `max(id) + 1`).
- `text`: texto de la tarea.
- `done`: `true` si está completada, `false` si está pendiente.

Si el archivo no existe o está corrupto, se trata como una lista vacía.

## Tests

Ejecuta la suite de pruebas con `unittest`:

```bash
python3 -m unittest test_todo -v
```

## Notas de diseno

- Los IDs de tarea se reutilizan cuando se borra la ultima tarea. Ej: con ids 1 y 2, si borras el 2 y anades otra, sera el 2 otra vez.
