from __future__ import print_function
import asyncore
import math
import Queue
import smbus
import socket
import struct
import sys
import threading
import time


I2C_address = 0x0E
USE_OFFSET = True
# = False

XC = 0
YC = 0
ZC = 0

m = open("magdata.txt","w")

class MAG3110(object):
	def __init__(self, i2c_address):
		self.i2c_address = i2c_address
		self.bus = smbus.SMBus(1)
		self.setup()


	def setup(self):
		self.write_reg(0x10, 0x00)
		self.write_reg(0x11, 0x10)		# mag RESET
		while True:
			if (not self.read_reg(0x11) & 0x10):
				break
			else:
				time.sleep(0.05)
		self.write_reg(0x10, 0x59)		# 2.5Hz output, 128 over sample, 320 Hz ADC, Enable

		if USE_OFFSET:
			CTRL2 = 0x80			# AUTO Mag RESET + NO Raw mode (no output correction applied)
		else:
			CTRL2 = 0xA0			# AUTO Mag RESET + Raw mode (no output correction applied)

		self.write_reg(0x11, CTRL2)


	def start_readings(self):
		self.queue = Queue.Queue()
		self.thread = threading.Thread(target=self.enqueue_output, args=(self.queue,))
		self.thread.daemon = True
		self.thread.start()


	def enqueue_output(self, queue):
		# run forever, looking for data and putting it in the queue
		x = None; y = None; z = None
		while True:
			status = self.read_reg(0)
			if status&0x08:			# new X, Y, or Z data
				if (status & 0x01):		# new X data
					x = self.read_s16(1)
					x = self.convert(x, XC)
				if (status & 0x02):		# new Y data
					y = self.read_s16(3)
					y = self.convert(y, YC)
				if (status & 0x04):		# new Z data
					z = self.read_s16(5)
					z = self.convert(z, ZC)
				if (x != None and y != None and z != None):
					M = math.sqrt(x**2 + y**2 + z**2)
					queue.put((x, y, z, M))
					x = None
					y = None
					z = None
			else:
				time.sleep(0.5)


	def get_readings(self,  timeout=0.01):
		try:
			(x, y, z, M) = self.queue.get(timeout=timeout)
		except Queue.Empty:
			return None
		else:
			return (x, y, z, M)


	def i2c_read(self, reg=None):
		for tries in range(0, 3):
			try:
				if (reg != None):
					data = self.bus.read_byte_data(self.i2c_address, reg)
				else:
					data = self.bus.read_byte(self.i2c_address)
				return data
			except IOError, err:
				print('Error I2Cread: %d, %s accessing 0x%02X: Check I2C'%(err.errno, err.strerror, self.i2c_address))
		return None


	def i2c_write(self, reg, value=None):
		for tries in range(0, 3):
			try:
				if (value != None):
					self.bus.write_byte_data(self.i2c_address, reg, value)
				else:
					self.bus.write_byte(self.i2c_address, reg)
				return True
			except IOError, err:
				print('Error I2C_write: %d, %s accessing 0x%02X: Check I2C'%(err.errno, err.strerror, self.i2c_address))
		return False


	def read_reg(self, reg):
		return self.i2c_read(reg)


	def write_reg(self, reg, value):
		data = struct.pack("B", value)
		self.i2c_write(reg, ord(data))


	def read_s16(self, regb):
		data = ""
		for r in range(regb, regb+2):
			d = self.read_reg(r)
			data += chr(d)
		n = struct.unpack(">h", data)[0]
		return n


	def calibrate(self):
		mins = [32767, 32767, 32767]
		maxs = [-32768, -32768, -32768]

		print("Calibrating, move sensor in all axes")
		self.write_reg(0x10, 0x01)
		x = None; y = None; z = None
		t0 = time.time()
		while (time.time() - t0 < 5):
			status = self.read_reg(0)
			if status&0x08:			# new X, Y, or Z data
				if (status & 0x01):		# new X data
					x = self.read_s16(1)
				if (status & 0x02):		# new Y data
					y = self.read_s16(3)
				if (status & 0x04):		# new Z data
					z = self.read_s16(5)
				if (x != None and y != None and z != None):
					print("X=%d, Y=%d, Z=%d" %(x, y, z))
					if x < mins[0]:
						mins[0] = x
					if y < mins[1]:
						mins[1] = y
					if z < mins[2]:
						mins[2] = z
					if x > maxs[0]:
						maxs[0] = x
					if y > maxs[1]:
						maxs[1] = y
					if z > maxs[2]:
						maxs[2] = z
			else:
				time.sleep(0.05)
		print("X(%d, %d), Y(%d, %d), Z(%d, %d)"%(mins[0], maxs[0], mins[1], maxs[1], mins[2], maxs[2]))
		self.XC = (maxs[0] + mins[0])/2.0
		self.YC = (maxs[1] + mins[1])/2.0
		self.ZC = (maxs[2] + mins[2])/2.0
		print("Calibration constants:")
		print("X=%d, Y=%d, Z=%d" %(XC,YC, ZC))


	def convert(self, n, N):
		n -= N
		n = n*(1/20.0)
		return n


	def get_id(self):
		return self.read_reg(7)


	def get_offsets(self):
		for i in range(0, 6):
			self.write_reg(9+i, 0)
		x = self.read_s16(9)
		y = self.read_s16(11)
		z = self.read_s16(13)
		return (x, y, z)


	def show_mode(self):
		mode = self.read_reg(8)
		print("MODE = %02X"%mode, end="")
		if (mode == 0):
			print(" (standby)")
		elif (mode == 1):
			print(" (active, raw)")
		if (mode == 2):
			print(" (active, non-raw)")



def main():
	mag = MAG3110(0x0E)

	id = mag.get_id()
	print("ID = %02X"%id)

	(x, y, z) = mag.get_offsets()
	print("Offsets: x=%04X, y=%04X, z=%04X" %(x, y, z))

	# To calibrate, use this method.  Then, change the XC, YC, ZC constants at the top of this module
	if False:
		mag.calibrate()
		sys.exit()

	mag.start_readings()
	while True:
		data = mag.get_readings()
		if data != None:
			(x, y, z, M) = data
			print("M=%1.1f, X=%1.1f, Y=%1.1f, Z=%1.1f" %(M, x, y, z))
			m.write("M=%1.1f, X=%1.1f, Y=%1.1f, Z=%1.1f" %(M, x, y, z,))
			m.write("\n")
		time.sleep(0.1)
