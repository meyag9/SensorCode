#
# Code for linear actuator, must always be set to NOT RELEASE unless commanded otherwise
# o = RELEASE
#

import RPi.GPIO as GPIO
import smbus
import time
import ad

ACTUATOR_VOLTAGE_CONVERSION = 2.0

def b_release(): #command triggers manual balloon release
	PIN = 24
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(PIN, GPIO.OUT)

	GPIO.output(PIN, True) # True means that balloon will be released
	# have parachute be released just a few seconds after this
	time.sleep(5)
	return get_ballon_actuator()


def p_release(): # command triggers manual
	PIN = 23
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(PIN, GPIO.OUT)

	GPIO.output(PIN, True) #parachute will be released
	time.sleep(5)
	return get_parachute_actuator()


def get_ballon_actuator():
	v = ad.ad_read(5)
	return v*ACTUATOR_VOLTAGE_CONVERSION


def get_parachute_actuator():
	v = ad.ad_read(6)
	return v*ACTUATOR_VOLTAGE_CONVERSION

# def send_actuator_status():
# 	t = time.time()
# 	b_status = get_ballon_actuator()
# 	p_status = get_parachute_actuator()
# 	br_s = "08 %d %1.2f V"%(t, b_status)
# 	pr_s = "08 %d %1.2f V"%(t, p_status)
# 	return (br_s, pr_s)

	# send it as TLM



# if __name__ == "__main__":
# 	b_release()
# 	status = get_ballon_actuator()
# 	print(status)

# 	p_release()
# 	status = get_parachute_actuator()
# 	print(status)
