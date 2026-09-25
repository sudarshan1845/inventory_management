(function () {
  const html = document.documentElement;
  const saved = localStorage.getItem("theme") || "light";
  html.setAttribute("data-theme", saved);

  const btn = document.getElementById("theme-toggle");
  if (btn) {
    btn.addEventListener("click", () => {
      const current = html.getAttribute("data-theme");
      const next = current === "dark" ? "light" : "dark";
      html.setAttribute("data-theme", next);
      localStorage.setItem("theme", next);
    });
  }
})();
