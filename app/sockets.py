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
    
    if data['action'] == 'add_remote':
        content = data['content']
        rc = RemoteControl()
        rc.create(content['rc_type'], content['rc_id'], content['rc_name'])
