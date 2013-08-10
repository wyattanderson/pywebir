import base64
import json
import os
import pickle
import serial
import time

from flask import render_template, jsonify, url_for
from state import ACState
from tasks.ir import send_ir_command
from webapp import app, redis

BUTTON_DIR = os.path.join(os.path.dirname(__file__), 'button_json')
buttons = dict()
for button_file in os.listdir(BUTTON_DIR):
    button_file = os.path.abspath(
            os.path.join(BUTTON_DIR, button_file))

    with open(button_file, 'r') as f:
        button_data = json.load(f)
        buttons[button_data['id']] = button_data

def get_state():
    state = None
    if redis.exists(app.config['REDIS_SETTINGS_KEY']):
        state = pickle.loads(redis.get(
            app.config['REDIS_SETTINGS_KEY']))
    else:
        state = ACState()
    return state

def save_state(state):
    redis.set(app.config['REDIS_SETTINGS_KEY'],
              pickle.dumps(state))

@app.route("/")
def index():
    global buttons
    state = get_state()

    config = {
            'buttons': buttons.values(),
            'state': state.export(),
            'apiUrl': url_for('.do_button', button='PLACEHOLDER'),
            }
    return render_template('index.jade', config=config)

@app.route("/do-button/<button>/")
def do_button(button):
    global buttons
    state = get_state()

    should_send = state.apply_button(button)
    save_state(state)

    button_data = buttons[button]
    buf = bytearray(base64.b64decode(button_data['irdata']))
    if should_send:
        send_ir_command.delay(buf)
    return jsonify(state.export())

@app.route("/state/")
def state():
    state = get_state()
    return jsonify(state.export())
