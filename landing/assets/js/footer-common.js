(function () {
  "use strict";

  var footer = document.querySelector("footer");
  var isContentPage = window.location.pathname.indexOf("/contenido/") !== -1;
  var base = isContentPage ? "../" : "";

  if (!footer) {
    footer = document.createElement("footer");
    footer.className = "ares-footer-plain";
    document.body.appendChild(footer);
  }

  if (footer.querySelector("[data-ares-footer-meta]")) return;

  var meta = document.createElement("div");
  meta.className = "ares-footer-meta";
  meta.dataset.aresFooterMeta = "true";
  meta.innerHTML =
    '<nav class="ares-footer-nav" aria-label="Enlaces del pie de página">' +
    '<a href="' + base + 'index.html">Inicio</a>' +
    '<a href="' + (isContentPage ? "pricing.html#planes" : "contenido/pricing.html#planes") + '">Planes y precios</a>' +
    '<a href="' + (isContentPage ? "pet-friendly.html" : "contenido/pet-friendly.html") + '">Sitios pet-friendly</a>' +
    '<a href="' + (isContentPage ? "proximamente.html" : "contenido/proximamente.html") + '">Reserva anticipada</a>' +
    '</nav>' +
    '<div class="ares-footer-data">Cookies y datos: <a href="' + base + 'cookies.html">Política de cookies</a> · <a href="' + base + 'privacidad.html">Privacidad</a> · <button type="button" data-ares-cookie-preferences>Preferencias de cookies</button></div>';

  footer.appendChild(meta);

  var preferences = meta.querySelector("[data-ares-cookie-preferences]");
  preferences.addEventListener("click", function () {
    if (window.aresAnalytics && typeof window.aresAnalytics.manageConsent === "function") {
      window.aresAnalytics.manageConsent();
      return;
    }
    window.location.href = base + "cookies.html";
  });
})();
