import errorParser from "./utils/errorParser.min.js";
import fetchRetry from "./utils/fetchRetry.min.js";

const form = document.getElementById("createSecret");
const resp = document.getElementById("response");
const msg = document.getElementById("msg");

// Default values
expiresValue.value = 3;
maxTries.value = 5;

inputSecret.onkeyup = _ =>
  (document.getElementById("counter").textContent =
    "Characters left: " + (150 - inputSecret.value.length));

form.addEventListener("submit", e => {
  e.preventDefault();
  resp.className = "";
  msg.textContent = "";

  let redirect = form.getAttribute("data-redirect");
  let headers = new Headers([
    ["Content-Type", "application/json"],
    ["Accept", "application/json"],
  ]);

  let formData = new FormData(form);
  let object = {};
  formData.forEach((value, key) => (object[key] = value));

  fetchRetry(form.getAttribute("action"), {
    method: form.getAttribute("method"),
    headers: headers,
    body: JSON.stringify(object),
    cache: "no-store",
  }).then(data => {
    switch (data.response.status) {
      case "created":
        let params = new URLSearchParams();
        params.set("link", data.response.link);
        params.set("expires_on", data.response.expires_on);
        window.location.href = `${redirect}?${params.toString()}`;
        return;
      case "error":
        resp.className = "notification is-danger pop mt-4";
        msg.textContent = errorParser(data.response.details.json);
        return;
    }
  });
});
