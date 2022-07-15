# kmr262 menus.py
#
# create working interactive menus on the piTFT to be used within a larger
# code for total system operation. This is a test code for this aspect of the system
#
# Two menus: 
#   tea selection - green, black, herbal, quit
#   tea strength - light, normal, strong, quit
#
# Implement physical quit

import RPi.GPIO as GPIO
import time
import os
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
my_font = pygame.font.Font(None, 40)

## GPIO quit button ##
GPIO.setmode(GPIO.BCM)

GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def GPIO27_cb(channel):
    global button_run
    print('Physical quit pressed')
    button_run = False

GPIO.add_event_detect(27, GPIO.FALLING, callback=GPIO27_cb, bouncetime=300)

# Dictionaries ##
dispense = {'quit':(220,200),'Green Tea':(80,40), 'Black Tea':(80,110), 'Herbal Tea':(80, 180)}
brew = {'quit':(220, 200), 'Weak':(160,50), 'Normal':(160,100), 'Strong':(160,150)}

screen.fill(white)
button_run = True
timeout = 30
test = 1
starttime = time.time()

while button_run:
    time.sleep(0.2)
   # screen.fill(white)
    
    #time bail
    now = time.time()
    elaptime = now - starttime
    if elaptime > timeout:
        button_run = False

    # dispense menu rect buttons
    dispense_rect = {}
    for my_text, text_pos in dispense.items():
        text_surface = my_font.render(my_text, True, black)
        rect = text_surface.get_rect(center=text_pos)
        screen.blit(text_surface, rect)
        dispense_rect[my_text] = rect

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
                    if(my_text == str('Green Tea')):
                        print('Green Tea Selected')
                        #teavolver motor to position
                        test = 1
                    if(my_text == str('Black Tea')):
                        print('Black Tea Selected')
                        #teavolver motor to position
                        test = 1
                    if(my_text == str('Herbal Tea')):
                        print('Herbal Tea Selected')
                        #teavolver motor to position
                        test = 1

time.sleep(1)
GPIO.cleanup()
