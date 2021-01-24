import serial
import RPi.GPIO as GPIO      
import os, time

def sendsms(msg):
    GPIO.setmode(GPIO.BCM)    
    # Enable Serial Communication
    port = serial.Serial("/dev/ttyAMA0", baudrate=115200, timeout=1)
    port.write('AT+CMGF=1'+'\r\n')  # Select Message format as Text mode 
    time.sleep(1)
    #port.write('AT+CMGS="+918527732908"'+'\r\n')
    port.write('AT+CMGS="+919871040400"'+'\r\n')
    time.sleep(1)
    port.write(msg +'\r\n')  # Message
    port.write("\x1A") # Enable to send SMS
