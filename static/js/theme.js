(function () {
  const html = document.documentElement;
  const saved = localStorage.getItem("theme") || "light";
  html.setAttribute("data-theme", saved);

  function refresh() {
    const dark = html.getAttribute("data-theme") === "dark";
    document.querySelectorAll("[data-theme-toggle]").forEach(b => {
      b.innerHTML = dark ? "☀️ Switch to Light Mode" : "🌙 Switch to Dark Mode";
    });
  }
  document.querySelectorAll("[data-theme-toggle]").forEach(b => {
    b.addEventListener("click", () => {
      const next = html.getAttribute("data-theme") === "dark" ? "light" : "dark";
      html.setAttribute("data-theme", next);
      localStorage.setItem("theme", next);
      refresh();
    });
  });
  refresh();
})();
