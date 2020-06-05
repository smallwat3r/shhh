# Shhh API

Checkout [shhh-cli](https://github.com/smallwat3r/shhh-cli), a Go 
client to interact with the Shhh API from the terminal.  

## Docs

The API endpoints are `/api/c` (create) and `/api/r` (read).  

### Parameters

**Create a secret**  

* endpoint: `/api/c`  
* type: `POST`  
* format: `json`  

parameter | type | mandatory | default | description | limitations
--- | --- | --- | --- | --- | ---
secret | `str` | yes | - | Secret to encrypt | max. 150 chars
passphrase | `str` | yes | - | Passphrase to open secret | min. 8 chars, 1 number, 1 uppercase
days | `int` | no | 3 | Number of days to keep the secret alive | min. 1, max. 7
tries | `int` | no | 5 | Number of tries to open secret before it gets deleted | min. 3, max. 10
haveibeenpwned | `bool` | no | false | Check passphrase against the **haveibeenpwned.com** API from Troy's Hunt before creating the secret | -

**read a secret**  

* endpoint: `/api/r`  
* type: `GET`  
* format: `querystring`  

parameter | type | mandatory | default | description 
--- | --- | --- | --- | --- 
slug | `str` | yes | - | Slug id of the secret
passphrase | `str` | yes | - | Passphrase to open the secret

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
