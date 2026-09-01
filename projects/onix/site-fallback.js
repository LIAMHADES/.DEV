(function () {
  window.setTimeout(function () {
    var preloader = document.getElementById("preloader");
    if (preloader && window.getComputedStyle(preloader).display !== "none") {
      preloader.style.opacity = "0";
      preloader.style.pointerEvents = "none";
      window.setTimeout(function () {
        preloader.style.display = "none";
      }, 250);
    }

    document.querySelectorAll(".reveal-title, .reveal-el, .reveal-card").forEach(function (element) {
      element.style.opacity = "1";
      element.style.transform = "none";
    });
  }, 4000);
})();
