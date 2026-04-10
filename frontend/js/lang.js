/**
 * Sahaf — i18n (TR / EN).
 */
const LANG = {
  tr: {
    title: "Sahaf",
    subtitle: "PDF / EPUB → Markdown",
    dropText: "Dosyayi surukle birak",
    dropSub: "veya tiklayarak sec",
    dropAccept: "PDF, EPUB",
    fileInfo: "Dosya Bilgisi",
    pages: "sayfa",
    chapters: "bolum",
    epub: "EPUB",
    convertBtn: "Markdown'a Donustur",
    progressTitle: "Ilerleme",
    progressPrepare: "Hazirlaniyor...",
    progressAnalyze: "Dosya analiz ediliyor...",
    progressUploading: "Yukleniyor...",
    progressStarting: "Donusum baslatiliyor...",
    progressConverting: "Donusturuluyor...",
    progressDone: "Tamamlandi!",
    tabPreview: "Onizleme",
    tabRaw: "Ham Metin",
    splitTitle: "Parcala & Indir",
    splitLabel: "Kac parcaya bolunecek?",
    splitSingle: "1 = tek dosya",
    splitParts: "parcaya bolunecek",
    rangeLabel: "Aralik (opsiyonel)",
    rangeFrom: "bas",
    rangeTo: "son",
    badgeDigital: "Dijital",
    badgeScanned: "Taranmis",
    badgeMixed: "Karma",
    splitPartLabel: "Bolum",
    downloadMd: ".md Indir",
    downloadZip: "ZIP Indir",
    errorOnly: "Sadece PDF ve EPUB dosyalari kabul edilir.",
    retry: "Tekrar Dene",
    failMsg: "Donusum basarisiz oldu.",
    langToggle: "EN",
    themeToggle: "Tema",
  },
  en: {
    title: "Sahaf",
    subtitle: "PDF / EPUB → Markdown",
    dropText: "Drag & drop your file",
    dropSub: "or click to browse",
    dropAccept: "PDF, EPUB",
    fileInfo: "File Info",
    pages: "pages",
    chapters: "chapters",
    epub: "EPUB",
    convertBtn: "Convert to Markdown",
    progressTitle: "Progress",
    progressPrepare: "Preparing...",
    progressAnalyze: "Analyzing file...",
    progressUploading: "Uploading...",
    progressStarting: "Starting conversion...",
    progressConverting: "Converting...",
    progressDone: "Done!",
    tabPreview: "Preview",
    tabRaw: "Raw Text",
    splitTitle: "Split & Download",
    splitLabel: "How many parts?",
    splitSingle: "1 = single file",
    splitParts: "parts",
    rangeLabel: "Range (optional)",
    rangeFrom: "from",
    rangeTo: "to",
    badgeDigital: "Digital",
    badgeScanned: "Scanned",
    badgeMixed: "Mixed",
    splitPartLabel: "Part",
    downloadMd: ".md Download",
    downloadZip: "ZIP Download",
    errorOnly: "Only PDF and EPUB files are accepted.",
    retry: "Try Again",
    failMsg: "Conversion failed.",
    langToggle: "TR",
    themeToggle: "Theme",
  },
};

let currentLang = localStorage.getItem("sahaf-lang") || "tr";

function t(key) {
  return LANG[currentLang]?.[key] || LANG.tr[key] || key;
}

function setLang(lang) {
  currentLang = lang;
  localStorage.setItem("sahaf-lang", lang);
  document.documentElement.setAttribute("lang", lang);
  applyTranslations();
}

function applyTranslations() {
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    el.textContent = t(key);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    el.placeholder = t(el.getAttribute("data-i18n-placeholder"));
  });
  // Update lang toggle button text
  const btn = document.getElementById("langToggle");
  if (btn) btn.textContent = t("langToggle");
}
