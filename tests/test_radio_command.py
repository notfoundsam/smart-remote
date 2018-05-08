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
ser.timeout = 10
ser.open()

# Only after writing sketch into Arduino
# print(repr(ser.readline()))
time.sleep(2)
ser.flushInput()
ser.flushOutput()

signal = 'c%s %s\n' % (radio, command)

n = 32
partial_signal = [signal[i:i+n] for i in range(0, len(signal), n)]

try:
    while True:
        ser.flushInput()
        ser.flushOutput()
        print "-----------------"

        response_in = ""

        for part in partial_signal:
            b_arr = bytearray(part)
            ser.write(b_arr)
            ser.flush()

            response_in = ser.readline()

            if response_in.rstrip() != 'next':
                break;

            response_in = ""
        
        if response_in == "":
            response_in = ser.readline()
        
        response = response_in.rstrip()

        data = response.split(':')
        print(repr(response_in))
        if data[1] == 'FAIL':
            fail += 1
            time.sleep(5)
        elif data[1] == 'OK':
            success += 1
        else:
            error += 1
            print(repr(response_in))

        print "Success: %d Fail: %d Error: %d" % (success, fail, error)

        if data[0]:
            print(data[0])
            # sensors_data = dict(s.split(' ') for s in data[0].split(','))
            # if 'bat' in sensors_data:
            #     bat = float(sensors_data['bat'])
            #     print(bat)

        time.sleep(0.5)

except KeyboardInterrupt:
    ser.flushInput()
    ser.flushOutput()
    ser.close()
    print("QUIT")
