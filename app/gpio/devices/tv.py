class Tv:

	COMMANDS = ('power', 'hdmi', 'vup', 'mute', 'vdown')

	def __init__(self, GPIO):
		print('Set TV device')

	def run(self, command):
		if command not in self.COMMANDS:
			return False
			
		return True

	def status(self):
		print('TV OK')