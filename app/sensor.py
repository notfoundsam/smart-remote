from __future__ import print_function
import sys, os
from .models import Radio
from app import db
from datetime import datetime
from run import arduino, lirc

class RadioSensor:
    def create(self, content):
        radio = Radio(name = content['radio_name'],
                        enabled = True,
                        battery = content['radio_battery'],
                        dht = content['radio_dht'],
                        timestamp = datetime.utcnow())

        db.session.add(radio)
        db.session.commit()
        return True

    def getRadiosList(self):
        radios = []

        for radio in Radio.query.order_by(Radio.id).all():
            r = {
                'id': radio.id,
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
                'name': radio.name,
            }

            radios.append(r)

        return radios
