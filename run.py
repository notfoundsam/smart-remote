#!/usr/bin/env python
import os, sys

# from app.drivers.arduino import Arduino
import starter
from app.drivers.lirc import Lirc, LircDev

if 'APP_ENV' in os.environ and os.environ['APP_ENV'] == 'development':
    debug = True
else:
    debug = False

# arduino = Arduino.Instance()
# service = Starter.Instance()
lirc = None

if not debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    first_request = starter.FirstRequest()
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
