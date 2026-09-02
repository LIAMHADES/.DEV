(function () {
  var menu = document.getElementById("menu-toggle");
  var links = document.querySelector(".nav-links");
  if (!menu || !links) return;

  function syncScrollLock() {
    var isOpen = links.classList.contains("open");
    document.documentElement.style.overflowY = isOpen ? "hidden" : "";
  }

  function closeMenu() {
    links.classList.remove("open");
    menu.classList.remove("is-open");
    menu.setAttribute("aria-expanded", "false");
    syncScrollLock();
  }

  new MutationObserver(syncScrollLock).observe(links, {
    attributes: true,
    attributeFilter: ["class"],
  });

  links.addEventListener("click", function (event) {
    if (event.target.closest("a")) window.setTimeout(closeMenu, 0);
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && links.classList.contains("open")) {
      closeMenu();
      menu.focus();
    }
  });

  syncScrollLock();
})();
