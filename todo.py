def get_next_id(tasks):
    return max((task["id"] for task in tasks), default=0) + 1


def add_task(tasks, title, description, priority, category, due_date):
    task = {
        "id": get_next_id(tasks),
        "title": title,
        "description": description,
        "priority": priority,
        "category": category,
        "due_date": due_date,
        "completed": False,
    }
    tasks.append(task)
    return task


def find_task(tasks, task_id):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None


def update_task(tasks, task_id, updates):
    task = find_task(tasks, task_id)
    if task is None:
        return None
    task.update(updates)
    return task


def complete_task(tasks, task_id):
    task = find_task(tasks, task_id)
    if task is None:
        return None
    task["completed"] = True
    return task


def delete_task(tasks, task_id):
    task = find_task(tasks, task_id)
    if task is None:
        return False
    tasks.remove(task)
    return True


def search_tasks(tasks, query):
    query = query.lower()
    return [
        task
        for task in tasks
        if query in task["title"].lower()
        or query in task["description"].lower()
        or query in task["category"].lower()
    ]


def filter_tasks(tasks, completed):
    return [task for task in tasks if task["completed"] == completed]


def get_statistics(tasks):
    completed = sum(task["completed"] for task in tasks)
    return {"total": len(tasks), "completed": completed, "pending": len(tasks) - completed}
