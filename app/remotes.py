from __future__ import print_function
import sys
from .models import Remote
from app import so, db

class RemoteControl:
    """docstring for RemoteControl"""
    def create(self, rc_type, rc_id, rc_name, rc_icon, rc_order = 1, public = True):
        if rc_type and rc_id and rc_name and rc_icon:
            remote = Remote(remote_type = rc_type, identificator = rc_id.lower(), name = rc_name, icon = rc_icon, order = rc_order, public = public)
            db.session.add(remote)
            db.session.commit()
            print('create remote type:%s' % type, file=sys.stderr)
            return True

    def getRemotesList(self):
        remotes = []

        for remote in Remote.query.order_by(Remote.id).all():
            r = {'identificator': remote.identificator, 'name': remote.name, 'type': remote.remote_type, 'icon': remote.icon}
            remotes.append(r)
            print('remote: %s' % remote.name, file=sys.stderr)

        return remotes
        