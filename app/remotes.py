from __future__ import print_function
import sys, os
from .models import Remote, Button
from app import so, db
import uuid
from datetime import datetime

class RemoteControl:
    def create(self, rc_type, rc_name, rc_icon, rc_order = 1, public = True):
        rc_id = "RC_" + str(uuid.uuid4()).replace('-', '_')

        if rc_type and rc_name and rc_icon:
            remote = Remote(remote_type = rc_type,
                            identificator = rc_id,
                            name = rc_name,
                            icon = rc_icon,
                            order = rc_order,
                            public = public,
                            timestamp = datetime.utcnow())

            db.session.add(remote)
            db.session.commit()
            # print('create remote type:%s' % type, file=sys.stderr)
            return True

    def addBtnToRemote(self, content):
        btn_id = "BTN_" + str(uuid.uuid4()).replace('-', '_')
        print(content['rc_id'], file=sys.stderr)

        rc = Remote.query.filter_by(identificator = content['rc_id']).first()

        # print(rc, file=sys.stderr)

        if rc is not None:
            btn = Button(identificator = btn_id,
                        name = content['btn_name'],
                        order_hor = content['btn_order_hor'],
                        order_ver = content['btn_order_ver'],
                        color = content['btn_color'],
                        signal = content['signal'],
                        remote_id = rc.id,
                        radio = content['radio'],
                        timestamp = datetime.utcnow())

            db.session.add(btn)
            db.session.commit()
            print('create btn: %s' % btn_id, file=sys.stderr)
            return True

    def removeBtnFromRemote(self, content):
        ids = content['buttons']

        for button in ids:
            btn = Button.query.filter_by(identificator = button).first()
            db.session.delete(btn)

        db.session.commit()

    def getRemotesList(self):
        remotes = []

        for remote in Remote.query.order_by(Remote.id).all():
            r = {'identificator': remote.identificator,
                'name': remote.name,
                'type': remote.remote_type,
                'icon': remote.icon}

            remotes.append(r)

        return remotes

    def getRemoteButtons(self, rc_id):
        buttons = []

        rc = Remote.query.filter_by(identificator = rc_id).first()

        if rc is not None:
            for button in rc.buttons.order_by(Button.order_ver.asc(), Button.order_hor.asc()).all():
                btn = {'identificator': button.identificator,
                        'name': button.name,
                        'color': button.color,
                        'order_ver': button.order_ver,
                        'order_hor': button.order_hor}

                buttons.append(btn)

        return buttons

