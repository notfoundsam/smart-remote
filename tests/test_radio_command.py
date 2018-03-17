import serial
import time
import array

command = "status"
radio = '3'

success = 0
fail = 0
error = 0

ser = serial.Serial()
ser.baudrate = 500000
ser.port = '/dev/ttyUSB0'
ser.timeout = 100
ser.open()

# Only after writing sketch into Arduino
time.sleep(2)
ser.flushInput()
ser.flushOutput()
ser.write(b'connect')
time.sleep(1)
print(repr(ser.readline()))
ser.flushInput()

signal = 'c%s %s\n' % (radio, command)

try:
    while True:
        print "-----------------"
        b_arr = bytearray(signal)
        ser.write(b_arr)
        ser.flush()
        
        response_in = ser.readline()

        response = response_in.rstrip()

        data = response.split(':')

        if data[1] == 'FAIL':
            fail += 1
        elif data[1] == 'OK':
            success += 1
        else:
            error += 1
            print(repr(response_in))

        print "Success: %d Fail: %d Error: %d" % (success, fail, error)
        if data[0]:
                print(data[0])

        time.sleep(0.2)

except KeyboardInterrupt:
    ser.flushInput()
    ser.flushOutput()
    ser.close()
    print("QUIT")
