#!/usr/bin/env python
########################################################################
# Filename    : led.py
# Description : Turn On/Off a led
# auther      : Sosetc
# modification: 2017/01/16
########################################################################
from devices.tv import Tv
from devices.led import Led

try:
    import RPi.GPIO as GPIO
    import Adafruit_DHT
except ImportError:
    print("Module RPi.GPIO not found. Switch to development mode")
    import GPIO_Dev as GPIO
    # print("Load Adafruit_DHT in development mode")
    # import Adafruit_DHT_Dev as Adafruit_DHT

drivers = {}

def init(devices):
    # global ledPin
    global drivers

    print("DRIVER: Setup GPIO")
    GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location

    for d in devices:
        if d['driver'] == 'led':
            drivers['led'] = Led(GPIO)
            continue
        if d['driver'] == 'tv':
            drivers['tv'] = Tv(GPIO)
            continue

    for k, v in drivers.items():
        v.status()
    # led = Led(GPIO)
    # tv.status()

    # import devi
    # GPIO.setup(ledPin, GPIO.OUT)   # Set ledPin's mode is output
    # GPIO.output(ledPin, GPIO.LOW)  # Set ledPin low to off led

def destroy():
    # global ledPin

    # GPIO.output(ledPin, GPIO.LOW)     # Turn led off
    GPIO.cleanup()                    # Release resource

def run(device, command):
    global drivers
    # global ledStatus

    if device in drivers:
        print("DRIVER: device found")
        if drivers[device].run(command):
            print("DRIVER: command ok")
            return True
            # if (command == 'power' and ledStatus):
            # GPIO.output(ledPin, GPIO.LOW)
            # ledStatus = False
            # print('OFF')
        else:
            print("DRIVER: bad command")
            return False
            # GPIO.output(ledPin, GPIO.HIGH)
            # ledStatus = True
            # print('ON')
    else:
        print("DRIVER: device [%s] not found" % device)
        return False

