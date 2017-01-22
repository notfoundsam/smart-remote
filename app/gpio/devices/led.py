class Led:
	PIN = 11
	COMMANDS = ('on', 'off')

	def __init__(self, GPIO):
		print('DEVICE LED: init')
		self.GPIO = GPIO
		self.GPIO.setup(self.PIN, self.GPIO.OUT)

	def status(self):
		print('DEVICE LED: OK')

	def run(self, command):
		print("DEVICE LED: Command ok")
		if command not in self.COMMANDS:
			return False
		
		if command == 'on':
			self.GPIO.output(self.PIN, self.GPIO.HIGH)
		if command == 'off':
			self.GPIO.output(self.PIN, self.GPIO.LOW)

		return True

	def __del__(self):
		print('DEVICE LED: Destroy')
		# GPIO.setup(self.PIN, GPIO.OUT)