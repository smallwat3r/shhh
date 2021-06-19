const status = {
  INVALID: "invalid",
  EXPIRED: "expired",
  SUCCESS: "success"
}

readSecretForm.addEventListener("submit", (e) => {
  e.preventDefault();

  decryptBtn.classList.add("is-loading");

  let endpoint = readSecretForm.getAttribute("action");
  let params = new URLSearchParams(new FormData(readSecretForm)).toString();

  readSecretFs.setAttribute("disabled", "disabled");  // lock form

  fetch(`${endpoint}?${params}`, {
    method: readSecretForm.getAttribute("method"),
    cache: "no-store",
  })
    .then((res) => res.json())
    .then((data) => {
      switch (data.response.status) {
        case status.INVALID:
          errorResponseHandler(data, "is-danger");
          readSecretFs.removeAttribute("disabled");  // let user retry
          break;
        case status.EXPIRED:
          errorResponseHandler(data, "is-warning");
          break;
        case status.SUCCESS:
          successResponseHandler(data);
          makeCopyable();
          break;
      }
    });
});

function successResponseHandler(data) {
  let content = notificationSecretTemplate.content.cloneNode(true);
  notification.innerHTML = "";
  notification.appendChild(content);
  decryptBtn.classList.remove("is-loading");
  passphrase.value = "";
  notificationSecretContent.textContent = data.response.msg;
  feather.replace();
}

function errorResponseHandler(data, notification_type) {
  let content = notificationTemplate.content.cloneNode(true);
  notification.innerHTML = "";
  notification.appendChild(content);
  notificationContent.parentNode.classList.add(notification_type);
  decryptBtn.classList.remove("is-loading");
  passphrase.value = "";
  notificationContent.textContent = data.response.msg;
}

function makeCopyable() {
  copy.addEventListener("click", (e) => {
    e.preventDefault();
    copy.classList.remove("pop");
    let range = document.createRange();
    range.selectNode(notificationSecretContent);
    window.getSelection().removeAllRanges();
    window.getSelection().addRange(range);
    document.execCommand("copy");
    copy.classList.add("pop");
  });
}
