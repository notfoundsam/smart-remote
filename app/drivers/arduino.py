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

    def prepareSignal(self, raw_signal, radio):
        prepared_signal = []
        prepared_signal.append('i%s' % radio)

        for x in raw_signal.split(' '):
            if int(x) > 65000:
                prepared_signal.append('65000')
            else:
                prepared_signal.append(x)

        prepared_signal.append('\n')

        return ' '.join(prepared_signal)

@Singleton
class ArduinoDev(Common):
    ser = None

    def connect(self):
        if self.ser is None:
            self.ser = True
            print('Connect to /dev/ttyUSB0', file=sys.stderr)

    def close(self):
        print('Close /dev/ttyUSB0', file=sys.stderr)

    def test(self):
        print('IT IS TEST', file=sys.stderr)

    def sendIrSignal(self, raw_signal, radio):
        signal = self.prepareSignal(raw_signal, radio)
        print('Signal to send: %s' % signal, file=sys.stderr)

        return True

@Singleton
class Arduino(Common):
    flag = True
    ser = None

    def test(self):
        if self.flag:
            print('Test', file=sys.stderr)
            self.flag = False

    def send(self):
        print('SEND', file=sys.stderr)

    def close(self):
        print('Close /dev/ttyUSB0', file=sys.stderr)

    def connect(self):
        if self.ser is None:
            # self.ser = True
            self.ser = serial.Serial()
            self.ser.baudrate = 500000
            self.ser.port = '/dev/ttyUSB0'
            self.ser.timeout = 0.5
            self.ser.open()

            # Only after write sketch into Arduino
            time.sleep(2)
            self.ser.flushInput()
            self.ser.flushOutput()
            self.ser.write(b'connect')
            time.sleep(1)
            self.ser.flushInput()
            self.ser.flushOutput()

    def sendIrSignal(self, raw_signal, radio):
        signal = self.prepareSignal(raw_signal, radio)
        b_arr = bytearray(signal.encode())

        self.ser.write(b_arr)
        self.ser.flush()

        response = self.ser.readline()
        response = response.rstrip()

        if response == 'OK':
            return True

        return False
