
from gpiozero import MCP3008
import RPi.GPIO as GPIO 
from firebase import firebase
import time
import os
import subprocess


import smtplib
import mimetypes
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.mime.image import MIMEImage
from email.Utils import COMMASPACE, formatdate
from email import Encoders

From = 'raspberrypimcp@gmail.com'
To = 'asmathna@gmail.com'

msg = MIMEMultipart()
msg['From'] = From
msg['To'] = To
msg['Date'] = formatdate(localtime=True)
msg['Subject'] = 'Sample subject'

msg.attach(MIMEText('Sample message'))

GPIO.setmode(GPIO.BOARD)                     
GPIO.setwarnings(False)
GPIO.setup(13, GPIO.IN)         
GPIO.setup(3, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)
current_state = 0
current_state = GPIO.input(13)

TRIG = 3                                  
ECHO = 7

GPIO.setup(TRIG,GPIO.OUT)                 
GPIO.setup(ECHO,GPIO.IN)                   
GPIO.setup(11,GPIO.OUT)


fire = firebase.FirebaseApplication('https://proyectorpi.firebaseio.com', None) 

sensorph  = MCP3008(0) 
sensorTemp = MCP3008(1)
sensorsoil = MCP3008(2)
def ultra():

  GPIO.output(TRIG, False)                 
  print "Waitng For Sensor To Settle"
  time.sleep(2)                            

  GPIO.output(TRIG, True)                 
  time.sleep(0.00001)                      
  GPIO.output(TRIG, False)                 

  while GPIO.input(ECHO)==0:               
    pulse_start = time.time()              

  while GPIO.input(ECHO)==1:               
    pulse_end = time.time()                 

  pulse_duration = pulse_end - pulse_start 

  distance = pulse_duration * 17150        
  distance = round(distance, 2)           

  if distance > 2 and distance < 20:      
    GPIO.output(11,True)
    time.sleep(2)
    GPIO.output(11,False)
    time.sleep(2)
    
    print "Distance:",distance - 0.5,"cm"  
  else:
    print "Out Of Range"


def pir():

    time.sleep(2)
    current_state = GPIO.input(13)
    if current_state == 0:                 
             print "No intruders",current_state
             GPIO.output(3, 0) 
             time.sleep(0.5)
    if current_state == 1:
              GPIO.output(3, 1) 
              time.sleep(0.5)
              print "Intruder detected",current_state
              subprocess.call("fswebcam -d /dev/video0 + /home/pi/project -r 1024x768 -S 3 + pic.jpg" ,shell=True)
              print("pic captured")
              time.sleep(0.5)
	      filePath = "pic.jpg"
              smtp = smtplib.SMTP('smtp.gmail.com:587')
              smtp.starttls()
              smtp.login('raspberrypimcp@gmail.com', 'pimcp3008')
              ctype, encoding = mimetypes.guess_type(filePath)

              if ctype is None or encoding is not None:
                    ctype = 'application/octet-stream'
              maintype, subtype = ctype.split('/', 1)
              if maintype == 'text':
                  fp = open(filePath)
                  part = MIMEText(fp.read(), _subtype=subtype)
                  fp.close()
              elif maintype == 'image':
                  fp = open(filePath, 'rb')
                  part = MIMEImage(fp.read(), _subtype=subtype)
                  fp.close()
              elif maintype == 'audio':
                  fp = open(filePath, 'rb')
                  part = MIMEAudio(fp.read(), _subtype=subtype)
                  fp.close()
              else:
                  fp = open(filePath, 'rb')
                  part = MIMEBase(maintype, subtype)
                  part.set_payload(fp.read())
                  fp.close()
                  Encoders.encode_base64(part)
              part.add_header('Content-Disposition', 'attachment; filename="%s"' % filePath)
              msg.attach(part)
              try:
                  smtp.sendmail(From, To, msg.as_string())
              except:
                  print "Mail not sent"
              else:
                  print "Mail sent"
              smtp.close()
    else:
        print "Connection failed"

while True:

    try:
        ValorSensorsoil = sensorsoil.value
        ValorSensorph  = sensorph.value*500 
        ValorSensorTemp = sensorTemp.value*330
	valorSensorsoil = sensorsoil.value*500  
        ValorSensorph  = round(ValorSensorph, 1) 
        ValorSensorTemp = round(ValorSensorTemp, 2)
	ValorSensorsoil = round(ValorSensorsoil, 2)

       
        print "************************************"
        print "Sensor ph: ", ValorSensorph
        print "Sensor Temp:", ValorSensorTemp
	print "Sensor soil:", ValorSensorsoil
        print "************************************\n"

       
        fire.put('/sensor/', 'temp', ValorSensorTemp)
        fire.put('/sensor/', 'ph',  ValorSensorph)
	fire.put('/sensor/', 'soil',ValorSensorsoil)
	
	if(ValorSensorsoil>0.7):
		GPIO.output(5,1)
	else:
		GPIO.output(5,0)
		

	ultra()

	pir()
  
        time.sleep(1)

    except KeyboardInterrupt:
      print "\nSalida"
      break
