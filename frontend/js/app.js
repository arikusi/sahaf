/**
 * Sahaf — Main application (state machine + event handlers).
 */
(function () {
  "use strict";

  const ALLOWED_EXT = [".pdf", ".epub"];
  let currentTaskId = null;
  let pollTimer = null;
  let previewTimer = null;

  // ===== Theme =====
  const themeToggle = document.getElementById("themeToggle");
  const savedTheme = localStorage.getItem("sahaf-theme") || "dark";
  document.documentElement.setAttribute("data-theme", savedTheme);

  themeToggle.addEventListener("click", () => {
    const current = document.documentElement.getAttribute("data-theme");
    const next = current === "light" ? "dark" : "light";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("sahaf-theme", next);
  });

  // ===== Language =====
  const langToggle = document.getElementById("langToggle");
  applyTranslations();

  langToggle.addEventListener("click", () => {
    setLang(currentLang === "tr" ? "en" : "tr");
  });

  // ===== Drop Zone =====
  const dropZone = document.getElementById("dropZone");
  const fileInput = document.getElementById("fileInput");

  dropZone.addEventListener("click", () => fileInput.click());

  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("drag-over");
  });

  dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("drag-over");
  });

  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("drag-over");
    const files = e.dataTransfer.files;
    if (files.length > 0) handleFile(files[0]);
  });

  fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) handleFile(fileInput.files[0]);
  });

  // ===== Convert Button =====
  const convertBtn = document.getElementById("convertBtn");
  convertBtn.addEventListener("click", startConversion);

  // ===== Tabs =====
  document.getElementById("tabPreview").addEventListener("click", () => switchTab("preview"));
  document.getElementById("tabRaw").addEventListener("click", () => switchTab("raw"));

  function switchTab(tab) {
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
    document.getElementById("tab" + capitalize(tab)).classList.add("active");
    document.getElementById("panel" + capitalize(tab)).classList.add("active");
  }

  function capitalize(s) { return s.charAt(0).toUpperCase() + s.slice(1); }

  // ===== Parts Input =====
  const partsInput = document.getElementById("partsInput");

  partsInput.addEventListener("input", () => {
    const parts = parseInt(partsInput.value, 10) || 1;
    UI.updateSplitHint(parts);
    UI.updateZipUrl(currentTaskId, parts);

    clearTimeout(previewTimer);
    if (parts > 1 && currentTaskId) {
      previewTimer = setTimeout(() => fetchSplitPreview(parts), 400);
    } else {
      UI.hideSplitPreview();
    }
  });

  async function fetchSplitPreview(parts) {
    try {
      const data = await API.splitPreview(currentTaskId, parts);
      UI.showSplitPreview(data);
    } catch {
      UI.hideSplitPreview();
    }
  }

  // ===== Retry =====
  document.getElementById("retryBtn").addEventListener("click", () => {
    UI.hideError();
    UI.reset();
    currentTaskId = null;
    fileInput.value = "";
  });

  // ===== Main Flow =====
  async function handleFile(file) {
    const ext = "." + file.name.split(".").pop().toLowerCase();
    if (!ALLOWED_EXT.includes(ext)) {
      UI.showError(t("errorOnly"));
      return;
    }

    UI.hideError();
    UI.hide("resultSection");
    UI.hide("downloadSection");
    UI.hide("convertSection");

    try {
      UI.showProgress(10, t("progressUploading"));
      const upload = await API.upload(file);
      currentTaskId = upload.task_id;

      UI.showProgress(30, t("progressAnalyze"));
      const classify = await API.classify(currentTaskId);

      UI.showFileInfo(file.name, classify.page_count, classify.pdf_type, classify.chapter_count || 0);
      UI.hideProgress();
      UI.show("convertSection");
    } catch (err) {
      UI.hideProgress();
      UI.showError(err.message);
    }
  }

  async function startConversion() {
    if (!currentTaskId) return;

    convertBtn.disabled = true;
    UI.hide("convertSection");
    UI.hideError();
    UI.showProgress(5, t("progressStarting"));

    // Read page range
    const pageFrom = parseInt(document.getElementById("pageFrom").value, 10) || 0;
    const pageTo = parseInt(document.getElementById("pageTo").value, 10) || 0;

    try {
      await API.convert(currentTaskId, pageFrom, pageTo);
      startPolling();
    } catch (err) {
      UI.hideProgress();
      UI.showError(err.message);
      convertBtn.disabled = false;
      UI.show("convertSection");
    }
  }

  function startPolling() {
    pollTimer = setInterval(async () => {
      try {
        const st = await API.status(currentTaskId);

        if (st.status === "converting") {
          const pct = Math.max(st.progress, 5);
          UI.showProgress(pct, `${t("progressConverting")} %${pct}`);
        } else if (st.status === "completed") {
          clearInterval(pollTimer);
          pollTimer = null;
          UI.showProgress(100, t("progressDone"));
          await showResult();
        } else if (st.status === "failed") {
          clearInterval(pollTimer);
          pollTimer = null;
          UI.hideProgress();
          UI.showError(st.error || t("failMsg"));
          convertBtn.disabled = false;
          UI.show("convertSection");
        }
      } catch (err) {
        clearInterval(pollTimer);
        pollTimer = null;
        UI.hideProgress();
        UI.showError(err.message);
      }
    }, 2000);
  }

  async function showResult() {
    try {
      const res = await API.result(currentTaskId);
      UI.showResult(res.markdown);
      UI.showDownloads(currentTaskId, 1);
      UI.hideProgress();
    } catch (err) {
      UI.showError(err.message);
    }
  }
})();
