#
# Code for linear actuator, must always be set to NOT RELEASE unless commanded otherwise
# o = RELEASE
#

import RPi.GPIO as GPIO

PIN = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.OUT)


while True:

	print "enter 'o' to open the pin, enter 'c' to close the pin"
	input = raw_input(">>>")

	if input == "status":
		if (GPIO.output == 0):
			print "Pin is waiting to deploy\n"
		else:
			print "Pin is in deploy mode"
	elif input == "o":
		GPIO.output(PIN, True)
	elif input == "c":
		GPIO.output(PIN, False)
	else:
		print "invalid selections"
