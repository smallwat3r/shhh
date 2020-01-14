/**
 * @file  : read.js
 * @author: Matthieu Petiteau <mpetiteau.pro@gmail.com>
 * Date   : 14.01.2020
 */
document.getElementById('decryptBtn').addEventListener('click', _ => {
    const slug_id = window.location.href.split('/').slice(-1)[0];
    const passphrase = document.getElementById('passPhrase').value;
    if (passphrase) {
        fetch(`/api/r?slug=${slug_id}&passphrase=${passphrase}`, {
                method: 'GET',
                cache: 'no-store'
            })
            .then(response => {
                return response.json();
            })
            .then(data => {
                switch (data.status) {
                    case 'error':
                        document.getElementById('response').className = 'notification is-danger';
                        break;
                    case 'expired':
                        document.getElementById('response').className = 'notification is-warning';
                        document.getElementById('passPhrase').value = '';
                        document.getElementById('passPhrase').disabled = true;
                        document.getElementById('decryptBtn').disabled = true;
                        break;
                    case 'success':
                        document.getElementById('response').className = 'notification is-success';
                        document.getElementById('passPhrase').value = '';
                        document.getElementById('passPhrase').disabled = true;
                        document.getElementById('decryptBtn').disabled = true;
                        document.getElementById('msg').setAttribute('style', 'white-space: pre;');
                        break;
                }
                document.getElementById('msg').innerHTML = data.msg;
            });
    }
});
