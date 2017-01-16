#!/usr/bin/env python
########################################################################
# Filename    : led.py
# Description : Turn On/Off a led
# auther      : Sosetc
# modification: 2017/01/16
########################################################################
try:
    import RPi.GPIO as GPIO
except ImportError:
    print("Module RPi.GPIO not found. Switch to development mode")
    import devgpio as GPIO

ledPin    = 11    # RPI Board pin11 connected to led
# setted    = False
ledStatus = False

def setup():
    global setted
    global ledPin

    # if (setted == False):
    print("Setup GPIO")
    GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
    GPIO.setup(ledPin, GPIO.OUT)   # Set ledPin's mode is output
    GPIO.output(ledPin, GPIO.LOW)  # Set ledPin low to off led
    # setted = True

def destroy():
    global ledPin

    GPIO.output(ledPin, GPIO.LOW)     # Turn led off
    GPIO.cleanup()                    # Release resource

def start(name, command):
    global ledPin
    global ledStatus

    if name == 'tv':
        if (command == 'power' and ledStatus):
            ledStatus = False
            GPIO.output(ledPin, GPIO.LOW)
            print('OFF')
        else:
            ledStatus = True
            print('ON')
            GPIO.output(ledPin, GPIO.HIGH)

