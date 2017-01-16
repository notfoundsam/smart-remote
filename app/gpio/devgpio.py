BOARD = "BOARD"
OUT = "OUT"
IN = "IN"
LOW = "LOW"
HIGH = "HIGH"

def setmode(m):
	print("Set mode to %s" % m)

def setup(p, s):
	print("Setup pin %s to %s" % (p, s))

def output(p, s):
	print("Set pin %s to %s" % (p, s))

def cleanup():
	print("Clean and destroy")
