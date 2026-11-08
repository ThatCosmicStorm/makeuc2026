const slider = document.getElementById("rgb");
const preview = document.getElementById("rgb-preview");

slider.addEventListener("input", () => {
  const color = `hsl(${slider.value}, 100%, 50%)`;
  preview.style.backgroundColor = color;

  // TODO: send the value to your device here, e.g.
  // sendColor(slider.value);
});


// "const rgb = getComputedStyle(preview).backgroundColor; // "rgb(255, 0, 0)"""