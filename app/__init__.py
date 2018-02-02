from __future__ import print_function
import os, sys
from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
so = SocketIO(app)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

from app import routes, models, sockets
import threading
from drivers import wire_recive
# from run import debug, ar
# from drivers.arduino import Arduino
# ar = 'popopo'
# if not debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
#     ar = Arduino.Instance()
#     ar.test()

# from drivers.arduino import Arduino
# from run import ser
# print('0000', file=sys.stderr)
# arduino.serial_connect()

# @app.before_first_request
# def before_first_request():
#     arduino = Arduino()

    # t1 = threading.Thread(target=wire_recive.read_signal)
    # t1.start()
