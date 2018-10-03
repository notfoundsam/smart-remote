import sys, os
from .models import Rc, Button, Node, Arduino, Radio
from app.service import Service
from app import db
from datetime import datetime

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

        return {'id': rc.id,
                'name': rc.name,
                'icon': rc.icon,
                'order': rc.order,
                'public': rc.public}

    def getRc(self):
        if self.rc is None:
            return None
        
        return {'id': self.rc.id,
                'name': self.rc.name,
                'icon': self.rc.icon,
                'order': self.rc.order,
                'public': self.rc.public}
    
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
                'public': self.rc.public}

    def deleteRc(self):
        if self.rc is None:
            return None

        for btn in self.rc.buttons:
            db.session.delete(btn)

        db.session.commit()
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
            b = {'id': button.id,
                'rc_id': button.rc_id,
                'node_id': button.node_id,
                'arduino_id': button.arduino_id,
                'radio_id': button.radio_id,
                'name': button.name,
                'color': button.color,
                'order_ver': button.order_ver,
                'order_hor': button.order_hor,
                'execute': button.execute,
                'type': button.type}

            buttons.append(b)

        return buttons

    def createButton(self, params):
        if self.rc is None:
            return None

        btn = Button(rc_id = self.rc.id,
                    node_id = params['node_id'],
                    arduino_id = params['arduino_id'],
                    radio_id = params['radio_id'],
                    name = params['name'],
                    order_hor = params['order_hor'],
                    order_ver = params['order_ver'],
                    color = params['color'],
                    type = params['type'],
                    execute = params['execute'],
                    timestamp = datetime.utcnow())

        db.session.add(btn)
        db.session.commit()

        return {'id': btn.id,
                'rc_id' : btn.rc_id,
                'node_id': btn.node_id,
                'arduino_id': btn.arduino_id,
                'radio_id': btn.radio_id,
                'name': btn.name,
                'order_hor': btn.order_hor,
                'order_ver': btn.order_ver,
                'color': btn.color,
                'type': btn.type,
                'execute': btn.execute}

    def getButton(self):
        if self.rc is None or self.button is None:
            return None

        return {'id': self.button.id,
                'rc_id' : self.button.rc_id,
                'node_id': self.button.node_id,
                'arduino_id': self.button.arduino_id,
                'radio_id': self.button.radio_id,
                'name': self.button.name,
                'order_hor': self.button.order_hor,
                'order_ver': self.button.order_ver,
                'color': self.button.color,
                'execute': self.button.execute,
                'type': self.button.type}

    def updateButton(self, params):
        if self.rc is None or self.button is None:
            return None

        self.button.radio_id = params['radio_id']
        self.button.node_id = params['node_id']
        self.button.arduino_id = params['arduino_id']
        self.button.name = params['name']
        self.button.order_hor = params['order_hor']
        self.button.order_ver = params['order_ver']
        self.button.color = params['color']
        self.button.type = params['type']
        self.button.execute = params['execute']
        self.button.timestamp = datetime.utcnow()

        db.session.commit()

        return {'id': self.button.id,
                'rc_id' : self.button.rc_id,
                'node_id': self.button.node_id,
                'arduino_id': self.button.arduino_id,
                'radio_id': self.button.radio_id,
                'name': self.button.name,
                'order_hor': self.button.order_hor,
                'order_ver': self.button.order_ver,
                'color': self.button.color,
                'type': self.button.type,
                'execute': self.button.execute}

    def deleteButton(self):
        if self.rc is None or self.button is None:
            return None

        db.session.delete(self.button)
        db.session.commit()
        self.button = None
        return True

    def pushButton(self, event):
        if self.rc is None or self.button is None:
            return None

        node = Node.query.filter_by(id = self.button.node_id).first()
        service = Service.Instance()

        event.host_name = node.host_name
        event.button_id = self.button.id
        
        if node is not None and service.node_sevice.pushToNode(event):
            return True

        return False


    # def getRemoteName(self, rc_id):
    #     rc = Rc.query.filter_by(identificator = rc_id).first()

    #     if rc is not None:
    #         return rc.name

    #     return ''

    # def execute(self, btn_id):
    #     btn = Button.query.filter_by(identificator = btn_id).first()
        
    #     if btn is not None:
    #         if btn.radio_id == 999:
    #             lirc.sendLircCommand(btn.remote.identificator, btn.identificator)
    #             return True
    #         else:
    #             arduino.send(btn, btn.radio.pipe, self.sid)

    # def test(self, content):
    #     if content['radio_id'] == '999':
    #         lirc.regenerateLircCommands()
    #         lirc.addTestSignal(content['signal'])
    #         lirc.reloadLirc()
    #         lirc.sendTestSignal()
            
    #         return True
    #     else:
    #         radio = Radio.query.filter_by(id = content['radio_id']).first()
    #         btn = Button(
    #             signal = content['signal'],
    #             radio_id = content['radio_id'],
    #             type = content['button_type'])
    #         arduino.send(btn, radio.pipe, self.sid)

class NodeHelper:

    def __init__(self, node_id = None):
        self.set(node_id)

    def get(self):
        return self.node

    def set(self, node_id):
        self.node = Node.query.filter_by(id = node_id).first()

    def getNodes(self):
        nodes = []

        for node in Node.query.order_by(Node.order).all():
            n = {'id': node.id,
                'name': node.name,
                'host_name': node.host_name,
                'order': node.order}

            nodes.append(n)

        return nodes

    def createNode(self, params):
        node = Node(name = params['name'],
                    host_name = params['host_name'],
                    order = params['order'],
                    timestamp = datetime.utcnow())

        db.session.add(node)
        db.session.commit()

        return {'id': node.id,
                'name': node.name,
                'host_name': node.host_name,
                'order': node.order}

    def getNode(self):
        if self.node is None:
            return None
        
        return {'id': self.node.id,
                'name': self.node.name,
                'host_name': self.node.host_name,
                'order': self.node.order}

    def updateNode(self, params):
        if self.node is None:
            return None

        self.node.name = params['name']
        self.node.host_name = params['host_name']
        self.node.order = params['order']
        self.node.timestamp = datetime.utcnow()

        db.session.commit()
        
        return {'id': self.node.id,
                'name': self.node.name,
                'host_name': self.node.host_name,
                'order': self.node.order}

    def deleteNode(self):
        if self.node is None:
            return None

        db.session.delete(self.node)
        db.session.commit()
        self.node = None
        return True

    def getNodeByName(self, host_name):
        return Node.query.filter_by(host_name = host_name).first()

class ArduinoHelper:

    def __init__(self, node_id, arduino_id = None):
        self.node = Node.query.filter_by(id = node_id).first()
        self.set(arduino_id)

    def get(self):
        return self.arduino

    def set(self, arduino_id):
        if self.node is None:
            self.arduino = None
        else:
            self.arduino = self.node.arduinos.filter((Arduino.id == arduino_id)).first()

    def getArduinos(self):
        if self.node is None:
            return None
        
        arduinos = []

        for arduino in self.node.arduinos.order_by(Arduino.order.asc()).all():
            a = {'id': arduino.id,
                'node_id': arduino.node_id,
                'usb': arduino.usb,
                'mode': arduino.mode,
                'name': arduino.name,
                'order': arduino.order}

            arduinos.append(a)

        return arduinos

    def createArduino(self, params):
        if self.node is None:
            return None

        arduino = Arduino(node_id = self.node.id,
                        usb = params['usb'],
                        mode = params['mode'],
                        name = params['name'],
                        order = params['order'],
                        timestamp = datetime.utcnow())

        db.session.add(arduino)
        db.session.commit()

        return {'id': arduino.id,
                'node_id': arduino.node_id,
                'usb': arduino.usb,
                'mode': arduino.mode,
                'name': arduino.name,
                'order': arduino.order}

    def getArduino(self):
        if self.node is None or self.arduino is None:
            return None

        return {'id': self.arduino.id,
                'node_id': self.arduino.node_id,
                'usb': self.arduino.usb,
                'mode': self.arduino.mode,
                'name': self.arduino.name,
                'order': self.arduino.order}

    def updateArduino(self, params):
        if self.node is None or self.arduino is None:
            return None

        self.arduino.usb = params['usb']
        self.arduino.mode = params['mode']
        self.arduino.name = params['name']
        self.arduino.order = params['order']
        self.arduino.timestamp = datetime.utcnow()

        db.session.commit()

        return {'id': self.arduino.id,
                'node_id': self.arduino.node_id,
                'usb': self.arduino.usb,
                'mode': self.arduino.mode,
                'name': self.arduino.name,
                'order': self.arduino.order}

    def deleteArduino(self):
        if self.node is None or self.arduino is None:
            return None

        db.session.delete(self.arduino)
        db.session.commit()
        self.arduino = None
        return True

class RadioHelper:

    def __init__(self, radio_id = None):
        self.set(radio_id)

    def get(self):
        return self.radio

    def set(self, radio_id):
        self.radio = Radio.query.filter_by(id = radio_id).first()

    def getRadios(self):
        radios = []

        for radio in Radio.query.order_by(Radio.order).all():
            r = {'id': radio.id,
                'arduino_id': radio.arduino_id,
                'pipe': radio.pipe,
                'name': radio.name,
                'enabled': radio.enabled,
                'order': radio.order}

            radios.append(r)

        return radios

    def createRadio(self, params):
        radio = Radio(arduino_id = params['arduino_id'],
                    pipe = params['pipe'],
                    name = params['name'],
                    enabled = params['enabled'],
                    order = params['order'],
                    timestamp = datetime.utcnow())

        db.session.add(radio)
        db.session.commit()

        return {'id': radio.id,
                'arduino_id': radio.arduino_id,
                'pipe': radio.pipe,
                'name': radio.name,
                'enabled': radio.enabled,
                'order': radio.order}

    def getRadio(self):
        if self.radio is None:
            return None
        
        return {'id': self.radio.id,
                'arduino_id': self.radio.arduino_id,
                'pipe': self.radio.pipe,
                'name': self.radio.name,
                'enabled': self.radio.enabled,
                'order': self.radio.order}

    def updateRadio(self, params):
        if self.radio is None:
            return None

        self.radio.arduino_id = params['arduino_id']
        self.radio.pipe = params['pipe']
        self.radio.name = params['name']
        self.radio.enabled = params['enabled']
        self.radio.order = params['order']
        self.radio.timestamp = datetime.utcnow()

        db.session.commit()
        
        return {'id': self.radio.id,
                'arduino_id': self.radio.arduino_id,
                'pipe': self.radio.pipe,
                'name': self.radio.name,
                'enabled': self.radio.enabled,
                'order': self.radio.order}

    def deleteRadio(self):
        if self.radio is None:
            return None

        db.session.delete(self.radio)
        db.session.commit()
        self.radio = None
        return True

class SocketEvent:

    def __init__(self):
        self.user_id = None
        self.host_name = None
        self.button_id = None
        