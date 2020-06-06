import error_parser from "./utils/error_parser.min.js";

const gId = id => document.getElementById(id);
const decryptBtn = gId("decryptBtn");

// Paramaters
const slug_id = gId("slugId");
const passphrase = gId("passPhrase");

const r = gId("response");
const m = gId("msg");

decryptBtn.addEventListener("click", _ => {
  fetch(`/api/r?slug=${slug_id.value}&passphrase=${passphrase.value}`, {
    method: "GET",
    cache: "no-store",
  })
    .then(response => {
      return response.json();
    })
    .then(data => {
      switch (data.response.status) {
        case "error":
          r.className = "notification is-danger pop";
          m.textContent = error_parser(data.response.details.query);
          return;
        case "invalid":
          r.className = "notification is-danger pop ";
          m.innerHTML = data.response.msg;
          return;
        case "expired":
          r.className = "notification is-warning pop";
          break;
        case "success":
          r.className = "notification is-success pop";
          break;
      }

      // Disable form
      passphrase.value = "";
      passphrase.disabled = true;
      decryptBtn.disabled = true;

      m.innerHTML = data.response.msg;
    });
});
