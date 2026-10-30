const state = { tasks: [], filter: "all", query: "" };
const $ = (selector) => document.querySelector(selector);
const list = $("#task-list");
const dialog = $("#task-dialog");
const form = $("#task-form");

const esc = (value = "") => String(value).replace(/[&<>"']/g, (char) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
}[char]));

function dateLabel(value) {
  if (!value) return "无截止日期";
  const date = new Date(`${value}T00:00:00`);
  return new Intl.DateTimeFormat("zh-CN", { month: "long", day: "numeric" }).format(date);
}

function render() {
  const total = state.tasks.length;
  const completed = state.tasks.filter((task) => task.completed).length;
  const pending = total - completed;
  $("#stat-total").textContent = total;
  $("#stat-pending").textContent = pending;
  $("#stat-completed").textContent = completed;
  $("#nav-total").textContent = total;

  const names = { all: "所有任务", pending: "待完成", completed: "已完成" };
  $("#page-title").textContent = names[state.filter];
  $("#crumb").textContent = names[state.filter];
  $("#page-subtitle").textContent = state.filter === "completed" ? "回顾你已经完成的每一步。" : "把重要的事，一件一件做好。";
  document.querySelectorAll("[data-filter]").forEach((button) => {
    button.classList.toggle("active", button.dataset.filter === state.filter);
  });

  const visible = state.tasks.filter((task) => {
    const matchesStatus = state.filter === "all" || task.completed === (state.filter === "completed");
    const text = `${task.title} ${task.description} ${task.category}`.toLocaleLowerCase();
    return matchesStatus && text.includes(state.query.toLocaleLowerCase());
  });
  if (!visible.length) {
    const searched = Boolean(state.query);
    list.innerHTML = `<div class="empty-state"><div class="empty-illustration">${searched ? "⌕" : "✳"}</div><h3>${searched ? "没有找到匹配任务" : "这里还很清静"}</h3><p>${searched ? "试试其他关键词。" : "新建一项任务，让今天有个开始。"}</p>${!searched && state.filter !== "completed" ? '<button class="primary-btn" data-empty-add>＋ 新建任务</button>' : ""}</div>`;
    const add = $("[data-empty-add]");
    if (add) add.addEventListener("click", () => openDialog());
    return;
  }
  list.innerHTML = visible.map((task) => `
    <article class="task-row ${task.completed ? "is-complete" : ""}" data-task="${task.id}">
      <button class="check ${task.completed ? "checked" : ""}" data-action="toggle" aria-label="${task.completed ? "标记为待完成" : "标记完成"}">${task.completed ? "✓" : ""}</button>
      <div class="task-main"><div class="task-title">${esc(task.title)}</div><div class="task-description">${esc(task.description || "暂无描述")}</div><div class="task-meta"><span class="category-tag">${esc(task.category)}</span><span class="priority ${task.priority.toLowerCase()}"><i></i>${task.priority === "High" ? "高优先级" : task.priority === "Low" ? "低优先级" : "中优先级"}</span><span class="due-date">◷ ${dateLabel(task.due_date)}</span></div></div>
      <div class="task-actions"><button data-action="edit" aria-label="编辑任务" title="编辑">✎</button><button data-action="delete" aria-label="删除任务" title="删除">⌫</button></div>
    </article>`).join("");
}

async function api(url, options = {}) {
  const response = await fetch(url, { ...options, headers: { "Content-Type": "application/json", ...(options.headers || {}) } });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "操作失败，请重试。");
  return data;
}

async function refresh() {
  try {
    const data = await api("/api/tasks");
    state.tasks = data.tasks;
    render();
  } catch (error) {
    list.innerHTML = `<div class="error-state">加载失败：${esc(error.message)}<br><small>请确认本机服务仍在运行，然后刷新页面。</small></div>`;
  }
}

function openDialog(task = null) {
  form.reset();
  $("#form-error").textContent = "";
  $("#task-id").value = task?.id || "";
  $("#dialog-title").textContent = task ? "编辑任务" : "新建任务";
  $("#title").value = task?.title || "";
  $("#description").value = task?.description || "";
  $("#priority").value = task?.priority || "Medium";
  $("#category").value = task?.category || "Personal";
  $("#due-date").value = task?.due_date || "";
  dialog.showModal();
  $("#title").focus();
}

function toast(message) {
  const el = $("#toast");
  el.textContent = message;
  el.classList.add("visible");
  setTimeout(() => el.classList.remove("visible"), 2200);
}

document.querySelectorAll("[data-filter]").forEach((button) => button.addEventListener("click", () => {
  state.filter = button.dataset.filter;
  render();
}));
$("#search").addEventListener("input", (event) => { state.query = event.target.value.trim(); render(); });
$("#add-open").addEventListener("click", () => openDialog());
$("#dialog-close").addEventListener("click", () => dialog.close());
$("#cancel").addEventListener("click", () => dialog.close());
dialog.addEventListener("click", (event) => { if (event.target === dialog) dialog.close(); });

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const id = $("#task-id").value;
  const payload = {
    title: $("#title").value.trim(), description: $("#description").value.trim(),
    priority: $("#priority").value, category: $("#category").value, due_date: $("#due-date").value
  };
  try {
    await api(id ? `/api/${id}` : "/api/tasks", { method: id ? "PATCH" : "POST", body: JSON.stringify(payload) });
    dialog.close();
    await refresh();
    toast(id ? "任务已更新" : "任务已创建");
  } catch (error) { $("#form-error").textContent = error.message; }
});

list.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-action]");
  if (!button) return;
  const row = button.closest("[data-task]");
  const task = state.tasks.find((item) => item.id === Number(row.dataset.task));
  if (!task) return;
  try {
    if (button.dataset.action === "toggle") {
      await api(`/api/${task.id}`, { method: "PATCH", body: JSON.stringify({ completed: !task.completed }) });
      toast(task.completed ? "已移回待完成" : "做得好，任务已完成");
    } else if (button.dataset.action === "edit") {
      openDialog(task);
      return;
    } else if (button.dataset.action === "delete") {
      if (!window.confirm(`确定删除“${task.title}”吗？`)) return;
      await api(`/api/${task.id}`, { method: "DELETE" });
      toast("任务已删除");
    }
    await refresh();
  } catch (error) { toast(error.message); }
});

$("#today").textContent = new Intl.DateTimeFormat("zh-CN", { weekday: "long", month: "long", day: "numeric" }).format(new Date());
refresh();
