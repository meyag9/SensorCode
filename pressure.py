# Demonstrates using the I2C on RazPi with with a Ti ADS7830 A/D Converter
from __future__ import print_function
from c import MyGlobals
import smbus
import time

bus = smbus.SMBus(1)
address = 0x48 #i2C address
Vin = 3.3 #external reference for A/D
Vs = 5.22 #Voltage source
MAX_AD = 255  # max a/d count ( an 8-it A/D)
reg=7 # channel

plog = open("pressdata.txt","a")

def i2c_read():
	while True:
		try:
			if (reg != None):
				data = bus.read_byte_data(address, reg<<4 | (0x84) )
			else:
				data = bus.read_byte(address)
			return data
		except IOError, err:
			print('Error I2Cread: %d, %s accessing 0x%02X: Check I2C'%(err.errno, err.strerror, address))
	return None

def padding(value):
	value = round(value, 1)
	if value >= 100:
		str_val = str(value)
	if value < 100 and value >= 10:
   		str_val = "0" + str(value)
	elif value < 10:
   		str_val = "00" + str(value)
	elif value == 0:
		str_val = "000.0"
	while len(str_val) < 5:
		str_val = str_val + "0"
	return str_val


PRESSURE_STATUS_INTERVAL = 15

def main():
#if __name__ == "__main__":
	last_status_time = time.time()
	while True:
		t = time.time()
		r = i2c_read()
		t = time.time()
		Vout = r*Vin/MAX_AD #converted value of A/D (from counts to a voltage)
		v2 = Vout/.6998
		pressure = ((v2/Vs)+ 0.095)/0.009 #Pressure in kPa
		padded_pressure = padding(pressure)
		s = "10 %d %s kPa\r\n"%(t, padded_pressure)
		if t - last_status_time > PRESSURE_STATUS_INTERVAL:
			last_status_time = time.time()
			MyGlobals.ser.write(s)
		print (s)
		plog.write(s)
		# print('count=%d, Vout=%.2f, Pressure=%.2f\n'%(r,Vout,pressure))
		#MyGlobals.ser.write('count=%d, Vout=%.2f, Pressure=%.2f\n'%(r,Vout,pressure)) # radio write
		#plog.write('count=%d, Vout=%.2f, Pressure=%.2f\n'%(r,Vout,pressure)) # text write
		time.sleep(1)

#main()
