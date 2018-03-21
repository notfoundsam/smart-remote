import serial
import time
import array

ir_signal = "8851 4435 565 1644 591 512 568 565 566 540 567 1642 568 565 567 1644 592 539 540 565 592 1623 592 1647 594 511 589 1650 562 1646 593 1643 594 513 595 511 590 516 565 569 592 510 595 1615 570 564 592 514 593 513 566 565 541 567 591 515 592 513 567 565 541 565 592 515 565 565 541 565 591 517 564 541 590 515 591 541 591 1619 568 564 538 568 566 539 591 513 592 543 561 545 589 516 593 512 565 567 565 539 566 1644 565 567 593 1618 593 1643 594 515 590 514 565 1675 589 514 593"
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
print(repr(ser.readline()))

prepared_signal = []
prepared_signal.append('i%s' % radio)

for x in ir_signal.split(' '):
    c = int(x)
    if int(x) > 65000:
        prepared_signal.append('65000')
    else:
        prepared_signal.append(x)

prepared_signal.append('\n')

signal = ' '.join(prepared_signal)

n = 30
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

        time.sleep(3)

except KeyboardInterrupt:
    ser.flushInput()
    ser.flushOutput()
    ser.close()
    print("QUIT")
