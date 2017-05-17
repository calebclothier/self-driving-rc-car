from RPi import GPIO
from time import sleep

class Motor(object):

    def __init__(self, forwardPin, backwardPin, controlStraightPin, leftPin, rightPin):
        """Initialize all the pins that control the motors and enable pulse-width modulation
        for speed-control"""
        self.forwardPin = forwardPin
        self.backwardPin = backwardPin
        self.controlStraightPin = controlStraightPin
        self.leftPin = leftPin
        self.rightPin = rightPin
        # Setup pins as outputs
        GPIO.setup(self.forwardPin, GPIO.OUT)
        GPIO.setup(self.backwardPin, GPIO.OUT)
        GPIO.setup(self.controlStraightPin, GPIO.OUT)
        GPIO.setup(self.leftPin, GPIO.OUT)
        GPIO.setup(self.rightPin, GPIO.OUT)
        # Setup pulse-width modulation, initialize the duty cycle at 0 (out of 100)
        self.forward_pwm = GPIO.PWM(self.forwardPin, 100)
        self.backward_pwm = GPIO.PWM(self.backwardPin, 100)
        self.forward_pwm.start(0)
        self.backward_pwm.start(0)
        # Enable PWM
        GPIO.output(self.controlStraightPin, GPIO.HIGH)

    def forward(self):
        """Go forward at a predetermined speed"""
        GPIO.output(self.leftPin, GPIO.LOW)
        GPIO.output(self.rightPin, GPIO.LOW)
        self.backward_pwm.ChangeDutyCycle(0)
        self.forward_pwm.ChangeDutyCycle(40)

    def backward(self):
        """Go backward at a predetermined speed"""
        GPIO.output(self.leftPin, GPIO.LOW)
        GPIO.output(self.rightPin, GPIO.LOW)
        self.forward_pwm.ChangeDutyCycle(0)
        self.backward_pwm.ChangeDutyCycle(40)

    def forward_left(self):
        """Steer the car forward and left (there is no gradient of steering)"""
        self.backward_pwm.ChangeDutyCycle(0)
        self.forward_pwm.ChangeDutyCycle(40)
        GPIO.output(self.rightPin, GPIO.LOW)
        GPIO.output(self.leftPin, GPIO.HIGH)

    def forward_right(self):
        """Steer the car forward and right (there is no gradient of steering)"""
        self.backward_pwm.ChangeDutyCycle(0)
        self.forward_pwm.ChangeDutyCycle(40)
        GPIO.output(self.leftPin, GPIO.LOW)
        GPIO.output(self.rightPin, GPIO.HIGH)

    def stop(self):
        """No action taken by the vehicle"""
        self.forward_pwm.ChangeDutyCycle(0)
        self.backward_pwm.ChangeDutyCycle(0)
        GPIO.output(self.leftPin, GPIO.LOW)
        GPIO.output(self.rightPin, GPIO.LOW)
