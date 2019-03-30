# Pharos Service

Service accessible via mobile allowing job submission to the Pharos printing service at MIT.

Yang Yan, Stella Yang, Tony Wang, Jing Lin

## Support

We support the printing of PDFs on iOS through Messenger. The options are:

* Sides: one or two-sided
* Color: black/white or color
* Copies: number of copies of PDF

## File organization

The main functionality is built into `messprint`, and this is linked to the Django server through `messpbot`. The necessity of `messpbot` is doubtful.

## Setup & installation

Instructions adapted from [quick-start](https://scripts.mit.edu/start/) and [django-upgrade](https://scripts.mit.edu/faq/161/how-do-i-upgrade-django-can-i-still-use-the-django-quickstart-if-i-do-so). `[lockername]` refers to your Kerberos.

On an Athena prompt, run the following:

```bash
add scripts
add consult
mkdir -p /mit/[lockername]/.local/
fsr sa /mit/[lockername]/.local/ daemon.scripts write
```

Then, `ssh` into the scripts server:

```bash
ssh -k [lockername]@scripts
pip install --user --upgrade django==1.10.5
python -c "import django; print(django.get_version())" # should print 1.10.5
```

Head back to Athena, and run

```bash
scripts
```

Follow the instructions to install Django for your script (Quick-Start auto-install > Django > personal Athena account > your username and password). Set the "desired address" to `messengerpbot` and the project to `messpbot`.

Open `/mit/[lockername]/web_scripts/[path]/index.fcgi` and after

```python
os.environ['DJANGO_SETTINGS_MODULE'] ...
```

add

```python
import django
django.setup()
```

Then delete

```python
from django.core.servers.fastcgi import runfastcgi
runfastcgi(method="threaded", daemonize="false")
```

Then add at the end

```python
from flup.server.fcgi import WSGIServer
from django.core.handlers.wsgi import WSGIHandler
WSGIServer(WSGIHandler()).run()
```

Then clone the repository into `/mit/[lockername]/Scripts/django/`. Now, all other directories used along the way may be deleted. Make sure to install all `python` dependencies in `requirements.txt` before proceeding. While `pip` is not available on the Athena dialup connection, `pip` may be used on the `scripts` connection. The, the Django server may be started by running

```bash
python manage.py runserver
```

This starts the Django server on `localhost:8000`. You may wish to run it in a `tmux` module in the background. In order to make it web accessible, we'll need to tunnel it. For this project, we will use `serveo.net`. This tunnel is easily established by running

```bash
ssh -R pharos-service:80:localhost:8000 serveo.net
```

which points `pharos-service.serveo.net` to `localhost:8000`. If that doesn't work, try replacing `localhost` with `127.0.0.1`. In order to stop the connection from dropping, it would be helpful to run `autossh` <https://www.harding.motd.ca/autossh/> instead of `ssh`, which you may `wget` into `/mit/[lockername]/Scripts/django/`. The `serveo` tunnel is probably best kept in a `tmux` module as well.

Finally, updates to `master` will update the Django server automatically, but still need pulling. Automatic pulling from `athena` with a `tmux` module will fail once the connection expires, and automatic pulling from the `scripts` server is slightly more difficult. For now, updates will need to be manually pulled.

## Developing

During development, you may use the host `pharos-service-test.serveo.net`, with the same `ssh` command above.

## Todo

Currently, static files are not being served in `debug = False`, so `debug = True` is turned on. However, this should be fixed ASAP.
