from __future__ import print_function
import sys, os
from .models import Rc, Button, Radio
from app import db
import uuid
from datetime import datetime
from run import arduino, lirc

class RcHelper:

    def __init__(self, rc_id = None):
        self.set(rc_id)

    def get(self):
        return self.rc

    def set(self, rc_id):
        self.rc = Rc.query.filter_by(id = rc_id).first()

    def getRcs(self):
        rcs = []

        for rc in Rc.query.order_by(Rc.order).all():
            r = {
                'id': rc.id,
                'name': rc.name,
                'icon': rc.icon,
                'order': rc.order,
                'public': rc.public
            }

            rcs.append(r)

        return rcs

    def createRc(self, params):
        rc = Rc(name = params['name'],
                icon = params['icon'],
                order = params['order'],
                public = params['public'],
                timestamp = datetime.utcnow())

        db.session.add(rc)
        db.session.commit()

        return {
            'id': rc.id,
            'name': rc.name,
            'icon': rc.icon,
            'order': rc.order,
            'public': rc.public,
        }

    def getRc(self):
        if self.rc is None:
            return None
        
        return {'id': self.rc.id,
                'name': self.rc.name,
                'icon': self.rc.icon,
                'order': self.rc.order,
                'public': self.rc.public
            }
    
    def updateRc(self, params):
        if self.rc is None:
            return None

        self.rc.name = params['name']
        self.rc.icon = params['icon']
        self.rc.order = params['order']
        self.rc.public = params['public']
        self.rc.timestamp = datetime.utcnow()

        db.session.commit()
        
        return {'id': self.rc.id,
                'name': self.rc.name,
                'icon': self.rc.icon,
                'order': self.rc.order,
                'public': self.rc.public
            }

    def deleteRc(self):
        db.session.delete(self.rc)
        db.session.commit()
        self.rc = None
        return True

class ButtonHelper:

    def __init__(self, rc_id, btn_id = None):
        self.rc = Rc.query.filter_by(id = rc_id).first()
        self.set(btn_id)

    def get(self):
        return self.button

    def set(self, btn_id):
        if self.rc is None:
            self.button = None
        else:
            self.button = self.rc.buttons.filter((Button.id == btn_id)).first()

    def getButtons(self):
        if self.rc is None:
            return None
        
        buttons = []

        for button in self.rc.buttons.order_by(Button.order_ver.asc(), Button.order_hor.asc()).all():
            btn = {
                'id': button.id,
                'name': button.name,
                'color': button.color,
                'order_ver': button.order_ver,
                'order_hor': button.order_hor,
                'command': button.command,
                'rc_id': button.rc_id,
                'radio_id': button.radio_id,
                'type': button.type
            }

            buttons.append(btn)

        return buttons

    def createButton(self, params):
        if self.rc is None:
            return None

        btn = Button(name = params['name'],
                    order_hor = params['order_hor'],
                    order_ver = params['order_ver'],
                    color = params['color'],
                    command = params['command'],
                    rc_id = self.rc.id,
                    radio_id = params['radio_id'],
                    type = params['type'],
                    timestamp = datetime.utcnow())

        db.session.add(btn)
        db.session.commit()

        return {
            'id': btn.id,
            'name': btn.name,
            'order_hor': btn.order_hor,
            'order_ver': btn.order_ver,
            'color': btn.color,
            'command': btn.command,
            'rc_id' : btn.rc_id,
            'radio_id': btn.radio_id,
            'type': btn.type,
        }

    def updateButton(self, btn_id, content):
        btn = Button.query.filter_by(id = btn_id).first()

        if self.rc is None or btn is None:
            return None

        btn.name = content['button_name']
        btn.order_hor = content['button_order_hor']
        btn.order_ver = content['button_order_ver']
        btn.color = content['button_color']
        btn.signal = content['signal']
        btn.radio_id = content['button_radio_id']
        btn.type = content['button_type']
        btn.rc_id = content['rc_id']
        btn.timestamp = datetime.utcnow()

        db.session.commit()

        return {
            'id': button.id,
            'name': button.name,
            'order_hor': button.order_hor,
            'order_ver': button.order_ver,
            'color': button.color,
            'signal': button.signal,
            'radio_id': button.radio_id,
            'type': button.type,
            'rc_id' : button.rc_id,
            'rc_name' : button.remote.name
        }

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

    def getRemoteName(self, rc_id):
        rc = Rc.query.filter_by(identificator = rc_id).first()

        if rc is not None:
            return rc.name

        return ''

    def execute(self, btn_id):
        btn = Button.query.filter_by(identificator = btn_id).first()
        
        if btn is not None:
            if btn.radio_id == 999:
                lirc.sendLircCommand(btn.remote.identificator, btn.identificator)
                return True
            else:
                arduino.send(btn, btn.radio.pipe, self.sid)

    def test(self, content):
        if content['radio_id'] == '999':
            lirc.regenerateLircCommands()
            lirc.addTestSignal(content['signal'])
            lirc.reloadLirc()
            lirc.sendTestSignal()
            
            return True
        else:
            radio = Radio.query.filter_by(id = content['radio_id']).first()
            btn = Button(
                signal = content['signal'],
                radio_id = content['radio_id'],
                type = content['button_type'])
            arduino.send(btn, radio.pipe, self.sid)
