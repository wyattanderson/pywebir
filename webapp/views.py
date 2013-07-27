import os
import json
import base64
import serial
import time

from flask import render_template, jsonify, url_for
from state import ACState
from tasks.ir import send_ir_command
from webapp import app

BUTTON_DIR = os.path.join(os.path.dirname(__file__), 'button_json')
buttons = dict()
for button_file in os.listdir(BUTTON_DIR):
    button_file = os.path.abspath(
            os.path.join(BUTTON_DIR, button_file))

    with open(button_file, 'r') as f:
        button_data = json.load(f)
        buttons[button_data['id']] = button_data

state = ACState()
try:
    with open(os.path.join(os.path.dirname(__file__),
        'state.json'), 'r') as state_save:
        state_values = json.load(state_save)
        state.unexport(state_values)
except IOError, e:
    pass

@app.route("/")
def index():
    global buttons, state

    config = {
            'buttons': buttons.values(),
            'state': state.export(),
            'apiUrl': url_for('.do_button', button='PLACEHOLDER'),
            }
    return render_template('index.jade', config=config)

@app.route("/do-button/<button>/")
def do_button(button):
    global buttons, state

    should_send = state.apply_button(button)
    with open(os.path.join(os.path.dirname(__file__),
        'state.json'), 'w') as state_save:
        json.dump(state.export(), state_save)

    send_ir_command.delay('what')
    return jsonify(state.export())

    should_send = False
    if should_send:
        button_data = buttons[button]
        buf = bytearray(base64.b64decode(button_data['irdata']))
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

    return jsonify(state.export())

@app.route("/state/")
def get_state():
    global state
    return jsonify(state.export())
