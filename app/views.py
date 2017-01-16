from flask import render_template, jsonify
from app import app
from config import status_code, devices, device_commands

from gpio import led

# Roure for start Framework7
@app.route('/')

def index():
    return render_template('index.html')

# REST API for Framework7
@app.route('/api/v1.0/devices', methods=['GET'])
def get_devices():
    return jsonify({'devices': devices, 'status_code': status_code['success']})

@app.route('/api/v1.0/device/<name>/<command>', methods=['GET'])
def get_task(name, command):
    if name in device_commands:
        if command in device_commands[name]:
            # print(name, command)
            led.start(name, command)
            return jsonify({'status_code': status_code['success']})

    return jsonify({'status_code': status_code['failed']})
