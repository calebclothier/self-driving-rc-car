from motor import Motor
from RPi import GPIO
import time, sys, termios, tty
import socket

GPIO.setmode(GPIO.BOARD)

'''def get_keys():
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
'''

forwardPin = 7
backwardPin = 11
leftPin = 13
rightPin = 15
controlStraightPin = 29

motor = Motor(forwardPin, backwardPin, controlStraightPin, leftPin, rightPin)

server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 8000))
server_socket.listen(0)
connection = server_socket.accept()[0]

try:
	while True:
		key = struct.unpack("s", self.connection.recv(1024))
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
finally:
	connection.close()
	server_socket.close()

GPIO.cleanup()






