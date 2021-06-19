expiresValue.value = 3;
maxTries.value = 5;

inputSecret.onkeyup = (_) =>
  (document.getElementById("counter").textContent =
    "Characters left: " + (inputSecret.maxLength - inputSecret.value.length));

const status = {
  CREATED: "created",
  ERROR: "error"
}

createSecretForm.addEventListener("submit", (e) => {
  e.preventDefault();
  createBtn.classList.add("is-loading");

  let headers = new Headers([
    ["Content-Type", "application/json"],
    ["Accept", "application/json"],
  ]);

  let formData = new FormData(createSecretForm);
  let object = {};
  formData.forEach((value, key) => (object[key] = value));

  createSecretFs.setAttribute("disabled", "disabled");  // lock form

  fetch(createSecretForm.getAttribute("action"), {
    method: createSecretForm.getAttribute("method"),
    headers: headers,
    body: JSON.stringify(object),
    cache: "no-store",
  })
    .then((res) => res.json())
    .then((data) => {
      switch (data.response.status) {
        case status.CREATED:
          successResponseHandler(data);
          break;
        case status.ERROR:
          errorResponseHandler(data);
          break;
      }
    });
});

function successResponseHandler(data) {
  let params = new URLSearchParams();
  params.set("link", data.response.link);
  params.set("expires_on", data.response.expires_on);

  const redirect = createSecretForm.getAttribute("data-redirect");
  window.location.href = `${redirect}?${params.toString()}`;
}

function errorResponseHandler(data) {
  const content = notificationTemplate.content.cloneNode(true);

  notification.innerHTML = "";
  notification.appendChild(content);

  notificationContent.parentNode.classList.add("is-danger");
  notificationContent.textContent = data.response.details;

  // Ability to close the notification
  (document.querySelectorAll(".notification .delete") || []).forEach((del) => {
    const notificationDeletion = del.parentNode;
    del.addEventListener("click", () => {
      notificationDeletion.parentNode.removeChild(notificationDeletion);
    });
  });

  createSecretFs.removeAttribute("disabled");
  createBtn.classList.remove("is-loading");
}
