# import config
from flask import render_template, flash, redirect, session, url_for, request, \
    g, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from .models import User
# from gpio import driver
from config import devices, status_code


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@lm.unauthorized_handler
def unauthorized():
    return jsonify({'status_code': status_code['login_faild']}), 401

@app.before_request
def before_request():
    # print(current_user)
    g.user = current_user

# Roure for start Framework7
@app.route('/')
# @login_required
def index():
    return render_template('index.html')

# REST API for Framework7
@app.route('/api/v1.0/devices', methods=['GET'])
@login_required
def get_devices():
    return jsonify({'devices': devices, 'status_code': status_code['success']})

# @app.route('/api/v1.0/device/<device>/<command>', methods=['GET'])
# def get_task(device, command):

@app.route('/api/v1.0/device/<device>/<command>', methods=['GET'])
def get_task(device, command):
    pass
    # result = driver.run(device, command)
    # if result is not False:
    #     return jsonify({'status_code': status_code['success'], 'result': result})
    # else:
    #     return jsonify({'status_code': status_code['failed']})

@app.route('/api/v1.0/login', methods=['POST'])
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    # form = LoginForm()
    if True:
        email = request.form['email']
        password = request.form['password']

        # username = request.form['username']
        print(email, password)
        return jsonify({'status_code': status_code['login_faild']})
        # session['remember_me'] = True
    #     return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
    return render_template('login.html',
                           title='Sign In',
                           form=form,
                           providers=app.config['OPENID_PROVIDERS'])
