from gpiozero import MCP3008
import RPi.GPIO as GPIO
from firebase import firebase
import time

# GPIO pi configuration
GPIO.setmode(GPIO.BCM)                     
GPIO.setwarnings(False)

GPIO.setup(19, GPIO.IN)         
GPIO.setup(21, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)
GPIO.setup(11, GPIO.OUT)

fire = firebase.FirebaseApplication('https://project-on-adc.firebaseio.com', None)

sensorph  = MCP3008(0) 
sensorTemp = MCP3008(1)
sensorsoil = MCP3008(2)

while True:
    try:
        ValorSensorsoil = sensorsoil.value
        ValorSensorph  = sensorph.value*14 
        ValorSensorTemp = sensorTemp.value*330
        ValorSensorsoil = sensorsoil.value*500  
        ValorSensorph  = round(ValorSensorph) 
        ValorSensorTemp = round(ValorSensorTemp)
        ValorSensorsoil = round(ValorSensorsoil)
        
        if (ValorSensorsoil == 70):
            GPIO.output(11, True)
            time.sleep(2)
            GPIO.output(11, False)
            time.sleep(2)
        
       
        print ("************************************")
        print ("Sensor ph: ", ValorSensorph)
        print ("Sensor Temp:", ValorSensorTemp)
        print ("Sensor soil:", ValorSensorsoil)
        print ("************************************\n")
        
        fire.put('/PH/', 'PH', ValorSensorph)
        fire.put('/Temperature/', 'Temperature',  ValorSensorTemp)
        fire.put('/Soil/', 'soil', ValorSensorsoil)
        

        time.sleep(1)

    except KeyboardInterrupt:
        print ("\nend")
        break

