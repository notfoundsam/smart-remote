import logging
from app.models import Rc, Button, Node, Arduino, Radio
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

    def getButtons(self):
        if self.rc is None:
            return None
        
        buttons = []

        for button in self.rc.buttons.order_by(Button.order_ver.asc(), Button.order_hor.asc()).all():
            b = {'id': button.id,
                'rc_id': button.rc_id,
                'radio_id': button.radio_id,
                'name': button.name,
                'color': button.color,
                'order_ver': button.order_ver,
                'order_hor': button.order_hor,
                'message': button.message,
                'type': button.type}

            buttons.append(b)

        return buttons
class BgroupHelper:

    def __init__(self, rc_id, group_id = None):
        self.rc = Rc.query.filter_by(id = rc_id).first()
        self.set(group_id)

    def get(self):
        return self.rc

    def set(self, group_id):
        if self.rc is None:
            self.button = None
        else:
            self.button = self.rc.bgroups.filter((Bgroup.id == group_id)).first()

    # def getRcs(self):
    #     rcs = []

    #     for rc in Rc.query.order_by(Rc.order).all():
    #         r = {
    #             'id': rc.id,
    #             'name': rc.name,
    #             'icon': rc.icon,
    #             'order': rc.order,
    #             'public': rc.public
    #         }

    #         rcs.append(r)

    #     return rcs

    # def createRc(self, params):
    #     rc = Rc(name = params['name'],
    #             icon = params['icon'],
    #             order = params['order'],
    #             public = params['public'],
    #             timestamp = datetime.utcnow())

    #     db.session.add(rc)
    #     db.session.commit()

    #     return {'id': rc.id,
    #             'name': rc.name,
    #             'icon': rc.icon,
    #             'order': rc.order,
    #             'public': rc.public}

    # def getRc(self):
    #     if self.rc is None:
    #         return None
        
    #     return {'id': self.rc.id,
    #             'name': self.rc.name,
    #             'icon': self.rc.icon,
    #             'order': self.rc.order,
    #             'public': self.rc.public}
    
    # def updateRc(self, params):
    #     if self.rc is None:
    #         return None

    #     self.rc.name = params['name']
    #     self.rc.icon = params['icon']
    #     self.rc.order = params['order']
    #     self.rc.public = params['public']
    #     self.rc.timestamp = datetime.utcnow()

    #     db.session.commit()
        
    #     return {'id': self.rc.id,
    #             'name': self.rc.name,
    #             'icon': self.rc.icon,
    #             'order': self.rc.order,
    #             'public': self.rc.public}

    # def deleteRc(self):
    #     if self.rc is None:
    #         return None

    #     for btn in self.rc.buttons:
    #         db.session.delete(btn)

    #     db.session.commit()
    #     db.session.delete(self.rc)
    #     db.session.commit()
    #     self.rc = None

    #     return True

class ButtonHelper:

    def __init__(self, btn_id = None):
        self.set(btn_id)

    def get(self):
        return self.button

    def set(self, btn_id):
        self.button = Button.query.filter_by(id = btn_id).first() if btn_id else None

    def createButton(self, params):
        btn = Button(rc_id = params['rc_id'],
                    radio_id = params['radio_id'],
                    name = params['name'],
                    order_hor = params['order_hor'],
                    order_ver = params['order_ver'],
                    color = params['color'],
                    type = params['type'],
                    message = params['message'],
                    timestamp = datetime.utcnow())

        db.session.add(btn)
        db.session.commit()

        self.button = btn

        return {'id': btn.id,
                'rc_id' : btn.rc_id,
                'radio_id': btn.radio_id,
                'name': btn.name,
                'order_hor': btn.order_hor,
                'order_ver': btn.order_ver,
                'color': btn.color,
                'type': btn.type,
                'message': btn.message}

    def getButton(self):
        if self.button is None:
            return None

        return {'id': self.button.id,
                'rc_id' : self.button.rc_id,
                'radio_id': self.button.radio_id,
                'name': self.button.name,
                'order_hor': self.button.order_hor,
                'order_ver': self.button.order_ver,
                'color': self.button.color,
                'message': self.button.message,
                'type': self.button.type}

    def updateButton(self, params):
        if self.button is None:
            return None

        self.button.radio_id = params['radio_id']
        self.button.name = params['name']
        self.button.order_hor = params['order_hor']
        self.button.order_ver = params['order_ver']
        self.button.color = params['color']
        self.button.type = params['type']
        self.button.message = params['message']
        self.button.timestamp = datetime.utcnow()

        db.session.commit()

        return {'id': self.button.id,
                'rc_id' : self.button.rc_id,
                'radio_id': self.button.radio_id,
                'name': self.button.name,
                'order_hor': self.button.order_hor,
                'order_ver': self.button.order_ver,
                'color': self.button.color,
                'type': self.button.type,
                'message': self.button.message}

    def deleteButton(self):
        if self.button is None:
            return None

        button = {'id': self.button.id,
                'rc_id' : self.button.rc_id,
                'radio_id': self.button.radio_id,
                'name': self.button.name,
                'order_hor': self.button.order_hor,
                'order_ver': self.button.order_ver,
                'color': self.button.color,
                'type': self.button.type,
                'message': self.button.message}

        db.session.delete(self.button)
        db.session.commit()
        self.button = None
        return button

    # def getNode(self):
    #     if self.rc is None or self.button is None:
    #         return None

    #     return Node.query.filter_by(id = self.button.node_id).first()

    def catchIrSignal(self, node_sevice, event):
        node = Node.query.filter_by(id = self.button.node_id).first()

        event.host_name = node.host_name
        event.button_id = self.button.id
        
        if node is not None and node_sevice.pushToNode(event):
            return True

        return False

    def getHostName(self):
        if self.button is None:
            return None

        radio = Radio.query.filter_by(id = self.button.radio_id).first()
        return radio.arduino.node.host_name

class NodeHelper:

    def __init__(self, node_id = None):
        self.set(node_id)

    def get(self):
        return self.node

    def set(self, node_id):
        self.node = Node.query.filter_by(id = node_id).first() if node_id else None

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
        node = Node(
                    # name = params['name'],
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
                # 'name': self.node.name,
                'host_name': self.node.host_name,
                'order': self.node.order}

    def updateNode(self, params):
        if self.node is None:
            return None

        # self.node.name = params['name']
        self.node.host_name = params['host_name']
        self.node.order = params['order']
        self.node.timestamp = datetime.utcnow()

        db.session.commit()
        
        return {'id': self.node.id,
                # 'name': self.node.name,
                'host_name': self.node.host_name,
                'order': self.node.order}

    def deleteNode(self):
        if self.node is None:
            return None

        for arduino in self.node.arduinos:
            db.session.delete(arduino)

        db.session.commit()
        db.session.delete(self.node)
        db.session.commit()
        self.node = None
        return True

    def getNodeByName(self, host_name):
        try:
            node = Node.query.filter_by(host_name = host_name).first()
        except Exception as e:
            db.session.rollback()
            logging.error('[helpers] db session error. rolled back')
            logging.error(str(e))
            return False

        return node

class ArduinoHelper:

    def __init__(self, arduino_id = None):
        self.set(arduino_id)

    def get(self):
        return self.arduino

    def getNode(self):
        if self.arduino is None:
            return None
        
        return self.arduino.node

    def set(self, arduino_id):
        self.arduino = Arduino.query.filter_by(id = arduino_id).first() if arduino_id else None

    def getArduinos(self):
        arduinos = []

        for arduino in Arduino.query.order_by(Arduino.order).all():
            a = {'id': arduino.id,
                'node_id': arduino.node_id,
                'usb': arduino.usb,
                'name': arduino.name,
                'order': arduino.order}

            arduinos.append(a)

        return arduinos

    def createArduino(self, params):
        arduino = Arduino(node_id = params['node_id'],
                        usb = params['usb'],
                        name = params['name'],
                        order = params['order'],
                        timestamp = datetime.utcnow())

        db.session.add(arduino)
        db.session.commit()

        self.arduino = arduino

        return {'id': arduino.id,
                'node_id': arduino.node_id,
                'usb': arduino.usb,
                'name': arduino.name,
                'order': arduino.order}

    def getArduino(self):
        if self.arduino is None:
            return None

        return {'id': self.arduino.id,
                'node_id': self.arduino.node_id,
                'usb': self.arduino.usb,
                'name': self.arduino.name,
                'order': self.arduino.order}

    def updateArduino(self, params):
        if self.arduino is None:
            return None

        self.arduino.usb = params['usb']
        self.arduino.name = params['name']
        self.arduino.order = params['order']
        self.arduino.timestamp = datetime.utcnow()

        db.session.commit()

        return {'id': self.arduino.id,
                'node_id': self.arduino.node_id,
                'usb': self.arduino.usb,
                'name': self.arduino.name,
                'order': self.arduino.order}

    def deleteArduino(self):
        if self.arduino is None:
            return None

        arduino = {'id': self.arduino.id,
                'node_id': self.arduino.node_id,
                'usb': self.arduino.usb,
                'name': self.arduino.name,
                'order': self.arduino.order}

        db.session.delete(self.arduino)
        db.session.commit()
        self.arduino = None
        return arduino

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
                'type': radio.type,
                'pipe': radio.pipe,
                'name': radio.name,
                'on_request': radio.on_request,
                'expired_after': radio.expired_after,
                'enabled': radio.enabled,
                'order': radio.order}

            radios.append(r)

        return radios

    def createRadio(self, params):
        radio = Radio(arduino_id = params['arduino_id'],
                    type = params['type'],
                    pipe = params['pipe'],
                    name = params['name'],
                    enabled = params['enabled'],
                    on_request = params['on_request'],
                    expired_after = params['expired_after'],
                    order = params['order'],
                    timestamp = datetime.utcnow())

        db.session.add(radio)
        db.session.commit()

        return {'id': radio.id,
                'arduino_id': radio.arduino_id,
                'type': radio.type,
                'pipe': radio.pipe,
                'name': radio.name,
                'on_request': radio.on_request,
                'expired_after': radio.expired_after,
                'enabled': radio.enabled,
                'order': radio.order}

    def getRadio(self):
        if self.radio is None:
            return None
        
        return {'id': self.radio.id,
                'arduino_id': self.radio.arduino_id,
                'type': self.radio.type,
                'pipe': self.radio.pipe,
                'name': self.radio.name,
                'on_request': self.radio.on_request,
                'expired_after': self.radio.expired_after,
                'enabled': self.radio.enabled,
                'order': self.radio.order}

    def updateRadio(self, params):
        if self.radio is None:
            return None

        self.radio.arduino_id = params['arduino_id']
        self.radio.type = params['type']
        self.radio.pipe = params['pipe']
        self.radio.name = params['name']
        self.radio.on_request = params['on_request']
        self.radio.expired_after = params['expired_after']
        self.radio.enabled = params['enabled']
        self.radio.order = params['order']
        self.radio.timestamp = datetime.utcnow()

        db.session.commit()
        
        return {'id': self.radio.id,
                'arduino_id': self.radio.arduino_id,
                'type': self.radio.type,
                'pipe': self.radio.pipe,
                'name': self.radio.name,
                'on_request': self.radio.on_request,
                'expired_after': self.radio.expired_after,
                'enabled': self.radio.enabled,
                'order': self.radio.order}

    def deleteRadio(self):
        if self.radio is None:
            return None

        db.session.delete(self.radio)
        db.session.commit()
        self.radio = None
        return True
        
    def getByPipe(self, pipe):
        return Radio.query.filter_by(pipe = pipe).first()