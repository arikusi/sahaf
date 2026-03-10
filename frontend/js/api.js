/**
 * Sahaf — API client (fetch wrappers).
 */
const API = {
  async upload(file) {
    const form = new FormData();
    form.append("file", file);
    const res = await fetch("/api/upload", { method: "POST", body: form });
    if (!res.ok) throw await this._error(res);
    return res.json();
  },

  async classify(taskId) {
    const res = await fetch(`/api/classify/${taskId}`);
    if (!res.ok) throw await this._error(res);
    return res.json();
  },

  async convert(taskId, pageFrom, pageTo) {
    const params = new URLSearchParams();
    if (pageFrom > 0) params.set("page_from", pageFrom);
    if (pageTo > 0) params.set("page_to", pageTo);
    const qs = params.toString();
    const url = `/api/convert/${taskId}` + (qs ? `?${qs}` : "");
    const res = await fetch(url, { method: "POST" });
    if (!res.ok) throw await this._error(res);
    return res.json();
  },

  async status(taskId) {
    const res = await fetch(`/api/status/${taskId}`);
    if (!res.ok) throw await this._error(res);
    return res.json();
  },

  async result(taskId) {
    const res = await fetch(`/api/result/${taskId}`);
    if (!res.ok) throw await this._error(res);
    return res.json();
  },

  async splitPreview(taskId, parts) {
    const res = await fetch(`/api/split-preview/${taskId}?parts=${parts}`);
    if (!res.ok) throw await this._error(res);
    return res.json();
  },

  downloadMdUrl(taskId) {
    return `/api/download/${taskId}`;
  },

  downloadZipUrl(taskId, parts) {
    const base = `/api/download/${taskId}/zip`;
    return parts > 1 ? `${base}?parts=${parts}` : base;
  },

  async _error(res) {
    try {
      const body = await res.json();
      return new Error(body.detail || `HTTP ${res.status}`);
    } catch {
      return new Error(`HTTP ${res.status}`);
    }
  },
};
