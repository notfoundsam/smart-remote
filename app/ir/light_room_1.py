import os

class light_room_1:

    commands = {
        'on': 'KEY_1',
        'off': 'KEY_2',
        'down': 'KEY_3',
        'up': 'KEY_4'
    }

    def run(self, cmd):
        if cmd not in self.commands:
            return False

        print("irsend SEND_ONCE light_room_1 %s" % self.commands[cmd])
        os.system("irsend SEND_ONCE light_room_1 %s" % self.commands[cmd])
            
        return True