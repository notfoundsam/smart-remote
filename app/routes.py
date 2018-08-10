# import config
from __future__ import print_function
import sys
from flask import render_template, flash, redirect, session, url_for, request, \
    g, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm, so
from .models import User
from config import status_code
from threading import Lock
from .remotes import RemoteControl
from .sensor import RadioSensor

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
# @app.route('/')
# def index():
#     return render_template('index.html')

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/api/v1/login', methods=['POST'])
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

        # return jsonify({'status_code': status_code['login_faild']}), 403

    return jsonify({'status_code': status_code['login_faild']}), 403

@app.route('/api/v1/logout', methods=['GET'])
def logout():
    logout_user()
    return jsonify({'status': 200})

@app.route('/api/v1/nodes', methods=['GET'])
def nodes():
    return jsonify({'nodes': [
            { 'id': 1, 'name': 'rpi-1' },
            { 'id': 2, 'name': 'rpi-2' },
            { 'id': 3, 'name': 'rpi-3' }
        ]})

@app.route('/api/v1/nodes/<int:node_id>', methods=['GET'])
def nodes(node_id):
    if not request.json:
        abort(400)
    return jsonify({'node': [
            { 'id': 1, 'name': 'rpi-1' }
        ]})

@app.route('/api/v1/nodes', methods=['POST'])
def nodes():
    if not request.json or not 'title' in request.json:
        abort(400)
    return jsonify({'node': [
            { 'id': 1, 'name': 'rpi-1' }
        ]})

@app.route('/api/v1/rcs', methods=['GET'])
def nodes():
    rc = RemoteControl()
    return jsonify({'rcs': rc.getRemotesList()})

@app.route('/api/v1/rcs/<int:rc_id>/buttons', methods=['GET'])
def nodes(rc_id):
    rc = RemoteControl(rc_id)
    return jsonify({'buttons': rc.getRemoteButtons(), 'rc': rc.getRemoteAttr()})

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
