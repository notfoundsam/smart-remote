from __future__ import print_function
import time
import os, sys
from ..models import Rc

class Common():

    def addTestSignal(self, test_signal):
        with open('ir_tmp_code.txt', 'a') as text_file:
            text_file.write("begin remote\n")
            text_file.write("\n")
            text_file.write("name test\n")
            text_file.write("flags RAW_CODES\n")
            text_file.write("eps 30\n")
            text_file.write("aeps 100\n")
            text_file.write("\n")
            text_file.write("ptrail 0\n")
            text_file.write("repeat 0 0\n")
            text_file.write("gap 108000\n")
            text_file.write("\n")
            text_file.write("begin raw_codes\n")

            text_file.write("  name test_signal\n")
            text_file.write("    %s\n" % test_signal)

            text_file.write("end raw_codes\n")
            text_file.write("\n")
            text_file.write("end remote\n")
    
    def regenerateLircCommands(self):

        ir_remotes = Rc.query.all()

        if ir_remotes is not None:
            print('---REGENERATE START---', file=sys.stderr)
            with open("ir_tmp_code.txt", "w") as text_file:

                for rc in ir_remotes:
                    buttons = rc.buttons.filter_by(type = 'ir').all()
                    print(buttons, file=sys.stderr)

                    if buttons:
                        text_file.write("begin remote\n")
                        text_file.write("\n")
                        text_file.write("name %s\n" % rc.identificator)
                        text_file.write("flags RAW_CODES\n")
                        text_file.write("eps 30\n")
                        text_file.write("aeps 100\n")
                        text_file.write("\n")
                        text_file.write("ptrail 0\n")
                        text_file.write("repeat 0 0\n")
                        text_file.write("gap 108000\n")
                        text_file.write("\n")
                        text_file.write("begin raw_codes\n")

                        for button in buttons:
                            text_file.write("  name %s\n" % button.identificator)
                            text_file.write("    %s\n" % button.signal)

                        text_file.write("end raw_codes\n")
                        text_file.write("\n")
                        text_file.write("end remote\n")
                        text_file.write("\n")

            print('---REGENERATE END---', file=sys.stderr)

class LircDev(Common):
    
    def reloadLirc(self):
        print('--- Lirc config reloaded ---', file=sys.stderr)

    def sendLircCommand(self, rc_id, btn_id):
        print('--- Sending command ---', file=sys.stderr)
        print(rc_id, file=sys.stderr)
        print(btn_id, file=sys.stderr)

    def sendTestSignal(self):
        print('--- Sending test signal ---', file=sys.stderr)
        print("irsend SEND_ONCE %s %s" % ('test', 'test_signal'), file=sys.stderr)

class Lirc(Common):

    def reloadLirc(self):
        os.system("sudo /etc/init.d/lircd stop")
        os.system("sudo cp ir_tmp_code.txt /etc/lirc/lircd.conf")
        os.system("sudo /etc/init.d/lircd start")

    def sendLircCommand(self, rc_id, btn_id):
        os.system("irsend SEND_ONCE %s %s" % (rc_id, btn_id))

    def sendTestSignal(self):
        os.system("irsend SEND_ONCE %s %s" % ('test', 'test_signal'))

