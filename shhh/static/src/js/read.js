const gId = (id) => document.getElementById(id);

gId("decryptBtn").addEventListener("click", (_) => {
  const slug_id = gId("slugId").value,
        passphrase = gId("passPhrase").value;

  fetch(`/api/r?slug=${slug_id}&passphrase=${passphrase}`, {
    method: "GET",
    cache: "no-store",
  })
    .then((response) => { return response.json(); })
    .then((data) => {
      gId("msg").setAttribute("style", "white-space: pre;");
      switch (data.response.status) {
        case "error":
          gId("response").className = "notification is-danger";
          // Passphrase is the only error that can happen.
          gId("msg").textContent = data.response.details.query.passphrase[0];
          return;
        case "invalid":
          gId("response").className = "notification is-danger";
          gId("msg").innerHTML = data.response.msg;
          return;
        case "expired":
          gId("response").className = "notification is-warning";
          break;
        case "success":
          gId("response").className = "notification is-success";
          break;
      }
      gId("passPhrase").value = "";
      gId("passPhrase").disabled = true;
      gId("decryptBtn").disabled = true;
      gId("msg").innerHTML = data.response.msg;
    });
});
