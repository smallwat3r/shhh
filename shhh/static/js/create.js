const gId = (id) => document.getElementById(id);

gId("inputSecret").onkeyup = function () {
  gId("count").textContent = "Characters left: " + (150 - this.value.length);
};

gId("createBtn").addEventListener("click", (_) => {
  const inputSecret = gId("inputSecret").value,
    passPhrase = gId("passPhrase").value,
    expiresValue = gId("expiresValue").value;

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
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      switch (data.response.status) {
        case "created":
          window.location.href = `/c?link=${data.response.link}&expires_on=${data.response.expires_on}`;
          return;
        case "error":
          gId("response").className = "notification is-danger";
          gId("msg").setAttribute("style", "white-space: pre;");
          let msg = "";
          for (const [key, value] of Object.entries(data.response.details.json)) {
            msg += `${value}\n`;
          }
          gId("msg").textContent = msg;
          return;
      }
    });
});
