import base64
import json
import os
import serial
import sys
import time

from redis import StrictRedis
from flask import Flask, render_template, jsonify, url_for
from flask.ext.assets import Environment, Bundle

from proxy import ReverseProxied

app = Flask(__name__)
app.config.from_object('webapp.settings')
if os.getenv('PYWEBIR_SETTINGS'):
    app.config.from_envvar('PYWEBIR_SETTINGS')

app.debug = os.getenv('DEBUG', 'true').lower() == 'true'
app.wsgi_app = ReverseProxied(app.wsgi_app)

assets = Environment(app)
assets.debug = app.debug
assets.auto_build = app.debug
app.config['STYLUS_PLUGINS'] = ['nib']

app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')

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

redis = StrictRedis(host=app.config['REDIS_HOST'],
                    port=app.config['REDIS_PORT'])

import views
