# from __future__ import print_function
# import sys
import time
from flask import Flask
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

# from app import routes
from app import routes, models, sockets
import threading
from threading import Lock

from drivers import wire_recive
t1 = None
thread_lock = Lock()

@app.before_first_request
def before_first_request():
    t1 = threading.Thread(target=wire_recive.read_signal)
    t1.start()

# with thread_lock:
#     if t1 is None:
#         t1 = threading.Thread(target=wire_recive.read_signal)
#         t1.start()
