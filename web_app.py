"""Small standard-library web interface for the to-do list."""

import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import RLock
from urllib.parse import urlparse

import todo
from file_handler import load_tasks, save_tasks

ROOT = Path(__file__).resolve().parent
WEB_ROOT = ROOT / "web"
DATA_FILE = ROOT / "tasks.json"
PORT = 8765
PRIORITIES = {"High", "Medium", "Low"}
CATEGORIES = {"DSA", "Python", "SQL", "Web Development", "College", "Job", "Personal", "Other"}
LOCK = RLock()


class TodoHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_ROOT), **kwargs)

    def _json(self, value, status=200):
        payload = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def _body(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length > 1_000_000:
            raise ValueError("Request body is too large.")
        return json.loads(self.rfile.read(length) or b"{}")

    def _task_id(self):
        parts = urlparse(self.path).path.strip("/").split("/")
        if len(parts) != 2 or parts[0] != "api" or not parts[1].isdigit():
            return None
        return int(parts[1])

    def do_GET(self):
        if urlparse(self.path).path == "/api/tasks":
            with LOCK:
                self._json({"tasks": load_tasks(DATA_FILE), "stats": todo.get_statistics(load_tasks(DATA_FILE))})
            return
        if urlparse(self.path).path.startswith("/api/"):
            self._json({"error": "Not found."}, 404)
            return
        if urlparse(self.path).path == "/":
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self):
        if urlparse(self.path).path != "/api/tasks":
            self._json({"error": "Not found."}, 404)
            return
        try:
            data = self._body()
            title = str(data.get("title", "")).strip()
            priority = data.get("priority", "Medium")
            category = data.get("category", "Personal")
            due_date = str(data.get("due_date", ""))
            if not title:
                raise ValueError("Task title is required.")
            if priority not in PRIORITIES or category not in CATEGORIES:
                raise ValueError("Choose a valid priority and category.")
            if due_date:
                from datetime import date
                date.fromisoformat(due_date)
            with LOCK:
                tasks = load_tasks(DATA_FILE)
                task = todo.add_task(tasks, title, str(data.get("description", "")).strip(), priority,
                                     category, due_date)
                save_tasks(tasks, DATA_FILE)
            self._json(task, 201)
        except (ValueError, TypeError, json.JSONDecodeError) as error:
            self._json({"error": str(error)}, 400)

    def do_PATCH(self):
        task_id = self._task_id()
        if task_id is None:
            self._json({"error": "Not found."}, 404)
            return
        try:
            updates = self._body()
            allowed = {"title", "description", "priority", "category", "due_date", "completed"}
            if not isinstance(updates, dict) or not updates or set(updates) - allowed:
                raise ValueError("Invalid task update.")
            if "title" in updates:
                updates["title"] = str(updates["title"]).strip()
                if not updates["title"]:
                    raise ValueError("Task title is required.")
            if "priority" in updates and updates["priority"] not in PRIORITIES:
                raise ValueError("Choose a valid priority.")
            if "category" in updates and updates["category"] not in CATEGORIES:
                raise ValueError("Choose a valid category.")
            if "due_date" in updates and updates["due_date"]:
                from datetime import date
                date.fromisoformat(updates["due_date"])
            with LOCK:
                tasks = load_tasks(DATA_FILE)
                task = todo.update_task(tasks, task_id, updates)
                if task is None:
                    self._json({"error": "Task not found."}, 404)
                    return
                save_tasks(tasks, DATA_FILE)
            self._json(task)
        except (ValueError, TypeError, json.JSONDecodeError) as error:
            self._json({"error": str(error)}, 400)

    def do_DELETE(self):
        task_id = self._task_id()
        if task_id is None:
            self._json({"error": "Not found."}, 404)
            return
        with LOCK:
            tasks = load_tasks(DATA_FILE)
            if not todo.delete_task(tasks, task_id):
                self._json({"error": "Task not found."}, 404)
                return
            save_tasks(tasks, DATA_FILE)
        self._json({"ok": True})

    def log_message(self, fmt, *args):
        print("[%s] %s" % (self.log_date_time_string(), fmt % args))


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", PORT), TodoHandler)
    print(f"To-do web app running at http://127.0.0.1:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()
