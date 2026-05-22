(function () {
  function toggleSubmenu(id) {
    var submenu = document.getElementById(id);
    if (!submenu) {
      return;
    }
    submenu.classList.toggle("is-open");
    var group = submenu.closest(".admin-sidebar__group");
    if (group) {
      group.classList.toggle("is-open");
    }
  }

  function openMobileSidebar() {
    document.body.classList.add("admin-sidebar-open");
  }

  function closeMobileSidebar() {
    document.body.classList.remove("admin-sidebar-open");
  }

  window.toggleAdminSubmenu = toggleSubmenu;

  document.addEventListener("DOMContentLoaded", function () {
    var openButton = document.getElementById("admin-mobile-toggle");
    var closeButton = document.getElementById("admin-mobile-close");
    var backdrop = document.getElementById("admin-sidebar-backdrop");

    if (openButton) {
      openButton.addEventListener("click", openMobileSidebar);
    }
    if (closeButton) {
      closeButton.addEventListener("click", closeMobileSidebar);
    }
    if (backdrop) {
      backdrop.addEventListener("click", closeMobileSidebar);
    }

    document.querySelectorAll(".admin-sidebar .submenu.is-active").forEach(function (submenu) {
      submenu.classList.add("is-open");
      var group = submenu.closest(".admin-sidebar__group");
      if (group) {
        group.classList.add("is-open");
      }
    });
  });
})();
