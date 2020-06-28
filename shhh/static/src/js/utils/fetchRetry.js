export default function fetchRetry(url, options = {}, retries = 4, backoff = 300) {
  return fetch(url, options)
    .then(res => {
      if (retries > 0 && res.status === 500) {
        setTimeout(() => {
          return fetchRetry(url, options, retries - 1, backoff * 2);
        }, backoff);
      }
      return res.json();
    })
    .catch(console.error);
}
