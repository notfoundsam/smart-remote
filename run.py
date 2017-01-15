#!/usr/bin/env python
from app import app
from app import l
#!flask/bin/python

if __name__ == '__main__':
	# print
	app.run(host='0.0.0.0', threaded=True)
	l.destroy()
	# app.run(debug=True, host='0.0.0.0', threaded=True)
