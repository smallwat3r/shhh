copy.addEventListener("click", (_) => {
  link.select();
  link.setSelectionRange(0, 99999); // mobile
  document.execCommand("copy");
  copy.textContent = "copied";
  copy.classList.replace("is-warning", "is-primary");
});
