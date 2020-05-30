import error_parser from "./utils/error_parser.min.js";

const gId = id => document.getElementById(id);

gId("inputSecret").onkeyup = function () {
  gId("count").textContent = "Characters left: " + (150 - this.value.length);
};

gId("createBtn").addEventListener("click", _ => {
  const inputSecret = gId("inputSecret").value;
  const passPhrase = gId("passPhrase").value;
  const expiresValue = gId("expiresValue").value;

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
      secret: inputSecret,
      passphrase: passPhrase,
      days: parseInt(expiresValue),
    }),
    cache: "no-store",
  })
    .then(response => { return response.json() })
    .then(data => {
      switch (data.response.status) {
        case "created":
          window.location.href = `/c?link=${data.response.link}&expires_on=${data.response.expires_on}`;
          return;
        case "error":
          gId("response").className = "notification is-danger pop";
          gId("msg").textContent = error_parser(data.response.details.json);
          return;
      }
    });
});
