const filterTriggers = document.querySelectorAll(".filter-trigger");
const filterOverlays = document.querySelectorAll(".filter-overlay");

const openOverlay = (overlay) => {
    overlay.classList.add("open");
    overlay.setAttribute("aria-hidden", "false");
    const focusTarget = overlay.querySelector("input, select, button, a");
    if (focusTarget) {
        focusTarget.focus();
    }
};

const closeOverlay = (overlay) => {
    overlay.classList.remove("open");
    overlay.setAttribute("aria-hidden", "true");
};

filterTriggers.forEach((trigger) => {
    trigger.addEventListener("click", () => {
        const targetId = trigger.getAttribute("data-filter-target");
        if (!targetId) {
            return;
        }
        const overlay = document.getElementById(targetId);
        if (overlay) {
            openOverlay(overlay);
        }
    });
});

filterOverlays.forEach((overlay) => {
    const closeButton = overlay.querySelector(".filter-close");
    if (closeButton) {
        closeButton.addEventListener("click", () => closeOverlay(overlay));
    }

    overlay.addEventListener("click", (event) => {
        if (event.target === overlay) {
            closeOverlay(overlay);
        }
    });
});

document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") {
        return;
    }
    filterOverlays.forEach((overlay) => {
        if (overlay.classList.contains("open")) {
            closeOverlay(overlay);
        }
    });
});
