const gId = (id) => document.getElementById(id);

const copy = gId("copy");
copy.addEventListener("click", (_) => {
  const link = gId("link");
  link.select();
  link.setSelectionRange(0, 99999); /* mobile */
  document.execCommand("copy");
  copy.textContent = "Copied ✅";
});
