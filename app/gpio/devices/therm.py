class Therm:
	PIN = 18 #GPIO 18 not pin number
	COMMANDS = ('status')

	def __init__(self, DHT):
		print('DEVICE THERM: init')
		self.DHT = DHT
		self.SENSOR = DHT.DHT11
		# self.GPIO.setup(self.PIN, self.GPIO.OUT)

	def status(self):
		print('DEVICE THERM: OK')

	def run(self, command):
		print("DEVICE THERM: Command ok")
		if command not in self.COMMANDS:
			return False
		
		hum, temp = self.DHT.read_retry(self.SENSOR, self.PIN)
		if hum is not None and temp is not None:
			print("THERM: return ok")
			return {'hum': hum, 'temp': temp}

		return False

	def __del__(self):
		print('DEVICE THERM: Destroy')
		# GPIO.setup(self.PIN, GPIO.OUT)