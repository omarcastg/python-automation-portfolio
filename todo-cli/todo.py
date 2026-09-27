#!/usr/bin/env python3
"""todo-cli: gestor simple de tareas pendientes con persistencia en JSON.

Operaciones:
    add <texto>      Anade una tarea nueva.
    list             Lista todas las tareas.
    done <id>        Marca una tarea como completada.
    rm <id>          Borra una tarea.
"""

import argparse
import json
import os
import sys

DEFAULT_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.json")


def load_tasks(path=DEFAULT_DB):
    """Carga la lista de tareas desde el JSON. Devuelve [] si no existe."""
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            return []
        return data
    except (json.JSONDecodeError, OSError):
        return []


def save_tasks(tasks, path=DEFAULT_DB):
    """Guarda la lista de tareas en el JSON."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


def _next_id(tasks):
    """Devuelve el siguiente id disponible (max + 1)."""
    if not tasks:
        return 1
    return max(t.get("id", 0) for t in tasks) + 1


def add_task(text, path=DEFAULT_DB):
    """Anade una tarea y devuelve el dict creado."""
    tasks = load_tasks(path)
    task = {"id": _next_id(tasks), "text": text, "done": False}
    tasks.append(task)
    save_tasks(tasks, path)
    return task


def list_tasks(path=DEFAULT_DB):
    """Devuelve la lista de tareas."""
    return load_tasks(path)


def complete_task(task_id, path=DEFAULT_DB):
    """Marca como completada la tarea con ese id. True si existia."""
    tasks = load_tasks(path)
    found = False
    for t in tasks:
        if t.get("id") == task_id:
            t["done"] = True
            found = True
            break
    if found:
        save_tasks(tasks, path)
    return found


def remove_task(task_id, path=DEFAULT_DB):
    """Borra la tarea con ese id. True si existia."""
    tasks = load_tasks(path)
    new_tasks = [t for t in tasks if t.get("id") != task_id]
    if len(new_tasks) == len(tasks):
        return False
    save_tasks(new_tasks, path)
    return True


def _format_task(t):
    mark = "[x]" if t.get("done") else "[ ]"
    return f"{mark} {t.get('id')}. {t.get('text')}"


def main(argv=None):
    parser = argparse.ArgumentParser(prog="todo", description="Gestor de tareas pendientes.")
    parser.add_argument("--db", default=DEFAULT_DB, help="Ruta del archivo JSON.")
    sub = parser.add_subparsers(dest="cmd")

    p_add = sub.add_parser("add", help="Anade una tarea.")
    p_add.add_argument("text", help="Texto de la tarea.")

    sub.add_parser("list", help="Lista las tareas.")

    p_done = sub.add_parser("done", help="Marca una tarea como completada.")
    p_done.add_argument("id", type=int)

    p_rm = sub.add_parser("rm", help="Borra una tarea.")
    p_rm.add_argument("id", type=int)

    args = parser.parse_args(argv)

    if args.cmd == "add":
        t = add_task(args.text, args.db)
        print(f"Anadida tarea {t['id']}: {t['text']}")
    elif args.cmd == "list":
        tasks = list_tasks(args.db)
        if not tasks:
            print("No hay tareas.")
        for t in tasks:
            print(_format_task(t))
    elif args.cmd == "done":
        if complete_task(args.id, args.db):
            print(f"Tarea {args.id} completada.")
        else:
            print(f"No existe la tarea {args.id}.")
            return 1
    elif args.cmd == "rm":
        if remove_task(args.id, args.db):
            print(f"Tarea {args.id} borrada.")
        else:
            print(f"No existe la tarea {args.id}.")
            return 1
    else:
        parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
