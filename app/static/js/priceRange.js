const priceRanges = document.querySelectorAll(".price-range-slider");

priceRanges.forEach((range) => {
    const minInput = range.querySelector(".range-min");
    const maxInput = range.querySelector(".range-max");
    const minLabel = range.querySelector("[data-price-min]");
    const maxLabel = range.querySelector("[data-price-max]");
    const track = range.querySelector(".price-range-track");
    const selection = range.querySelector(".price-range-selection");

    if (!minInput || !maxInput || !minLabel || !maxLabel || !track || !selection) {
        return;
    }

    const minAllowed = Number(range.dataset.min || minInput.min || 0);
    const maxAllowed = Number(range.dataset.max || maxInput.max || 10000);
    minInput.min = String(minAllowed);
    maxInput.min = String(minAllowed);
    minInput.max = String(maxAllowed);
    maxInput.max = String(maxAllowed);

    const updateTrack = (minValue, maxValue) => {
        const rangeSize = maxAllowed - minAllowed || 1;
        const minPercent = ((minValue - minAllowed) / rangeSize) * 98;
        const maxPercent = ((maxValue - minAllowed) / rangeSize) * 98;
        selection.style.left = `${minPercent+2.5}%`;
        selection.style.right = `${100 - maxPercent - 2.5}%`;
    };

    const minGap = 1;

    const clampValues = () => {
        let minValue = Number(minInput.value || minAllowed);
        let maxValue = Number(maxInput.value || maxAllowed);

        if (minValue >= maxValue) {
            if (document.activeElement === minInput) {
                minValue = Math.min(maxValue - minGap, maxAllowed - minGap);
                minInput.value = String(minValue);
            } else {
                maxValue = Math.max(minValue + minGap, minAllowed + minGap);
                maxInput.value = String(maxValue);
            }
        }

        minLabel.textContent = String(minValue);
        maxLabel.textContent = String(maxValue);
        updateTrack(minValue, maxValue);
    };

    clampValues();

    minInput.addEventListener("input", clampValues);
    maxInput.addEventListener("input", clampValues);
});
