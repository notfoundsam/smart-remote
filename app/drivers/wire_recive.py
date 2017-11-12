from __future__ import print_function
import sys, os
import time

def read_signal():
    # Using for development
    if 'APP_ENV' in os.environ and os.environ['APP_ENV'] == 'development':
        counter = 0;
        while True:
            counter += 1
            print('Out received message decodes to: Hello - %d' % counter, file=sys.stderr)
            time.sleep(1)
    else:
        import RPi.GPIO as GPIO
        from lib_nrf24 import NRF24
        import spidev

    GPIO.setmode(GPIO.BCM)

    pipes = [[0xE8, 0xE8, 0xF0, 0xF0, 0xE1], [0xF0, 0xF0, 0xF0, 0xF0, 0xE1]]

    radio = NRF24(GPIO, spidev.SpiDev())
    radio.begin(0, 25)

    radio.setPayloadSize(32)
    radio.setChannel(0x76)
    radio.setDataRate(NRF24.BR_1MBPS)
    radio.setPALevel(NRF24.PA_MIN)

    radio.setAutoAck(True)
    radio.enableDynamicPayloads()
    radio.enableAckPayload()

    radio.openReadingPipe(1, pipes[1])
    radio.printDetails()
    radio.startListening()

    while(1):
        # ackPL = [1]
        while not radio.available(0):
            time.sleep(1 / 100)
        receivedMessage = []
        radio.read(receivedMessage, radio.getDynamicPayloadSize())
        print("Received: {}".format(receivedMessage))

        print("Translating the receivedMessage into unicode characters")
        string = ""
        for n in receivedMessage:
            # Decode into standard unicode set
            if (n >= 32 and n <= 126):
                string += chr(n)
        print("Out received message decodes to: {}".format(string))
