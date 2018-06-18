import serial
import time
import array


def encodeBits(data):
    counter = 0
    zero = None
    encode = ''
    
    for digit in data:
        if digit == '0':
            if zero == None:
                zero = True

            if counter > 0 and zero == False:
                encode += str(counter) + 'b'
                counter = 1
                zero = True
            else:
                counter += 1

        elif digit == '1':
            if zero == None:
                zero = False

            if counter > 0 and zero == True:
                encode += str(counter) + 'a'
                counter = 1
                zero = False
            else:
                counter += 1

    if counter > 0:
        if zero == True:
            encode += str(counter) + 'a'
        if zero == False:
            encode += str(counter) + 'b'


    print(encode)
    return encode


ir_signal = "8851 4435 565 1644 591 512 568 565 566 540 567 1642 568 565 567 1644 592 539 540 565 592 1623 592 1647 594 511 589 1650 562 1646 593 1643 594 513 595 511 590 516 565 569 592 510 595 1615 570 564 592 514 593 513 566 565 541 567 591 515 592 513 567 565 541 565 592 515 565 565 541 565 591 517 564 541 590 515 591 541 591 1619 568 564 538 568 566 539 591 513 592 543 561 545 589 516 593 512 565 567 565 539 566 1644 565 567 593 1618 593 1643 594 515 590 514 565 1675 589 514 593"
# ir_signal = "3430 1748 438 439 437 1314 435 433 436 435 438 430 438 433 437 432 436 433 437 434 438 432 435 435 436 433 437 433 439 1307 437 435 436 433 436 432 439 432 439 431 437 432 437 433 438 433 437 431 437 1316 432 431 435 434 439 430 438 435 477 393 435 434 437 433 435 434 438 1309 437 438 437 1314 439 1307 438 1307 439 1306 438 441 434 442 436 1314 436 432 437 1311 437 1307 438 1309 437 1312 437 435 436 1310 436 75114 3486 1749 438 435 432 1310 436 434 437 434 436 435 434 435 436 433 436 434 436 434 437 435 433 436 436 432 436 433 438 1309 437 434 435 433 437 434 435 434 438 433 437 433 435 434 437 433 436 435 434 1309 439 438 438 440 434 440 436 440 435 440 437 439 438 438 438 438 436 1316 437 431 437 1308 438 1310 436 1309 438 1313 436 435 436 434 435 1309 437 433 437 1308 438 1309 436 1314 438 1310 435 435 434 1311 435 75118 3488 1750 436 441 435 1316 435 435 435 436 434 434 436 435 434 434 435 437 433 435 437 433 435 435 435 436 435 433 437 1309 436 433 438 433 439 430 435 435 437 433 435 435 436 434 437 432 437 434 437 1308 435 436 435 432 438 435 434 436 436 433 435 433 437 434 436 435 435 1309 435 442 435 1314 438 1309 436 1309 437 1309 436 441 435 439 439 1314 436 432 436 1311 436 1309 437 1310 434 1316 436 433 438 1308 437"
# ir_signal = "8851 4435 565 1644 591 512 568 565 566 540 567 1642 568 565 567 1644 592 539 1623 592 1647 594 511 589 1650 562 562 562 1650 562 1650 562 1650 562 1650 562 1650 562 1650 562 1650 562 1650 562 1650 562 1650"
radio_pipe = 'AABBCCDD33'

success = 0
fail = 0
error = 0

ser = serial.Serial()
ser.baudrate = 500000
ser.port = '/dev/ttyUSB1'
ser.timeout = 10
ser.open()

# Only after writing sketch into Arduino
# print(repr(ser.readline()))
time.sleep(2)
ser.flushInput()
ser.flushOutput()

pre_test_data = []
test_data = []
pre_test_data.append('%si' % radio_pipe)

zero = []
one = []
compressed = ''

for value in ir_signal.split(' '):
    x = int(value)
    if x > 65000:
        test_data.append('65535')
        if compressed != '':
            test_data.append("[%s]" % encodeBits(compressed))
            compressed = ''
    else:
        if x < 1800:
            code = '0'
            if x < 1000:
                zero.append(x)
            elif 1000 <= x:
                one.append(x)
                code = '1'
            compressed += code
        else:
            if compressed != '':
                test_data.append("[%s]" % encodeBits(compressed))
                compressed = ''
            test_data.append(value)

if compressed != '':
    # encodeBits(compressed)
    test_data.append("[%s]" % encodeBits(compressed))



test_data.append('\n')


pre_test_data.append(str(sum(zero)/len(zero)))
pre_test_data.append(str(sum(one)/len(one)))
signal = ' '.join(pre_test_data + test_data)

print("-----signal------")
print(signal)

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
            print(b_arr)
            ser.write(b_arr)
            ser.flush()

            response_in = ser.readline()
            # print(repr(response_in))

            if response_in.rstrip() != 'next':
                break;
            response_in = ""
        
        if response_in == "":
            response_in = ser.readline()
        
        print("-----------")
        print(repr(response_in))
        
        response = response_in.rstrip()

        data = response.split(':')

        if 1 < len(data):
            if data[1] == 'FAIL':
                fail += 1
                print('fail')
                time.sleep(5)
            elif data[1] == 'OK':
                success += 1
        else:
            error += 1
            print(repr(response_in))

        print "Success: %d Fail: %d Error: %d" % (success, fail, error)
        if data[0]:
                print(data[0])

        time.sleep(2)

except KeyboardInterrupt:
    ser.flushInput()
    ser.flushOutput()
    ser.close()
    print("QUIT")

