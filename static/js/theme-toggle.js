(function () {
  var storageKey = "plataforma-maric-theme";
  var root = document.documentElement;

  function getPreferredTheme() {
    var stored = null;
    try {
      stored = localStorage.getItem(storageKey);
    } catch (error) {
      stored = null;
    }

    if (stored === "light" || stored === "dark") {
      return stored;
    }

    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    var toggles = document.querySelectorAll("[data-theme-toggle]");

    toggles.forEach(function (toggle) {
      var label = theme === "dark" ? "Ativar modo claro" : "Ativar modo escuro";

      toggle.setAttribute("aria-label", label);
      toggle.setAttribute("title", label);
      toggle.setAttribute("data-theme-current", theme);
      toggle.setAttribute("aria-pressed", theme === "dark" ? "true" : "false");

      var labelTarget = toggle.querySelector("[data-theme-toggle-label]");
      if (labelTarget) {
        labelTarget.textContent = label;
      }
    });
  }

  function saveTheme(theme) {
    try {
      localStorage.setItem(storageKey, theme);
    } catch (error) {
      return;
    }
  }

  function toggleTheme() {
    var nextTheme = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    applyTheme(nextTheme);
    saveTheme(nextTheme);
  }

  applyTheme(getPreferredTheme());

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-theme-toggle]").forEach(function (toggle) {
      toggle.addEventListener("click", toggleTheme);
    });
  });
})();
