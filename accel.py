# Reading data from the accelerometer and writing data to a text file.
# Last updated on 7/5/17. Update consisted of rounding floating point precision to two decimal places and creating a readable timestamp.


from __future__ import print_function
import threading
import time
import Queue
import smbus
import sys
import time
import RPi.GPIO as GPIO



a = open("acceldata.txt","w")

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


if __name__ == "__main__":
	print("main()")
	acc = ACCELEROMETER(17, 27)
	while True:
		data = acc.get_acceleration()
		if data != None:
			tstr = time.strftime('%Y-%m-%d %H:%M:%S')	#for timestamp
			(acc_x, acc_y, t) = data
			s = tstr + " " + str(data[2]) + "  X:" + str(round(data[0],2)) + "  Y:" + str(round(data[1],2)) + "\n"	#string to write into text file
			a.write(s)	#writing to the file "acceldata.txt"
			print("%d, acc_x = %1.2f, acc_y = %1.2f" %(t, acc_x, acc_y))
		time.sleep(.5)
