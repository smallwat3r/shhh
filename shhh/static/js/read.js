const gId = (id) => document.getElementById(id);

gId("decryptBtn").addEventListener("click", (_) => {
  const slug_id = gId("slugId").value,
        passphrase = gId("passPhrase").value;

  if (passphrase) {
    fetch(`/api/r?slug=${slug_id}&passphrase=${passphrase}`, {
      method: "GET",
      cache: "no-store",
    })
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        switch (data.response.status) {
          case "error":
            gId("response").className = "notification is-danger";
            break;
          case "expired":
            gId("response").className = "notification is-warning";
            gId("passPhrase").value = "";
            gId("passPhrase").disabled = true;
            gId("decryptBtn").disabled = true;
            break;
          case "success":
            gId("response").className = "notification is-success";
            gId("passPhrase").value = "";
            gId("passPhrase").disabled = true;
            gId("decryptBtn").disabled = true;
            gId("msg").setAttribute("style", "white-space: pre;");
            break;
        }
        gId("msg").innerHTML = data.response.msg;
      });
  }
});
