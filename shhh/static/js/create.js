/**
 * @file  : create.js
 * @author: Matthieu Petiteau <mpetiteau.pro@gmail.com>
 * Date   : 14.01.2020
 */
document.getElementById('inputSecret').onkeyup = function() {
    document.getElementById('count').textContent = "Characters left: " + (150 - this.value.length);
};

document.getElementById('createBtn').addEventListener('click', _ => {
    const inputSecret = document.getElementById('inputSecret').value;
    const passPhrase = document.getElementById('passPhrase').value;
    const expiresValue = document.getElementById('expiresValue').value;
    fetch('/api/c', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                secret: inputSecret,
                passphrase: passPhrase,
                days: parseInt(expiresValue)
            }),
            cache: 'no-store'
        })
        .then(response => {
            return response.json();
        })
        .then(data => {
            switch (data.response.status) {
                case 'created':
                    window.location.href = `/c?link=${data.response.link}&expires_on=${data.response.expires_on}`;
                    break;
                case 'error':
                    document.getElementById('response').className = 'notification is-danger';
                    document.getElementById('msg').textContent = data.response.details;
                    break;
            }
        });
});
