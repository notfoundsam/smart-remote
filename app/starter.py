import os, sys
import requests, time
import threading

class FirstRequest(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        time.sleep(2)
        r = requests.get('http://127.0.0.1:5000/')

class Config:

  def __init__(self, app):
    self.app = app

    if 'APP_DOCKER' in os.environ:
        self.DB_HOST = 'db'
        self.DB_PORT = '3306'
        self.DB_NAME = 'smart_remote'
        self.DB_USER = 'root'
        self.DB_PASS = 'root'
    else:
        self.DB_HOST = '192.168.100.100'
        self.DB_PORT = '3390'
        self.DB_NAME = 'smart_remote'
        self.DB_USER = 'root'
        self.DB_PASS = 'root'

    self.app.config['TRAP_HTTP_EXCEPTIONS'] = True
    self.app.config['CSRF_ENABLED'] = True
    self.app.config['SECRET_KEY'] = 'you-will-never-guess'
    self.app.config['SQLALCHEMY_DATABASE_URI'] = self.createDbUri()

  def createDbUri(self):
      return 'mysql+mysqlconnector://%s:%s@%s:%s/%s' % (self.DB_USER,self.DB_PASS,self.DB_HOST,self.DB_PORT,self.DB_NAME)
