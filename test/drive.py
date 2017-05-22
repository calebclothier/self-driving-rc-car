from motor import Motor
from RPi import GPIO
import time, sys, termios, tty
import socket

GPIO.setmode(GPIO.BOARD)

def get_keys():
	fd = sys.stdin.fileno()
	old_settings = termios.tcgetattr(fd)
	try:
		tty.setraw(sys.stdin.fileno())
		key = sys.stdin.read(1)
	finally:
		termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
	return key

forwardPin = 7
backwardPin = 11
leftPin = 13
rightPin = 15
controlStraightPin = 29

motor = Motor(forwardPin, backwardPin, controlStraightPin, leftPin, rightPin)

while True:
	key = get_keys()
	if (key == "w"):
		motor.forward()
	elif (key == "s"):
		motor.backward()
	elif (key == "a"):
		motor.forward_left()
	elif (key == "d"): 
		motor.forward_right()
	elif (key == "space"):
		motor.stop()
	elif (key == "x"):
		print("Program terminated")
		break
	else:
		motor.stop()
	key = ""

GPIO.cleanup()

