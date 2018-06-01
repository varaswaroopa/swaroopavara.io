import hashlib

import RPi.GPIO as GPIO 
import serial
import os, sys
import time
from firebase import firebase

GPIO.setmode(GPIO.BOARD)                     
GPIO.setwarnings(False)
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

count=0
ppm=0

fire = firebase.FirebaseApplication('https://projectonadc-fcd56.firebaseio.com', None)
def my_callback(channel):
    
    global count
    count=count+1
    
GPIO.add_event_detect(11, GPIO.FALLING, callback=my_callback) 
def counter():
        stamp1=count
        time.sleep(60)
        stamp2=count
        print ('pulses per minute')
        global ppm
        ppm = (abs(stamp1 - stamp2))
        ppm=round(ppm/3)
        print (ppm)

while True:
    try:
        
            ser = serial.Serial('/dev/ttyUSB0', 9600)
            ValorSensorph = ser.readline()
            ValorSensorph2 = ValorSensorph[:3]
            ValorSensorph3 = (int(ValorSensorph2))*5   
            ValorSensorph1  = ppm

            if(ValorSensorph1 >= 75):
                ValorSensorph1 = 0


            value = str(ValorSensorph3).encode()
            value1 = str(ValorSensorph1).encode()
            code = hashlib.sha256(value).hexdigest()
            code1 = hashlib.sha256(value1).hexdigest()

            
            print ("************************************")
            print ("Sensor BP: ", ValorSensorph3)
            print ("Sensor Heartrate:", ValorSensorph1)
            #print ("hash:", code)
            #print ("hash value:", code1)
            print ("************************************\n")

            fire.put('/sensor/', 'BP', ValorSensorph3)
            fire.put('/sensor/', 'heartrate',  ValorSensorph1)
            fire.put('/sensor/', 'hash', code)
            fire.put('/sensor/', 'hash value', code1)

            counter()
  
    except KeyboardInterrupt:
        print ("\nSalida")
        break
        
