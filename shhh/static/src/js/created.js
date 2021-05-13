const copy = document.getElementById("copy");
const link = document.getElementById("link");

copy.addEventListener("click", (_) => {
  link.select();
  link.setSelectionRange(0, 99999); // mobile
  document.execCommand("copy");
  copy.textContent = "copied";
  copy.className = "button is-success";
});
