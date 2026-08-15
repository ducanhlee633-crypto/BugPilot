(() => {
  "use strict";

  const $ = (sel) => document.querySelector(sel);

  const chat = $("#chat");
  const emptyState = $("#empty-state");
  const form = $("#chat-form");
  const promptEl = $("#prompt");
  const sendBtn = $("#send-btn");
  const cloneForm = $("#clone-form");
  const cloneUrl = $("#clone-url");
  const cloneBtn = $("#clone-btn");
  const cloneStatus = $("#clone-status");
  const repoList = $("#repo-list");
  const repoCount = $("#repo-count");
  const railLog = $("#rail-log");

  /* ---------- helpers ---------- */

  function esc(s) {
    return String(s)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function renderMarkdown(text) {
    const blocks = [];
    text = text.replace(/```([\s\S]*?)```/g, (_, code) => {
      blocks.push(esc(code));
      return `\u0000${blocks.length - 1}\u0000`;
    });

    let html = esc(text);

    html = html
      .replace(/^### (.+)$/gm, "<h3>$1</h3>")
      .replace(/^## (.+)$/gm, "<h2>$1</h2>")
      .replace(/^# (.+)$/gm, "<h1>$1</h1>")
      .replace(/^[-*] (.+)$/gm, "<li>$1</li>")
      .replace(/^\d+\. (.+)$/gm, "<li>$1</li>");

    html = html.replace(/(<li>[\s\S]*?<\/li>)(?!<\/li>)/g, "");
    html = html.replace(/((?:<li>.*?<\/li>\n?)+)/g, "<ul>$1</ul>");
    html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
    html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    html = html.replace(/\n{2,}/g, "</p><p>").replace(/\n/g, "<br/>");

    html = html.replace(/\u0000(\d+)\u0000/g, (_, i) => `<pre><code>${blocks[Number(i)]}</code></pre>`);

    return html;
  }

  function addMessage(kind, text, { raw = false, error = false } = {}) {
    emptyState?.remove();
    const wrap = document.createElement("div");
    wrap.className = `msg ${kind}${error ? " error" : ""}`;
    const meta = document.createElement("div");
    meta.className = "meta";
    meta.textContent = kind === "user" ? "you" : kind === "error" ? "system" : "bugpilot";
    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.innerHTML = raw ? text : renderMarkdown(text);
    wrap.append(meta, bubble);
    chat.appendChild(wrap);
    scrollBottom();
    return wrap;
  }

  function scrollBottom() {
    chat.scrollTop = chat.scrollHeight;
  }

  function railEvent(name, metaText, state) {
    const empty = $(".rail-empty");
    empty?.remove();
    const li = document.createElement("li");
    li.className = `rail-event ${state || ""}`;
    const nameEl = document.createElement("div");
    nameEl.className = "ev-name";
    nameEl.textContent = name;
    li.appendChild(nameEl);
    if (metaText) {
      const meta = document.createElement("div");
      meta.className = "ev-meta";
      meta.textContent = metaText;
      li.appendChild(meta);
    }
    railLog.prepend(li);
    return li;
  }

  function setCloneStatus(msg, cls) {
    cloneStatus.textContent = msg;
    cloneStatus.className = `clone-status ${cls || ""}`;
  }

  /* ---------- repos ---------- */

  async function loadRepos() {
    try {
      const res = await fetch("/repos");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const repos = await res.json();
      repoList.innerHTML = "";
      repoCount.textContent = `${repos.length} repo${repos.length === 1 ? "" : "s"}`;
      if (repos.length === 0) {
        const li = document.createElement("li");
        li.textContent = "projects/ is empty";
        li.classList.add("rail-empty");
        repoList.appendChild(li);
        return;
      }
      for (const r of repos) {
        const li = document.createElement("li");
        li.classList.add("repo-item");
        const name = document.createElement("span");
        name.textContent = r;
        name.title = r;
        name.classList.add("repo-name");
        const del = document.createElement("button");
        del.type = "button";
        del.classList.add("repo-del");
        del.title = `Delete ${r}`;
        del.textContent = "×";
        del.dataset.repo = r;
        del.addEventListener("click", () => deleteRepo(r, del));
        li.append(name, del);
        repoList.appendChild(li);
      }
    } catch (e) {
      repoCount.textContent = "repos unavailable";
    }
  }

  /* ---------- clone ---------- */

  cloneForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const url = cloneUrl.value.trim();
    if (!url) return;
    cloneBtn.disabled = true;
    setCloneStatus("cloning…", "busy");
    const ev = railEvent("git clone", url, "busy");
    try {
      const res = await fetch("/clone_repo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      const data = await res.json().catch(() => ({}));
      const msg = data.message || JSON.stringify(data);
      const ok = res.ok && msg.toLowerCase().includes("success");
      setCloneStatus(msg, ok ? "ok" : "err");
      ev.classList.add(ok ? "done" : "fail");
      cloneUrl.value = "";
      if (ok) {
        addMessage("agent", `Cloned **${url.split("/").pop()}** into \`projects/\`.`);
        loadRepos();
      } else {
        addMessage("error", `Clone failed: ${esc(msg)}`, { raw: true, error: true });
      }
    } catch (err) {
      setCloneStatus(`request failed: ${err.message}`, "err");
      ev.classList.add("fail");
    } finally {
      cloneBtn.disabled = false;
    }
  });

  /* ---------- delete repo ---------- */

  async function deleteRepo(name, btn) {
    if (!confirm(`Delete repository "${name}" from projects/?`)) return;
    btn.disabled = true;
    const ev = railEvent("delete repo", name, "busy");
    try {
      const res = await fetch("/delete_repo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ folder: name }),
      });
      const data = await res.json().catch(() => ({}));
      const msg = data.message || JSON.stringify(data);
      const ok = res.ok && msg.toLowerCase().includes("success");
      ev.classList.add(ok ? "done" : "fail");
      addMessage(ok ? "agent" : "error", ok
        ? `Deleted **${name}** from \`projects/\`.`
        : `Delete failed: ${esc(msg)}`, { raw: ok ? false : true, error: !ok });
      loadRepos();
    } catch (err) {
      ev.classList.add("fail");
      addMessage("error", `Delete request failed: ${esc(err.message)}`, { raw: true, error: true });
    }
  }

  /* ---------- chat ---------- */

  let sending = false;

  async function sendPrompt(text) {
    if (sending) return;
    sending = true;
    const typing = addMessage("typing", "working…");
    const ev = railEvent("agent task", text.slice(0, 80), "busy");
    try {
      const res = await fetch("/call_agent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: text }),
      });
      const data = (await res.json().catch(async () => ({ raw: await res.text() }))) || {};
      typing.remove();
      const detail = data.raw ?? (typeof data.detail === "string" ? data.detail : JSON.stringify(data));
      if (!res.ok) {
        ev.classList.add("fail");
        addMessage("error", `Request failed (${res.status}): ${esc(detail)}`, { raw: true, error: true });
        return;
      }
      if (data.raw) {
        ev.classList.add("done");
        addMessage("agent", data.raw);
        return;
      }
      const content = typeof data === "string" ? data : (data.message ?? data.content ?? data);
      const out = typeof content === "string" && content.trim() ? content : "(no answer)";
      ev.classList.add("done");
      addMessage("agent", out);
    } catch (err) {
      typing.remove();
      ev.classList.add("fail");
      addMessage("error", `Network error: ${esc(err.message)}`, { raw: true, error: true });
    } finally {
      sending = false;
    }
  }

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const text = promptEl.value.trim();
    if (!text || sending) return;
    addMessage("user", text);
    promptEl.value = "";
    autoGrow();
    sendPrompt(text);
  });

  promptEl.addEventListener("input", autoGrow);
  promptEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey && !e.isComposing) {
      e.preventDefault();
      form.requestSubmit();
    }
  });

  function autoGrow() {
    promptEl.style.height = "auto";
    promptEl.style.height = `${Math.min(promptEl.scrollHeight, 140)}px`;
  }

  document.addEventListener("click", (e) => {
    const hint = e.target.closest(".hint-btn");
    if (!hint) return;
    promptEl.value = hint.dataset.hint;
    autoGrow();
    promptEl.focus();
  });

  /* ---------- boot ---------- */

  loadRepos();
})();
