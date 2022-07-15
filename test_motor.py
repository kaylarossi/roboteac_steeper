# test programming for standard servo 
# test_motor.py


import RPi.GPIO as GPIO
import time
import sys
import subprocess
import pigpio

GPIO.setmode(GPIO.BCM)

# connect to pi gpio deamon
pi_hw = pigpio.pi() 

# pulse width from 0.75  ms to 2.25 ms - 0 to 180 deg
# inital pos 0deg - 0.75 ms/20 ms = 3.75%
# max pos 180deg - 2.25 ms/20 ms = 11.25%
# neutral pos 90 deg - 1.5 ms/20 ms = 7.5%
# DC between 3.75 and 11.25%

freq = 50
pacman = 12
teavolver = 13
# percentage multipled by 1M because hardware PWM makes 1M steps when fully on
dczero = int(.0375 * 1000000)
dcmax = int(.1125 * 1000000)
dcmid = int(.075 * 1000000)

def setAngleP(angleP):
    # dutycyle multiplied by 10000 because dc var is in units (%), need to 
    # convert back to decimal percentage and multiply by 1M for hardware PWM
    # multiply dc by 0.01 and then by 1000000 equates to one multi by 10000
    #
    # Start on 0 deg and rotate 180 for tea drop then return to 0 deg once
    # tea has been dispensed
    print('home')
    dc = int((((7.5*angleP)/180) + 3.75) * 10000)
    pi_hw.hardware_PWM(pacman, freq, dczero)
    print('tea drop')
    time.sleep(2)
    pi_hw.hardware_PWM(pacman, freq, dc)
    print('home')
    time.sleep(2)
    pi_hw.hardware_PWM(pacman, 0, 0)
    

def setAngleT(angleT):
    # Start on 0 degrees irrelavant of tea choice and depending on choice
    # rotate just 60 or rotate dc + dc 
    dc = int((((7.5*angleT)/180) + 3.75) * 10000)
    pi_hw.hardware_PWM(teavolver, freq, dczero)
    print('tea motor 0')
    time.sleep(2)
    pi_hw.hardware_PWM(teavolver, freq, dc)
    print('tea motor angle')
    time.sleep(2)
    pi_hw.hardware_PWM(teavolver, freq, dc+dc)
    print('tea motor 2 angle')
    time.sleep(2)
    pi_hw.hardware_PWM(teavolver, 0, 0)
    

setAngleT(30)
setAngleP(180)
