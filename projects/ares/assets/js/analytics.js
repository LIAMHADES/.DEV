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
    if (typeof window.gtag === "function") {
      window.gtag("consent", "update", {
        analytics_storage: value === "accepted" ? "granted" : "denied",
        ad_storage: "denied",
      });
    }
    if (value === "accepted") loadAnalytics();
  }

  function getConsent() {
    try { return localStorage.getItem(CONSENT_KEY); } catch (e) { return null; }
  }

  function showManageButton() {
    if (document.querySelector(".ares-consent-manage")) return;
    var manage = document.createElement("button");
    manage.type = "button";
    manage.className = "ares-consent-manage";
    manage.textContent = "Preferencias de cookies";
    manage.addEventListener("click", showConsent);
    document.body.appendChild(manage);
  }

  function showConsent() {
    var existing = document.querySelector(".ares-consent-banner");
    if (existing) return;
    var manage = document.querySelector(".ares-consent-manage");
    if (manage) manage.remove();
    var banner = document.createElement("aside");
    banner.setAttribute("role", "dialog");
    banner.setAttribute("aria-label", "Preferencias de cookies");
    banner.className = "ares-consent-banner";
    var base = location.pathname.indexOf("/contenido/") !== -1 ? "../" : "";
    banner.innerHTML = "<div class=\"ares-consent-copy\"><strong>Ayúdanos a mejorar ARES</strong><p>Usamos analítica opcional para saber qué páginas interesan más.</p><details><summary>Ver detalles sobre cookies</summary><p>Las cookies necesarias permiten que la web funcione. Si aceptas, Google Analytics puede usar cookies como <code>_ga</code> para medir visitas y navegación. No enviamos a Analytics el contenido de tus formularios.</p><p>Puedes cambiar tu decisión cuando quieras desde Preferencias de cookies.</p></details><p class=\"ares-consent-links\"><a href=\"" + base + "cookies.html\">Política de cookies</a> · <a href=\"" + base + "privacidad.html\">Privacidad</a></p></div><div class=\"ares-consent-actions\"><button type=\"button\" class=\"ares-consent-secondary\" data-consent=\"reject\"><span>Rechazar</span></button><button type=\"button\" class=\"ares-consent-primary\" data-consent=\"accept\"><span>Aceptar analítica</span></button></div>";
    var style = document.createElement("style");
    style.textContent = ".ares-consent-banner{position:fixed;z-index:10050;left:1rem;right:1rem;bottom:1rem;display:flex;gap:1.25rem;align-items:center;justify-content:space-between;padding:1rem 1.25rem;background:#151d25;color:#f6f8fa;border:1px solid rgba(134,187,216,.45);box-shadow:0 10px 35px rgba(0,0,0,.35);font:12px/1.5 Arial,sans-serif}.ares-consent-copy{max-width:60rem}.ares-consent-banner strong{display:block;margin-bottom:.2rem;font:500 13px/1.2 Orbitron,Arial,sans-serif;letter-spacing:.04em;text-transform:uppercase}.ares-consent-banner p{margin:.2rem 0;color:rgba(246,248,250,.78)}.ares-consent-banner details{margin-top:.35rem;color:rgba(246,248,250,.78)}.ares-consent-banner summary{cursor:pointer;color:#86bbd8}.ares-consent-banner code{color:#f6ae2d}.ares-consent-links{font-size:11px}.ares-consent-links a{color:#86bbd8}.ares-consent-actions{display:flex;gap:.55rem;flex-shrink:0}.ares-consent-actions button,.ares-consent-manage{position:relative;font:500 10px/1 Orbitron,Arial,sans-serif;letter-spacing:.06em;text-transform:uppercase;cursor:pointer;clip-path:polygon(9px 0,100% 0,100% calc(100% - 9px),calc(100% - 9px) 100%,0 100%,0 9px)}.ares-consent-actions button{padding:.75rem 1rem;border:1px solid #f26419}.ares-consent-actions button::before{content:'';position:absolute;inset:2px;z-index:0;clip-path:polygon(7px 0,100% 0,100% calc(100% - 7px),calc(100% - 7px) 100%,0 100%,0 7px);background:#151d25}.ares-consent-actions button span{position:relative;z-index:1}.ares-consent-secondary{background:rgba(246,248,250,.55);color:#f6f8fa;border-color:rgba(246,248,250,.55)!important}.ares-consent-primary{background:#f26419;color:#fff}.ares-consent-primary::before{background:#f26419!important}.ares-consent-secondary:hover::before{background:#23303a}.ares-consent-primary:hover::before{background:#fff!important}.ares-consent-primary:hover span{color:#f26419}.ares-consent-manage{position:fixed;z-index:10040;right:1rem;bottom:1rem;padding:.55rem .8rem;background:#151d25;color:#86bbd8;border:1px solid rgba(134,187,216,.5)}@media(max-width:600px){.ares-consent-banner{display:block;left:.75rem;right:.75rem;bottom:.75rem;padding:1rem}.ares-consent-actions{margin-top:.8rem;justify-content:flex-end;flex-wrap:wrap}.ares-consent-actions button{flex:1 1 10rem}.ares-consent-manage{right:.75rem;bottom:.75rem}}@media(prefers-reduced-motion:reduce){.ares-consent-actions button,.ares-consent-manage{transition:none!important}}";
    style.textContent += ".ares-consent-banner{clip-path:polygon(14px 0,calc(100% - 14px) 0,100% 14px,100% calc(100% - 14px),calc(100% - 14px) 100%,14px 100%,0 calc(100% - 14px),0 14px)}";
    document.head.appendChild(style);
    document.body.appendChild(banner);
    banner.addEventListener("click", function (event) {
      var button = event.target.closest("[data-consent]");
      if (!button) return;
       saveConsent(button.dataset.consent === "accept" ? "accepted" : "rejected");
       banner.remove();
       style.remove();
       showManageButton();
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
    if (getConsent() === "accepted") { loadAnalytics(); showManageButton(); }
    else if (getConsent() === "rejected") showManageButton();
    else showConsent();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
