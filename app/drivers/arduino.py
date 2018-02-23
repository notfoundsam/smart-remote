from __future__ import print_function
import serial
import time
import array
import os, sys

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

@Singleton
class ArduinoDev(Common):
    ser = None

    def connect(self):
        if self.ser is None:
            self.ser = True
            print('Connect to /dev/ttyUSB0', file=sys.stderr)

    def close(self):
        print('Close /dev/ttyUSB0', file=sys.stderr)

    def sendCommand(self, command):
        data = self.prepareCommand(command, radio)
        print('Command to send: %s' % data, file=sys.stderr)

    def sendIrSignal(self, raw_signal, radio):
        data = self.prepareIrSignal(raw_signal, radio)
        print('Signal to send: %s' % data, file=sys.stderr)

        return True

@Singleton
class Arduino(Common):
    ser = None

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
    
    def send(self, data):
        print(data, file=sys.stderr)
        b_arr = bytearray(data.encode())

        self.ser.flushInput()
        self.ser.write(b_arr)
        self.ser.flush()

        response = self.ser.readline()
        result = response.rstrip()

        if result:
            return result

        return False

    def sendCommand(self, command):
        data = self.prepareCommand(command, radio)
        return self.send(data)

    def sendIrSignal(self, raw_signal, radio):
        data = self.prepareIrSignal(raw_signal, radio)
        return self.send(data)
        
