const gId = id => document.getElementById(id);

const copy = gId("copy");
const link = gId("link");

copy.addEventListener("click", _ => {
  link.select();
  link.setSelectionRange(0, 99999); // mobile
  document.execCommand("copy");
  copy.textContent = "copied";
  copy.className = "button is-success";
});
