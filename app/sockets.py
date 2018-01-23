from __future__ import print_function
import sys
import functools
from flask_socketio import emit
from app import so
from .remotes import *
from flask_login import current_user
from flask_socketio import disconnect
from drivers import ir_reader
from run import arduino, lirc

def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped

@so.on('connect', namespace='/remotes')
def handle_connect():
    pass
    # global thread
    # with thread_lock:
    #     if thread is None:
    #         thread = so.start_background_task(target=background_thread)
    # emit('json', {'data': 'Connected', 'count': 0})

@so.on('json', namespace='/remotes')
@authenticated_only
def handle_json(data):
    # arduino.send()
    # print(arduino, file=sys.stderr)
    print('received json: ' + str(data), file=sys.stderr)
    
    rc = RemoteControl()
    
    if data['action'] == 'rc_save':
        if rc.create(data['content']) == True:
            emit('json', {'response': {'result': 'success', 'callback': 'rc_saved'}})

    elif data['action'] == 'rc_button_save':
        content = data['content']
        if rc.createButton(content) == True:
            lirc.regenerateLircCommands()
            lirc.reloadLirc()
            emit('json', {'response': {'result': 'success', 'callback': 'back_to_remote', 'rc_id': content['rc_id'], 'rc_name': content['rc_name']}})

    elif data['action'] == 'remove_ir_buttons':
        content = data['content']

        rc.removeBtnFromRemote(content)
        emit('json', {'response': {'result': 'success', 'callback': 'back_to_remote', 'rc_id': content['rc_id'], 'rc_name': content['rc_name']}})

    elif data['action'] == 'rc_refresh':
        remotes = rc.getRemotesList()
        emit('json', {'response': {'result': 'success', 'callback': 'rc_refresh', 'remotes': remotes}}, broadcast = True)
    
    elif data['action'] == 'rc_buttons_refresh':
        content = data['content']
        buttons = rc.getRemoteButtons(content['rc_id'])
        emit('json', {'response': {'result': 'success', 'callback': 'rc_buttons_refresh', 'buttons': buttons}})

    elif data['action'] == 'catch_ir_signal':
        # emit('json', {'response': {'result': 'success', 'callback': 'waiting_ir_signal'}})
        signal = ir_reader.read_signal()

        if signal != False:
            emit('json', {'response': {'result': 'success', 'callback': 'rc_button_save', 'signal': signal}})
        else:
            print('faild', file=sys.stderr)
            emit('json', {'response': {'result': 'success', 'callback': 'ir_signal_failed'}})

    elif data['action'] == 'regenerate_lirc_commands':
        lirc.regenerateLircCommands()
        lirc.reloadLirc()

        # if signal != False:
        #     print('signal ok', file=sys.stderr)
        #     emit('json', {'response': {'result': 'success', 'callback': 'ir_signal_recived', 'signal': signal}})
        # else:
        #     print('faild', file=sys.stderr)
        #     emit('json', {'response': {'result': 'success', 'callback': 'ir_signal_failed'}})

    elif data['action'] == 'rc_button_pushed':
        content = data['content']

        result = lirc.sendLircCommand(content['rc_id'], content['btn_id'])
    
    elif data['action'] == 'ir_test_signal':

        content = data['content']

        if content['radio'] == 'lirc':
            lirc.regenerateLircCommands()
            lirc.addTestSignal(content['signal'])
            lirc.reloadLirc()
            lirc.sendTestSignal()
        else:
            if arduino.send_ir_signal(content['signal'], content['radio']) == False:
                emit('json', {'response': {'result': 'error', 'message': 'Failed ;('}})
