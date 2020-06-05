import error_parser from "./utils/error_parser.min.js";

const gId = id => document.getElementById(id);

const inputSecret = gId("inputSecret");
const passPhrase = gId("passPhrase");
const expiresValue = gId("expiresValue");
const maxTries = gId("maxTries");
const haveibeenpwned = gId("haveibeenpwned");

// Default values
expiresValue.value = 3;
maxTries.value = 5;

inputSecret.onkeyup = function () {
  gId("count").textContent = "Characters left: " + (150 - this.value.length);
};

gId("createBtn").addEventListener("click", _ => {
  gId("response").className = "";
  gId("msg").textContent = "";

  // prettier-ignore
  fetch("/api/c", {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      secret: inputSecret.value,
      passphrase: passPhrase.value,
      days: parseInt(expiresValue.value),
      tries: parseInt(maxTries.value),
      haveibeenpwned: haveibeenpwned.checked,
    }),
    cache: "no-store",
  })
    .then(response => { return response.json() })
    .then(data => {
      switch (data.response.status) {
        case "created":
          window.location.href =
            `/c?link=${data.response.link}&expires_on=${data.response.expires_on}`;
          return;
        case "error":
          gId("response").className = "notification is-danger pop";
          gId("msg").textContent = error_parser(data.response.details.json);
          return;
      }
    });
});
