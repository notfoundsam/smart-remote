import serial
import time
import array

command = "status"
# radio_pipe = 'AABBCCDD33'
radio_pipe = 'AABBCCDD44'

success = 0
fail = 0
error = 0

ser = serial.Serial()
ser.baudrate = 500000
ser.port = '/dev/ttyUSB0'
ser.timeout = 1
ser.open()

# Only after writing sketch into Arduino
# print(repr(ser.readline()))
time.sleep(2)
ser.flushInput()
ser.flushOutput()

signal = '%sc%s\n' % (radio_pipe, command)

print(signal)

n = 32
partial_signal = [signal[i:i+n] for i in range(0, len(signal), n)]

try:
    while True:
        ser.flushInput()
        ser.flushOutput()

        # if ser.in_waiting > 0:
            # print(ser.in_waiting)
            # print "-----------------"
        response_in = ser.readline()
        response = response_in.rstrip()

        if response == '':
            continue
        
        data = response.split(':')
        print(repr(response_in))
        
        if data[1] == 'FAIL':
            fail += 1
            time.sleep(0.5)
        elif data[1] == 'OK':
            success += 1
        else:
            error += 1
            print(repr(response_in))

        print "Success: %d Fail: %d Error: %d" % (success, fail, error)

        if data[0]:
            print(data[0])
        # else:
        #     pass
            # time.sleep(0.05)


except KeyboardInterrupt:
    ser.flushInput()
    ser.flushOutput()
    ser.close()
    print("QUIT")
