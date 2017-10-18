# import config
from __future__ import print_function
import sys
from flask import render_template, flash, redirect, session, url_for, request, \
    g, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm, so
from .models import User
# from gpio import driver
from config import devices, status_code
from threading import Lock
from flask_socketio import emit, send
from threading import Lock


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@lm.unauthorized_handler
def unauthorized():
    return jsonify({'status_code': status_code['login_faild']}), 401

@app.before_request
def before_request():
    g.user = current_user

# Roure for start Framework7
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/v1.0/login', methods=['POST'])
def login():
    if g.user is not None and g.user.is_authenticated:
        return jsonify({'status_code': status_code['alredy_logedin']})

    if 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user is not None and user.password == password:
            session['remember_me'] = True
            login_user(user)
            return jsonify({'status_code': status_code['login_success']})

        return jsonify({'status_code': status_code['login_faild']})

    return jsonify({'status_code': status_code['login_faild']}), 401

@app.route('/api/v1.0/logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify({'status_code': status_code['logout']})

# thread = None
# thread_lock = Lock()

# def background_thread():
#     """Example of how to send server generated events to clients."""
#     count = 0
#     while True:
#         so.sleep(20)
#         count += 1
#         so.emit('json',
#                       {'data': 'Server generated event', 'count': count},
#                       namespace='/remotes')

# @so.on('connect', namespace='/remotes')
# def test_connect():
#     global thread
#     with thread_lock:
#         if thread is None:
#             thread = so.start_background_task(target=background_thread)
#     emit('json', {'data': 'Connected', 'count': 0})

# @so.on('message', namespace='/remotes')
# def handle_message(message):
#     print('received message: ' + message, file=sys.stderr)
