#!/usr/bin/env python
import time
import pygame
import CHIP_IO.GPIO as GPIO
import CHIP_IO.SOFTPWM as SPWM

# Set which GPIO pins the drive outputs are connected to
drive_0 = "GPIO6"
drive_1 = "GPIO4"
drive_2 = "GPIO2"
drive_3 = "XIO-P1"
PWM_0 = "LCD-VSYNC"
PWM_1 = "LCD-HSYNC"

# Set all of the drive pins as output pins
GPIO.setup(drive_0, GPIO.OUT)
GPIO.setup(drive_1, GPIO.OUT)
GPIO.setup(drive_2, GPIO.OUT)
GPIO.setup(drive_3, GPIO.OUT)

# SoftPWM setup
SPWM.start(PWM_0, 50)
SPWM.start(PWM_1, 50)

# Settings
leftdrive = drive_0                     # drive number for left motor
rightdrive = drive_3                    # drive number for right motor
leftback = drive_1                      # drive number for left motor, backwards
rightback = drive_2                     # drive number for right motor, backwards
axisleftmotor = 1                       # Joystick axis to read for up / down position
axisleftmotorinverted = True            # Set this to True if up and down appear to be swapped
axisrightmotor = 3                      # Joystick axis to read for left / right position
axisrightmotorinverted = True           # Set this to True if left and right appear to be swapped
interval = 0.05                         # Time between keyboard updates in seconds, smaller responds faster but uses more processor time

drive0 = rightdrive
drive1 = leftdrive
off0 = rightback
off1 = leftback
global leftmotor
global rightmotor
leftmotor = 0
rightmotor = 0

# Setup pygame
pygame.init()

# Wait for joystick to become available
joystick_count = pygame.joystick.get_count()
while joystick_count == 0:
    print "joystick disconnected, waiting.."
    pygame.joystick.quit()
    time.sleep(5)
    pygame.init()
    joystick_count = pygame.joystick.get_count()

# Initialize joystick
joystick = pygame.joystick.Joystick(0)
joystick.init()

# Set all drives to off
def motoroff():
    GPIO.output(drive_0, GPIO.LOW)
    GPIO.output(drive_1, GPIO.LOW)
    GPIO.output(drive_2, GPIO.LOW)
    GPIO.output(drive_3, GPIO.LOW)
    SPWM.set_duty_cycle(PWM_0, 0)
    SPWM.set_duty_cycle(PWM_1, 0)

# Function to handle pygame events
def pygamehandler(events):
    global leftmotor
    global rightmotor
    # Handle each event individually
    for event in events:
        if event.type == pygame.JOYAXISMOTION:
            # A joystick has been moved, read axis positions (-1 to +1)
            hadevent = True
            leftmotor = joystick.get_axis(axisleftmotor)
            rightmotor = joystick.get_axis(axisrightmotor)
            # Invert any axes which are incorrect
            if axisleftmotorinverted:
                leftmotor = -leftmotor
            if axisrightmotorinverted:
                rightmotor = -rightmotor
    return leftmotor, rightmotor

try:
    print 'Press ctrl+c to quit'
    # Loop indefinitely
    while True:
        leftmotor, rightmotor = pygamehandler(pygame.event.get())
        if rightmotor > 0:
            drive0 = rightdrive
            off0 = rightback
        if rightmotor < 0:
            drive0 = rightback
            off0 = rightdrive
        if leftmotor > 0:
            drive1 = leftdrive
            off1 = leftback
        if leftmotor < 0:
            drive1 = leftback
            off1 = leftdrive
        GPIO.output(drive0, GPIO.HIGH)
        GPIO.output(drive1, GPIO.HIGH)
        GPIO.output(off0, GPIO.LOW)
        GPIO.output(off1, GPIO.LOW)
        SPWM.set_duty_cycle(PWM_0, abs(leftmotor*100))
        SPWM.set_duty_cycle(PWM_1, abs(rightmotor*100))
        time.sleep(interval)
    motoroff()

except KeyboardInterrupt:
    # CTRL+C exit, disable all drives
    motoroff()
    SPWM.cleanup()
    GPIO.cleanup()
