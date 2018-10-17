#!/usr/bin/env python3
import os, sys

from app.bootstrap import FirstRequest
from app.drivers.lirc import Lirc, LircDev
from app import flask_app

if __name__ == '__main__':
    first_request = FirstRequest()
    first_request.start()

    flask_app.run(host='0.0.0.0', threaded=True)
