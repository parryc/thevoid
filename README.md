# Version v1.0alpha

# Installation

Still in alpha - I cannot guarantee anything will work. Especially I rewrote this shit in Python.

# Follow along at home!

## Pre-requisites
* Postgres and associated command-line tools must be installed
* virtualenv must be installed


Activate Python virtual environment and install (you may need to delete ```.env/include/python2.7```)

```
cd /path/to/directory
virtualenv --no-site-packages --distribute .env && source .env/bin/activate && pip install -r requirements.txt
. .env/bin/activate
```

Setup database (after installing Postgres)

```
createdb beer
python manage.py db init
```
If migrations already exist, use ```python manage.py db upgrade``` instead of ```python manage.py db init```. 


## Database migration
````
python manage.py db migrate
python manage.py db upgrade
````

## THE FUTURE

* ALL OF THE D3. SO MUCH I'LL BE USING D4.
* ALSO, MORE BEER.
* More mobile friendly 

## License

[MIT](http://parryc.mit-license.org/)