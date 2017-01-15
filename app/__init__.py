from flask import Flask
from app.gpio import led

l = led.Led()
app = Flask(__name__)
from app import views

