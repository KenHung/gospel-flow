(function () {
    var menu = document.querySelector(".site-menu");
    if (!menu) return;
    var toggle = menu.querySelector(".site-menu-toggle");
    if (!toggle) return;

    function setOpen(open) {
        menu.classList.toggle("is-open", open);
        toggle.setAttribute("aria-expanded", open ? "true" : "false");
    }

    toggle.addEventListener("click", function () {
        setOpen(!menu.classList.contains("is-open"));
    });

    document.addEventListener("click", function (event) {
        if (!menu.classList.contains("is-open") || menu.contains(event.target)) return;
        setOpen(false);
    });

    document.addEventListener("keydown", function (event) {
        if (event.key !== "Escape" || !menu.classList.contains("is-open")) return;
        setOpen(false);
        toggle.focus();
    });
})();
