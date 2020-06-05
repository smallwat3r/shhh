# Shhh API

Checkout [shhh-cli](https://github.com/smallwat3r/shhh-cli), a Go 
client to interact with the Shhh API from the terminal.  

## Doc

The API endpoints are `/api/c` (create) and `/api/r` (read).  

Notes: 
* Passphrases needs min. 8 characters, including at least 1 number 
and 1 uppercase.  
* Max number of days to keep a secret alive is 7.  
* Max number of characters for the secret is 150.  
* Min number of tries to open the secret is 3 and max is 10.  
* This will query the **haveibeenpwned** API from Troy's Hunt if 
`haveibeenpwned` is set to `true` to check if the passphrase has 
already been hacked, forcing the user to chose a secure one.  

**Example using CURL**  

Create a secret  
```sh 
curl -X POST \
    -H "Content-Type: application/json" \
    -d '{"secret": "This is secret.", "passphrase": "Phdeiuwd!!hs", "days": 3, "tries": 5, "haveibeenpwned": true}' \
    https://<domain>/api/c

# outputs
{
    "response": {
        "status": "created",
        "details": "Secret successfully created.",
        "slug": "VC16EgYLsXTuECsX9fTZ",
        "link": "<domain>/r/VC16EgYLsXTuECsX9fTZ",
        "expires_on": "2020-03-17 at 16:44 UTC"
    }
}
```

Read a secret  
```sh
curl -X GET \
    https://<domain>/api/r?slug=VC16EgYLsXTuECsX9fTZ&passphrase=Phdeiuwd!!hs

# outputs
{
    "response": {
        "status": "success",
        "msg": "This is secret."
    }
}
```
