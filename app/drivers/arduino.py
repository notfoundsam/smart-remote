import serial
import time
import array

ser = serial.Serial('/dev/ttyUSB0', 500000)

# Only after write sketch into Arduino
time.sleep(2)
ser.flushInput()
ser.flushOutput()
ser.write(b'connect')
time.sleep(1)

def send_ir_signal(raw_signal, radio):
    prepared_signal = []
    prepared_signal.append('i1')

    for x in raw_signal.split(' '):
        c = int(x)
        if int(x) > 65000:
            prepared_signal.append('65000')
        else:
            prepared_signal.append(x)

    prepared_signal.append('\n')

    signal = ' '.join(prepared_signal)

    repeat2 = current_milli_time()
    data = ""
    b_arr = bytearray(signal)
    ser.write(b_arr)
    ser.flush()

    while current_milli_time() - repeat2 < 50:
        while ser.in_waiting > 0:
            data += ser.read()

    data = data.rstrip()

    if data == 'FAIL':
        fail += 1
    elif data == 'OK':
        total += 1
    elif data == 'TIMEOUT':
        arduino_timeout += 1
    else:
        no_response += 1

    print "Success: %d Fail: %d Arduino timeout: %d No responce: %d" % (total, fail, arduino_timeout, no_response)

