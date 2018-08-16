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
from .helpers import RcHelper, ButtonHelper, NodeHelper
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
    return jsonify({'result': True})

# Nodes routes
@app.route('/api/v1/nodes', methods=['GET'])
# @login_required
def get_nodes():
    nh = NodeHelper()
    return jsonify({'rcs': nh.getNodes()})

@app.route('/api/v1/nodes', methods=['POST'])
# @login_required
def create_node():
    if not request.json or not 'name' in request.json or not 'host_name' in request.json or not 'order' in request.json:
        abort(400)

    nh = NodeHelper()
    node = nh.createNode(request.json)
    return jsonify({'node': node}), 201

@app.route('/api/v1/nodes/<int:node_id>', methods=['GET'])
# @login_required
def get_node(node_id):
    nh = NodeHelper(node_id)
    node = nh.getNode()

    if node is None:
        abort(404)

    return jsonify({'node': node})

@app.route('/api/v1/nodes/<int:node_id>', methods=['PUT'])
# @login_required
def update_node(node_id):
    nh = NodeHelper(node_id)

    if not request.json or not 'name' in request.json or not 'host_name' in request.json or not 'order' in request.json:
        abort(400)
    
    node = nh.updateNode(request.json)

    if node is None:
        abort(404) 

    return jsonify({'node': node})

@app.route('/api/v1/nodes/<int:node_id>', methods=['DELETE'])
# @login_required
def delete_node(node_id):
    nh = NodeHelper(node_id)
    result = nh.deleteNode()

    if result is None:
        abort(404)
    
    return jsonify({'result': result})

# Rc routes
@app.route('/api/v1/rcs', methods=['GET'])
# @login_required
def get_rcs():
    rch = RcHelper()
    return jsonify({'rcs': rch.getRcs()})

@app.route('/api/v1/rcs', methods=['POST'])
# @login_required
def create_rc():
    if not request.json or not 'name' in request.json or not 'icon' in request.json or not 'order' in request.json or not 'public' in request.json:
        abort(400)

    rch = RcHelper()
    rc = rch.createRc(request.json)
    return jsonify({'rc': rc}), 201

@app.route('/api/v1/rcs/<int:rc_id>', methods=['GET'])
# @login_required
def get_rc(rc_id):
    rch = RcHelper(rc_id)
    rc = rch.getRc()

    if rc is None:
        abort(404)

    return jsonify({'rc': rc})

@app.route('/api/v1/rcs/<int:rc_id>', methods=['PUT'])
# @login_required
def update_rc(rc_id):
    rch = RcHelper(rc_id)

    if not request.json or not 'name' in request.json or not 'icon' in request.json or not 'order' in request.json or not 'public' in request.json:
        abort(400)
    
    rc = rch.updateRc(request.json)

    if rc is None:
        abort(404) 

    return jsonify({'rc': rc})

@app.route('/api/v1/rcs/<int:rc_id>', methods=['DELETE'])
# @login_required
def delete_rc(rc_id):
    rch = RcHelper(rc_id)
    result = rch.deleteRc()

    if result is None:
        abort(404)
    
    return jsonify({'result': result})

# Buttons routes
@app.route('/api/v1/rcs/<int:rc_id>/buttons', methods=['GET'])
# @login_required
def get_rc_buttons(rc_id):
    bh = ButtonHelper(rc_id)
    buttons = bh.getButtons()

    if buttons is None:
        abort(404)

    return jsonify({'buttons': buttons}), 201

@app.route('/api/v1/rcs/<int:rc_id>/buttons', methods=['POST'])
# @login_required
def create_rc_button(rc_id):
    bh = ButtonHelper(rc_id)
    
    if not request.json or not 'name' in request.json or not 'order_hor' in request.json or not 'order_ver' in request.json or not 'color' in request.json or not 'command' in request.json or not 'radio_id' in request.json or not 'type' in request.json:
        abort(400)

    button = bh.createButton(request.json)

    if button is None:
        abort(404)

    return jsonify({'button': button}), 201

@app.route('/api/v1/rcs/<int:rc_id>/buttons/<int:btn_id>', methods=['GET'])
# @login_required
def get_rc_button(rc_id, btn_id):
    bh = ButtonHelper(rc_id, btn_id)
    button = bh.getButton()

    if button is None:
        abort(404)

    return jsonify({'button': button})

@app.route('/api/v1/rcs/<int:rc_id>/buttons/<int:btn_id>', methods=['PUT'])
# @login_required
def update_rc_button(rc_id, btn_id):
    bh = ButtonHelper(rc_id, btn_id)
    
    if not request.json or not 'name' in request.json or not 'order_hor' in request.json or not 'order_ver' in request.json or not 'color' in request.json or not 'command' in request.json or not 'radio_id' in request.json or not 'type' in request.json:
        abort(400)

    button = bh.updateButton(request.json)

    if button is None:
        abort(404)

    return jsonify({'button': button})

@app.route('/api/v1/rcs/<int:rc_id>/buttons/<int:btn_id>', methods=['DELETE'])
# @login_required
def delete_rc_button(rc_id, btn_id):
    bh = ButtonHelper(rc_id, btn_id)
    result = bh.deleteButton()

    if result is None:
        abort(404)

    return jsonify({'result': result})

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
