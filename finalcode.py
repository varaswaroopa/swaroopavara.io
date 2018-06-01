import numpy
import RPi.GPIO as GPIO 
import serial
import os, sys
import time
from firebase import firebase
import twilio
import twilio.rest
from twilio.rest import Client
import csv
import json

GPIO.setmode(GPIO.BOARD)                     
GPIO.setwarnings(False)
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


count=0
ppm=0
global sensorph
sensorph=0

 


fire = firebase.FirebaseApplication('https://projecthealth-b2291.firebaseio.com', None)
def my_callback(channel):
    
    global count
    count=count+1
    
GPIO.add_event_detect(11, GPIO.FALLING, callback=my_callback) # add rising edge detection on a channel
# if (GPIO.IN(11) == True):
    # count1=count1+1;
def counter():
        stamp1=count
        time.sleep(60)
        stamp2=count
        print ('pulses per minute')
        global ppm
        ppm = (abs(stamp1 - stamp2))
        ppm=round(ppm/3)
        
        print (ppm)
data = ['0']*1000
data1 = ['0']*1000 
File = open('example.csv','wb+')

while True:
    try:
        
            columnTitleRow="Bh"
            writer=csv.writer(File)
            
            ser = serial.Serial('/dev/ttyUSB0', 9600)
            ValorSensorph = ser.readline()
            ValorSensorph2 = ValorSensorph[:3]
            ValorSensorph3 = int(ValorSensorph2)   
            ValorSensorph1  = ppm

            if (ValorSensorph1 <= 50): 
                ValorSensorph1 = 0

            if (ValorSensorph1 >= 100):  
                ValorSensorph1 = 0
            
            print ("************************************")
            print ("Sensor BP: ", ValorSensorph3)
            print ("Sensor Heartrate:", ValorSensorph1)
	
            print ("************************************\n")

            fire.put('/sensor/', 'BP', ValorSensorph3)
            fire.put('/sensor/', 'heartrate',  ValorSensorph1)

            
            columnTitleRow = [ValorSensorph3, ValorSensorph1]
            writer=csv.writer(File)
            writer.writerow(columnTitleRow)
            writer.writerow('\n')
            
            
            File1=open('example.csv','r')
            reader=csv.DictReader(File1)

            data[i] = str(ValorSensorph3)
            
            data1[i] = str(ValorSensorph1)
            i = i+1
  
            
            f=open('BP.json','wb+')
            f1=open('heartrate.json','wb+')
            
            encoded = json.dumps(data)
            f.write(encoded)

            encoded1 = json.dumps(data1)
            f1.write(encoded1)

            sent = json.dumps(encoded)
            result = fire.post("Sensor1", sent)
            sent1 = json.dumps(encoded1)
            result = fire.post("Sensor2", sent1)
            
           
            

            if ( ValorSensorph3 <= 120 or ValorSensorph1 <= 60):
                account_ssid = "ACc6754590cf54cc1b57f41f48f9e5bc38"
                auth_token = "0b56240f9184dc4fb28f42f1acde3534"
                client = Client(account_ssid, auth_token)

                #message = client.messages.create(body = "patient1 in danger call to this number", to = "+91 9538728685", from_="+18188575663")
                #call = client.calls.create(to = "+91 9538728685", from_="+18188575663", url = "http://demo.twilio.com/docs/voice.xml")
	
            counter()
            


    except KeyboardInterrupt:
        print ("\nSalida")
        break
        
