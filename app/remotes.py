from __future__ import print_function
import sys
from .models import Remote
from app import so, db

class RemoteControl:
    """docstring for RemoteControl"""
    def create(self, rc_type, rc_id, rc_name, public = True):
        remote = Remote(remote_type = rc_type, identificator = rc_id.lower(), name = rc_name, public = public)
        db.session.add(remote)
        db.session.commit()
        print('create remote type:%s' % type, file=sys.stderr)
        