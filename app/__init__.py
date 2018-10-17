from flask import Flask, redirect, session, request, g, jsonify, make_response, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_migrate import Migrate
from app.starter import Config

flask_app = Flask(__name__)
config = Config(flask_app)
CORS(flask_app)

db = SQLAlchemy(flask_app)
mg = Migrate(flask_app, db)
so = SocketIO(flask_app)
lm = LoginManager()
lm.init_app(flask_app)

from app import service
from app.helpers import RcHelper, ButtonHelper, NodeHelper, ArduinoHelper, RadioHelper, SocketEvent
from app.models import User

serv = service.Service(config)

@flask_app.before_first_request
def before_first_request():
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

@flask_app.route('/api/v1/login', methods=['POST'])
def login():
    if g.user is not None and g.user.is_authenticated:
        return jsonify({'result': True})

    if 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

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

# Home
# @flask_app.route('/api/v1/home', methods=['GET'])
# # @login_required
# def get_rcs():
#     rch = RcHelper()
#     return jsonify({'rcs': rch.getRcs()})

# Rc routes
@flask_app.route('/api/v1/rcs', methods=['GET'])
# @login_required
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

    return jsonify({'rc': rc})

@flask_app.route('/api/v1/rcs/<int:rc_id>', methods=['DELETE'])
@login_required
def delete_rc(rc_id):
    rch = RcHelper(rc_id)
    result = rch.deleteRc()

    if result is None:
        abort(404)
    
    return jsonify({'result': result})

# Button routes
@flask_app.route('/api/v1/rcs/<int:rc_id>/buttons', methods=['GET'])
@login_required
def get_rc_buttons(rc_id):
    bh = ButtonHelper(rc_id)
    buttons = bh.getButtons()

    if buttons is None:
        abort(404)

    return jsonify({'buttons': buttons})

@flask_app.route('/api/v1/rcs/<int:rc_id>/buttons', methods=['POST'])
@login_required
def create_rc_button(rc_id):
    bh = ButtonHelper(rc_id)
    
    if not request.json or not 'name' in request.json or not 'order_hor' in request.json or not 'order_ver' in request.json or not 'color' in request.json or not 'execute' in request.json or not 'radio_id' in request.json or not 'node_id' in request.json or not 'arduino_id' in request.json or not 'type' in request.json:
        abort(400)

    button = bh.createButton(request.json)

    if button is None:
        abort(404)

    return jsonify({'button': button}), 201

@flask_app.route('/api/v1/rcs/<int:rc_id>/buttons/<int:btn_id>', methods=['GET'])
@login_required
def get_rc_button(rc_id, btn_id):
    bh = ButtonHelper(rc_id, btn_id)
    button = bh.getButton()

    if button is None:
        abort(404)

    return jsonify({'button': button})

@flask_app.route('/api/v1/rcs/<int:rc_id>/buttons/<int:btn_id>', methods=['PUT'])
@login_required
def update_rc_button(rc_id, btn_id):
    bh = ButtonHelper(rc_id, btn_id)
    
    if not request.json or not 'name' in request.json or not 'order_hor' in request.json or not 'order_ver' in request.json or not 'color' in request.json or not 'execute' in request.json or not 'radio_id' in request.json or not 'node_id' in request.json or not 'arduino_id' in request.json or not 'type' in request.json:
        abort(400)

    button = bh.updateButton(request.json)

    if button is None:
        abort(404)

    return jsonify({'button': button})

@flask_app.route('/api/v1/rcs/<int:rc_id>/buttons/<int:btn_id>', methods=['DELETE'])
@login_required
def delete_rc_button(rc_id, btn_id):
    bh = ButtonHelper(rc_id, btn_id)
    result = bh.deleteButton()

    if result is None:
        abort(404)

    return jsonify({'result': result})

@flask_app.route('/api/v1/rcs/<int:rc_id>/buttons/<int:btn_id>/push', methods=['GET'])
@login_required
def push_rc_button(rc_id, btn_id):
    # sys.stderr.write(str(g.user))
    event = SocketEvent()
    event.user_id = g.user.id
    bh = ButtonHelper(rc_id, btn_id)
    result = bh.pushButton(serv.node_sevice, event)

    if result is None:
        abort(404)

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

    if not request.json or not 'name' in request.json or not 'host_name' in request.json or not 'order' in request.json:
        abort(400)
    
    node = nh.updateNode(request.json)

    if node is None:
        abort(404) 

    return jsonify({'node': node})

@flask_app.route('/api/v1/nodes/<int:node_id>', methods=['DELETE'])
@login_required
def delete_node(node_id):
    nh = NodeHelper(node_id)
    result = nh.deleteNode()

    if result is None:
        abort(404)
    
    return jsonify({'result': result})

# Arduino routes
@flask_app.route('/api/v1/nodes/<int:node_id>/arduinos', methods=['GET'])
@login_required
def get_node_arduinos(node_id):
    ah = ArduinoHelper(node_id)
    arduinos = ah.getArduinos()

    if arduinos is None:
        abort(404)

    return jsonify({'arduinos': arduinos})

@flask_app.route('/api/v1/nodes/<int:node_id>/arduinos', methods=['POST'])
@login_required
def create_node_arduino(node_id):
    ah = ArduinoHelper(node_id)
    
    if not request.json or not 'usb' in request.json or not 'mode' in request.json or not 'name' in request.json or not 'order' in request.json:
        abort(400)

    arduino = ah.createArduino(request.json)

    if arduino is None:
        abort(404)

    return jsonify({'arduino': arduino}), 201

@flask_app.route('/api/v1/nodes/<int:node_id>/arduinos/<int:arduino_id>', methods=['GET'])
@login_required
def get_node_arduino(node_id, arduino_id):
    ah = ArduinoHelper(node_id, arduino_id)
    arduino = ah.getArduino()

    if arduino is None:
        abort(404)

    return jsonify({'arduino': arduino})

@flask_app.route('/api/v1/nodes/<int:node_id>/arduinos/<int:arduino_id>', methods=['PUT'])
@login_required
def update_node_arduino(node_id, arduino_id):
    ah = ArduinoHelper(node_id, arduino_id)
    
    if not request.json or not 'usb' in request.json or not 'mode' in request.json or not 'name' in request.json or not 'order' in request.json:
        abort(400)

    arduino = ah.updateArduino(request.json)

    if arduino is None:
        abort(404)

    return jsonify({'arduino': arduino})

@flask_app.route('/api/v1/nodes/<int:node_id>/arduinos/<int:arduino_id>', methods=['DELETE'])
@login_required
def delete_node_arduino(node_id, arduino_id):
    ah = ArduinoHelper(node_id, arduino_id)
    result = ah.deleteArduino()

    if result is None:
        abort(404)

    return jsonify({'result': result})

# Radio routes
@flask_app.route('/api/v1/radios', methods=['GET'])
@login_required
def get_radios():
    rh = RadioHelper()
    return jsonify({'radios': rh.getRadios()})

@flask_app.route('/api/v1/radios', methods=['POST'])
@login_required
def create_radio():
    if not request.json or not 'arduino_id' in request.json or not 'pipe' in request.json or not 'name' in request.json or not 'enabled' in request.json or not 'order' in request.json:
        abort(400)

    rh = RadioHelper()
    radio = rh.createRadio(request.json)
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

    if not request.json or not 'arduino_id' in request.json or not 'pipe' in request.json or not 'name' in request.json or not 'enabled' in request.json or not 'order' in request.json:
        abort(400)
    
    radio = rh.updateRadio(request.json)

    if radio is None:
        abort(404) 

    return jsonify({'radio': radio})

@flask_app.route('/api/v1/radios/<int:radio_id>', methods=['DELETE'])
@login_required
def delete_radio(radio_id):
    rh = RadioHelper(radio_id)
    result = rh.deleteRadio()

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
