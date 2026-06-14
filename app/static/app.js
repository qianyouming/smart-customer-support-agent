// Main console script for chat, session management, document upload, and traces.
const state = {
  sessionId: localStorage.getItem("agent.sessionId") || "demo-session",
  sessions: [],
  editingSessionId: null,
};

const $ = (selector) => document.querySelector(selector);

function setSession(sessionId) {
  state.sessionId = sessionId;
  localStorage.setItem("agent.sessionId", sessionId);
  $("#sessionLabel").textContent = `session: ${sessionId}`;
}

function escapeHtml(value) {
  // User/document content is inserted into HTML in several render functions.
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function appendMessage(role, content) {
  const messages = $("#messages");
  const el = document.createElement("div");
  el.className = `message ${role}`;
  el.textContent = content;
  messages.appendChild(el);
  messages.scrollTop = messages.scrollHeight;
}

function showSidebarNotice(message) {
  const notice = $("#sidebarNotice");
  notice.textContent = message;
  notice.hidden = false;
  window.clearTimeout(showSidebarNotice.timer);
  showSidebarNotice.timer = window.setTimeout(() => {
    notice.hidden = true;
  }, 2600);
}

function hasUserMessage() {
  return Boolean(document.querySelector(".message.user"));
}

function renderMessages(messages) {
  $("#messages").innerHTML = "";
  messages.forEach((message) => appendMessage(message.role, message.content));
}

function renderHandoff(needHuman, reason) {
  // The right trace panel explains whether a human should take over.
  const target = $("#handoff");
  if (!needHuman) {
    target.className = "trace-list empty";
    target.textContent = "暂不需要人工";
    return;
  }
  target.className = "trace-list";
  target.innerHTML = `
    <div class="trace-item handoff">
      <strong>建议转人工</strong>
      <span>${escapeHtml(reason || "知识库证据不足。")}</span>
    </div>
  `;
}

function renderTools(tools) {
  // Tool traces make the Agent behavior visible during demos and debugging.
  const target = $("#toolTrace");
  $("#lastToolCount").textContent = `${tools.length} tools`;
  if (!tools.length) {
    target.className = "trace-list empty";
    target.textContent = "暂无工具调用";
    return;
  }

  target.className = "trace-list";
  target.innerHTML = tools
    .map(
      (tool) => `
        <div class="trace-item">
          <strong>${escapeHtml(tool.tool_name)}</strong>
          <span>input: ${escapeHtml(tool.tool_input)}</span><br />
          <code>${escapeHtml(tool.tool_output)}</code>
        </div>
      `,
    )
    .join("");
}

function renderCitations(citations) {
  // Citations come from retrieval output and show which chunks supported an answer.
  const target = $("#citations");
  if (!citations.length) {
    target.className = "trace-list empty";
    target.textContent = "暂无引用";
    return;
  }

  target.className = "trace-list";
  target.innerHTML = citations
    .map(
      (item) => `
        <div class="trace-item">
          <strong>${escapeHtml(item.source)}</strong>
          <span>${escapeHtml(item.snippet)}</span>
        </div>
      `,
    )
    .join("");
}

function resetTrace() {
  renderHandoff(false);
  renderTools([]);
  renderCitations([]);
}

async function checkHealth() {
  // The header status dot is a lightweight backend liveness indicator.
  try {
    const response = await fetch("/health");
    if (!response.ok) throw new Error("health check failed");
    $("#healthDot").classList.add("ok");
    $("#healthText").textContent = "online";
  } catch {
    $("#healthDot").classList.remove("ok");
    $("#healthText").textContent = "offline";
  }
}

function renderSessions() {
  // Session rows are rendered from server state so refreshes stay consistent.
  const target = $("#sessionList");
  const keyword = $("#sessionSearch").value.trim().toLowerCase();
  const sessions = state.sessions.filter((session) => {
    const haystack = `${session.title} ${session.preview || ""}`.toLowerCase();
    return haystack.includes(keyword);
  });

  if (!sessions.length) {
    target.innerHTML = `
      <div class="sidebar-empty">
        <strong>没有匹配的会话</strong>
        <span>换个关键词试试，或先在当前会话里提问。</span>
      </div>
    `;
    return;
  }

  target.innerHTML = sessions
    .map((session) => {
      const isEditing = session.session_id === state.editingSessionId;
      const preview = session.preview || "暂无预览";
      if (isEditing) {
        // Inline rename keeps the sidebar interaction close to Codex-style UX.
        return `
          <form class="session-row active editing" data-rename-form="${escapeHtml(session.session_id)}">
            <input class="session-title-input" name="title" value="${escapeHtml(session.title)}" maxlength="120" />
            <div class="session-edit-actions">
              <button type="submit">保存</button>
              <button type="button" data-cancel-rename>取消</button>
            </div>
          </form>
        `;
      }

      return `
        <div class="session-row ${session.session_id === state.sessionId ? "active" : ""}">
          <button class="session-item" data-session-id="${escapeHtml(session.session_id)}">
            <span class="session-title">${escapeHtml(session.title)}</span>
            <span class="session-meta">${session.message_count} messages · ${escapeHtml(preview)}</span>
          </button>
          <div class="session-actions">
            <button
              class="session-more"
              type="button"
              title="重命名"
              aria-label="重命名 ${escapeHtml(session.title)}"
              data-rename-id="${escapeHtml(session.session_id)}"
            >
              ...
            </button>
            <button
              class="session-delete"
              type="button"
              title="删除会话"
              aria-label="删除会话 ${escapeHtml(session.title)}"
              data-delete-id="${escapeHtml(session.session_id)}"
            >
              删
            </button>
          </div>
        </div>
      `;
    })
    .join("");

  target.querySelectorAll("[data-session-id]").forEach((button) => {
    button.addEventListener("click", () => loadSession(button.dataset.sessionId));
  });
  target.querySelectorAll("[data-rename-id]").forEach((button) => {
    button.addEventListener("click", () => startRenameSession(button.dataset.renameId));
  });
  target.querySelectorAll("[data-delete-id]").forEach((button) => {
    button.addEventListener("click", () => deleteSession(button.dataset.deleteId));
  });
  target.querySelectorAll("[data-rename-form]").forEach((form) => {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      await renameSession(form.dataset.renameForm, new FormData(form).get("title"));
    });
  });
  target.querySelectorAll("[data-cancel-rename]").forEach((button) => {
    button.addEventListener("click", () => {
      state.editingSessionId = null;
      renderSessions();
    });
  });
  const input = target.querySelector(".session-title-input");
  if (input) {
    input.focus();
    input.select();
    input.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        state.editingSessionId = null;
        renderSessions();
      }
    });
  }
}

function startRenameSession(sessionId) {
  state.editingSessionId = sessionId;
  renderSessions();
}

function sortSessions(sessions) {
  return [...sessions].sort((left, right) => {
    const leftTime = Date.parse(left.updated_at || left.created_at || "") || 0;
    const rightTime = Date.parse(right.updated_at || right.created_at || "") || 0;
    return rightTime - leftTime;
  });
}

async function loadSessions() {
  // Load summaries only; individual messages are fetched when a session opens.
  const target = $("#sessionList");
  target.innerHTML = "<div class='sidebar-empty'>加载中</div>";
  const response = await fetch("/api/sessions");
  state.sessions = sortSessions(await response.json());

  if (!state.sessions.length) {
    target.innerHTML = `
      <div class="sidebar-empty">
        <strong>还没有历史会话</strong>
        <span>发送第一条消息后，会话会自动出现在这里。</span>
      </div>
    `;
    return;
  }

  renderSessions();
}

async function renameSession(sessionId, nextTitle) {
  const title = String(nextTitle || "").trim();
  if (!title) {
    showSidebarNotice("会话名不能为空。");
    return;
  }

  const response = await fetch(`/api/sessions/${encodeURIComponent(sessionId)}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
  if (!response.ok) {
    showSidebarNotice("修改会话名失败，请稍后再试。");
    return;
  }
  state.editingSessionId = null;
  showSidebarNotice("会话名已更新。");
  await loadSessions();
}

async function deleteSession(sessionId) {
  // Deleting the active session switches to a new blank local session.
  const current = state.sessions.find((session) => session.session_id === sessionId);
  const title = current?.title || "这个会话";
  const confirmed = window.confirm(`确认删除“${title}”吗？删除后将无法恢复。`);
  if (!confirmed) return;

  const response = await fetch(`/api/sessions/${encodeURIComponent(sessionId)}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    showSidebarNotice("删除会话失败，请稍后再试。");
    return;
  }

  if (state.sessionId === sessionId) {
    setSession(`demo-${Date.now()}`);
    $("#messages").innerHTML = "";
    appendMessage("assistant", "当前会话已删除，我们已经切换到一个新的空白会话。");
    resetTrace();
  }

  state.editingSessionId = null;
  showSidebarNotice("会话已删除。");
  await loadSessions();
}

async function loadSession(sessionId) {
  setSession(sessionId);
  const response = await fetch(`/api/sessions/${encodeURIComponent(sessionId)}/messages`);
  const messages = await response.json();
  renderMessages(messages);
  resetTrace();
  await loadSessions();
}

async function loadFiles() {
  // The sidebar shows metadata; clicking opens the full document detail page.
  const target = $("#fileList");
  target.innerHTML = "<p class='trace-list empty'>加载中</p>";
  const response = await fetch("/api/files");
  const files = await response.json();

  if (!files.length) {
    target.innerHTML = "<p class='trace-list empty'>还没有上传文档</p>";
    return;
  }

  target.innerHTML = files
    .map(
      (file) => `
        <div class="file-item">
          <button class="file-open" type="button" data-open-document-id="${escapeHtml(file.document_id)}">
            <strong>${escapeHtml(file.filename)}</strong>
            <span>${file.chunks_count} chunks · 打开文档详情</span>
          </button>
          <button class="file-delete" type="button" data-document-id="${escapeHtml(file.document_id)}">删除</button>
        </div>
      `,
    )
    .join("");

  target.querySelectorAll("[data-open-document-id]").forEach((button) => {
    button.addEventListener("click", () => {
      window.location.href = `/documents/${encodeURIComponent(button.dataset.openDocumentId)}`;
    });
  });
  target.querySelectorAll("[data-document-id]").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.stopPropagation();
      deleteFile(button.dataset.documentId);
    });
  });
}

async function deleteFile(documentId) {
  const response = await fetch(`/api/files/${encodeURIComponent(documentId)}`, { method: "DELETE" });
  if (!response.ok) {
    appendMessage("assistant", "删除文档失败，请稍后再试。");
    return;
  }
  appendMessage("assistant", "文档已删除。");
  await loadFiles();
}

async function uploadFile(file) {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch("/api/files", {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "请检查文件格式。" }));
    appendMessage("assistant", `文件上传失败：${error.detail}`);
    return;
  }

  const result = await response.json();
  appendMessage("assistant", `已上传 ${result.filename}，生成 ${result.chunks_created} 个 chunk。同名文档会自动覆盖旧版本。`);
  await loadFiles();
}

async function sendMessage(message) {
  // Chat responses include answer text plus tool traces, citations, and handoff state.
  appendMessage("user", message);
  $("#sendButton").disabled = true;

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, session_id: state.sessionId }),
    });
    const result = await response.json();

    setSession(result.session_id);
    appendMessage("assistant", result.answer);
    renderHandoff(result.need_human, result.handoff_reason);
    renderTools(result.used_tools || []);
    renderCitations(result.citations || []);
    await loadSessions();
  } catch (error) {
    appendMessage("assistant", `请求失败：${error.message}`);
  } finally {
    $("#sendButton").disabled = false;
  }
}

$("#chatForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const input = $("#messageInput");
  const message = input.value.trim();
  if (!message) return;
  input.value = "";
  await sendMessage(message);
});

$("#fileInput").addEventListener("change", async (event) => {
  const [file] = event.target.files;
  if (file) await uploadFile(file);
  event.target.value = "";
});

$("#refreshFiles").addEventListener("click", async () => {
  await loadFiles();
  await loadSessions();
});

$("#refreshSessions").addEventListener("click", loadSessions);
$("#sessionSearch").addEventListener("input", renderSessions);

$("#newSession").addEventListener("click", async () => {
  // Avoid filling the sidebar with empty sessions.
  if (!hasUserMessage()) {
    showSidebarNotice("已创建新会话，请先在当前会话提问。");
    return;
  }
  setSession(`demo-${Date.now()}`);
  $("#messages").innerHTML = "";
  appendMessage("assistant", "已创建新会话。旧会话可以在左侧最近会话里找回。");
  resetTrace();
  await loadSessions();
});

document.querySelectorAll("[data-prompt]").forEach((button) => {
  button.addEventListener("click", () => {
    $("#messageInput").value = button.dataset.prompt;
    $("#messageInput").focus();
  });
});

setSession(state.sessionId);
appendMessage("assistant", "项目已就绪。你可以先上传文档，或直接试试计算、客服搜索、RAG 和转人工演示。");
resetTrace();
checkHealth();
loadFiles();
loadSessions();
