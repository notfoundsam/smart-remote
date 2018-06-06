from __future__ import print_function
import sys, os
from .models import Radio
from app import db
from datetime import datetime
from run import arduino
import threading, time

class RadioSensor():
    def create(self, content):
        if content['radio_id']:
            radio = Radio.query.filter_by(id = content['radio_id']).first()

            if radio is None:
                return False

            radio.name = content['radio_name']
            radio.pipe = content['radio_pipe']
            # radio.enabled = content['enabled']
            radio.order = content['radio_order']
            radio.battery = content['radio_battery']
            radio.dht = content['radio_dht']
            radio.timestamp = datetime.utcnow()
        else:
            radio = Radio(name = content['radio_name'],
                            pipe = content['radio_pipe'],
                            enabled = True,
                            order = content['radio_order'],
                            battery = content['radio_battery'],
                            dht = content['radio_dht'],
                            timestamp = datetime.utcnow())

            db.session.add(radio)

        db.session.commit()
        
        return True

    def remove(self, content):
        radio = Radio.query.filter_by(id = content['radio']).first()

        if radio is not None:
            db.session.delete(radio)

        db.session.commit()

    def getRadiosList(self):
        radios = []

        for radio in Radio.query.order_by(Radio.id).all():
            r = {
                'id': radio.id,
                'pipe': radio.pipe,
                'name': radio.name,
                'battery': radio.battery,
                'dht': radio.dht,
            }

            radios.append(r)

        return radios

    def getRadiosIdName(self):
        radios = []

        for radio in Radio.query.order_by(Radio.id).all():
            r = {
                'id': radio.id,
                'pipe': radio.pipe,
                'name': radio.name,
            }

            radios.append(r)

        return radios

    def getRadio(self, content):
        id = content['id']
        radio = Radio.query.filter_by(id = id).first()
        print(radio, file=sys.stderr)

        if radio is not None:
            return {
                'id': radio.id,
                'name': radio.name,
                'pipe': radio.pipe,
                'order': radio.order,
                'battery': radio.battery,
                'dht': radio.dht,
            }

        return False

class StateChecker(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            time.sleep(10)

            for radio in Radio.query.order_by(Radio.id).all():
                arduino.status(radio)
