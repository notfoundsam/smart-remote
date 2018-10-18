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

    # Application settings
    if 'APP_DOCKER' in os.environ:
        self.NODE_RED_HOST = 'node-red'
        self.NODE_RED_PORT = 9090
        self.DB_HOST       = 'db'
        self.DB_PORT       = '3306'
        self.DB_NAME       = 'smart_remote'
        self.DB_USER       = 'root'
        self.DB_PASS       = 'root'
    else:
        self.NODE_RED_HOST = '192.168.100.100'
        self.NODE_RED_PORT = 9090
        self.DB_HOST       = '192.168.100.100'
        self.DB_PORT       = '3390'
        self.DB_NAME       = 'smart_remote'
        self.DB_USER       = 'root'
        self.DB_PASS       = 'root'

    # DiscoverService settings
    self.BROADCAST_MASK      = '255.255.255.255'
    self.BROADCAST_PORT      = 32000
    self.BROADCAST_INTERVAL  = 5

    # RpiNode settings
    self.SOCKET_BIND_ADDRESS = ''
    self.SOCKET_BIND_PORT    = 32001
    self.SOCKET_CONNECTIONS  = 5

    # Flask settings
    self.app.config['TRAP_HTTP_EXCEPTIONS']           = True
    self.app.config['CSRF_ENABLED']                   = True
    self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    self.app.config['SECRET_KEY']                     = 'you-will-never-guess'
    self.app.config['SQLALCHEMY_DATABASE_URI']        = self.createDbUri()

  def createDbUri(self):
      return 'mysql+mysqlconnector://%s:%s@%s:%s/%s' % (self.DB_USER,self.DB_PASS,self.DB_HOST,self.DB_PORT,self.DB_NAME)
