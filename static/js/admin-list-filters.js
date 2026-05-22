(function () {
  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-admin-filter-toggle]").forEach(function (toggle) {
      var panel = toggle.closest(".admin-list-toolbar__filters").querySelector("[data-admin-filter-panel]");
      if (!panel) {
        return;
      }

      toggle.addEventListener("click", function (event) {
        event.stopPropagation();
        panel.hidden = !panel.hidden;
      });

      document.addEventListener("click", function (event) {
        if (!panel.contains(event.target) && !toggle.contains(event.target)) {
          panel.hidden = true;
        }
      });
    });

    document.querySelectorAll("[data-admin-filter-apply]").forEach(function (button) {
      button.addEventListener("click", function () {
        var form = document.getElementById("admin-list-filter-form");
        if (!form) {
          return;
        }

        form.querySelectorAll("[data-admin-filter-field]").forEach(function (field) {
          var targetId = "filter-" + field.getAttribute("data-admin-filter-field");
          var hidden = document.getElementById(targetId);
          if (hidden) {
            hidden.value = field.value;
          }
        });

        form.submit();
      });
    });
  });
})();
