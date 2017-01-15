#!/usr/bin/env python
########################################################################
# Filename    : Blink.py
# Description : Make an led blinking.
# auther      : www.freenove.com
# modification: 2016/06/07
########################################################################
import RPi.GPIO as GPIO
# import time

class Led:

    ledPin = 11    # RPI Board pin11
    ledStatus = False

    def __init__(self):
        print("INIT")
        GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
        GPIO.setup(self.ledPin, GPIO.OUT)   # Set ledPin's mode is output
        GPIO.output(self.ledPin, GPIO.LOW) # Set ledPin low to off led
        # print 'using pin%d'%ledPin
        # 
        

    # def loop():
    #     while True:
    #         GPIO.output(ledPin, GPIO.HIGH)  # led on
    #         print '...led on'
    #         time.sleep(1)   
    #         GPIO.output(ledPin, GPIO.LOW) # led off
    #         print 'led off...'
    #         time.sleep(1)

    def destroy():
      GPIO.output(self.ledPin, GPIO.LOW)     # led off
      GPIO.cleanup()                     # Release resource

# if __name__ == '__main__':     # Program start from here
#   setup()
#   try:
#       loop()
#   except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
#       destroy()

    def start(self, name, command):
        # setup()
        if name == 'tv':
            if (command == 'power' and self.ledStatus):
                self.ledStatus = False
                GPIO.output(self.ledPin, GPIO.LOW)
                print('OFF')
            else:
                self.ledStatus = True
                print('ON')
                GPIO.output(self.ledPin, GPIO.HIGH)

