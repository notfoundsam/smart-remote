#!/usr/bin/env python
from app import app
from app.gpio import driver
from app.config import devices_drivers

if __name__ == '__main__':
	driver.init(devices_drivers)
	app.run(host='0.0.0.0', threaded=True)
	# app.run(debug=True, host='0.0.0.0', threaded=True)
	driver.destroy()
