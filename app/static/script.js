const obj = {
  KemerovoOblast: 'kemerovo',
}

window.addEventListener("load", function () {
  const mapObject = document.querySelector("#map");
  const svg = mapObject.contentDocument;
  const states = svg.querySelectorAll(".state");
  states.forEach((state, i) => {
    state.addEventListener("mouseenter", (event) => {
      state.style.fill = '#FF9200'
    });
    state.addEventListener("mouseleave", (event) => {
      state.style.fill = '#FFBF40'
    });
    state.addEventListener("click", (event) => {
      window.location.href = `${window.location.origin}/region/${state.id}`
    });
  });
});
