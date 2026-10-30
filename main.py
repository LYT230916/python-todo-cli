from datetime import datetime

from file_handler import load_tasks, save_tasks
import todo

DATA_FILE = "tasks.json"
PRIORITIES = ["High", "Medium", "Low"]
CATEGORIES = ["DSA", "Python", "SQL", "Web Development", "College", "Job", "Personal", "Other"]


def print_menu():
    print("=" * 40)
    print("          PYTHON TO-DO MANAGER")
    print("=" * 40)
    print()
    print("1. Add Task")
    print("2. View All Tasks")
    print("3. View Pending Tasks")
    print("4. View Completed Tasks")
    print("5. Search Tasks")
    print("6. Mark Task as Completed")
    print("7. Update Task")
    print("8. Delete Task")
    print("9. Task Statistics")
    print("0. Exit")


def print_task(task):
    status = "Completed" if task["completed"] else "Pending"
    description = task["description"] if task["description"] else "No description"
    due_date = task["due_date"] if task["due_date"] else "Not set"
    print("-" * 50)
    print(f"{task['id']}. {task['title']}")
    print(f"   Status     : {status}")
    print(f"   Priority   : {task['priority']}")
    print(f"   Category   : {task['category']}")
    print(f"   Due date   : {due_date}")
    print(f"   Description: {description}")
    print("-" * 50)


def print_tasks(tasks, heading=""):
    if heading:
        print(f"\n{heading}")
    if not tasks:
        print("No tasks found.")
        return
    for task in tasks:
        print_task(task)


def get_non_empty(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty.")


def get_task_id():
    while True:
        value = input("Enter task ID: ").strip()
        if value.isdigit():
            return int(value)
        print("Invalid task ID. Please enter a positive number.")


def prompt_priority(current=None):
    while True:
        value = input("Priority (High/Medium/Low): ").strip()
        if not value and current is not None:
            return current
        normalized = value.title()
        if normalized in PRIORITIES:
            return normalized
        print(f"Invalid priority. Allowed values: {', '.join(PRIORITIES)}")


def prompt_category(current=None):
    while True:
        print("Categories:")
        for index, category in enumerate(CATEGORIES, start=1):
            print(f"  {index}. {category}")
        choice = input("Choose a category number: ").strip()
        if not choice and current is not None:
            return current
        if choice.isdigit() and 1 <= int(choice) <= len(CATEGORIES):
            return CATEGORIES[int(choice) - 1]
        print("Invalid category choice.")


def prompt_due_date(current=None):
    while True:
        value = input("Due date (YYYY-MM-DD): ").strip()
        if not value:
            return current if current is not None else ""
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError:
            print("Invalid date. Expected format: YYYY-MM-DD")


def handle_add(tasks):
    print("\n--- Add New Task ---")
    title = get_non_empty("Title: ")
    description = input("Description: ").strip()
    priority = prompt_priority()
    category = prompt_category()
    due_date = prompt_due_date()
    task = todo.add_task(tasks, title, description, priority, category, due_date)
    save_tasks(tasks, DATA_FILE)
    print(f"Task added with ID {task['id']}.")


def handle_view_all(tasks):
    print_tasks(tasks, "All Tasks:")


def handle_view_pending(tasks):
    print_tasks(todo.filter_tasks(tasks, False), "Pending Tasks:")


def handle_view_completed(tasks):
    print_tasks(todo.filter_tasks(tasks, True), "Completed Tasks:")


def handle_search(tasks):
    query = get_non_empty("Search: ")
    results = todo.search_tasks(tasks, query)
    print_tasks(results, f'Search results for "{query}":')


def handle_complete(tasks):
    task_id = get_task_id()
    task = todo.find_task(tasks, task_id)
    if task is None:
        print(f"No task found with ID {task_id}.")
        return
    if task["completed"]:
        print("Task is already completed.")
        return
    todo.complete_task(tasks, task_id)
    save_tasks(tasks, DATA_FILE)
    print("Task marked as completed.")


def handle_update(tasks):
    task_id = get_task_id()
    task = todo.find_task(tasks, task_id)
    if task is None:
        print(f"No task found with ID {task_id}.")
        return
    print("\nCurrent details:")
    print_task(task)
    print("\nPress Enter to keep the current value.")
    updates = {}
    title = input(f"Title ({task['title']}): ").strip()
    if title:
        updates["title"] = title
    description = input(f"Description ({task['description']}): ").strip()
    if description:
        updates["description"] = description
    priority = prompt_priority(task["priority"])
    if priority != task["priority"]:
        updates["priority"] = priority
    category = prompt_category(task["category"])
    if category != task["category"]:
        updates["category"] = category
    due_date = prompt_due_date(task["due_date"])
    if due_date != task["due_date"]:
        updates["due_date"] = due_date
    if not updates:
        print("No changes made.")
        return
    todo.update_task(tasks, task_id, updates)
    save_tasks(tasks, DATA_FILE)
    print("Task updated.")


def handle_delete(tasks):
    task_id = get_task_id()
    task = todo.find_task(tasks, task_id)
    if task is None:
        print(f"No task found with ID {task_id}.")
        return
    print("\nTask to delete:")
    print_task(task)
    confirmation = input("Are you sure you want to delete this task? (y/n): ").strip().lower()
    if confirmation in ("y", "yes"):
        todo.delete_task(tasks, task_id)
        save_tasks(tasks, DATA_FILE)
        print("Task deleted.")
    else:
        print("Deletion cancelled.")


def handle_statistics(tasks):
    stats = todo.get_statistics(tasks)
    print("\n--- Task Statistics ---")
    print(f"Total Tasks: {stats['total']}")
    print(f"Completed:   {stats['completed']}")
    print(f"Pending:     {stats['pending']}")


HANDLERS = {
    "1": handle_add,
    "2": handle_view_all,
    "3": handle_view_pending,
    "4": handle_view_completed,
    "5": handle_search,
    "6": handle_complete,
    "7": handle_update,
    "8": handle_delete,
    "9": handle_statistics,
}


def main():
    tasks = load_tasks(DATA_FILE)
    while True:
        print_menu()
        choice = input("\nEnter your choice: ").strip()
        if choice == "0":
            break
        if choice not in HANDLERS:
            print("Invalid choice. Please select a number from the menu.")
            continue
        HANDLERS[choice](tasks)
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
