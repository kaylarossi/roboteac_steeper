import RPi.GPIO as GPIO
import time
import os
import sys
import subprocess
import pigpio
import pygame
from pygame.locals import*

os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_FBDEV', '/dev/fb0')
os.putenv('SDL_MOUSEDRV', 'TSLIB')
os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

pygame.init()
#pygame.mouse.set_visible(False)
screen = pygame.display.set_mode((320,240))
white = [255, 255, 255]
black = [0, 0, 0]
red = [255, 0, 0]
green = [0, 255, 0]

#blue = [0, 32, 255]
#pink = [219, 48, 130]
grey = [50, 50, 50]
my_font = pygame.font.Font(None, 40)
big_font = pygame.font.Font(None, 100)

countquit = 1

##### GPIO set up  #####
GPIO.setmode(GPIO.BCM)
GPIO.setup(19, GPIO.OUT)
cm = GPIO.PWM(19, 50)   #set up continous motor
cm.start(0)             #give continuous motor 0 duty cycle
freqms = 20             #freq in milliseconds for 50 Hz
ccw = (1.3/20) * 100    #countclockwise viewed from back of motor
cw = (1.7/20) * 100     #clockwise viewed from back of motor

# connect to pi gpio deamon for hardware PWM for stnd servo
pi_hw = pigpio.pi()

# pulse width from 0.75  ms to 2.25 ms - 0 to 180 deg
# inital pos 0deg - 0.75 ms/20 ms = 3.75%
# max pos 180deg - 2.25 ms/20 ms = 11.25%
# neutral pos 90 deg - 1.5 ms/20 ms = 7.5%
# DC between 3.75 and 11.25% for standard servo

freq = 50
pacman = 12
teavolver = 13
# percentage multipled by 1M because hardware PWM makes 1M steps when fully on
dczero = int(.0375 * 1000000)
dcmax = int(.1125 * 1000000)
dcmid = int(.075 * 1000000)

# call back routine and function for physical quit button on piTFT
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def GPIO27_cb(channel):
    global button_run
    global countquit 
    print('Physical quit pressed')
    countquit = 0
    button_run = False

GPIO.add_event_detect(27, GPIO.FALLING, callback=GPIO27_cb, bouncetime=300)

##### Function definitions #####

def countdown(t):
    # actuate motor for tea pour into diffuser
    setMotorP()
    time.sleep(2) 
    PullTea(ccw,7)

    global countquit
    toggle = 0
    chcolor = 1
    
    while (t >= 0 and countquit):
        screen.fill(grey)
        mins, secs = divmod(t,60)  
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(timer, end="\r")

        textsurf = big_font.render(str(timer), True, white)
        recttime = textsurf.get_rect(center = (160,120))
        screen.blit(textsurf, recttime)

        time.sleep(3)
        if(toggle):
            print('stop')
        else:
            t -= 5
        for my_wtext, wtext_pos in wait.items():
            wtext_surface = my_font.render(my_wtext, True, white)
            wrect = wtext_surface.get_rect(center=wtext_pos)
            screen.blit(wtext_surface, wrect)
        pygame.display.flip()

        PullTea(cw,1)
        PullTea(ccw,1)

    PullTea(cw,4)

    print('quitting')    

def setMotorP():
    # dutycyle multiplied by 10000 because dc var is in units (%), need to
    # convert back to decimal percentage and multiply by 1M for hardware PWM
    # multiply dc by 0.01 and then by 1000000 equates to one multi by 10000
    #
    # Start on 0 deg and rotate 180 for tea drop then return to 0 deg once
    # tea has been dispensed
    angleP = 180
    print('home')
    dc = int((((7.5*angleP)/180) + 3.75) * 10000)
    pi_hw.hardware_PWM(pacman, freq, dczero)
    print('tea drop')
    time.sleep(2)
    pi_hw.hardware_PWM(pacman, freq, dc)
    print('home')
    time.sleep(2)
    pi_hw.hardware_PWM(pacman, 0, 0)

def setMotorT(angleT):
    # Start on 0 degrees irrelavant of tea choice and depending on choice
    # rotate just 60 or rotate dc + dc
    dc = int((((7.5*angleT)/180) + 3.75) * 10000)
    #pi_hw.hardware_PWM(teavolver, freq, dczero)
    #print('tea motor 0')
    #time.sleep(2)
    pi_hw.hardware_PWM(teavolver, freq, dc)
    print('tea motor angle')
    time.sleep(2)
    pi_hw.hardware_PWM(teavolver, 0, 0)

def PullTea(direction,secs):
    # Roll up chain of diffuser all the way until it comes out of slide
    # and lands in mug 
    # takes in a direction and duration of time in seconds 
    cm.ChangeDutyCycle(direction)
    time.sleep(secs)
    cm.ChangeDutyCycle(0)

def HomingP():
    # Insure tea dispensing motor is in home position
    # if motor isn't at angle 0, set to angle 0
    ##########!!!!!!! CHANGE WITH NEW HARDWARE TO BE DCZERO VAR!!!!!!!!!!!!
    if pi_hw.hardware_PWM(pacman, freq, 112500) == False:
        pi_hw.hardware_PWM(pacman, freq, 112500)

def HomingT():
    # Insure teavolver is in home position
    # if motor isn't at angle 0, set to angle 0
    if pi_hw.hardware_PWM(teavolver, freq, 0) == False:
        pi_hw.hardware_PWM(teavolver, freq, 0)

# Dictionaries ##
dispense = {'quit':(280,200), 'Green Tea':(80,40), 'Black Tea':(80, 120), 'Herbal Tea':(80,200)}
brew = {'quit':(280, 200), 'Weak':(80,40), 'Normal':(80, 120), 'Strong':(80, 200)}
wait = {'quit-->':(280, 200)}
teatype = {'Green Tea':(60), 'Normal':(1), 'Weak':(.75), 'Strong':(1.5), 'Black Tea':(180),'Herbal Tea':(180)}

screen.fill(grey)
button_run = True
timeout = 30
starttime = time.time()
m1 = 1
m2 = 0


while button_run:
    time.sleep(0.2)
    screen.fill(grey)
    
    #time bail
    now = time.time()
    elaptime = now - starttime
    if elaptime > timeout:
        button_run = False

#menu 1
    if (m1==1):
        HomingP()
        HomingT()
    # dispense menu rect buttons
        dispense_rect = {}
        for my_text, text_pos in dispense.items():
            text_surface = my_font.render(my_text, True, white)
            rect = text_surface.get_rect(center=text_pos)
            screen.blit(text_surface, rect)
            dispense_rect[my_text] = rect
            #drawrect()
        pygame.display.flip()

    #look for touch
        for event in pygame.event.get():
            if(event.type is MOUSEBUTTONDOWN):
                pos=pygame.mouse.get_pos()
            elif(event.type is MOUSEBUTTONUP):
                pos = pygame.mouse.get_pos()
                x,y = pos
                print(pos)
                for (my_text, rect) in dispense_rect.items():
                    if(rect.collidepoint(pos)):
                        if(my_text == str('quit')):
                            print('quit pressed')
                            button_run = False
                        else: 
                            print(my_text + ' selected')
                            teatime = teatype[(my_text)]
                            ##### rotate teavolver
                            if (my_text == 'Green Tea'):
                                time.sleep(1)
                                setMotorT(60)
                                print('in position')
                            elif (my_text == 'Black Tea'):
                                time.sleep(1)
                                setMotorT(120)
                                print('in position')
                            elif (my_text == 'Herbal Tea'):
                                time.sleep(1)
                                setMotorT(0)
                                print('in position')
                        m2 = 1 
                        m1 = 0

    
    if (m2==1):
        brew_rect = {}
        for my_btext, btext_pos in brew.items():
            btext_surface = my_font.render(my_btext, True, white)
            brect = btext_surface.get_rect(center=btext_pos)
            screen.blit(btext_surface, brect)
            brew_rect[my_btext] = brect
        pygame.display.flip()
        for event in pygame.event.get():
            if(event.type is MOUSEBUTTONDOWN):
                pos=pygame.mouse.get_pos()
            elif(event.type is MOUSEBUTTONUP):
                pos = pygame.mouse.get_pos()
                x,y = pos
                print(pos)
                for (my_btext, brect) in brew_rect.items():
                    if(brect.collidepoint(pos)):
                        if(my_btext == str('quit')):
                            print('quit pressed')
                            button_run = False

                        else:
                            print(my_btext + ' selected')
                            teatime = int(teatime * teatype[(my_btext)])
                            time.sleep(1)
                            countdown(teatime)
                            button_run = False

print('outta here')
        
pi_hw.stop()
cm.stop()
time.sleep(0.1)
GPIO.cleanup()
