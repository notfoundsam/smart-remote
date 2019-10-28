#!/usr/bin/env python3
import os, sys
from gevent.pywsgi import WSGIServer

from app.bootstrap import FirstRequest
from app import flask_app

if __name__ == '__main__':
    first_request = FirstRequest()
    first_request.start()

    http_server = WSGIServer((first_request.APP_HOST, first_request.APP_PORT), flask_app)
    http_server.serve_forever()
