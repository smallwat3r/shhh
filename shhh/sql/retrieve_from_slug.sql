SELECT passphrase,
       encrypted_text
FROM links
WHERE slug_link = %(slug)s;
