(function () {
  var offset = "1.25rem";

  function pinVLibrasButton() {
    document.querySelectorAll("[vw], div[vw-access-button]").forEach(function (element) {
      element.style.setProperty("position", "fixed", "important");
      element.style.setProperty("right", offset, "important");
      element.style.setProperty("bottom", offset, "important");
      element.style.setProperty("top", "auto", "important");
      element.style.setProperty("left", "auto", "important");
      element.style.setProperty("margin", "0", "important");
      element.style.setProperty("transform", "none", "important");
    });
  }

  function init() {
    pinVLibrasButton();
    window.setTimeout(pinVLibrasButton, 300);
    window.setTimeout(pinVLibrasButton, 1500);

    var wrapper = document.querySelector("[vw]");
    if (wrapper && window.MutationObserver) {
      var observer = new MutationObserver(pinVLibrasButton);
      observer.observe(wrapper, {
        attributes: true,
        attributeFilter: ["style", "class"],
        childList: true,
        subtree: true,
      });
    }
  }

  document.addEventListener("DOMContentLoaded", init);
  window.addEventListener("load", pinVLibrasButton);
  window.addEventListener("resize", pinVLibrasButton);
  window.addEventListener("scroll", pinVLibrasButton, { passive: true });
})();
