import release
from c import MyGlobals
import time

alog = open("actdata.txt","a")

def main():
	while True:
		t = time.time()
		b_status = release.get_ballon_actuator()
		p_status = release.get_parachute_actuator()
		br_s = "08 %d %1.2f V"%(t, b_status)
		pr_s = "09 %d %1.2f V"%(t, p_status)
		print(br_s+"\r\n"+pr_s+"\r\n")
		alog.write(br_s+"\r\n"+pr_s+"\r\n")
		MyGlobals.ser.write(br_s+"\r\n"+pr_s+"\r\n")

		time.sleep(15)
		# send it as TLM