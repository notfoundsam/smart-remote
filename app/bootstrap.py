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
        self.app.config['SECRET_KEY']                     = 'you-will-never-guess'
        
        if 'FLASK_ENV' in os.environ and os.environ['FLASK_ENV'] == 'development':
            self.debug                                       = True
            self.app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = True
            self.app.config['SQLALCHEMY_RECORD_QUERIES']     = True

        # Logging settings
        logging.basicConfig(
            format='%(asctime)s - [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            level= logging.DEBUG if self.debug else logging.ERROR,
            handlers=[
                logging.FileHandler("app.log"),
                logging.StreamHandler()
            ])

        engine = create_engine(self.createDbUri(), echo=self.debug, pool_recycle=3600, pool_pre_ping=True)
        # engine = create_engine(self.createDbUri(),
        #                             echo=self.debug,
        #                             pool_recycle=28880,
        #                             pool_size=5,
        #                             max_overflow=10,
        #                             pool_timeout=30,
        #                             pool_pre_ping=True)

        self.db_session = sessionmaker(bind=engine)

    def getNewDbSession(self):
        return self.db_session()

    def createDbUri(self):
        return 'mysql+mysqlconnector://%s:%s@%s:%s/%s' % (self.DB_USER,self.DB_PASS,self.DB_HOST,self.DB_PORT,self.DB_NAME)

class Cache:

    def __init__(self):
        self.radios_params = {}

    def getRadioParams(self, radio_id):
        if radio_id in self.radios_params:
            return self.radios_params[radio_id]
        
        return {}

    def setRadioParams(self, radio_id, params):
        self.radios_params[radio_id] = params
    
    def clearRadioParams(self, radio_id, params):
        if radio_id in self.radios_params:
            del self.radios_params[radio_id]
