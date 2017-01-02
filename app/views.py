from flask import render_template, jsonify
from app import app
from config import status_code, devices


# Roure for start Framework7
@app.route('/')
# @app.route('/index')
def index():
    return render_template('index.html')


# REST API for Framework7
@app.route('/api/v1.0/devices', methods=['GET'])
def get_devices():
    return jsonify({'devices': devices})

@app.route('/api/v1.0/device/<name>/<command>', methods=['GET'])
def get_task(name, command):
    # print(name, command)
    # task = filter(lambda t: t['id'] == task_id, tasks)
    # if len(task) == 0:
    #     abort(404)
    return jsonify({'status_code': status_code['failed']})
