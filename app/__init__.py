import os, functools, json, logging
from flask import Flask, redirect, session, request, g, jsonify, make_response, abort, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from flask_migrate import Migrate
from app.bootstrap import Config
from threading import Lock

flask_app = Flask(__name__)
config = Config(flask_app)
CORS(flask_app, supports_credentials=True)

db = SQLAlchemy(flask_app)
mg = Migrate(flask_app, db)
so = SocketIO(flask_app)
lm = LoginManager()
lm.init_app(flask_app)

from app import service
from app.helpers import RcHelper, ButtonHelper, NodeHelper, ArduinoHelper, RadioHelper
from app.models import User

serv = service.Service(config)

@flask_app.before_first_request
def activate_services():
    serv.activateDiscoverService()
    serv.activateNodeService()

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@lm.unauthorized_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized'}), 401)

@flask_app.before_request
def before_request():
    g.user = current_user

@flask_app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@flask_app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)

@flask_app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(flask_app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@flask_app.route('/api/v1/login', methods=['POST'])
def login():
    if g.user is not None and g.user.is_authenticated:
        return jsonify({'result': True})

    if request.json and 'username' in request.json and 'password' in request.json:
        username = request.json['username']
        password = request.json['password']

        user = User.query.filter_by(username=username).first()

        if user is not None and user.password == password:
            session['remember_me'] = True
            login_user(user)

            return jsonify({'result': True})

    return jsonify({'result': False}), 403

@flask_app.route('/api/v1/logout', methods=['GET'])
def logout():
    logout_user()
    return jsonify({'result': True})

@login_required
@flask_app.route('/api/v1/user', methods=['GET'])
def get_user():
    return jsonify({'username': g.user.username})

# Rc routes
@flask_app.route('/api/v1/rcs', methods=['GET'])
@login_required
def get_rcs():
    rch = RcHelper()
    return jsonify({'rcs': rch.getRcs()})

@flask_app.route('/api/v1/rcs', methods=['POST'])
@login_required
def create_rc():
    if not request.json or not 'name' in request.json or not 'icon' in request.json or not 'order' in request.json or not 'public' in request.json:
        abort(400)

    rch = RcHelper()
    rc = rch.createRc(request.json)
    so.emit('updateRcs', {'rcs': rch.getRcs()}, broadcast=True)
    return jsonify({'rc': rc}), 201

@flask_app.route('/api/v1/rcs/<int:rc_id>', methods=['GET'])
@login_required
def get_rc(rc_id):
    rch = RcHelper(rc_id)
    rc = rch.getRc()

    if rc is None:
        abort(404)

    return jsonify({'rc': rc})

@flask_app.route('/api/v1/rcs/<int:rc_id>', methods=['PUT'])
@login_required
def update_rc(rc_id):
    rch = RcHelper(rc_id)

    if not request.json or not 'name' in request.json or not 'icon' in request.json or not 'order' in request.json or not 'public' in request.json:
        abort(400)
    
    rc = rch.updateRc(request.json)

    if rc is None:
        abort(404) 

    so.emit('updateRcs', {'rcs': rch.getRcs()}, broadcast=True)
    return jsonify({'rc': rc})

@flask_app.route('/api/v1/rcs/<int:rc_id>', methods=['DELETE'])
@login_required
def delete_rc(rc_id):
    rch = RcHelper(rc_id)
    result = rch.deleteRc()

    if result is None:
        abort(404)
    
    so.emit('updateRcs', {'rcs': rch.getRcs()}, broadcast=True)
    return jsonify({'result': result})

@flask_app.route('/api/v1/rcs/<int:rc_id>/buttons', methods=['GET'])
@login_required
def get_rc_buttons(rc_id):
    rch = RcHelper(rc_id)
    buttons = rch.getButtons()

    if buttons is None:
        abort(404)

    return jsonify({'buttons': buttons})

# Button routes
@flask_app.route('/api/v1/buttons', methods=['POST'])
@login_required
def create_button():
    bh = ButtonHelper()
    
    if not request.json or not 'rc_id' in request.json or not 'name' in request.json or not 'order_hor' in request.json or not 'order_ver' in request.json or not 'color' in request.json or not 'message' in request.json or not 'type' in request.json or not 'radio_id' in request.json:
        abort(400)

    button = bh.createButton(request.json)

    if button is None:
        abort(404)

    rch = RcHelper(request.json['rc_id'])
    so.emit('updateButtons', {'rc_id': button['rc_id'], 'buttons': rch.getButtons()}, broadcast=True)
    return jsonify({'button': button}), 201

@flask_app.route('/api/v1/buttons/<int:btn_id>', methods=['GET'])
@login_required
def get_button(btn_id):
    bh = ButtonHelper(btn_id)
    button = bh.getButton()

    if button is None:
        abort(404)

    return jsonify({'button': button})

@flask_app.route('/api/v1/buttons/<int:btn_id>', methods=['PUT'])
@login_required
def update_button(btn_id):
    bh = ButtonHelper(btn_id)
    
    if not request.json or not 'name' in request.json or not 'order_hor' in request.json or not 'order_ver' in request.json or not 'color' in request.json or not 'message' in request.json or not 'type' in request.json or not 'radio_id' in request.json:
        abort(400)

    button = bh.updateButton(request.json)

    if button is None:
        abort(404)

    rch = RcHelper(bh.get().rc_id)
    so.emit('updateButtons', {'rc_id': button['rc_id'], 'buttons': rch.getButtons()}, broadcast=True)
    return jsonify({'button': button})

@flask_app.route('/api/v1/buttons/<int:btn_id>', methods=['DELETE'])
@login_required
def delete_button(btn_id):
    bh = ButtonHelper(btn_id)
    button = bh.deleteButton()

    if button is None:
        abort(404)

    so.emit('updateButtons', {'rc_id': button['rc_id'], 'buttons': bh.getButtons()}, broadcast=True)
    return jsonify({'result': True})

@flask_app.route('/api/v1/buttons/<int:btn_id>/push', methods=['GET'])
@login_required
def push_button(btn_id):
    bh = ButtonHelper(btn_id)
    button = bh.getButton()

    if bh.get() is None:
        abort(404)

    if bh.get().type == 'radio':
        logging.info(bh.getHostName())
        event = {
            'event': 'pushButton',
            'user_id': g.user.id,
            'button_id': bh.get().id,
            'host_name': bh.getHostName()
        }
        result = serv.node_sevice.pushToNode(event)

    return jsonify({'result': result})

# Node routes
@flask_app.route('/api/v1/nodes', methods=['GET'])
@login_required
def get_nodes():
    nh = NodeHelper()
    return jsonify({'nodes': nh.getNodes()})

@flask_app.route('/api/v1/nodes', methods=['POST'])
@login_required
def create_node():
    if not request.json or not 'name' in request.json or not 'host_name' in request.json or not 'order' in request.json:
        abort(400)

    nh = NodeHelper()
    node = nh.createNode(request.json)
    so.emit('updateNodes', {'nodes': nh.getNodes()}, broadcast=True)
    return jsonify({'node': node}), 201

@flask_app.route('/api/v1/nodes/<int:node_id>', methods=['GET'])
@login_required
def get_node(node_id):
    nh = NodeHelper(node_id)
    node = nh.getNode()

    if node is None:
        abort(404)

    return jsonify({'node': node})

@flask_app.route('/api/v1/nodes/<int:node_id>', methods=['PUT'])
@login_required
def update_node(node_id):
    nh = NodeHelper(node_id)

    if not request.json or not 'host_name' in request.json or not 'order' in request.json:
        abort(400)
    
    node = nh.updateNode(request.json)

    if node is None:
        abort(404) 

    so.emit('updateNodes', {'nodes': nh.getNodes()}, broadcast=True)
    return jsonify({'node': node})

@flask_app.route('/api/v1/nodes/<int:node_id>', methods=['DELETE'])
@login_required
def delete_node(node_id):
    nh = NodeHelper(node_id)
    result = nh.deleteNode()

    if result is None:
        abort(404)
    
    so.emit('updateNodes', {'nodes': nh.getNodes()}, broadcast=True)
    return jsonify({'result': result})

# Arduino routes
@flask_app.route('/api/v1/arduinos', methods=['GET'])
@login_required
def get_arduinos():
    ah = ArduinoHelper()
    arduinos = ah.getArduinos()

    if arduinos is None:
        abort(404)

    return jsonify({'arduinos': arduinos})

@flask_app.route('/api/v1/arduinos', methods=['POST'])
@login_required
def create_arduino():
    ah = ArduinoHelper()
    
    if not request.json or not 'usb' in request.json or not 'node_id' in request.json or not 'name' in request.json or not 'order' in request.json:
        abort(400)

    arduino = ah.createArduino(request.json)

    if arduino is None:
        abort(404)

    so.emit('updateArduinos', {'node_id': arduino['node_id'], 'arduinos': ah.getArduinos()}, broadcast=True)
    event = {
        'event': 'restart',
        'host_name': ah.getNode().host_name
    }
    if serv.node_sevice.pushToNode(event) == False:
        pass
        # so.emit('recievedIr', {'result': 'error', 'errors': 'Node is offline'})

    return jsonify({'arduino': arduino}), 201

@flask_app.route('/api/v1/arduinos/<int:arduino_id>', methods=['GET'])
@login_required
def get_arduino(arduino_id):
    ah = ArduinoHelper(arduino_id)
    arduino = ah.getArduino()

    if arduino is None:
        abort(404)

    return jsonify({'arduino': arduino})

@flask_app.route('/api/v1/arduinos/<int:arduino_id>', methods=['PUT'])
@login_required
def update_arduino(arduino_id):
    ah = ArduinoHelper(arduino_id)
    
    if not request.json or not 'usb' in request.json or not 'node_id' in request.json or not 'name' in request.json or not 'order' in request.json:
        abort(400)

    arduino = ah.updateArduino(request.json)

    if arduino is None:
        abort(404)

    so.emit('updateArduinos', {'node_id': arduino['node_id'], 'arduinos': ah.getArduinos()}, broadcast=True)
    event = {
        'event': 'restart',
        'host_name': ah.getNode().host_name
    }
    if serv.node_sevice.pushToNode(event) == False:
        pass
        # so.emit('recievedIr', {'result': 'error', 'errors': 'Node is offline'})
    
    return jsonify({'arduino': arduino})

@flask_app.route('/api/v1/arduinos/<int:arduino_id>', methods=['DELETE'])
@login_required
def delete_arduino(arduino_id):
    ah = ArduinoHelper(arduino_id)
    host_name = ah.getNode().host_name
    arduino = ah.deleteArduino()

    if arduino is None:
        abort(404)

    so.emit('updateArduinos', {'node_id': arduino['node_id'], 'arduinos': ah.getArduinos()}, broadcast=True)
    event = {
        'event': 'restart',
        'host_name': host_name
    }
    if serv.node_sevice.pushToNode(event) == False:
        pass
        # so.emit('recievedIr', {'result': 'error', 'errors': 'Node is offline'})

    return jsonify({'result': True})

# Radio routes
@flask_app.route('/api/v1/radios', methods=['GET'])
@login_required
def get_radios():
    rh = RadioHelper()
    return jsonify({'radios': rh.getRadios()})

@flask_app.route('/api/v1/radios', methods=['POST'])
@login_required
def create_radio():
    if not request.json or not 'arduino_id' in request.json or not 'type' in request.json or not 'name' in request.json or not 'pipe' in request.json or not 'order' in request.json or not 'on_request' in request.json or not 'expired_after' in request.json or not 'enabled' in request.json:
        abort(400)

    rh = RadioHelper()
    radio = rh.createRadio(request.json)

    so.emit('updateRadios', {'radios': rh.getRadios()}, broadcast=True)
    return jsonify({'radio': radio}), 201

@flask_app.route('/api/v1/radios/<int:radio_id>', methods=['GET'])
@login_required
def get_radio(radio_id):
    rh = RadioHelper(radio_id)
    radio = rh.getRadio()

    if radio is None:
        abort(404)

    return jsonify({'radio': radio})

@flask_app.route('/api/v1/radios/<int:radio_id>', methods=['PUT'])
@login_required
def update_radio(radio_id):
    rh = RadioHelper(radio_id)

    if not request.json or not 'pipe' in request.json or not 'name' in request.json or not 'enabled' in request.json or not 'order' in request.json:
        abort(400)
    
    radio = rh.updateRadio(request.json)

    if radio is None:
        abort(404) 

    so.emit('updateRadios', {'radios': rh.getRadios()}, broadcast=True)
    return jsonify({'radio': radio})

@flask_app.route('/api/v1/radios/<int:radio_id>', methods=['DELETE'])
@login_required
def delete_radio(radio_id):
    rh = RadioHelper(radio_id)
    result = rh.deleteRadio()

    if result is None:
        abort(404)
    
    so.emit('updateRadios', {'radios': rh.getRadios()}, broadcast=True)
    return jsonify({'result': result})

#############
# Socket io #
#############
def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped

@so.on('connect')
def handle_connect():
    id = request.sid
    logging.info("%s socket connected" % id)
    emit('customEmit', {'data': 'Connected', 'count': 0}, broadcast=True)

@so.on('json')
@authenticated_only
def handle_json(data):
    # Debug
    logging.info("received json: %s" % data)
    
    # if data['action'] == 'catch_ir_signal':
    #     # signal = ir_reader.read_signal()
    #     emit('json', {'response': {'result': 'success', 'callback': 'ir_signal', 'signal': '1500 800 800 800 1500 1500'}})


# thread = None
# thread_lock = Lock()

# def background_thread():
#     """Example of how to send server generated events to clients."""
#     count = 0
#     # status = True
#     while True:
#         so.sleep(20)
#         count += 1
#         so.emit('test', {'count': count}, broadcast=True)

        # if status:
        #     status = False
        #     event = {
        #         'event': 'stop',
        #         'host_name': 'rpi-node-1'
        #     }
        # else:
        #     status = True
        #     event = {
        #         'event': 'start',
        #         'host_name': 'rpi-node-1'
        #     }

        # event = {
        #         'event': 'restart',
        #         'host_name': 'rpi-node-1'
        #     }
        # if serv.node_sevice.pushToNode(event) == False:
        #     pass
            # so.emit('recievedIr', {'result': 'error', 'errors': 'Node is offline'})
        # nh = NodeHelper()
        # so.emit('updateNodes', {'nodes': nh.getNodes()}, broadcast=True)

# @so.on('connect')
# def test_connect():
#     global thread
#     with thread_lock:
#         if thread is None:
#             thread = so.start_background_task(target=background_thread)
    # so.emit('test', ('foo', 'bar'), broadcast=True)

@so.on('catch_ir')
def handle_catch_ir(json_data):
    data = json.loads(json_data)

    if 'node_id' in data:
        node = NodeHelper(data['node_id']).get()

        if node is not None:
            event = {
                'event': 'catchIr',
                'user_id': current_user.id,
                'host_name': node.host_name
            }

            if serv.node_sevice.pushToNode(event) == False:
                so.emit('recievedIr', {'result': 'error', 'errors': 'Node is offline'})

@so.on('emit_method')
def handle_emit_method(message):
    logging.info("received emit_method: %s" % message)
