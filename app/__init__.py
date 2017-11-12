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

from app import routes, models, sockets
import threading
from drivers import wire_recive

# @app.before_first_request
# def before_first_request():
#     t1 = threading.Thread(target=wire_recive.read_signal)
#     t1.start()
