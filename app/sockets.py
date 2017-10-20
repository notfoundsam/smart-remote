from __future__ import print_function
import sys
import functools
from flask_socketio import emit
from app import so
from .remotes import *
from flask_login import current_user
from flask_socketio import disconnect

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
    print('received json: ' + str(data), file=sys.stderr)
    
    rc = RemoteControl()
    
    if data['action'] == 'remote_add':
        content = data['content']

        if rc.create(content['rc_type'], content['rc_id'], content['rc_name'], content['rc_icon']) == True:
            emit('json', {'response': {'result': 'success', 'callback': 'add_remote_to_menu'}})

    elif data['action'] == 'remote_list':
        remotes = rc.getRemotesList()
        emit('json', {'response': {'result': 'success', 'callback': 'refresh_remote_menu', 'remotes': remotes}})
