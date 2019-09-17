# Shhh

Shhh is a tiny Flask App to write secrets and share them with people with a secure link.  
The user can set up an expire date and a passphrase to access the secret.    

Secrets and Passphrases are encoded in order to make the data anonymous, especially in MySQL.  

**Sender demo:**    
![Alt Text](https://github.com/smallwat3r/shhh/blob/master/demo/sender.gif)  

**Reader demo:**  
![Alt Text](https://github.com/smallwat3r/shhh/blob/master/demo/reader.gif)  


## ⚙️ Set up & Dependencies

### MySql 
Create a MySQL database and run the following script to generate the table `links` that will store our data.

```sql
CREATE TABLE `links` (
  `slug_link` text,
  `passphrase` text,
  `encrypted_text` text,
  `date_created` datetime DEFAULT NULL,
  `date_expires` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```

We need to make sure the `event_scheduler` in MySql is activated to schedule database clean-ups (in order to remove the records that has expired).

In MySQL run the following to activate the `event_scheduler`

```sql
SET GLOBAL event_scheduler = ON;
```

Then we need to schedule a run at least every 2 hours to remove our expired records.
```sql
CREATE EVENT AutoDeleteExpiredRecords
ON SCHEDULE
EVERY 2 HOUR
DO 
  DELETE FROM links WHERE date_expires <= now()
```

### Launch Sssh in local
We need to create a virtual environment, enter it, and install the needed dependencies.
```sh
$ virtualenv -p python3 venv --no-site-package
$ source venv/bin/activate
$ pip install -r requirements.txt
```

We then need to set-up our Environment Variables.
```
export FLASK_APP=shhh
export FLASK_ENV=<development/production>
export HOST_MYSQL=<localhost>
export USER_MYSQL=<username>
export PASS_MYSQL=<password>
export DB_MYSQL=<name>
```
Then run the below command to launch Shhh in local.

```sh
$ python3 -m flask run --host='0.0.0.0'
```

## 💡 Idea credits  

- OneTimeSecret https://github.com/onetimesecret/onetimesecret
- PasswordPusher https://github.com/pglombardo/PasswordPusher
