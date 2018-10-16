#!/usr/bin/env python3
import os, sys

# from app.drivers.arduino import Arduino
from app.starter import FirstRequest
from app.drivers.lirc import Lirc, LircDev

if 'FLASK_ENV' in os.environ and os.environ['FLASK_ENV'] == 'development':
    debug = True
else:
    debug = False

# arduino = Arduino.Instance()
# service = Starter.Instance()
lirc = None

if not debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    first_request = FirstRequest()
    first_request.start()
    
    if debug:
        sys.stderr.write('RUN AS DEVELOPMENT\n')
        # arduino.connect('dev')
        lirc = LircDev()
    else:
        sys.stderr.write('RUN AS PRODUCTION\n')
        # arduino.connect()
        lirc = Lirc()

from app import app

if __name__ == '__main__':
    app.run(debug=debug, host='0.0.0.0', threaded=True)