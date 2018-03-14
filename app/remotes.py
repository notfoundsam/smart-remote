from __future__ import print_function
import sys, os
from .models import Remote, Button
from app import db
import uuid
from datetime import datetime
from run import arduino, lirc

class RemoteControl:

    def __init__(self, sid):
        self.sid = sid

    def create(self, content):
        rc_id = "RC_" + str(uuid.uuid4()).replace('-', '_')
        remote = Remote(identificator = rc_id,
                        name = content['rc_name'],
                        icon = content['rc_icon'],
                        order = 1,
                        public = True,
                        timestamp = datetime.utcnow())

        db.session.add(remote)
        db.session.commit()

        return True

    def createButton(self, content):
        rc = Remote.query.filter_by(identificator = content['rc_id']).first()

        if rc is not None:
            if content['btn_id']:
                btn = Button.query.filter_by(identificator = content['btn_id']).first()

                if btn is None:
                    return False

                btn.name = content['btn_name']
                btn.order_hor = content['btn_order_hor']
                btn.order_ver = content['btn_order_ver']
                btn.color = content['btn_color']
                btn.signal = content['btn_signal']
                btn.radio_id = content['btn_radio_id']
                btn.type = content['btn_type']
                btn.timestamp = datetime.utcnow()
            else:
                btn_id = "BTN_" + str(uuid.uuid4()).replace('-', '_')
                btn = Button(identificator = btn_id,
                            name = content['btn_name'],
                            order_hor = content['btn_order_hor'],
                            order_ver = content['btn_order_ver'],
                            color = content['btn_color'],
                            signal = content['btn_signal'],
                            remote_id = rc.id,
                            radio_id = content['btn_radio_id'],
                            type = content['btn_type'],
                            timestamp = datetime.utcnow())

                db.session.add(btn)
            
            db.session.commit()

            return True

    def removeButton(self, content):
        ids = content['buttons']

        for button in ids:
            btn = Button.query.filter_by(identificator = button).first()
            db.session.delete(btn)

        db.session.commit()

    def getButton(self, content):
        btn_id = content['button']
        button = Button.query.filter_by(identificator = btn_id).first()

        if button is not None:
            return {
                'btn_id': button.identificator,
                'btn_name': button.name,
                'btn_order_hor': button.order_hor,
                'btn_order_ver': button.order_ver,
                'btn_color': button.color,
                'btn_signal': button.signal,
                'btn_radio_id': button.radio_id,
                'btn_type': button.type,
                'rc_id' : button.remote.identificator,
                'rc_name' : button.remote.name
            }

        return False

    def getRemotesList(self):
        remotes = []

        for remote in Remote.query.order_by(Remote.id).all():
            r = {
                'identificator': remote.identificator,
                'name': remote.name,
                'icon': remote.icon
            }

            remotes.append(r)

        return remotes

    def getRemoteButtons(self, rc_id):
        buttons = []

        rc = Remote.query.filter_by(identificator = rc_id).first()

        if rc is not None:
            for button in rc.buttons.order_by(Button.order_ver.asc(), Button.order_hor.asc()).all():
                btn = {
                    'identificator': button.identificator,
                    'name': button.name,
                    'color': button.color,
                    'order_ver': button.order_ver,
                    'order_hor': button.order_hor
                }

                buttons.append(btn)

        return buttons

    def execute(self, btn_id):
        btn = Button.query.filter_by(identificator = btn_id).first()
        if btn is not None:
            if btn.type == 'ir':
                if btn.radio_id == 999:
                    lirc.sendLircCommand(btn.remote.identificator, btn.identificator)
                    return True
                else:
                    response = arduino.sendIrSignal(btn.signal, btn.radio_id, self.sid)

            elif btn.type == 'cmd':
                return arduino.sendCommand(btn.signal, btn.radio_id, self.sid)

    def test(self, content):
        if content['radio_id'] == '999':
            lirc.regenerateLircCommands()
            lirc.addTestSignal(content['signal'])
            lirc.reloadLirc()
            lirc.sendTestSignal()
            
            return True
        else:
            response = arduino.sendIrSignal(content['signal'], content['radio_id'])
