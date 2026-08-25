(function () {
  "use strict";

  var MEASUREMENT_ID = "G-X9NRPGKT75";
  var CONSENT_KEY = "ares_analytics_consent_v1";
  var loaded = false;

  function track(name, params) {
    if (typeof window.gtag === "function") window.gtag("event", name, params || {});
  }

  function loadAnalytics() {
    if (loaded) return;
    loaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
    window.gtag("js", new Date());
    window.gtag("config", MEASUREMENT_ID, { send_page_view: true });
    var script = document.createElement("script");
    script.async = true;
    script.src = "https://www.googletagmanager.com/gtag/js?id=" + MEASUREMENT_ID;
    document.head.appendChild(script);
  }

  function saveConsent(value) {
    try { localStorage.setItem(CONSENT_KEY, value); } catch (e) {}
    if (value === "accepted") loadAnalytics();
  }

  function getConsent() {
    try { return localStorage.getItem(CONSENT_KEY); } catch (e) { return null; }
  }

  function showConsent() {
    var banner = document.createElement("aside");
    banner.setAttribute("aria-label", "Preferencias de analítica");
    banner.className = "ares-consent-banner";
    banner.innerHTML = "<div><strong>Ayúdanos a mejorar ARES</strong><p>Usamos analítica para entender qué páginas interesan más. No activamos nada sin tu permiso.</p></div><div class=\"ares-consent-actions\"><button type=\"button\" data-consent=\"reject\">Rechazar</button><button type=\"button\" data-consent=\"accept\">Aceptar analítica</button></div>";
    var style = document.createElement("style");
    style.textContent = ".ares-consent-banner{position:fixed;z-index:10050;left:1rem;right:1rem;bottom:1rem;display:flex;gap:1rem;align-items:center;justify-content:space-between;padding:1rem 1.2rem;background:#151d25;color:#f6f8fa;border:1px solid rgba(134,187,216,.35);box-shadow:0 10px 35px rgba(0,0,0,.35);font:12px/1.5 Arial,sans-serif}.ares-consent-banner strong{display:block;margin-bottom:.25rem;font-size:13px}.ares-consent-banner p{margin:0;color:rgba(246,248,250,.72)}.ares-consent-actions{display:flex;gap:.5rem;flex-shrink:0}.ares-consent-actions button{border:1px solid rgba(246,248,250,.35);background:transparent;color:#f6f8fa;padding:.55rem .8rem;cursor:pointer}.ares-consent-actions button:last-child{background:#f26419;border-color:#f26419}@media(max-width:600px){.ares-consent-banner{display:block}.ares-consent-actions{margin-top:.8rem;justify-content:flex-end}}";
    document.head.appendChild(style);
    document.body.appendChild(banner);
    banner.addEventListener("click", function (event) {
      var button = event.target.closest("[data-consent]");
      if (!button) return;
      saveConsent(button.dataset.consent === "accept" ? "accepted" : "rejected");
      banner.remove();
      style.remove();
    });
  }

  function bindTracking() {
    document.addEventListener("click", function (event) {
      var link = event.target.closest("a");
      if (!link) return;
      var href = link.getAttribute("href") || "";
      var text = (link.textContent || "").trim().replace(/\s+/g, " ").slice(0, 80);
      if (href.indexOf("calculadora") !== -1) track("calculator_interest", { link_text: text, link_url: href });
      else if (href.indexOf("pricing") !== -1 || href.indexOf("planes") !== -1) track("pricing_interest", { link_text: text, link_url: href });
      else if (href.indexOf("proximamente") !== -1 || href.indexOf("geocerca") !== -1) track("feature_interest", { feature: "geocerca", link_text: text });
      else if (href.indexOf("pet-friendly") !== -1) track("pet_friendly_interest", { link_text: text, link_url: href });
    });
    document.addEventListener("submit", function (event) {
      var form = event.target.closest("[data-lead-form]");
      if (form) track("generate_lead", { lead_source: form.dataset.leadSource || "unknown" });
    }, true);
  }

  function init() {
    window.aresAnalytics = { track: track };
    bindTracking();
    if (getConsent() === "accepted") loadAnalytics();
    else if (!getConsent()) showConsent();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
