# Shhh  

**Shhh** is a tiny Flask app to write encrypted secrets and share them with people
using a secure link.  

The sender has to set up an expiration date along with a passphrase to access 
the secret. After the specified date the secret will be removed from the database.
Also as soon as someone decrypts a message, it is erased permanently from the 
database.  

The secrets are encrypted in order to make the data anonymous, especially
in MySQL.  
_Encryption method used: Fernet with password, random salt value and strong
iteration count (100 000)._  

Shhh is now live at https://shhh-encrypt.com, but for even more privacy / security you can
find in this repo everything you need to host the app on a personal / private server.  

_Tip: For added security, avoid telling in Shhh what is the use of the secret you're 
sharing. Instead, explain this in your email, and copy paste the Shhh link with the passphrase
so the user can retrieve it._  

**Demo:**  
![shhh demo](https://github.com/smallwat3r/shhh/blob/master/_demo/demo.gif)

## Set up & Dependencies

- **MySQL** to store the links generated, the encrypted messages, creation
and expiration dates.  
- **Celery** to run scheduled tasks that checks for expired records to delete in MySQL
every minutes.  
- **Redis** that works as our Celery broker.  
- **Flask**.  

### Launch Shhh

These methods are for development purpose only. If you want to use it in production
you probably want to use Gunicorn, and use a more secure configuration.  

<details>
<summary>Natively</summary>
  
#### MySQL

You will need a MySQL server running on localhost in the background.  
Create a MySQL database and run the following script to generate the
table `links` that will store our data.  

```sql
CREATE TABLE `links` (
  `slug_link` text,
  `encrypted_text` text,
  `date_created` datetime DEFAULT NULL,
  `date_expires` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```

This MySQL query can also be executed against the MySQL server instance via
the `mysql/initialize.sql` file.  

#### Redis  

You will also need Redis running on localhost in the background has it will
work as our Celery broker. Open a new terminal window and launch it.    
```sh
redis-server
```

#### Flask and Celery   

In another terminal window, clone this repository and go inside it.
```sh 
git clone https://github.com/smallwat3r/shhh.git && cd shhh
```

We recommend that you create a virtual environment for this project, so you can
install the required dependencies.  

```sh
virtualenv -p python3 venv --no-site-package
source venv/bin/activate
pip install -r requirements.txt
```

Stay in the virtual environment created.  

You then need to set up a few environment variables. These will be used to
configure Flask, as well as the app's connection to MySQL.  

```sh
export FLASK_APP=shhh
export FLASK_ENV=dev-local
export HOST_MYSQL=127.0.0.1
export USER_MYSQL=<your MySQL username>
export PASS_MYSQL=<your MySQL password>
export DB_MYSQL=<name of the MySQL database created>
```

We then need to launch our Celery worker.  

To launch our Celery worker, open a new terminal window, go to the
project and run  

```sh
source venv/bin/activate  # make sure we are connected to our virtual env.
celery -A shhh.tasks worker --loglevel=INFO
```

Then we need to launch Celery beat that will be triggered by the worker to
delete the expired records from the database every minutes.  

To launch Celery beat, open a third terminal window, go to the
project and run  

```sh
source venv/bin/activate  # make sure we are connected to our virtual env.
celery -A shhh.tasks beat --loglevel=INFO
```

Then go back to your first terminal where you first set-up your virtual env
and launch flask with

```sh
python3 -m flask run --host='0.0.0.0'
```

You can now access Shhh on http://localhost:5000/  

You should be able to see in your other terminal windows the logs from 
Redis, Celery and Celery beat trigerring and receiving tasks to check
and deleted the expired records.  

</details>

<details>
<summary>Using docker-compose (recommended)</summary>

#### docker-compose  

You will need Docker, docker-compose and make installed on your machine.  

For development instances of Shhh, this repo contains a docker-compose
configuration. The configuration defines default settings for Shhh,
default settings for a containerized instance of MySQL server as well
as default settings for Redis and Celery (worker + beat). To build and
run Shhh via docker-compose:  

```sh
docker-compose up -d
```

or via Makefile:

```sh
make dc-start    # start app
                 
                 # other commands
                 # --------------
make dc-stop     # stop app
make dc-reboot   # reboot app
make dc-cleanup  # clean
```

Once the container image has finished building and starting, Shhh will be
available via http://localhost:5000/  

You can also inspect the MySQL data via http://localhost:8080/  
  
</details>

## Create and read secrets using the API

If you like living in the terminal, you can use Shhh with CURL to create
and read secrets.  

Notes: 
* Passphrases needs min. 5 chars, 1 number and 1 uppercase.  
* Max number of days to keep a secret alive is 7.  
* Max number of characters for the secret is 150.  

**Example**  

Create a secret  
```sh 
curl -X POST \
    -H "Content-Type: application/json" \
    -d '{"secret": "This is secret.", "passphrase": "Passw123", "days": 3}' \
    https://shhh-encrypt.com/api/c

# outputs
{
    "expires_on": "2020-01-16 at 22:53 GMT",
    "link": "https://shhh-encrypt.com/r/BuMwIftk-T2GQIuewRB-",
    "slug": "BuMwIftk-T2GQIuewRB-",
    "status": "created"
}
```

Read a secret  
```sh
curl -X GET \
    https://shhh-encrypt/api/r?slug=BuMwIftk-T2GQIuewRB-&passphrase=Passw123

# outputs
{
    "msg": "This is secret.",
    "status": "success"
}
```

## Credits

#### Existing cool apps that gave me the idea to develop my own version using Flask

* [OneTimeSecret](https://github.com/onetimesecret/onetimesecret)
* [PasswordPusher](https://github.com/pglombardo/PasswordPusher)

#### Thanks to

* [@AustinTSchaffer](https://github.com/AustinTSchaffer) for contributing to set-up a Docker environment.
* [@kleinfelter](https://github.com/kleinfelter) for finding bugs and security issues.

## License

See [LICENSE](https://github.com/smallwat3r/shhh/blob/master/LICENSE) file.  

## Contact

Please report issues or questions [here](https://github.com/smallwat3r/shhh/issues).
