from flask import render_template
from app import app

@app.route('/')
@app.route('/index')
@app.route('/bid')

def index():
	return render_template('index.html')
def bid():
	return render_template('bid.html')
