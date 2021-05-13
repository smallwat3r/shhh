export default function fetchRetry(
  url,
  options = {},
  retries = 10,
  backoff = 250
) {
  return fetch(url, options)
    .then((res) => {
      if (retries > 0 && res.status === 500) {
        setTimeout(() => {
          console.log("Retrying...");
          return fetchRetry(url, options, retries - 1, backoff * 2);
        }, backoff);
      }
      return res.json();
    })
    .catch(console.error);
}
