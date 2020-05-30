import error_parser from "./utils/error_parser.min.js";

const gId = id => document.getElementById(id);

gId("decryptBtn").addEventListener("click", _ => {
  const slug_id = gId("slugId").value;
  const passphrase = gId("passPhrase").value;

  gId("response").className = "";
  gId("msg").textContent = "";

  // prettier-ignore
  fetch(`/api/r?slug=${slug_id}&passphrase=${passphrase}`, {
    method: "GET",
    cache: "no-store",
  })
    .then(response => { return response.json() })
    .then(data => {
      gId("msg").setAttribute("style", "white-space: pre;");
      switch (data.response.status) {
        case "error":
          gId("response").className = "notification is-danger pop";
          gId("msg").textContent = error_parser(data.response.details.query);
          return;
        case "invalid":
          gId("response").className = "notification is-danger pop ";
          gId("msg").innerHTML = data.response.msg;
          return;
        case "expired":
          gId("response").className = "notification is-warning pop";
          break;
        case "success":
          gId("response").className = "notification is-success pop";
          break;
      }
      gId("passPhrase").value = "";
      gId("passPhrase").disabled = true;
      gId("decryptBtn").disabled = true;
      gId("msg").innerHTML = data.response.msg;
    });
});
