import serial
import time
import array

def createIrSignal(radio_id, button_exec):
    nec_protocol = 0
    pre_data = []
    data = []
    pre_data.append('%si' % radio_id)

    zero = []
    one = []
    zero_bit = 0
    one_bit = 0
    compressed = ''

    for value in button_exec.split(' '):
        if nec_protocol < 2:
            data.append(value)
            nec_protocol += 1
            continue

        x = int(value)

        if x <= 1000:
            # 0
            zero.append(x)
            if one_bit > 0:
                compressed += "%db" % one_bit
                one_bit = 0
                zero_bit = 1
            else:
                zero_bit += 1

        elif x < 1800:
            # 1
            one.append(x)
            if zero_bit > 0:
                compressed += "%da" % zero_bit
                zero_bit = 0
                one_bit = 1
            else:
                one_bit += 1
        else:
            # as it
            if zero_bit > 0:
                compressed += "%da" % zero_bit
                zero_bit = 0
            if one_bit > 0:
                compressed += "%db" % one_bit
                one_bit = 0
            if compressed:
                data.append("[%s]" % compressed)
                compressed = ''
            # Arduino int is too small, so cut it
            if x > 65000:
                value = '65000'
            data.append(value)

    if zero_bit > 0:
        compressed += "%da" % zero_bit
    if one_bit > 0:
        compressed += "%db" % one_bit
    if compressed:
        data.append("[%s]" % compressed)

    # data.append('\n')

    pre_data.append(str(round(sum(zero)/len(zero))))
    pre_data.append(str(round(sum(one)/len(one))))

    execute = ' '.join(pre_data + data)
    return '%s\n' % execute

ir_signal = "8627 4464 584 539 586 1663 587 541 587 539 587 540 587 540 586 541 585 1664 587 1662 590 540 585 1666 585 1664 587 542 585 1663 586 1663 588 541 586 540 586 542 585 1665 587 1662 586 1665 586 1664 586 542 586 538 589 1664 586 1664 586 541 586 542 584 542 586 542 585 1662 587 1666 588"
# ir_signal = "8851 4435 565 1644 591 512 568 565 566 540 567 1642 568 565 567 1644 592 539 540 565 592 1623 592 1647 594 511 589 1650 562 1646 593 1643 594 513 595 511 590 516 565 569 592 510 595 1615 570 564 592 514 593 513 566 565 541 567 591 515 592 513 567 565 541 565 592 515 565 565 541 565 591 517 564 541 590 515 591 541 591 1619 568 564 538 568 566 539 591 513 592 543 561 545 589 516 593 512 565 567 565 539 566 1644 565 567 593 1618 593 1643 594 515 590 514 565 1675 589 514 593"
# ir_signal = "3430 1748 438 439 437 1314 435 433 436 435 438 430 438 433 437 432 436 433 437 434 438 432 435 435 436 433 437 433 439 1307 437 435 436 433 436 432 439 432 439 431 437 432 437 433 438 433 437 431 437 1316 432 431 435 434 439 430 438 435 477 393 435 434 437 433 435 434 438 1309 437 438 437 1314 439 1307 438 1307 439 1306 438 441 434 442 436 1314 436 432 437 1311 437 1307 438 1309 437 1312 437 435 436 1310 436 75114 3486 1749 438 435 432 1310 436 434 437 434 436 435 434 435 436 433 436 434 436 434 437 435 433 436 436 432 436 433 438 1309 437 434 435 433 437 434 435 434 438 433 437 433 435 434 437 433 436 435 434 1309 439 438 438 440 434 440 436 440 435 440 437 439 438 438 438 438 436 1316 437 431 437 1308 438 1310 436 1309 438 1313 436 435 436 434 435 1309 437 433 437 1308 438 1309 436 1314 438 1310 435 435 434 1311 435 75118 3488 1750 436 441 435 1316 435 435 435 436 434 434 436 435 434 434 435 437 433 435 437 433 435 435 435 436 435 433 437 1309 436 433 438 433 439 430 435 435 437 433 435 435 436 434 437 432 437 434 437 1308 435 436 435 432 438 435 434 436 436 433 435 433 437 434 436 435 435 1309 435 442 435 1314 438 1309 436 1309 437 1309 436 441 435 439 439 1314 436 432 436 1311 436 1309 437 1310 434 1316 436 433 438 1308 437"
# ir_signal = "8851 4435 565 1644 591 512 568 565 566 540 567 1642 568 565 567 1644 592 539 1623 592 1647 594 511 589 1650 562 562 562 1650 562 1650 562 1650 562 1650 562 1650 562 1650 562 1650 562 1650 562 1650 562 1650"
radio_id = '2'

success = 0
fail = 0
error = 0
serial_buff = 64

ser = serial.Serial()
ser.baudrate = 500000
ser.port = '/dev/ttyUSB0'
ser.timeout = 0.5
ser.open()

# Only after writing sketch into Arduino
# print(repr(ser.readline()))
time.sleep(2)
ser.flushInput()
ser.flushOutput()

signal = createIrSignal(radio_id, ir_signal)
print("-----signal------")
print(signal)

n = 64
partial_signal = [signal[i:i+n] for i in range(0, len(signal), n)]

now = time.time()

try:
    while True:
        if int(time.time() - now) > 0.5:
            now = time.time()
            # continue
            partial_signal = [signal[i:i+serial_buff] for i in range(0, len(signal), serial_buff)]

            for part in partial_signal:
                # print(part)
                b_arr = bytearray(part.encode())
                ser.write(b_arr)
                ser.flush()

                error = False

                while True:
                    response = ser.readline()
                    response = response.decode('ascii', 'replace')
                    # print(response)

                    if int(time.time() - now) > 0.5:
                        print('waiting timeout')
                        error = True
                        break
                    elif response.strip() == '':
                        print('empty response')
                    elif response.strip() == ':next:':
                        break
                    elif response.strip() == ':overflow:':
                        print('overflow')
                        error = True
                        break
                    elif response.strip() == ':timeout:':
                        print('timeout')
                        error = True
                        break
                    elif response.strip() == ':ack:':
                        print('ack')
                        continue
                        # response = ser.readline()
                        # response = response.decode('ascii', 'replace')
                        # print(response)

                    elif response.strip() == ':fail:':
                        error = True
                        break
                    elif response.strip() == ':success:':
                        print('transfer success')
                        break
                    else:
                        print('.')

                if error:
                    print('transfer error')
                    break

        else:
            incoming_size = ser.in_waiting
            if incoming_size > 0:
                response = ser.readline()
                response = response.decode('ascii', 'replace')
                # response = response.rstrip().decode('ascii', 'replace')
                # print(response)
                # last = response.strip()
                # print(last)
                # if last[-1].encode() == b"\x17":
                #     print('aaavvvv')
            else:
                time.sleep(0.05)

except KeyboardInterrupt:
    ser.flushInput()
    ser.flushOutput()
    ser.close()
    print("QUIT")

