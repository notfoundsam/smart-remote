import os, logging
import requests, time
import threading
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class FirstRequest(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        time.sleep(2)
        r = requests.get('http://127.0.0.1:5000/')

class Config:

    def __init__(self, app):
        self.app = app
        self.debug = False

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
            self.NODE_RED_HOST = '192.168.100.111'
            self.NODE_RED_PORT = 9090
            self.DB_HOST       = '192.168.100.111'
            self.DB_PORT       = '3306'
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
        self.app.config['SQLALCHEMY_POOL_RECYCLE']        = 60
        self.app.config['SQLALCHEMY_POOL_SIZE']           = 20
        # self.app.config['SQLALCHEMY_MAX_OVERFLOW']        = 10
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
        self.app.config['SECRET_KEY']                     = 'you-will-never-guess'
        self.app.config['SQLALCHEMY_DATABASE_URI']        = self.createDbUri()
        
        if 'FLASK_ENV' in os.environ and os.environ['FLASK_ENV'] == 'development':
            self.debug                                       = True
            self.app.config['SQLALCHEMY_ECHO']               = True
            self.app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = True
            self.app.config['SQLALCHEMY_RECORD_QUERIES']     = True

        # DB engine
        self.engine = create_engine(self.createDbUri(), echo=self.debug, pool_recycle=3600)
        self.Session = sessionmaker(bind=self.engine)

        # Logging settings
        logging.basicConfig(
            format='%(asctime)s - [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            level= logging.DEBUG if self.debug else logging.ERROR,
            handlers=[
                logging.FileHandler("app.log"),
                logging.StreamHandler()
            ])

    def createDbUri(self):
        return 'mysql+mysqlconnector://%s:%s@%s:%s/%s' % (self.DB_USER,self.DB_PASS,self.DB_HOST,self.DB_PORT,self.DB_NAME)
