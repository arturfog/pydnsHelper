./manage.py makemigrations

./manage.py migrate --database=default --run-syncdb
./manage.py migrate --database=stats --run-syncdb
#./manage.py migrate --run-syncdb

./manage.py createsuperuser

./manage.py runserver 0.0.0.0:8000
