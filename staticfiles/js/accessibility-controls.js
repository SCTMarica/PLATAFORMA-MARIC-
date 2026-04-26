(function () {
  var storageKey = "plataforma-maric-font-scale";
  var root = document.documentElement;
  var defaultScale = 100;
  var minScale = 90;
  var maxScale = 130;
  var step = 10;

  function clampScale(value) {
    return Math.min(maxScale, Math.max(minScale, value));
  }

  function readStoredScale() {
    try {
      var stored = parseInt(localStorage.getItem(storageKey), 10);
      return Number.isNaN(stored) ? defaultScale : clampScale(stored);
    } catch (error) {
      return defaultScale;
    }
  }

  function saveScale(value) {
    try {
      localStorage.setItem(storageKey, String(value));
    } catch (error) {
      return;
    }
  }

  function applyScale(value) {
    var normalized = clampScale(value);
    root.style.fontSize = normalized + "%";
    root.setAttribute("data-font-scale-current", String(normalized));
    return normalized;
  }

  function updateControls(value) {
    document.querySelectorAll("[data-font-scale='reset']").forEach(function (button) {
      button.textContent = value + "%";
      button.setAttribute("aria-label", "Restaurar fonte para 100%. Tamanho atual " + value + "%");
    });

    document.querySelectorAll("[data-font-scale='decrease']").forEach(function (button) {
      button.disabled = value <= minScale;
    });

    document.querySelectorAll("[data-font-scale='increase']").forEach(function (button) {
      button.disabled = value >= maxScale;
    });
  }

  function handleAction(action) {
    var current = parseInt(root.getAttribute("data-font-scale-current"), 10) || defaultScale;
    var next = current;

    if (action === "decrease") {
      next = current - step;
    } else if (action === "increase") {
      next = current + step;
    } else {
      next = defaultScale;
    }

    next = applyScale(next);
    saveScale(next);
    updateControls(next);
  }

  var initialScale = applyScale(readStoredScale());

  document.addEventListener("DOMContentLoaded", function () {
    updateControls(initialScale);

    document.querySelectorAll("[data-font-scale]").forEach(function (button) {
      button.addEventListener("click", function () {
        handleAction(button.getAttribute("data-font-scale"));
      });
    });
  });
})();
