source venv/bin/activate

cd dnsserver

./manage.py makemigrations

./manage.py migrate --run-syncdb

./manage.py createsuperuser

./manage.py runserver
