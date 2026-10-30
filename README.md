# Python To-Do List CLI

A simple command-line to-do list application built with Python that stores tasks permanently in a JSON file. It demonstrates core Python fundamentals: file handling, JSON serialization, CRUD operations, input validation, and building an interactive CLI.

## Features

- Add a task with title, description, priority, category, and due date
- View all, pending, or completed tasks
- Search tasks by title, description, or category (case-insensitive)
- Mark a task as completed
- Update any field of an existing task
- Delete a task with confirmation
- View simple task statistics
- Permanent storage in `tasks.json`

## Technologies Used

- Python 3
- Python Standard Library only (`json`, `pathlib`, `datetime`)
- JSON file for persistent storage

No third-party packages, databases, or external services are used.

## Project Structure

```text
todo-cli/
├── main.py          # Application startup, menu, and user input
├── todo.py          # Task logic: add, update, delete, complete, search, statistics
├── file_handler.py  # Reading from and writing to tasks.json
├── tasks.json       # Data file (created automatically if missing)
├── README.md
└── requirements.txt
```

## How to Run

```bash
python main.py
```

## Run the local web app

Start the browser interface with Python:

```bash
python web_app.py
```

Then open <http://127.0.0.1:8765>. The web app uses the same `tasks.json` file as the CLI and requires no third-party packages. Stop the local server with Ctrl+C.

Requires Python 3.6 or later. No installation or dependencies needed.

## Example Usage

```text
========================================
           PYTHON TO-DO MANAGER
========================================

1. Add Task
2. View All Tasks
3. View Pending Tasks
4. View Completed Tasks
5. Search Tasks
6. Mark Task as Completed
7. Update Task
8. Delete Task
9. Task Statistics
0. Exit

Enter your choice: 1

--- Add New Task ---
Title: Complete Python DSA
Description: Solve array problems
Priority (High/Medium/Low): High
Categories:
  1. DSA
  2. Python
  3. SQL
  4. Web Development
  5. College
  6. Job
  7. Personal
  8. Other
Choose a category number: 1
Due date (YYYY-MM-DD): 2026-08-20
Task added with ID 1.
```

## Future Improvements

- Sort tasks by priority or due date
- Show reminders for overdue tasks
- Export and import tasks as CSV
- Edit or reorder task IDs
- Add a simple graphical interface

