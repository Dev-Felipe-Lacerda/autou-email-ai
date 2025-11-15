// Text input elements (manual email content)
const emailText = document.getElementById("emailText");
const analyzeTextBtn = document.getElementById("analyzeTextBtn");
const textError = document.getElementById("textError");

// File upload elements (.txt / .pdf input)
const emailFile = document.getElementById("emailFile");
const analyzeFileBtn = document.getElementById("analyzeFileBtn");
const fileError = document.getElementById("fileError");

// Result UI elements (classification and suggested reply)
const resultCard = document.getElementById("resultCard");
const categoryBadge = document.getElementById("categoryBadge");
const subCategoryText = document.getElementById("subCategoryText");
const reasonText = document.getElementById("reasonText");
const replyText = document.getElementById("replyText");
const copyReplyBtn = document.getElementById("copyReplyBtn");

// Loading overlay element
const loadingOverlay = document.getElementById("loadingOverlay");

// Theme toggle elements (light / dark)
const themeToggleBtn = document.getElementById("themeToggleBtn");
const themeToggleIcon = document.getElementById("themeToggleIcon");

// Input mode switch elements (text vs file)
const modeTextBtn = document.getElementById("modeTextBtn");
const modeFileBtn = document.getElementById("modeFileBtn");
const segmentedThumb = document.getElementById("segmentedThumb");
const panelText = document.getElementById("panelText");
const panelFile = document.getElementById("panelFile");

/**
 * Show or hide the full-screen loading overlay.
 */
function showLoading(show) {
  if (!loadingOverlay) return;
  loadingOverlay.classList.toggle("hidden", !show);
}

/**
 * Render the classification result in the result card.
 */
function showResult(data) {
  const category = (data.category || "-").trim();
  const subCategory = data.sub_category || "";
  const reason = data.reason || "";
  const reply = data.auto_reply || "";

  categoryBadge.textContent = "Categoria: " + category;

  categoryBadge.classList.remove(
    "bg-emerald-500/10",
    "text-emerald-700",
    "bg-sky-500/10",
    "text-sky-700",
    "bg-slate-800",
    "text-slate-100"
  );

  const lower = category.toLowerCase();
  if (lower.includes("produtivo")) {
    categoryBadge.classList.add("bg-emerald-500/10", "text-emerald-700");
  } else if (lower.includes("improdutivo")) {
    categoryBadge.classList.add("bg-sky-500/10", "text-sky-700");
  } else {
    categoryBadge.classList.add("bg-slate-800", "text-slate-100");
  }

  if (subCategoryText) {
    subCategoryText.textContent = subCategory || "—";
  }

  reasonText.textContent = reason;
  replyText.value = reply;

  resultCard.classList.remove("hidden");
}

/**
 * Show or hide validation error for text input mode.
 */
function showTextError(msg) {
  textError.textContent = msg || "";
  textError.classList.toggle("hidden", !msg);
}

/**
 * Show or hide validation error for file upload mode.
 */
function showFileError(msg) {
  fileError.textContent = msg || "";
  fileError.classList.toggle("hidden", !msg);
}

/**
 * Apply light or dark theme to the document root.
 */
function applyTheme(theme) {
  const root = document.documentElement;
  if (theme === "dark") {
    root.classList.add("dark");
    if (themeToggleIcon) themeToggleIcon.textContent = "☀️";
  } else {
    root.classList.remove("dark");
    if (themeToggleIcon) themeToggleIcon.textContent = "🌙";
  }
}

/**
 * Initialize theme based on localStorage or system preference.
 */
function initTheme() {
  try {
    const stored = localStorage.getItem("emailsmart-theme");
    let theme = stored;
    if (!theme) {
      const prefersDark =
        window.matchMedia &&
        window.matchMedia("(prefers-color-scheme: dark)").matches;
      theme = prefersDark ? "dark" : "light";
    }
    applyTheme(theme);
  } catch (e) {
    applyTheme("light");
  }
}

// Theme toggle button handler
if (themeToggleBtn) {
  themeToggleBtn.addEventListener("click", () => {
    const isDark = document.documentElement.classList.contains("dark");
    const newTheme = isDark ? "light" : "dark";
    applyTheme(newTheme);
    try {
      localStorage.setItem("emailsmart-theme", newTheme);
    } catch (e) {
      console.warn("Não foi possível salvar o tema:", e);
    }
  });
}

/**
 * Toggle between text input mode and file upload mode.
 */
function setInputMode(mode) {
  if (!segmentedThumb || !panelText || !panelFile || !modeTextBtn || !modeFileBtn) return;

  if (mode === "text") {
    segmentedThumb.classList.remove("segmented-thumb-right");

    panelText.classList.remove("hidden");
    panelFile.classList.add("hidden");

    modeTextBtn.classList.add("text-slate-900", "dark:text-slate-100");
    modeTextBtn.classList.remove("text-slate-500", "dark:text-slate-400");

    modeFileBtn.classList.add("text-slate-500", "dark:text-slate-400");
    modeFileBtn.classList.remove("text-slate-900", "dark:text-slate-100");
  } else {
    segmentedThumb.classList.add("segmented-thumb-right");

    panelFile.classList.remove("hidden");
    panelText.classList.add("hidden");

    modeFileBtn.classList.add("text-slate-900", "dark:text-slate-100");
    modeFileBtn.classList.remove("text-slate-500", "dark:text-slate-400");

    modeTextBtn.classList.add("text-slate-500", "dark:text-slate-400");
    modeTextBtn.classList.remove("text-slate-900", "dark:text-slate-100");
  }
}

// Input mode switch handlers
if (modeTextBtn) {
  modeTextBtn.addEventListener("click", () => setInputMode("text"));
}
if (modeFileBtn) {
  modeFileBtn.addEventListener("click", () => setInputMode("file"));
}

/**
 * Promise-based delay helper used to enforce a minimal loading time.
 */
function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// Analyze text button handler
if (analyzeTextBtn) {
  analyzeTextBtn.addEventListener("click", async () => {
    showTextError("");
    showFileError("");

    const text = (emailText.value || "").trim();
    if (!text) {
      showTextError("Por favor, cole o conteúdo de um e-mail antes de analisar.");
      return;
    }

    const MIN_DELAY = 350;
    const start = Date.now();
    showLoading(true);

    try {
      const res = await fetch("/analyze-text", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({ text }),
      });

      if (!res.ok) {
        let errMsg = "Erro ao analisar o texto.";
        try {
          const err = await res.json();
          if (err.detail) errMsg = err.detail;
        } catch {
          // ignore
        }
        const elapsed = Date.now() - start;
        if (elapsed < MIN_DELAY) {
          await wait(MIN_DELAY - elapsed);
        }
        showTextError(errMsg);
        return;
      }

      const data = await res.json();
      const elapsed = Date.now() - start;
      if (elapsed < MIN_DELAY) {
        await wait(MIN_DELAY - elapsed);
      }

      showResult(data);
    } catch (e) {
      console.error(e);
      const elapsed = Date.now() - start;
      if (elapsed < MIN_DELAY) {
        await wait(MIN_DELAY - elapsed);
      }
      showTextError("Erro de conexão com o servidor.");
    } finally {
      showLoading(false);
    }
  });
}

// Analyze file button handler
if (analyzeFileBtn) {
  analyzeFileBtn.addEventListener("click", async () => {
    showTextError("");
    showFileError("");

    if (!emailFile.files || emailFile.files.length === 0) {
      showFileError("Selecione um arquivo .txt ou .pdf para analisar.");
      return;
    }

    const file = emailFile.files[0];
    const formData = new FormData();
    formData.append("file", file);

    const MIN_DELAY = 350;
    const start = Date.now();
    showLoading(true);

    try {
      const res = await fetch("/analyze-file", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        let errMsg = "Erro ao analisar o arquivo.";
        try {
          const err = await res.json();
          if (err.detail) errMsg = err.detail;
        } catch {
          // ignore
        }
        const elapsed = Date.now() - start;
        if (elapsed < MIN_DELAY) {
          await wait(MIN_DELAY - elapsed);
        }
        showFileError(errMsg);
        return;
      }

      const data = await res.json();
      const elapsed = Date.now() - start;
      if (elapsed < MIN_DELAY) {
        await wait(MIN_DELAY - elapsed);
      }

      showResult(data);
    } catch (e) {
      console.error(e);
      const elapsed = Date.now() - start;
      if (elapsed < MIN_DELAY) {
        await wait(MIN_DELAY - elapsed);
      }
      showFileError("Erro de conexão com o servidor.");
    } finally {
      showLoading(false);
    }
  });
}

// Copy suggested reply to clipboard handler
if (copyReplyBtn) {
  copyReplyBtn.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(replyText.value || "");
      const originalLabel = copyReplyBtn.textContent;
      copyReplyBtn.textContent = "Copiado!";
      setTimeout(() => {
        copyReplyBtn.textContent = originalLabel;
      }, 1200);
    } catch (e) {
      console.error(e);
    }
  });
}

/**
 * App initialization: theme and default input mode.
 */
initTheme();
setInputMode("text");
