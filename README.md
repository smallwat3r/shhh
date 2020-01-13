![shhh](https://github.com/smallwat3r/shhh/blob/master/shhh/static/img/lock.png)  

Shhh is a tiny Flask app to write encrypted secrets and share them with people
using a secure link.  

The sender has to set up an expiration date along with a passphrase to access 
the secret. After the specified date the secret will be removed from the database.
Also as soon as someone decrypt a message, it is erased permanently from the 
database.  

The secrets are encrypted in order to make the data anonymous, especially
in MySQL.  
_Encryption method used: Fernet with password, random salt value and strong
iteration count (100 000)._  

**Click this image to see the demo:**    
[![shhh demo](http://i.imgur.com/Exa8dUu.png)](https://vimeo.com/384411739 "Shhh demo - Click to Watch!")

## Set up & Dependencies

- **MySQL** to store the links generated, the encrypted messages, creation
and expiration dates.  
- **Celery** to run scheduled tasks that checks for expired records to delete in MySQL
every minutes.  
- **Redis** that works as our Celery broker.  
- **Flask**.  

### Launch Shhh

#### Natively Using Flask (dev-local)

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

We recommend that you create a virtual environment for this project, so you can
install the required dependencies.

```sh
virtualenv -p python3 venv --no-site-package
source venv/bin/activate
pip install -r requirements.txt
```

Stay in the virtual environment created.  

You then need to set up a few environment variables. These will be used to
configure Flask, as well as the app's connection to an instance of MySQL.

```sh
export FLASK_APP=shhh
export FLASK_ENV=dev-local
export HOST_MYSQL=<localhost>
export USER_MYSQL=<username>
export PASS_MYSQL=<password>
export DB_MYSQL=<name>
```

You will need to run in parrallel Redis, Celery (both worker + beat) and Flask,
to do so, you can run the below commands in a terminal window
(note: the single `&` allows you to run these commands in the same terminal, but
you can also open 4 terminals and type in the commands in this order without `&`):  
```sh
redis-server &
celery -A shhh.tasks worker --loglevel=INFO &
celery -A shhh.tasks beat --loglevel=INFO &
python3 -m flask run --host='0.0.0.0'
```

You can now access Shhh on http://localhost:5000/  

#### Using Docker Compose (dev-docker)

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
make dc-cleanup  # clean
```

Once the container image has finished building and starting, Shhh will be
available via http://localhost:5000/  
You can also check the MySQL records data via http://localhost:8080/  

## Idea credits  

- [OneTimeSecret](https://github.com/onetimesecret/onetimesecret)
- [PasswordPusher](https://github.com/pglombardo/PasswordPusher)
