#!/usr/bin/env python3
import os, sys
from gevent.pywsgi import WSGIServer

from app.bootstrap import FirstRequest
# from app.drivers.lirc import Lirc, LircDev
from app import flask_app

if __name__ == '__main__':
    first_request = FirstRequest()
    first_request.start()

    if False and 'FLASK_ENV' in os.environ and os.environ['FLASK_ENV'] == 'development':
        flask_app.run(host='0.0.0.0', threaded=True)
    else:
        http_server = WSGIServer(('', 5000), flask_app)
        http_server.serve_forever()
