import os, functools, json, logging, socket
from flask import Flask, redirect, session, request, g, jsonify, make_response, abort, send_from_directory
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_socketio import SocketIO, emit, disconnect
from flask_cors import CORS
from app.bootstrap import Config, Cache
from threading import Lock

flask_app = Flask(__name__)
config = Config(flask_app)
cache = Cache()

CORS(flask_app, supports_credentials=True)

so = SocketIO(flask_app)
lm = LoginManager()
lm.init_app(flask_app)

from app import service
from app.helpers import RcHelper, ButtonHelper, NodeHelper, ArduinoHelper, RadioHelper
from app.models import User

serv = service.Service()

so_clients = {}

@flask_app.before_first_request
def activate_services():
    serv.activateDiscoverService()
    serv.activateNodeService()

@lm.user_loader
def load_user(id):
    db_session = config.getNewDbSession()
    # if not id:
    #     return make_response(jsonify({'error': 'Unauthorized'}), 401)

    user = db_session.query(User).get(int(id))
    db_session.close()
    return user

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

        db_session = config.getNewDbSession()
        user = db_session.query(User).filter_by(username=username).first()
        db_session.close()

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
    db_session = config.getNewDbSession()
    rch = RcHelper(db_session)
    rcs = rch.getRcs()
    db_session.close()
    return jsonify({'rcs': rcs})

@flask_app.route('/api/v1/rcs', methods=['POST'])
@login_required
def create_rc():
    if not request.json or not 'name' in request.json or not 'icon' in request.json or not 'order' in request.json or not 'public' in request.json:
        abort(400)

    db_session = config.getNewDbSession()
    rch = RcHelper(db_session)
    rc = rch.createRc(request.json)
    rcs = rch.getRcs()
    db_session.close()

    so.emit('updateRcs', {'rcs': rcs}, broadcast=True)
    return jsonify({'rc': rc}), 201

@flask_app.route('/api/v1/rcs/<int:rc_id>', methods=['GET'])
@login_required
def get_rc(rc_id):
    db_session = config.getNewDbSession()
    rch = RcHelper(db_session, rc_id)
    rc = rch.getRc()
    db_session.close()

    if rc is None:
        abort(404)

    return jsonify({'rc': rc})

@flask_app.route('/api/v1/rcs/<int:rc_id>', methods=['PUT'])
@login_required
def update_rc(rc_id):
    if not request.json or not 'name' in request.json or not 'icon' in request.json or not 'order' in request.json or not 'public' in request.json:
        abort(400)

    db_session = config.getNewDbSession()
    rch = RcHelper(db_session, rc_id)    
    rc = rch.updateRc(request.json)
    rcs = rch.getRcs()
    db_session.close()

    if rc is None:
        abort(404) 

    so.emit('updateRcs', {'rcs': rcs}, broadcast=True)
    return jsonify({'rc': rc})

@flask_app.route('/api/v1/rcs/<int:rc_id>', methods=['DELETE'])
@login_required
def delete_rc(rc_id):
    db_session = config.getNewDbSession()
    rch = RcHelper(db_session, rc_id)
    result = rch.deleteRc()
    rcs = rch.getRcs()
    db_session.close()

    if result is None:
        abort(404)
    
    so.emit('updateRcs', {'rcs': rcs}, broadcast=True)
    return jsonify({'result': result})

@flask_app.route('/api/v1/rcs/<int:rc_id>/buttons', methods=['GET'])
@login_required
def get_rc_buttons(rc_id):
    db_session = config.getNewDbSession()
    rch = RcHelper(db_session, rc_id)
    buttons = rch.getButtons()
    db_session.close()

    if buttons is None:
        abort(404)

    return jsonify({'buttons': buttons})

# Button routes
@flask_app.route('/api/v1/buttons', methods=['POST'])
@login_required
def create_button():
    if not request.json or not 'rc_id' in request.json or not 'name' in request.json or not 'order_hor' in request.json or not 'order_ver' in request.json or not 'color' in request.json or not 'message' in request.json or not 'type' in request.json or not 'radio_id' in request.json and not 'mqtt_topic' in request.json:
        abort(400)
    
    db_session = config.getNewDbSession()
    bh = ButtonHelper(db_session)
    button = bh.createButton(request.json)
    rch = RcHelper(db_session, request.json['rc_id'])
    buttons = rch.getButtons()
    db_session.close()

    if button is None:
        abort(404)

    so.emit('updateButtons', {'rc_id': button['rc_id'], 'buttons': buttons}, broadcast=True)
    return jsonify({'button': button}), 201

@flask_app.route('/api/v1/buttons/<int:btn_id>', methods=['GET'])
@login_required
def get_button(btn_id):
    db_session = config.getNewDbSession()
    bh = ButtonHelper(db_session, btn_id)
    button = bh.getButton()
    db_session.close()

    if button is None:
        abort(404)

    return jsonify({'button': button})

@flask_app.route('/api/v1/buttons/<int:btn_id>', methods=['PUT'])
@login_required
def update_button(btn_id):
    if not request.json or not 'name' in request.json or not 'order_hor' in request.json or not 'order_ver' in request.json or not 'color' in request.json or not 'message' in request.json or not 'type' in request.json or not 'radio_id' in request.json:
        abort(400)
    
    db_session = config.getNewDbSession()
    bh = ButtonHelper(db_session, btn_id)
    button = bh.updateButton(request.json)
    rch = RcHelper(db_session, bh.get().rc_id)
    buttons = rch.getButtons()
    db_session.close()

    if button is None:
        abort(404)

    so.emit('updateButtons', {'rc_id': button['rc_id'], 'buttons': buttons}, broadcast=True)
    return jsonify({'button': button})

@flask_app.route('/api/v1/buttons/<int:btn_id>', methods=['DELETE'])
@login_required
def delete_button(btn_id):
    db_session = config.getNewDbSession()
    bh = ButtonHelper(db_session, btn_id)
    button = bh.deleteButton()
    buttons = bh.getButtons()
    db_session.close()

    if button is None:
        abort(404)

    so.emit('updateButtons', {'rc_id': button['rc_id'], 'buttons': buttons}, broadcast=True)
    return jsonify({'result': True})

@flask_app.route('/api/v1/buttons/<int:btn_id>/push', methods=['GET'])
@login_required
def push_button(btn_id):
    db_session = config.getNewDbSession()
    bh = ButtonHelper(db_session, btn_id)
    button = bh.get()

    if button is None:
        db_session.close()
        abort(404)

    if button.type == 'radio':
        event = {
            'event': 'pushButton',
            'user_id': current_user.id,
            'room': so_clients[current_user.id],
            'button_id': button.id,
            'host_name': bh.getHostName()
        }
        result = serv.node_sevice.pushToNode(event)
    elif button.type == 'mqtt':
        message = {
            'type': 'mqtt',
            'topic': button.mqtt_topic,
            'message': button.message
        }
        dump = '%s' % json.dumps(message)

        try:
            sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            sock.connect((config.NODE_RED_HOST, config.NODE_RED_PORT))
            sock.send(dump.encode())
        except Exception as e:
            logging.error('Node-red is offline')

    db_session.close()
    return jsonify({'result': True})

# Node routes
@flask_app.route('/api/v1/nodes', methods=['GET'])
@login_required
def get_nodes():
    db_session = config.getNewDbSession()
    nh = NodeHelper(db_session)
    nodes = nh.getNodes()
    db_session.close()
    return jsonify({'nodes': nodes})

@flask_app.route('/api/v1/nodes', methods=['POST'])
@login_required
def create_node():
    if not request.json or not 'name' in request.json or not 'host_name' in request.json or not 'order' in request.json:
        abort(400)

    db_session = config.getNewDbSession()
    nh = NodeHelper(db_session)
    node = nh.createNode(request.json)
    nodes = nh.getNodes()
    db_session.close()
    so.emit('updateNodes', {'nodes': nodes}, broadcast=True)
    return jsonify({'node': node}), 201

@flask_app.route('/api/v1/nodes/<int:node_id>', methods=['GET'])
@login_required
def get_node(node_id):
    db_session = config.getNewDbSession()
    nh = NodeHelper(db_session, node_id)
    node = nh.getNode()
    db_session.close()

    if node is None:
        abort(404)

    return jsonify({'node': node})

@flask_app.route('/api/v1/nodes/<int:node_id>', methods=['PUT'])
@login_required
def update_node(node_id):
    if not request.json or not 'host_name' in request.json or not 'order' in request.json:
        abort(400)

    db_session = config.getNewDbSession()
    nh = NodeHelper(db_session, node_id)
    node = nh.updateNode(request.json)
    nodes = nh.getNodes()
    db_session.close()

    if node is None:
        abort(404) 

    so.emit('updateNodes', {'nodes': nodes}, broadcast=True)
    return jsonify({'node': node})

@flask_app.route('/api/v1/nodes/<int:node_id>', methods=['DELETE'])
@login_required
def delete_node(node_id):
    db_session = config.getNewDbSession()
    nh = NodeHelper(db_session, node_id)
    result = nh.deleteNode()
    nodes = nh.getNodes()
    db_session.close()

    if result is None:
        abort(404)
    
    so.emit('updateNodes', {'nodes': nodes}, broadcast=True)
    return jsonify({'result': result})

# Arduino routes
@flask_app.route('/api/v1/arduinos', methods=['GET'])
@login_required
def get_arduinos():
    db_session = config.getNewDbSession()
    ah = ArduinoHelper(db_session)
    arduinos = ah.getArduinos()
    db_session.close()

    if arduinos is None:
        abort(404)

    return jsonify({'arduinos': arduinos})

@flask_app.route('/api/v1/arduinos', methods=['POST'])
@login_required
def create_arduino():
    if not request.json or not 'usb' in request.json or not 'node_id' in request.json or not 'name' in request.json or not 'order' in request.json:
        abort(400)
    
    db_session = config.getNewDbSession()
    ah = ArduinoHelper(db_session)
    arduino = ah.createArduino(request.json)
    arduinos = ah.getArduinos()

    if arduino is None:
        db_session.close()
        abort(404)

    so.emit('updateArduinos', {'node_id': arduino['node_id'], 'arduinos': arduinos}, broadcast=True)
    event = {
        'event': 'restart',
        'host_name': ah.getNode().host_name
    }
    db_session.close()

    if serv.node_sevice.pushToNode(event) == False:
        pass
        # so.emit('recievedIr', {'result': 'error', 'errors': 'Node is offline'})

    return jsonify({'arduino': arduino}), 201

@flask_app.route('/api/v1/arduinos/<int:arduino_id>', methods=['GET'])
@login_required
def get_arduino(arduino_id):
    db_session = config.getNewDbSession()
    ah = ArduinoHelper(db_session, arduino_id)
    arduino = ah.getArduino()
    db_session.close()

    if arduino is None:
        abort(404)

    return jsonify({'arduino': arduino})

@flask_app.route('/api/v1/arduinos/<int:arduino_id>', methods=['PUT'])
@login_required
def update_arduino(arduino_id):
    if not request.json or not 'usb' in request.json or not 'node_id' in request.json or not 'name' in request.json or not 'order' in request.json:
        abort(400)
    
    db_session = config.getNewDbSession()
    ah = ArduinoHelper(db_session, arduino_id)
    arduino = ah.updateArduino(request.json)
    arduinos = ah.getArduinos()

    if arduino is None:
        db_session.close()
        abort(404)

    so.emit('updateArduinos', {'node_id': arduino['node_id'], 'arduinos': arduinos}, broadcast=True)
    event = {
        'event': 'restart',
        'host_name': ah.getNode().host_name
    }
    db_session.close()

    if serv.node_sevice.pushToNode(event) == False:
        pass
        # so.emit('recievedIr', {'result': 'error', 'errors': 'Node is offline'})
    
    return jsonify({'arduino': arduino})

@flask_app.route('/api/v1/arduinos/<int:arduino_id>', methods=['DELETE'])
@login_required
def delete_arduino(arduino_id):
    db_session = config.getNewDbSession()
    ah = ArduinoHelper(db_session, arduino_id)
    host_name = ah.getNode().host_name
    arduino = ah.deleteArduino()
    arduinos = ah.getArduinos()
    db_session.close()

    if arduino is None:
        abort(404)

    so.emit('updateArduinos', {'node_id': arduino['node_id'], 'arduinos': arduinos}, broadcast=True)
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
    db_session = config.getNewDbSession()
    rh = RadioHelper(db_session)
    radios = rh.getRadios()
    db_session.close()

    for r in radios:
        r['params'] = cache.getRadioParams(r['id'])

    return jsonify({'radios': radios})

@flask_app.route('/api/v1/radios', methods=['POST'])
@login_required
def create_radio():
    if not request.json or not 'arduino_id' in request.json or not 'type' in request.json or not 'name' in request.json or not 'pipe' in request.json or not 'order' in request.json or not 'on_request' in request.json or not 'expired_after' in request.json or not 'enabled' in request.json:
        abort(400)

    db_session = config.getNewDbSession()
    rh = RadioHelper(db_session)
    radio = rh.createRadio(request.json)
    radios = rh.getRadios()
    db_session.close()

    for r in radios:
        r['params'] = cache.getRadioParams(r['id'])

    so.emit('updateRadios', {'radios': radios}, broadcast=True)
    return jsonify({'radio': radio}), 201

@flask_app.route('/api/v1/radios/<int:radio_id>', methods=['GET'])
@login_required
def get_radio(radio_id):
    db_session = config.getNewDbSession()
    rh = RadioHelper(db_session, radio_id)
    radio = rh.getRadio()
    db_session.close()

    if radio is None:
        abort(404)

    return jsonify({'radio': radio})

@flask_app.route('/api/v1/radios/<int:radio_id>', methods=['PUT'])
@login_required
def update_radio(radio_id):
    if not request.json or not 'pipe' in request.json or not 'name' in request.json or not 'enabled' in request.json or not 'order' in request.json:
        abort(400)

    db_session = config.getNewDbSession()
    rh = RadioHelper(db_session, radio_id)
    radio = rh.updateRadio(request.json)
    radios = rh.getRadios()
    db_session.close()

    if radio is None:
        abort(404) 

    for r in radios:
        r['params'] = cache.getRadioParams(r['id'])

    so.emit('updateRadios', {'radios': radios}, broadcast=True)
    return jsonify({'radio': radio})

@flask_app.route('/api/v1/radios/<int:radio_id>', methods=['DELETE'])
@login_required
def delete_radio(radio_id):
    db_session = config.getNewDbSession()
    rh = RadioHelper(db_session, radio_id)
    result = rh.deleteRadio()
    radios = rh.getRadios()
    db_session.close()

    if result is None:
        abort(404)
    
    for r in radios:
        r['params'] = cache.getRadioParams(r['id'])

    so.emit('updateRadios', {'radios': radios}, broadcast=True)
    return jsonify({'result': result})

# Node routes
@flask_app.route('/api/v1/mqtts', methods=['GET'])
@login_required
def get_mqtts():
    db_session = config.getNewDbSession()
    mh = MqttHelper(db_session)
    nodes = mh.getMqtts()
    db_session.close()
    return jsonify({'mqtts': mqtts})

@flask_app.route('/api/v1/mqtts', methods=['POST'])
@login_required
def create_mqtt():
    if not request.json or not 'name' in request.json or not 'topic' in request.json or not 'order' in request.json:
        abort(400)

    db_session = config.getNewDbSession()
    mh = MqttHelper(db_session)
    mqtt = mh.createMqtt(request.json)
    mqtts = mh.getMqtts()
    db_session.close()
    so.emit('updateMqtts', {'mqtts': mqtts}, broadcast=True)
    return jsonify({'mqtt': mqtt}), 201

@flask_app.route('/api/v1/mqtts/<int:mqtt_id>', methods=['GET'])
@login_required
def get_mqtt(mqtt_id):
    db_session = config.getNewDbSession()
    mh = MqttHelper(db_session, mqtt_id)
    mqtt = nh.getMqtt()
    db_session.close()

    if mqtt is None:
        abort(404)

    return jsonify({'mqtt': mqtt})

@flask_app.route('/api/v1/mqtts/<int:mqtt_id>', methods=['PUT'])
@login_required
def update_mqtt(mqtt_id):
    if not request.json or not 'name' in request.json or not 'topic' in request.json or not 'order' in request.json:
        abort(400)

    db_session = config.getNewDbSession()
    mh = MqttHelper(db_session, mqtt_id)
    mqtt = mh.updateMqtt(request.json)
    mqtts = mh.getMqtts()
    db_session.close()

    if mqtt is None:
        abort(404) 

    so.emit('updateMqtts', {'mqtts': mqtts}, broadcast=True)
    return jsonify({'mqtt': mqtt})

@flask_app.route('/api/v1/mqtts/<int:mqtt_id>', methods=['DELETE'])
@login_required
def delete_mqtt(mqtt_id):
    db_session = config.getNewDbSession()
    mh = MqttHelper(db_session, mqtt_id)
    result = mh.deleteMqtt()
    mqtts = mh.getMqtts()
    db_session.close()

    if result is None:
        abort(404)
    
    so.emit('updateMqtts', {'mqtts': mqtts}, broadcast=True)
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
@authenticated_only
def handle_connect():
    so_clients[current_user.id] = request.sid
    logging.info("Add user %s to socketio" % current_user.id)

@so.on('disconnect')
@authenticated_only
def handle_disconnect():
    logging.info("Delete user %s from socketio" % current_user.id)
    # del so_clients[current_user.id]

# @so.on('json')
# @authenticated_only
# def handle_json(data):
    # Debug
    # logging.info("received json: %s" % data)
    
    # if data['action'] == 'catch_ir_signal':
    #     # signal = ir_reader.read_signal()
    #     emit('json', {'response': {'result': 'success', 'callback': 'ir_signal', 'signal': '1500 800 800 800 1500 1500'}})

@so.on('catch_ir')
def handle_catch_ir(json_data):
    data = json.loads(json_data)

    if 'node_id' in data:
        db_session = config.getNewDbSession()
        node = NodeHelper(db_session, data['node_id']).get()
        db_session.close()

        if node is not None:
            event = {
                'event': 'catchIr',
                'user_id': current_user.id,
                'room': so_clients[current_user.id],
                'host_name': node.host_name
            }

            if serv.node_sevice.pushToNode(event) == False:
                so.emit('recievedIr', {'result': 'error', 'errors': 'Node is offline'})

# @so.on('emit_method')
# def handle_emit_method(message):
#     logging.info("received emit_method: %s" % message)
