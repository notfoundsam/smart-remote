#!flask/bin/python
from app import app
# from app import gpio

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', threaded=True)
