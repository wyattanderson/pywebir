# pywebir

`pywebir` is the preliminary name for a web-based infrared control system I'm
working on that's primarily designed for controlling in-window air
conditioners. It uses a [USB IR
Toy](http://dangerousprototypes.com/docs/USB_Infrared_Toy) and a [Raspberry
Pi](http://www.raspberrypi.org/) to accomplish the task.

This is a toy project and as such is needlessly complex: it uses Redis as
a datastore and message queue for a Celery distributed task worker that
actually sends the IR commands as they occur. So, it's pretty fast, consistent
and commands will always execute in order, but there's a fair bit of setup
involved.

## Screenshot

![iPhone 5](http://wyattanderson.github.io/pywebir/screenshot.png)

## Making it work on Arch

Install Arch on your RaspberryPi. You can use Raspbian if you want, but uWSGI
won't work since the Raspbian Python package doesn't include a shared library.

    # pacman -Syu
    # pacman -S nodejs python2 python2-virtualenv base-devel redis tmux

You'll also need to either run all of this as `root` or add a user for
yourself. Make sure the new user is in the `uucp` group so that it can access
the serial port:

    # useradd -G wheel,uucp -m <YOUR USER>
    # passwd <YOUR USER>

Clone the `pywebir` repo and set up a virtualenv:

    $ git clone git@github.com:wyattanderson/pywebir.git
    $ cd pywebir
    $ virtualenv-2.7 env
    $ source env/bin/activate
    $ pip install -r requirements.txt

Sit back and relax. This'll take some time. When you're done, then install the
necessary NodeJS packages for building the static assets:

    # sudo npm install -g uglify-js coffee-script stylus nib

Take a look at the `settings.py` file and either edit that file or add your
own `webapp.cfg` file to the `webapp/` directory. Then, build the assets and
start the server:

    $ python manage.py assets build
    $ tmux uwsgi -y webapp/uwsgi.yaml --env PYWEBIR_SETTINGS=webapp.cfg

Then, you can access the web interface at `http://alarmpi:5000/` (or whatever
your RPi's hostname/IP is).
