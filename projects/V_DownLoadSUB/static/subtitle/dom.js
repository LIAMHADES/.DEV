// DOM helpers — vanilla JS, no framework
window.SubtitleDOM = (function () {
  function $(selector, parent) {
    return (parent || document).querySelector(selector);
  }
  function $$(selector, parent) {
    return Array.from((parent || document).querySelectorAll(selector));
  }
  function escapeHtml(value) {
    return String(value || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }
  return { $, $$, escapeHtml };
})();
