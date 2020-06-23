import error_parser from "./utils/error_parser.min.js";

const form = document.getElementById("readSecret");
const resp = document.getElementById("response");
const msg = document.getElementById("msg");

form.addEventListener("submit", e => {
  e.preventDefault();

  let endpoint = form.getAttribute("action");
  let params = new URLSearchParams(new FormData(form)).toString();

  fetch(`${endpoint}?${params}`, {
    method: form.getAttribute("method"),
    cache: "no-store",
  })
    .then(response => response.json())
    .then(data => {
      switch (data.response.status) {
        case "error":
          resp.className = "notification is-danger pop";
          msg.textContent = error_parser(data.response.details.query);
          return;
        case "invalid":
          resp.className = "notification is-danger pop ";
          msg.innerHTML = data.response.msg;
          return;
        case "expired":
          resp.className = "notification is-warning pop";
          break;
        case "success":
          msg.setAttribute("style", "white-space: pre;");
          resp.className = "notification is-success pop";
          break;
      }

      document.getElementById("passphrase").value = "";
      Array.from(form.elements).forEach(element => (element.disabled = true));

      msg.innerHTML = data.response.msg;
    });
});
