#!/usr/bin/env python
from app import app
from app.gpio import led

if __name__ == '__main__':
	led.setup()
	app.run(host='0.0.0.0', threaded=True)
	# app.run(debug=True, host='0.0.0.0', threaded=True)
	led.destroy()
