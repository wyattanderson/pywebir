import base64
import json
import os
import serial
import sys
import time

from flask import Flask, render_template, jsonify
from flask.ext.assets import Environment, Bundle

from state import ACState

app = Flask(__name__)
app.debug = os.getenv('DEBUG', 'true').lower() == 'true'

assets = Environment(app)
assets.debug = app.debug
assets.auto_build = app.debug
app.config['STYLUS_PLUGINS'] = ['nib']

BUTTON_DIR = os.path.join(os.path.dirname(__file__), 'button_json')
buttons = dict()
for button_file in os.listdir(BUTTON_DIR):
    button_file = os.path.abspath(
            os.path.join(BUTTON_DIR, button_file))

    with open(button_file, 'r') as f:
        button_data = json.load(f)
        buttons[button_data['id']] = button_data

app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')

state = ACState()
try:
    with open(os.path.join(os.path.dirname(__file__),
        'state.json'), 'r') as state_save:
        state_values = json.load(state_save)
        state.unexport(state_values)
except IOError, e:
    pass

def sleep():
    time.sleep(0.05)

@app.route("/")
def index():
    global buttons, state

    config = {
            'buttons': buttons.values(),
            'state': state.export(),
            }
    return render_template('index.jade', config=config)

@app.route("/do-button/<button>/")
def do_button(button):
    global buttons, state

    should_send = state.apply_button(button)
    with open(os.path.join(os.path.dirname(__file__),
        'state.json'), 'w') as state_save:
        json.dump(state.export(), state_save)

    # if should_send:
    #     button_data = buttons[button]
    #     buf = bytearray(base64.b64decode(button_data['irdata']))
    #     sp = serial.Serial('/dev/ttyACM0')
    #     sp.write("\0\0\0\0\0")
    #     sleep()
    #     sp.write("S")
    #     sleep()
    #     sp.write("\x03")
    #     sleep()
    #     sp.write(buf)
    #     sleep()
    #     sp.write("\0")
    #     sleep()
    #     sp.write("S")
    #     sleep()
    #     sp.close()

    return jsonify(state.export())

@app.route("/state/")
def get_state():
    global state
    return jsonify(state.export())

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
