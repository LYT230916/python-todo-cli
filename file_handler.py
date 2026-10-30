import json
from pathlib import Path


def _is_valid_task(task):
    required_fields = ("id", "title", "description", "priority", "category", "due_date", "completed")
    return (
        isinstance(task, dict)
        and all(field in task for field in required_fields)
        and isinstance(task["id"], int)
    )


def load_tasks(path="tasks.json"):
    file_path = Path(path)
    if not file_path.exists():
        file_path.write_text("[]", encoding="utf-8")
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            tasks = json.load(file)
    except (json.JSONDecodeError, OSError) as error:
        print(f"Warning: could not read {path} ({error}). Starting with an empty task list.")
        return []

    if not isinstance(tasks, list):
        print(f"Warning: {path} does not contain a task list. Starting with an empty task list.")
        return []

    valid_tasks = [task for task in tasks if _is_valid_task(task)]
    if len(valid_tasks) != len(tasks):
        print(f"Warning: ignored invalid task entries in {path}.")

    return valid_tasks


def save_tasks(tasks, path="tasks.json"):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(tasks, file, indent=4)
        file.write("\n")
