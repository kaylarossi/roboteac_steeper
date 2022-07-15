#test program for continuous motor

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(19, GPIO.OUT)
cm = GPIO.PWM(19,50)
cm.start(0)


freq = 20   # in milliseconds - 1/20ms = 50 Hz
ccw = (1.3/20) * 100    # direction viewed from behind motor
cw = (1.7/20) * 100


cm.ChangeDutyCycle(ccw)
time.sleep(5)
cm.ChangeDutyCycle(0)
time.sleep(2)
cm.ChangeDutyCycle(cw)
time.sleep(5)


cm.stop()
GPIO.cleanup()
