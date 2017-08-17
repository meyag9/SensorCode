from __future__ import print_function
from c import MyGlobals
import threading
import time
import Queue
import smbus
import sys
import time
import RPi.GPIO as GPIO


a = open("acceldata.txt","a")

class ACCELEROMETER(object):
	def __init__(self, GPIO_x, GPIO_y):
		self.GPIO_x = GPIO_x
		self.GPIO_y = GPIO_y
		self.x_th = 0
		self.x_tl = 0
		self.y_th = 0
		self.y_tl = 0
		self.setup(GPIO_x, GPIO_y)
		self.queue = Queue.Queue()
		self.thread = threading.Thread(target=self.enqueue_output, args=(self.queue,))
		self.thread.daemon = True
		self.thread.start()


	def setup(self, GPIO_x, GPIO_y):
		GPIO.setmode(GPIO.BCM)		# use RazPi's pin numbering (not the connector, nor the uProcessor)
		GPIO.setup(GPIO_x, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(GPIO_y, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.add_event_detect(GPIO_x, GPIO.BOTH, callback=self.gpio_x_callback)
		GPIO.add_event_detect(GPIO_y, GPIO.BOTH, callback=self.gpio_y_callback)


	def enqueue_output(self, queue):
		# run forever, looking for a line and putting it in the queue
		while True:
			if self.x_tl==0 or self.x_th==0 or self.y_tl==0 or self.y_th==0:
				continue
			TH_x = self.x_tl - self.x_th
			TH_y = self.y_tl - self.y_th
			if TH_x > 0 and TH_y > 0:
#				print("TH_x = %1.5f, TH_y = %1.5f"%(TH_x, TH_y))
				acc_x = ((TH_x/0.01) - 0.5)/0.125
				acc_y = ((TH_y/0.01) - 0.5)/0.125
				queue.put((acc_x, acc_y, time.time()))
			time.sleep(1)


	def gpio_x_callback(self, channel):
		if GPIO.input(self.GPIO_x) == 1:
			self.x_th = time.time()
		else:
			self.x_tl = time.time()


	def gpio_y_callback(self, channel):
		if GPIO.input(self.GPIO_y) == 1:
			self.y_th = time.time()
		else:
			self.y_tl = time.time()


	def get_acceleration(self,  timeout=0.01):
		try:
#			print("Q size=%d"%self.queue.qsize())
			data = self.queue.get(timeout=timeout)
		except Queue.Empty:
			return None
		else:
			return data

        def log(self, data):
                s = "01 {} {} {} ug\r\n".format(time.time(), data[0], data[1])
                a.write(s)
                print(s)

# def main():
# 	acc = ACCELEROMETER(12, 25) #17, 27
# 	while True:
# 		data = acc.get_acceleration()
# 		if data != None:
# 			(acc_x, acc_y, t) = data
# 			s = "%d, %d, acc_x = %1.2f, acc_y = %1.2f\r\n" %(t, time.time(), acc_x, acc_y)
# 			print(s)
# 			m.write(s)
# 			MyGlobals.ser.write(s)
# 		print(".")
# 		time.sleep(.5)

#
# if __name__ == "__main__":
# 	acc = ACCELEROMETER(12, 25)
# 	while True:
# 		data = acc.get_acceleration()
# 		if data != None:
#             s = "01 {} {} {} ug\r\n".format( time.time(), data[0], data[1])
# 			a.write(s)	#writing to the file "acceldata.txt"
# 			MyGlobals.ser.write(s)
# 			print(s)
# 		time.sleep(.5)
