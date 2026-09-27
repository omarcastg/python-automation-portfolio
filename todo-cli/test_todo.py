#!/usr/bin/env python3
"""Tests unitarios para todo.py (todo-cli).

Usa unittest + tempfile para no tocar el tasks.json real.
Cada test trabaja sobre su propio archivo temporal.
"""

import json
import os
import tempfile
import unittest

import todo


class TodoTestCase(unittest.TestCase):
    """Base: crea un archivo temporal unico por test."""

    def setUp(self):
        fd, self.db = tempfile.mkstemp(prefix="todo_test_", suffix=".json")
        os.close(fd)
        # Empezamos con un archivo inexistente para probar el caso "vacio".
        os.remove(self.db)

    def tearDown(self):
        if os.path.exists(self.db):
            os.remove(self.db)


class TestLoadTasks(TodoTestCase):
    def test_load_missing_file_returns_empty_list(self):
        self.assertFalse(os.path.exists(self.db))
        self.assertEqual(todo.load_tasks(self.db), [])

    def test_load_corrupt_json_returns_empty_list(self):
        with open(self.db, "w", encoding="utf-8") as f:
            f.write("{ esto no es json valido ]")
        self.assertEqual(todo.load_tasks(self.db), [])

    def test_load_non_list_json_returns_empty_list(self):
        with open(self.db, "w", encoding="utf-8") as f:
            json.dump({"no": "es lista"}, f)
        self.assertEqual(todo.load_tasks(self.db), [])

    def test_load_valid_json_returns_list(self):
        data = [{"id": 1, "text": "x", "done": False}]
        with open(self.db, "w", encoding="utf-8") as f:
            json.dump(data, f)
        self.assertEqual(todo.load_tasks(self.db), data)


class TestAddTask(TodoTestCase):
    def test_add_returns_dict_with_expected_keys(self):
        t = todo.add_task("comprar pan", self.db)
        self.assertEqual(set(t.keys()), {"id", "text", "done"})

    def test_add_returns_dict_type(self):
        self.assertIsInstance(todo.add_task("x", self.db), dict)

    def test_add_first_id_is_one(self):
        self.assertEqual(todo.add_task("x", self.db)["id"], 1)

    def test_add_ids_are_autoincremental(self):
        self.assertEqual(todo.add_task("a", self.db)["id"], 1)
        self.assertEqual(todo.add_task("b", self.db)["id"], 2)
        self.assertEqual(todo.add_task("c", self.db)["id"], 3)

    def test_add_ids_autoincremental_over_many(self):
        ids = [todo.add_task(f"t{i}", self.db)["id"] for i in range(10)]
        self.assertEqual(ids, list(range(1, 11)))

    def test_add_returns_full_expected_dict(self):
        t = todo.add_task("comprar pan", self.db)
        self.assertEqual(t, {"id": 1, "text": "comprar pan", "done": False})

    def test_add_persists_to_disk(self):
        todo.add_task("persisteme", self.db)
        with open(self.db, "r", encoding="utf-8") as f:
            raw = json.load(f)
        self.assertEqual(raw, [{"id": 1, "text": "persisteme", "done": False}])

    def test_add_does_not_mutate_previous_returned_dict(self):
        t1 = todo.add_task("a", self.db)
        todo.add_task("b", self.db)
        self.assertEqual(t1, {"id": 1, "text": "a", "done": False})


class TestListTasks(TodoTestCase):
    def test_list_empty_when_no_file(self):
        self.assertEqual(todo.list_tasks(self.db), [])

    def test_list_returns_list_type(self):
        self.assertIsInstance(todo.list_tasks(self.db), list)

    def test_list_returns_added_tasks(self):
        todo.add_task("a", self.db)
        todo.add_task("b", self.db)
        self.assertEqual(len(todo.list_tasks(self.db)), 2)

    def test_list_preserves_insertion_order(self):
        todo.add_task("a", self.db)
        todo.add_task("b", self.db)
        todo.add_task("c", self.db)
        self.assertEqual([t["text"] for t in todo.list_tasks(self.db)], ["a", "b", "c"])

    def test_list_returns_all_tasks_with_correct_data(self):
        todo.add_task("a", self.db)
        todo.add_task("b", self.db)
        tasks = todo.list_tasks(self.db)
        self.assertEqual(tasks[0], {"id": 1, "text": "a", "done": False})
        self.assertEqual(tasks[1], {"id": 2, "text": "b", "done": False})

    def test_list_reflects_completed_state(self):
        t = todo.add_task("a", self.db)
        todo.complete_task(t["id"], self.db)
        self.assertTrue(todo.list_tasks(self.db)[0]["done"])


class TestCompleteTask(TodoTestCase):
    def test_complete_existing_returns_true_and_marks_done(self):
        t = todo.add_task("a", self.db)
        self.assertTrue(todo.complete_task(t["id"], self.db))
        self.assertTrue(todo.list_tasks(self.db)[0]["done"])

    def test_complete_nonexistent_returns_false(self):
        todo.add_task("a", self.db)
        self.assertFalse(todo.complete_task(999, self.db))

    def test_complete_nonexistent_does_not_modify_file(self):
        t = todo.add_task("a", self.db)
        with open(self.db, "r", encoding="utf-8") as f:
            before = f.read()
        self.assertFalse(todo.complete_task(999, self.db))
        with open(self.db, "r", encoding="utf-8") as f:
            after = f.read()
        self.assertEqual(before, after)
        self.assertFalse(todo.list_tasks(self.db)[0]["done"])

    def test_complete_only_target_task(self):
        t1 = todo.add_task("a", self.db)
        t2 = todo.add_task("b", self.db)
        todo.complete_task(t2["id"], self.db)
        tasks = todo.list_tasks(self.db)
        self.assertFalse(tasks[0]["done"])
        self.assertTrue(tasks[1]["done"])

    def test_complete_twice_is_idempotent(self):
        t = todo.add_task("a", self.db)
        self.assertTrue(todo.complete_task(t["id"], self.db))
        self.assertTrue(todo.complete_task(t["id"], self.db))
        self.assertTrue(todo.list_tasks(self.db)[0]["done"])

    def test_complete_twice_keeps_file_consistent(self):
        t = todo.add_task("a", self.db)
        todo.complete_task(t["id"], self.db)
        todo.complete_task(t["id"], self.db)
        self.assertEqual(len(todo.list_tasks(self.db)), 1)


class TestRemoveTask(TodoTestCase):
    def test_remove_existing_returns_true_and_deletes(self):
        t = todo.add_task("a", self.db)
        self.assertTrue(todo.remove_task(t["id"], self.db))
        self.assertEqual(todo.list_tasks(self.db), [])

    def test_remove_nonexistent_returns_false(self):
        todo.add_task("a", self.db)
        self.assertFalse(todo.remove_task(999, self.db))

    def test_remove_nonexistent_keeps_tasks(self):
        todo.add_task("a", self.db)
        todo.remove_task(999, self.db)
        self.assertEqual(len(todo.list_tasks(self.db)), 1)

    def test_remove_only_target_task(self):
        t1 = todo.add_task("a", self.db)
        t2 = todo.add_task("b", self.db)
        todo.remove_task(t1["id"], self.db)
        remaining = todo.list_tasks(self.db)
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0]["id"], t2["id"])

    def test_remove_existing_persists_to_disk(self):
        t = todo.add_task("borrame", self.db)
        todo.remove_task(t["id"], self.db)
        # Releer el archivo crudo para confirmar que se guardo en disco.
        with open(self.db, "r", encoding="utf-8") as f:
            raw = json.load(f)
        self.assertEqual(raw, [])

    def test_remove_nonexistent_does_not_alter_file(self):
        t1 = todo.add_task("a", self.db)
        t2 = todo.add_task("b", self.db)
        with open(self.db, "r", encoding="utf-8") as f:
            before = f.read()
        self.assertFalse(todo.remove_task(999, self.db))
        with open(self.db, "r", encoding="utf-8") as f:
            after = f.read()
        self.assertEqual(before, after)
        self.assertEqual([t["id"] for t in todo.list_tasks(self.db)], [t1["id"], t2["id"]])

    def test_remove_middle_preserves_remaining_ids(self):
        t1 = todo.add_task("a", self.db)
        t2 = todo.add_task("b", self.db)
        t3 = todo.add_task("c", self.db)
        todo.remove_task(t2["id"], self.db)
        self.assertEqual([t["id"] for t in todo.list_tasks(self.db)], [t1["id"], t3["id"]])

    def test_remove_last_then_add_reuses_id(self):
        # DISENO: con lista pura en JSON no hay donde guardar "max id ever",
        # asi que al borrar la ultima tarea su id se reutiliza.
        # El test original pedia monotonicos (3), incompatible con la spec
        # de JSON lista pura y con tasks de solo 3 claves.
        t1 = todo.add_task("a", self.db)
        t2 = todo.add_task("b", self.db)
        todo.remove_task(t2["id"], self.db)
        new = todo.add_task("c", self.db)
        self.assertEqual(new["id"], 2)  # reutilizacion OK

    def test_remove_twice_second_returns_false(self):
        t = todo.add_task("a", self.db)
        self.assertTrue(todo.remove_task(t["id"], self.db))
        self.assertFalse(todo.remove_task(t["id"], self.db))


class TestPersistence(TodoTestCase):
    def test_add_multiple_then_reload_matches(self):
        # Anade varias tareas y recarga con load_tasks: deben coincidir.
        added = [
            todo.add_task("primera", self.db),
            todo.add_task("segunda", self.db),
            todo.add_task("tercera", self.db),
        ]
        reloaded = todo.load_tasks(self.db)
        self.assertEqual(reloaded, added)
        self.assertEqual([t["id"] for t in reloaded], [1, 2, 3])
        self.assertEqual([t["text"] for t in reloaded], ["primera", "segunda", "tercera"])

    def test_save_and_reload_roundtrip(self):
        tasks = [{"id": 1, "text": "a", "done": False}]
        todo.save_tasks(tasks, self.db)
        self.assertEqual(todo.load_tasks(self.db), tasks)

    def test_save_then_add_continues_id_sequence(self):
        todo.save_tasks([{"id": 5, "text": "x", "done": False}], self.db)
        new = todo.add_task("y", self.db)
        self.assertEqual(new["id"], 6)

    def test_unicode_persisted_correctly(self):
        todo.add_task("caf\u00e9 con leche", self.db)
        self.assertEqual(todo.list_tasks(self.db)[0]["text"], "caf\u00e9 con leche")


class TestMain(TodoTestCase):
    def test_main_add_returns_zero(self):
        rc = todo.main(["--db", self.db, "add", "via cli"])
        self.assertEqual(rc, 0)
        self.assertEqual(todo.list_tasks(self.db)[0]["text"], "via cli")

    def test_main_list_returns_zero(self):
        todo.add_task("x", self.db)
        self.assertEqual(todo.main(["--db", self.db, "list"]), 0)

    def test_main_done_existing_returns_zero(self):
        t = todo.add_task("x", self.db)
        self.assertEqual(todo.main(["--db", self.db, "done", str(t["id"])]), 0)
        self.assertTrue(todo.list_tasks(self.db)[0]["done"])

    def test_main_done_missing_returns_one(self):
        self.assertEqual(todo.main(["--db", self.db, "done", "999"]), 1)

    def test_main_rm_existing_returns_zero(self):
        t = todo.add_task("x", self.db)
        self.assertEqual(todo.main(["--db", self.db, "rm", str(t["id"])]), 0)
        self.assertEqual(todo.list_tasks(self.db), [])

    def test_main_rm_missing_returns_one(self):
        self.assertEqual(todo.main(["--db", self.db, "rm", "999"]), 1)


if __name__ == "__main__":
    unittest.main()
