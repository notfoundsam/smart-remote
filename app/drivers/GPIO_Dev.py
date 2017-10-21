BOARD = "BOARD"
OUT = "OUT"
IN = "IN"
LOW = "LOW"
HIGH = "HIGH"

def setmode(m):
	print("GPIO: Set mode to %s" % m)

def setup(p, s):
	print("GPIO: Setup pin %s to %s" % (p, s))

def output(p, s):
	print("GPIO: Set pin %s to %s" % (p, s))

def cleanup():
	print("GPIO: Clean and destroy")
