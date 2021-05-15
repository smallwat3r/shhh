const form = document.getElementById("readSecret");
const formFs = document.getElementById("readSecretFs");
const resp = document.getElementById("response");
const msg = document.getElementById("msg");
const copy = document.getElementById("copy");

form.addEventListener("submit", (e) => {
  e.preventDefault();

  decryptBtn.className = "button is-primary is-loading";

  resp.className = "";
  msg.textContent = "";

  let endpoint = form.getAttribute("action");
  let params = new URLSearchParams(new FormData(form)).toString();

  formFs.setAttribute("disabled", "disabled");

  fetch(`${endpoint}?${params}`, {
    method: form.getAttribute("method"),
    cache: "no-store",
  })
    .then((res) => {
      return res.json();
    })
    .then((data) => {
      switch (data.response.status) {
        case "invalid":
          resp.className = "notification is-danger pop mt-4";
          msg.innerHTML = data.response.msg;
          decryptBtn.className = "button is-primary";
          formFs.removeAttribute("disabled");
          return;
        case "expired":
          resp.className = "notification is-warning pop mt-4";
          break;
        case "success":
          msg.className = "secret-message";
          resp.className =
            "notification has-text-left is-family-monospace is-success is-light pop mt-1";
          copy.textContent = "Copy to clipboard";
          copy.className = "has-text-left help has-text-success mt-4 clickable";
          break;
      }

      decryptBtn.className = "button is-primary";
      document.getElementById("passphrase").value = "";

      msg.innerHTML = data.response.msg;
    });
});

copy.addEventListener("click", (e) => {
  e.preventDefault();
  let range = document.createRange();
  range.selectNode(msg);
  window.getSelection().removeAllRanges();
  window.getSelection().addRange(range);
  document.execCommand("copy");
  window.getSelection().removeAllRanges();
  copy.textContent = "Copied to clipboard";
  copy.className = "has-text-left help has-text-success-dark mt-4 clickable";
  feather.replace();
});
