# Shhh API

Checkout [shhh-cli](https://github.com/smallwat3r/shhh-cli), a Go 
client to interact with Shhh API via command line.  

The endpoints are `/api/c` (create) and `/api/r` (read).  

Notes: 
* Passphrases needs min. 8 characters, including at least 1 number 
and 1 uppercase.  
* Max number of days to keep a secret alive is 7.  
* Max number of characters for the secret is 150.  

**Example using CURL**  

Create a secret  
```sh 
curl -X POST \
    -H "Content-Type: application/json" \
    -d '{"secret": "This is secret.", "passphrase": "Passw123", "days": 3}' \
    https://shhh-encrypt.com/api/c

# outputs
{
    "response": {
        "status": "created",
        "details": "Secret successfully created.",
        "slug": "VC16EgYLsXTuECsX9fTZ",
        "link": "http://shhh-encrypt.com/r/VC16EgYLsXTuECsX9fTZ",
        "expires_on": "2020-03-17 at 16:44 UTC"
    }
}
```

Read a secret  
```sh
curl -X GET \
    https://shhh-encrypt.com/api/r?slug=VC16EgYLsXTuECsX9fTZ&passphrase=Passw123

# outputs
{
    "response": {
        "status": "success",
        "msg": "This is secret."
    }
}
```
