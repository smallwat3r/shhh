import error_parser from "./utils/error_parser.min.js";

const gId = id => document.getElementById(id);
const createBtn = gId("createBtn");

// Parameters
const inputSecret = gId("inputSecret");
const passPhrase = gId("passPhrase");
const expiresValue = gId("expiresValue");
const maxTries = gId("maxTries");
const haveibeenpwned = gId("haveibeenpwned");

const r = gId("response");
const m = gId("msg");

// Default values
expiresValue.value = 3;
maxTries.value = 5;

inputSecret.onkeyup = function () {
  gId("count").textContent = "Characters left: " + (150 - this.value.length);
};

createBtn.addEventListener("click", _ => {
  r.className = "";
  m.textContent = "";

  let payload = JSON.stringify({
    secret: inputSecret.value,
    passphrase: passPhrase.value,
    days: parseInt(expiresValue.value),
    tries: parseInt(maxTries.value),
    haveibeenpwned: haveibeenpwned.checked,
  });

  let headers = new Headers([
    ["Content-Type", "application/json"],
    ["Accept", "application/json"],
  ]);

  fetch("/api/c", {
    method: "POST",
    headers: headers,
    body: payload,
    cache: "no-store",
  })
    .then(response => {
      return response.json();
    })
    .then(data => {
      switch (data.response.status) {
        case "created":
          window.location.href = `/c?link=${data.response.link}&expires_on=${data.response.expires_on}`;
          return;
        case "error":
          r.className = "notification is-danger pop";
          m.textContent = error_parser(data.response.details.json);
          return;
      }
    });
});
