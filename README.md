<p align="center">
  <img width="100px" src="https://github.com/smallwat3r/shhh/blob/master/shhh/static/img/logo.png" />
</p>
<p align="center">Keep secrets out of emails and chat logs.</p>

<p align="center">
  <a href="https://codecov.io/gh/smallwat3r/shhh" rel="nofollow"><img src="https://codecov.io/gh/smallwat3r/shhh/branch/master/graph/badge.svg" style="max-width:100%;"></a>
  <a href="https://codeclimate.com/github/smallwat3r/shhh/maintainability" rel="nofollow"><img src="https://api.codeclimate.com/v1/badges/f7c33b1403dd719407c8/maintainability" style="max-width:100%;"></a>
  <a href="https://github.com/smallwat3r/shhh/blob/master/LICENSE" rel="nofollow"><img src="https://img.shields.io/badge/License-MIT-green.svg" style="max-width:100%;"></a>
</p>

## What is it?

**Shhh** is a tiny Flask app to create encrypted secrets and share 
them securely with people. The goal of this application is to get rid
of plain text sensitive information into emails or chat logs.  

Shhh is deployed [here](https://www.shhh-encrypt.com) (_temporary unavailable
until new deployment solution_), but **it's better for organisations and people 
to deploy it on their own personal / private server** for even better security. 
You can find in this repo everything you need to host the app yourself.  

Or you can **one-click deploy to Heroku** using the below button.
It will generate a fully configured private instance of Shhh 
immediately (using your own server running Flask behind Gunicorn and Nginx, 
and your own Postgres database, **for free**).  

[![Deploy][heroku-shield]][heroku]  

Also, checkout [shhh-cli](https://github.com/smallwat3r/shhh-cli), 
a Go client to interact with the Shhh API from the command line.  

## How does it work?

The sender has to set an expiration date along with a passphrase to
protect the information he wants to share.  

A unique link is generated by Shhh that the sender can share with the
receiver in an email, alongside the temporary passphrase he created
in order to reveal the secret.  

The secret will be **permanently removed** from the database as soon 
as one of these events happens:  

* the expiration date has passed. 
* the receiver has decrypted the message. 
* the amount of tries to open the secret has exceeded. 

The secrets are encrypted in order to make the data anonymous, 
especially in the database, and the passphrases are not stored 
anywhere.  

_Encryption method used: Fernet with password, random salt value and
strong iteration count (100 000)._  

_Tip: for better security, avoid writing any info on how/where to use the secret you're sharing (like urls, websites or emails). Instead, explain this in your email or chat, with the link and passphrase generated from Shhh. So even if someone got access to your secret, there is no way for the attacker to know how and where to use it._

## Is there an API?

Yes, you can find some doc [here](https://app.swaggerhub.com/apis-docs/smallwat3r/shhh-api/1.0.0).  

## How to launch Shhh locally?

These instructions are for development purpose only. For production 
use you might want to use a more secure configuration.

#### Deps

Make sure you have `make`, `docker`, `yarn`, and a version of Python 3.10 installed on your machine.  

The application will use the development env variables from [/environments/docker.dev](https://github.com/smallwat3r/shhh/blob/master/environments/docker.dev).  

#### Docker

From the root of the repository, run

```sh
make dc-start          # to start the app 
make dc-start-adminer  # to start the app with adminer (SQL editor)
make dc-stop           # to stop the app
```

Once the container image has finished building and has started, you 
can access:  

* Shhh at <http://localhost:8081>
* Adminer at <http://localhost:8082/?pgsql=db&username=shhh&db=shhh> (if launched with `dc-start-adminer`)

_You can find the development database credentials from the env file at [/environments/docker.dev](https://github.com/smallwat3r/shhh/blob/master/environments/docker.dev)._

##### Create the database tables

Enter a Flask shell in running container with:
``` sh
make shell
```

From the Python Flask shell, run:
``` python
>>> from shhh.adapters import orm
>>> from shhh.extensions import db
>>> orm.metadata.create_all(db.get_engine())
>>> exit()
```

#### Development tools

You can run tests and linting / security reports using the Makefile.  

The following command will display all the commands available from the Makefile:
``` sh
make help
```

* Enter a Flask shell
  ``` sh
  make shell 
  ```

* Run sanity checks
  ```sh
  make tests   # run tests
  make ruff    # run Ruff report
  make bandit  # run Bandit report
  make mypy    # run Mypy report
  ```

* Run code formatter
  ```sh
  make yapf    # format code using Yapf
  ```

* Generate frontend lockfile
  ```sh
  make yarn    # install the frontend deps using Yarn
  ```

## Environment variables

Bellow is the list of environment variables used by Shhh.  

#### Mandatory
* `FLASK_ENV`: the environment config to load (`testing`, `dev-local`, `dev-docker`, `heroku`, `production`).
* `POSTGRES_HOST`: Postgresql hostname
* `POSTGRES_USER`: Postgresql username
* `POSTGRES_PASSWORD`: Postgresql password
* `POSTGRES_DB`: Database name

#### Optional
* `SHHH_HOST`: This variable can be used to specify a custom hostname to use as the
domain URL when Shhh creates a secret (ex: `https://<domain-name.com>`). If not set, the hostname 
defaults to request.url_root, which should be fine in most cases.
* `SHHH_SECRET_MAX_LENGTH`: This variable manages how long the secrets your share with Shhh can 
be. It defaults to 250 characters.
* `SHHH_DB_LIVENESS_RETRY_COUNT`: This variable manages the number of tries to reach the database 
before performing a read or write operation. It could happens that the database is not reachable or is 
asleep (for instance this happens often on Heroku free plans). The default retry number is 5.
* `SHHH_DB_LIVENESS_SLEEP_INTERVAL`: This variable manages the interval in seconds between the database
liveness retries. The default value is 1 second.

## Acknowledgements

Special thanks: [@AustinTSchaffer](https://github.com/AustinTSchaffer), [@kleinfelter](https://github.com/kleinfelter)  

## License

See [LICENSE](https://github.com/smallwat3r/shhh/blob/master/LICENSE) file.  

## Contact

Please report issues or questions 
[here](https://github.com/smallwat3r/shhh/issues).  


[![Buy me a coffee][buymeacoffee-shield]][buymeacoffee]


[buymeacoffee-shield]: https://www.buymeacoffee.com/assets/img/guidelines/download-assets-sm-2.svg
[buymeacoffee]: https://www.buymeacoffee.com/smallwat3r

[heroku-shield]: https://www.herokucdn.com/deploy/button.svg
[heroku]: https://heroku.com/deploy?template=https://github.com/smallwat3r/shhh
