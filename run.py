#!/usr/bin/env python
from __future__ import print_function
import os, sys

from app.drivers.arduino import Arduino, ArduinoDev

if 'APP_ENV' in os.environ and os.environ['APP_ENV'] == 'development':
    debug = True
else:
    debug = False

arduino = None

if not debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    if debug:
        print('RUN AS DEVELOPMENT', file=sys.stderr)
        arduino = ArduinoDev.Instance()
    else:
        print('RUN AS PRODUCTION', file=sys.stderr)
        arduino = Arduino.Instance()
        
    arduino.connect()

from app import app

# from app.gpio import driver
# from app.config import devices_drivers

if __name__ == '__main__':
    # arduino.serial_connect(ser)
    # driver.init(devices_drivers)
    # app.run(host='0.0.0.0', threaded=True)
    # my_test = 'ooooooopppp'
    
    app.run(debug=debug, host='0.0.0.0', threaded=True)
    # driver.destroy()
