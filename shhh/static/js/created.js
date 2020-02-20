/**
 * @file  : created.js
 * @author: Matthieu Petiteau <mpetiteau.pro@gmail.com>
 * Date   : 14.01.2020
 */

const copy = document.getElementById('copy');
copy.addEventListener('click', _ => {
    const link = document.getElementById('link');
    link.select();
    link.setSelectionRange(0, 99999); /* mobile */
    document.execCommand('copy');
    copy.textContent = 'Copied ✅';
});
