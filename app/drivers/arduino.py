from __future__ import print_function
import serial
import time
import array
import os, sys
import threading, Queue
import requests

class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Also, the decorated class cannot be
    inherited from. Other than that, there are no restrictions that apply
    to the decorated class.

    To get the singleton instance, use the `Instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    """

    def __init__(self, decorated):
        self._decorated = decorated

    def Instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)

class Common():
    ser = None
    queue = None
    starter = None

    def startQueue(self):
        self.queue = ArduinoQueue(self.ser)
        self.queue.start()
    
    def activateQueueStarter(self):
        self.starter = ArduinoQueueStarter()
        self.starter.start()

    def prepareIrSignal(self, raw_signal, radio):
        data = []
        data.append('i%s' % radio)

        for x in raw_signal.split(' '):
            if int(x) > 65000:
                data.append('65000')
            else:
                data.append(x)

        data.append('\n')

        return ' '.join(data)

    def prepareCommand(self, command, radio):
        return 'c%s %s\n' % (radio, command)

    def sendCommand(self, command, radio):
        self.send(self.prepareCommand(command, radio), radio)

    def sendIrSignal(self, raw_signal, radio):
        self.send(self.prepareIrSignal(raw_signal, radio), radio)

@Singleton
class ArduinoDev(Common):

    def connect(self):
        if self.ser is None:
            self.ser = True
            print('Connect to /dev/ttyUSB0', file=sys.stderr)
            self.activateQueueStarter()

    def send(self, data, radio):
        self.queue.putItem(ArduinoQueueItemDev(self.ser, data, radio, 1))

@Singleton
class Arduino(Common):

    def close(self):
        print('Close /dev/ttyUSB0', file=sys.stderr)

    def connect(self):
        if self.ser is None:
            print('Connect to /dev/ttyUSB0', file=sys.stderr)
            self.ser = serial.Serial()
            self.ser.baudrate = 500000
            self.ser.port = '/dev/ttyUSB0'
            self.ser.timeout = 5
            self.ser.open()

            # Only after write sketch into Arduino
            time.sleep(2)
            self.ser.flushInput()
            self.ser.flushOutput()
            self.ser.write(b'connect')
            time.sleep(1)
            print(repr(self.ser.readline()), file=sys.stderr)
            self.ser.flushInput()
            self.activateQueueStarter()
    
    def send(self, data):
        self.queue.putItem(ArduinoQueueItem(self.ser, data, radio, 1))

class ArduinoQueue(threading.Thread):

    def __init__(self, ser):
        threading.Thread.__init__(self)
        self.ser = ser
        self.workQueue = Queue.PriorityQueue()

    def run(self):
        while True:
            if not self.workQueue.empty():
                queue_item = self.workQueue.get()
                queue_item.run()
            else:
                time.sleep(0.05)

    def putItem(self, item):
        self.workQueue.put(item)

class ArduinoQueueStarter(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        time.sleep(2)
        r = requests.get('http://127.0.0.1:5000/')
        print('Send first request', file=sys.stderr)

class ArduinoQueueItem():

    def __init__(self, ser, data, radio, priority):
        self.ser = ser
        self.data = data
        self.radio = radio
        self.priority = priority

    def __cmp__(self, other):
        return cmp(self.priority, other.priority)

    def run(self):
        print(data, file=sys.stderr)

        b_arr = bytearray(data.encode())

        self.ser.flushInput()
        self.ser.write(b_arr)
        self.ser.flush()

        response = self.ser.readline()
        response = response.rstrip()

        data = response.split(':')

        if data[1] == 'FAIL':
            return {'error': True,'message': data[0]}
        elif data[1] == 'OK':
            return {'error': False,'message': data[0]}
        else:
            emit('json', {'response': {'result': 'error', 'message': 'Unknown error'}})

class ArduinoQueueItemDev(ArduinoQueueItem):

    def run(self):
        # emit('json', {'response': {'result': 'error', 'message': 'Unknown error'}})
        print('Data to send: %s' % self.data, file=sys.stderr)

