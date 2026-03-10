/**
 * Sahaf — DOM update helpers.
 */
const UI = {
  // Section visibility
  show(id) { document.getElementById(id).classList.remove("hidden"); },
  hide(id) { document.getElementById(id).classList.add("hidden"); },

  // File info
  showFileInfo(name, pages, pdfType, chapterCount) {
    document.getElementById("fileName").textContent = name;

    const detail = document.getElementById("filePages");
    if (chapterCount > 0) {
      detail.textContent = `${chapterCount} ${t("chapters") || "bolum"}`;
    } else if (pages > 0) {
      detail.textContent = `${pages} ${t("pages")}`;
    } else {
      detail.textContent = t("epub");
    }

    const badge = document.getElementById("pdfTypeBadge");
    const labels = { digital: "Digital", scanned: "Scanned", mixed: "Mixed", unknown: "?" };
    badge.textContent = labels[pdfType] || pdfType;
    badge.className = "badge badge-" + pdfType;

    this.show("fileInfoSection");

    // Show page range section with proper hint
    const total = chapterCount || pages;
    if (total > 0) {
      const hint = document.getElementById("pageRangeHint");
      hint.textContent = `/ ${total}`;
      document.getElementById("pageTo").max = total;
      document.getElementById("pageFrom").max = total;
      document.getElementById("pageRangeSection").classList.remove("hidden");
    }
  },

  // Progress
  showProgress(percent, text) {
    document.getElementById("progressFill").style.width = percent + "%";
    document.getElementById("progressText").textContent = text;
    this.show("progressSection");
  },

  hideProgress() {
    this.hide("progressSection");
  },

  // Result
  showResult(markdown) {
    document.getElementById("markdownPreview").innerHTML = marked.parse(markdown);
    document.getElementById("markdownRaw").textContent = markdown;
    this.show("resultSection");
  },

  // Download links
  showDownloads(taskId, parts) {
    parts = parts || 1;
    document.getElementById("downloadMd").href = API.downloadMdUrl(taskId);
    document.getElementById("downloadZip").href = API.downloadZipUrl(taskId, parts);
    document.getElementById("partsInput").value = parts;
    this.updateSplitHint(parts);
    this.show("downloadSection");
  },

  updateZipUrl(taskId, parts) {
    document.getElementById("downloadZip").href = API.downloadZipUrl(taskId, parts);
  },

  updateSplitHint(parts) {
    const hint = document.getElementById("splitHint");
    if (parts <= 1) {
      hint.textContent = t("splitSingle");
    } else {
      hint.textContent = `${parts} ${t("splitParts")}`;
    }
  },

  showSplitPreview(data) {
    const list = document.getElementById("splitPartsList");
    const rows = data.parts.map((p) => {
      const kb = (p.chars / 1024).toFixed(1);
      const label = p.starts_with || "...";
      return `<div class="split-part-row">
        <span class="split-part-num">Part ${p.part}</span>
        <span class="split-part-label">${this._esc(label)}</span>
        <span class="split-part-size">${kb} KB</span>
      </div>`;
    });
    list.innerHTML = rows.join("");
    document.getElementById("splitPreview").classList.remove("hidden");
  },

  hideSplitPreview() {
    document.getElementById("splitPreview").classList.add("hidden");
  },

  _esc(s) {
    const d = document.createElement("div");
    d.textContent = s;
    return d.innerHTML;
  },

  // Error
  showError(message) {
    document.getElementById("errorText").textContent = message;
    this.show("errorSection");
  },

  hideError() {
    this.hide("errorSection");
  },

  // Reset all sections
  reset() {
    ["fileInfoSection", "convertSection", "progressSection", "resultSection", "downloadSection", "errorSection"]
      .forEach(id => this.hide(id));
    this.show("uploadSection");
    this.hideSplitPreview();
    document.getElementById("partsInput").value = 1;
    document.getElementById("pageFrom").value = "";
    document.getElementById("pageTo").value = "";
    document.getElementById("pageRangeSection").classList.add("hidden");
  },
};
