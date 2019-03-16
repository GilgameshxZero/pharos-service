# Pharos Service

Service accessible via mobile allowing job submission to the Pharos printing service at MIT.

Yang Yan, Stella Yang, Tony Wang, Jing lin

## Support

Currently, we support PDF files on iOS platforms through Messenger.

## Installation

Instructions adapted from [quick-start](https://scripts.mit.edu/start/) and [django-upgrade](https://scripts.mit.edu/faq/161/how-do-i-upgrade-django-can-i-still-use-the-django-quickstart-if-i-do-so).

On an Athena prompt, run the following:

```
add scripts
add consult
mkdir -p /mit/[lockername]/.local/
fsr sa /mit/[lockername]/.local/ daemon.scripts write
```

Then, ssh into the scripts server:

```
ssh -k [lockername]@scripts
pip install --user --upgrade django==1.10.5
python -c "import django; print(django.get_version())" # should print 1.10.5
```

Head back to Athena, and run

```
scripts
```

Follow the instructions to install Django for your script. Set the path to `messengerpbot` and the project to `messpbot`.

Open `/mit/[lockername]/web_scripts/[path]/index.fcgi` and after

```
os.environ['DJANGO_SETTINGS_MODULE'] ...
```

add 

```
import django
django.setup()
```

Then delete

```
from django.core.servers.fastcgi import runfastcgi
runfastcgi(method="threaded", daemonize="false")
```

Then add at the end

```
from flup.server.fcgi import WSGIServer
from django.core.handlers.wsgi import WSGIHandler
WSGIServer(WSGIHandler()).run()
```

Then clone the repository into `/mit/[lockername]/Scripts/django/` and head to ALLOWED_HOSTS = `[lockername].scripts.mit.edu`





