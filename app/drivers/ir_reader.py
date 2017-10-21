from __future__ import print_function
import sys
import math
import os
from datetime import datetime
import time

def read_signal():
    # This pin is also referred to as GPIO18
    INPUT_WIRE = 12

    env = os.environ['APP_ENV']
    t_end = time.time() + 60 / 30

    if env != 'development':
        import RPi.GPIO as GPIO
    else:
        print('%s - Waiting - %s' % (time.time(), t_end), file=sys.stderr)
        while time.time() < t_end:
            # print('ooooooo', file=sys.stderr)
            pass
        
        return False    

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(INPUT_WIRE, GPIO.IN)


    while time.time() < t_end:
        value = 1
        # Loop until we read a 0
        while value:
            value = GPIO.input(INPUT_WIRE)

        # Grab the start time of the command
        startTime = datetime.now()

        # Used to buffer the command pulses
        command = []

        # The end of the "command" happens when we read more than
        # a certain number of 1s (1 is off for my IR receiver)
        numOnes = 0

        # Used to keep track of transitions from 1 to 0
        previousVal = 0

        while True:

            if value != previousVal:
                # The value has changed, so calculate the length of this run
                now = datetime.now()
                pulseLength = now - startTime
                startTime = now

                command.append((previousVal, pulseLength.microseconds))

            if value:
                numOnes = numOnes + 1
            else:
                numOnes = 0

            # 10000 is arbitrary, adjust as necessary
            if numOnes > 10000:
                break

            previousVal = value
            value = GPIO.input(INPUT_WIRE)
        
            result = []

            for (val, pulse) in command:
                result.append(str(pulse))

            text = '-'.join(result)

            with open("ir_tmp_code.txt", "w") as text_file:
                text_file.write(text)

            return True

    return False
