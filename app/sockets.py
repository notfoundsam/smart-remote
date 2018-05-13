from __future__ import print_function
import sys, Queue
import functools
from flask_socketio import emit
from app import so
from .remotes import RemoteControl
from .sensor import RadioSensor
from flask_login import current_user
from flask_socketio import disconnect
from drivers import ir_reader
from run import lirc
from threading import Lock
from flask import request

def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped

# thread = None
# thread_lock = Lock()

# def background_thread():
#     """Example of how to send server generated events to clients."""

#     q = Queue.PriorityQueue()
#     q.put(priority_queue.ArduinoQueue(5, 'Proficient5'))
#     q.put(priority_queue.ArduinoQueue(3, 'Proficient3'))
#     q.put(priority_queue.ArduinoQueue(1, 'Proficient1'))
#     count = 0
#     while not q.empty():
#         el = q.get()
#         el.run()
#         so.sleep(2)
        # count += 1
        # print(count, file=sys.stderr)


@so.on('connect', namespace='/remotes')
def handle_connect():
    id = request.sid
    print("%s connected" % id, file=sys.stderr)
    emit('json', {'data': 'Connected', 'count': 0})

@so.on('json', namespace='/remotes')
@authenticated_only
def handle_json(data):
    # Debug
    print('received json: ' + str(data), file=sys.stderr)
    
    rc = RemoteControl(request.sid)
    
    if data['action'] == 'rc_save':
        if rc.create(data['content']) == True:
            remotes = rc.getRemotesList()
            emit('json', {'response': {'result': 'success', 'callback': 'rc_refresh', 'remotes': remotes}}, broadcast = True)

    elif data['action'] == 'rc_button_save':
        content = data['content']
        if rc.createButton(content) == True:
            lirc.regenerateLircCommands()
            lirc.reloadLirc()
            emit('json', {'response': {'result': 'success', 'callback': 'back_to_remote', 'rc_id': content['rc_id'], 'rc_name': content['rc_name']}})

    elif data['action'] == 'rc_buttons_remove':
        content = data['content']

        rc.removeButton(content)
        emit('json', {'response': {'result': 'success', 'callback': 'back_to_remote', 'rc_id': content['rc_id'], 'rc_name': content['rc_name']}})

    elif data['action'] == 'rc_button_edit':
        content = data['content']

        button = rc.getButton(content)
        if button is not None:
            sensor = RadioSensor()
            radios = sensor.getRadiosIdName()
            emit('json', {'response': {'result': 'success', 'callback': 'rc_button_save', 'button': button, 'radios': radios, 'edit': True}})
        else:
            emit('json', {'response': {'result': 'error', 'message': 'Failed ;('}})

    elif data['action'] == 'rc_refresh':
        remotes = rc.getRemotesList()
        emit('json', {'response': {'result': 'success', 'callback': 'rc_refresh', 'remotes': remotes}}, broadcast = True)
    
    elif data['action'] == 'get_rc_buttons':
        content = data['content']
        rc_name = rc.getRemoteName(content['rc_id'])
        buttons = rc.getRemoteButtons(content['rc_id'])
        emit('json', {'response': {'result': 'success', 'callback': 'rc_buttons_refresh', 'rc_name': rc_name, 'buttons': buttons}})

    elif data['action'] == 'catch_ir_signal':
        signal = ir_reader.read_signal()
        emit('json', {'response': {'result': 'success', 'callback': 'ir_signal', 'signal': signal}})

    elif data['action'] == 'lirc_update':
        lirc.regenerateLircCommands()
        lirc.reloadLirc()

    elif data['action'] == 'rc_button_pushed':
        data = rc.execute(data['content']['btn_id'])

    elif data['action'] == 'test_signal':
        data = rc.test(data['content'])

@so.on('json', namespace='/radios')
@authenticated_only
def handle_json(data):

    sensor = RadioSensor()

    if data['action'] == 'radio_save':
        if sensor.create(data['content']) != True:
            emit('json', {'response': {'result': 'error', 'message': 'Failed ;('}})
        else:
            radios = sensor.getRadiosList()
            emit('json', {'response': {'result': 'success', 'callback': 'radios_refresh', 'radios': radios}}, broadcast = True)
    
    elif data['action'] == 'radio_edit':
        radio = sensor.getRadio(data['content'])
        if radio != False:
            emit('json', {'response': {'result': 'success', 'callback': 'radio_edit', 'radio': radio}})

    elif data['action'] == 'radio_remove':
        content = data['content']
        sensor.remove(content)
        radios = sensor.getRadiosList()
        emit('json', {'response': {'result': 'success', 'callback': 'radios_refresh', 'radios': radios}}, broadcast = True)

    elif data['action'] == 'radios_refresh':
        radios = sensor.getRadiosList()
        emit('json', {'response': {'result': 'success', 'callback': 'radios_refresh', 'radios': radios}}, broadcast = True)

    elif data['action'] == 'get_radio_options':
        radios = sensor.getRadiosIdName()
        if radios != False:
            emit('json', {'response': {'result': 'success', 'callback': 'set_radio_options', 'radios': radios}})
