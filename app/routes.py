# import config
from __future__ import print_function
import sys
from flask import render_template, flash, redirect, session, url_for, request, \
    g, jsonify, make_response, abort
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
    print('received message:', file=sys.stderr)
    return make_response(jsonify({'status_code': status_code['login_faild']}), 401)

@app.before_request
def before_request():
    g.user = current_user

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)

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
@login_required
def get_nodes():
    return jsonify({'nodes': [
            { 'id': 1, 'name': 'rpi-1' },
            { 'id': 2, 'name': 'rpi-2' },
            { 'id': 3, 'name': 'rpi-3' }
        ]})

@app.route('/api/v1/nodes/<int:node_id>', methods=['GET'])
@login_required
def get_node(node_id):
    if not request.json:
        abort(400)

@app.route('/api/v1/nodes', methods=['POST'])
@login_required
def create_node():
    if not request.json or not 'title' in request.json:
        abort(400)
    return jsonify({'node': [
            { 'id': 1, 'name': 'rpi-1' }
        ]})

@app.route('/api/v1/rcs', methods=['GET'])
# @login_required
def get_rcs():
    rc = RemoteControl()
    return jsonify({'rcs': rc.getRemotesList()})

@app.route('/api/v1/rcs', methods=['POST'])
# @login_required
def create_rc():
    if not request.json or not 'name' in request.json or not 'icon' in request.json or not 'order' in request.json or not 'public' in request.json:
        abort(400)

    rc = RemoteControl()
    result = rc.create(request.json)
    return jsonify({'rc': result}), 201

@app.route('/api/v1/rcs/<int:rc_id>', methods=['GET'])
# @login_required
def get_rc(rc_id):
    rc = RemoteControl(rc_id)
    result = rc.get()

    if result is None:
        abort(404)
    return jsonify({'rc': result})

@app.route('/api/v1/rcs/<int:rc_id>', methods=['PUT'])
# @login_required
def update_rc(rc_id):
    rc = RemoteControl(rc_id)
    result = rc.get()

    if result is None:
        abort(404)
    if not request.json or not 'name' in request.json or not 'icon' in request.json or not 'order' in request.json or not 'public' in request.json:
        abort(400)
    
    result = rc.update(request.json)
    return jsonify({'rc': result})

@app.route('/api/v1/rcs/<int:rc_id>/buttons', methods=['GET'])
# @login_required
def get_rc_buttons(rc_id):
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
