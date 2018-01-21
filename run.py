#!/usr/bin/env python
from __future__ import print_function
import os, sys

from app.drivers.arduino import Arduino, ArduinoDev
from app.drivers.lirc import Lirc, LircDev

if 'APP_ENV' in os.environ and os.environ['APP_ENV'] == 'development':
    debug = True
else:
    debug = False

arduino = None
lirc = None

if not debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    if debug:
        print('RUN AS DEVELOPMENT', file=sys.stderr)
        arduino = ArduinoDev.Instance()
        lirc = LircDev()
    else:
        print('RUN AS PRODUCTION', file=sys.stderr)
        arduino = Arduino.Instance()
        lirc = Lirc()
        
    arduino.connect()

from app import app

if __name__ == '__main__':    
    app.run(debug=debug, host='0.0.0.0', threaded=True)
