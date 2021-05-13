import errorParser from "./utils/errorParser.min.js";
import fetchRetry from "./utils/fetchRetry.min.js";

const form = document.getElementById("readSecret");
const resp = document.getElementById("response");
const msg = document.getElementById("msg");

form.addEventListener("submit", (e) => {
  e.preventDefault();

  decryptBtn.className = "button is-primary is-loading";

  let endpoint = form.getAttribute("action");
  let params = new URLSearchParams(new FormData(form)).toString();

  fetchRetry(`${endpoint}?${params}`, {
    method: form.getAttribute("method"),
    cache: "no-store",
  }).then((data) => {
    switch (data.response.status) {
      case "error":
        resp.className = "notification is-danger pop mt-4";
        msg.textContent = errorParser(data.response.details.query);
        decryptBtn.className = "button is-primary";
        return;
      case "invalid":
        resp.className = "notification is-danger pop mt-4";
        msg.innerHTML = data.response.msg;
        decryptBtn.className = "button is-primary";
        return;
      case "expired":
        resp.className = "notification is-warning pop mt-4";
        break;
      case "success":
        msg.setAttribute("style", "white-space: pre;");
        resp.className = "notification is-success pop mt-4";
        break;
    }

    decryptBtn.className = "button is-primary";

    document.getElementById("passphrase").value = "";
    Array.from(form.elements).forEach((element) => (element.disabled = true));

    msg.innerHTML = data.response.msg;
  });
});
