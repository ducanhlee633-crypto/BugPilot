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

  /* ---------- syntax highlighting ---------- */

  const HL_RE =
    /(\/\/[^\n]*|\/\*[\s\S]*?\*\/|<!--[\s\S]*?-->|#[^\n]*)|(&quot;.*?&quot;|'[^'\n]*')|(`[^`]*`)|(\b\d[\d_]*(?:\.\d+)?\b)|(\b(?:def|class|import|from|return|if|elif|else|for|while|try|except|finally|with|as|lambda|pass|break|continue|global|nonlocal|yield|raise|assert|del|in|is|not|and|or|async|await|match|case|function|const|let|var|new|typeof|instanceof|void|switch|do|catch|throw|export|require|true|false|null|undefined|this|static|extends|super|of|using|namespace|public|private|protected|int|str|float|bool|list|dict|tuple|set|void|char|double|long|self)\b)|(\b[A-Z][A-Za-z0-9_]*\b)|(\b[A-Za-z_][A-Za-z0-9_]*(?=\s*\())/g;

  function highlightLine(line) {
    return line.replace(HL_RE, (m, com, str, bck, num, key, type, fn) => {
      if (com) return `<span class="c-com">${com}</span>`;
      if (str) return `<span class="c-str">${str}</span>`;
      if (bck) return `<span class="c-str">${bck}</span>`;
      if (num) return `<span class="c-num">${num}</span>`;
      if (key) return `<span class="c-key">${key}</span>`;
      if (type) return `<span class="c-type">${type}</span>`;
      return `<span class="c-fn">${fn}</span>`;
    });
  }

  function isErrorLine(line) {
    const t = line.trim();
    if (/^(?:error|fatal|traceback|exception|failed|fail|abort|denied|refused|cannot|unable|✗|❌)(?:\s|:|!|$)/i.test(t)) return "hl-err-line";
    if (/^traceback \(most recent call last\)/i.test(t)) return "hl-err-line";
    if (/^\w+(?:Error|Exception|Failure)\b/i.test(t)) return "hl-err-line";
    if (/[:：]\s*(?:error|fatal|exception|failed)\s*$/i.test(t)) return "hl-err-line";
    if (/^remote:.*(?:error|fatal|denied)/i.test(t)) return "hl-err-line";
    if (/^(?:warning|warn)(?:\s|:|!|$)/i.test(t)) return "hl-warn-line";
    return null;
  }

  function highlightCode(src) {
    return src
      .split("\n")
      .map((rawLine) => {
        const line = highlightLine(esc(rawLine));
        const cls = isErrorLine(rawLine);
        return cls ? `<span class="${cls}">${line}</span>` : line;
      })
      .join("\n");
  }

  function renderMarkdown(text) {
    const blocks = [];
    text = text.replace(/```([\w+-]*)\n?([\s\S]*?)```/g, (_, lang, code) => {
      blocks.push(highlightCode(code));
      return `\u0000${blocks.length - 1}\u0000`;
    });

    let html = esc(text);

    html = html
      .replace(/^### (.+)$/gm, "<h3>$1</h3>")
      .replace(/^## (.+)$/gm, "<h2>$1</h2>")
      .replace(/^# (.+)$/gm, "<h1>$1</h1>")
      .replace(/^[-*] (.+)$/gm, "<li>$1</li>")
      .replace(/^\d+\. (.+)$/gm, "<li>$1</li>");

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

  let evCounter = 0;

  const EV_GLYPH = { busy: "●", done: "✓", fail: "✗" };

  function nowTime() {
    return new Date().toTimeString().slice(0, 8);
  }

  function railEvent(name, metaText, state) {
    const empty = $(".rail-empty");
    empty?.remove();
    evCounter += 1;
    const li = document.createElement("li");
    li.className = `rail-event ${state || ""}`;
    const glyph = document.createElement("span");
    glyph.className = "ev-glyph";
    glyph.textContent = EV_GLYPH[state] || "·";
    glyph.setAttribute("aria-hidden", "true");
    const body = document.createElement("div");
    body.className = "ev-body";
    const nameEl = document.createElement("div");
    nameEl.className = "ev-name";
    nameEl.textContent = name;
    body.appendChild(nameEl);
    if (metaText) {
      const meta = document.createElement("div");
      meta.className = "ev-meta";
      const time = document.createElement("span");
      time.className = "ev-time";
      time.textContent = `#${String(evCounter).padStart(2, "0")} ${nowTime()}`;
      meta.append(time, document.createTextNode(metaText));
      body.appendChild(meta);
    }
    li.append(glyph, body);
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
