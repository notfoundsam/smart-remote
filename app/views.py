# import config
from flask import render_template, jsonify
from app import app
from gpio import driver
from config import devices, status_code

# Roure for start Framework7
@app.route('/')
def index():
    return render_template('index.html')

# REST API for Framework7
@app.route('/api/v1.0/devices', methods=['GET'])
def get_devices():
    return jsonify({'devices': devices, 'status_code': status_code['success']})

@app.route('/api/v1.0/device/<device>/<command>', methods=['GET'])
def get_task(device, command):
    if driver.run(device, command):
        return jsonify({'status_code': status_code['success']})
    else:
        return jsonify({'status_code': status_code['failed']})
