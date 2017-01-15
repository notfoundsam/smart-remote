#!/usr/bin/env python
from app import app
#!flask/bin/python
# from app import gpio

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', threaded=True)
