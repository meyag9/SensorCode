import math
import socket
import sys, os
import struct
import time
import ad

templog = open("tempdata.txt","a")

# Return CPU temperature as a character string
def getCPU():
    p = os.popen('vcgencmd measure_temp').readline() # temperature values are stored inside of this file
    values = [float(p.replace("temp=","").replace("'C\n",""))]  # remove 'C' => float
    return values[0]


def get_thermistor():
    v = ad.ad_read(4)
    Rf = 91.5E3
    Vi = 3.3
    Rt = Rf*(Vi/v) - Rf
    # OMEGA 4008
    A = 9.376E-4
    B = 2.208E-04
    C = 1.276E-07
    Tc = (1/(A + B*math.log(Rt) + C*(math.pow(math.log(Rt), 3)))) - 273.15
    return Tc


def get_temps():
    t = time.time()
    cpu = getCPU()
    therm_t = get_thermistor()
    s = "03 %d %6.2f %6.2f C\r\n"%(t, therm_t, cpu)
    print(s) 
    templog.write(s) # log it 
    return

TEMP_STATUS_INTERVAL = 20

if __name__ == "__main__":
    last_status_interval = time.time()
    while True:
            t = time.time()
            cpu = getCPU()
            therm_t = get_thermistor()
            s = "03 %d %6.2f %6.2f C\r\n"%(t, therm_t, cpu)
            if t - last_status_interval > TEMP_STATUS_INTERVAL:
                    last_status_interval = time.time()
                    MyGlobals.ser.write(s)
            templog.write(s)
            print (s)
            #	s = "03 %d"%(t) + " " + "%05d"%therm_t + " " + "%5d"%cpu
            time.sleep(2)
