import os
import serial
import sys
import time

from flask import Flask, render_template
from flask.ext.assets import Environment, Bundle
app = Flask(__name__)
app.debug = os.getenv('DEBUG', 'true').lower() == 'true'

assets = Environment(app)
assets.debug = app.debug
assets.auto_build = app.debug

BIN_DIR = 'bins'
bins = dict()
for binfile in os.listdir(BIN_DIR):
    binfile = os.path.abspath(
            os.path.join(BIN_DIR, binfile))
    with open(binfile, 'r') as f:
        (root, ext) = os.path.splitext(
                os.path.basename(binfile))
        bins[root] = f.read()

app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')

def sleep():
    time.sleep(0.05)

@app.route("/")
def index():
    global bins

    config = {
            'bins': sorted([dict(id=key) for key in bins.keys()]),
            }
    return render_template('index.jade', config=config)

@app.route("/do-bin/<bin_name>/")
def do_bin(bin_name):
    return "OK"
    with open(os.path.join(BIN_DIR, "%s.bin" % bin_name), 'r') as f:
        buf = bytearray(f.read())
        sp = serial.Serial('/dev/ttyACM0')
        sp.write("\0\0\0\0\0")
        sleep()
        sp.write("S")
        sleep()
        sp.write("\x03")
        sleep()
        sp.write(buf)
        sleep()
        sp.write("\0")
        sleep()
        sp.write("S")
        sleep()
        sp.close()

    return "OK"

css = Bundle(
        'stylus/base.styl',
        filters='stylus',
        output='assets/css/base.css',
        debug=False)
assets.register('css', css)

coffee = Bundle(
        'coffee/app.coffee',
        filters='coffeescript',
        output='assets/js/app.js')
js = Bundle(
        'js/jquery-2.0.3.js',
        'js/underscore.js',
        'js/backbone.js',
        'js/backbone.marionette.js',
        'js/fastclick.js',
        coffee,
        filters='uglifyjs',
        output='assets/js/base.js')
assets.register('js', js)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
