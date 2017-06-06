# Self Driving RC Car
In order to graduate, every senior at my high school has to complete a project. I decided to modify a cheap RC car to be controlled by an onboard Raspberry Pi connected to several sonar sensors and a Pi camera. Below I will try to explain how I built both the hardware and the software for the car.
## Car Specifications
Below is a picture of the car that I used for this project. It is a 1:14 scale BMW X6 manufactured by Costzon, and it only cost around $30.

![](https://images-na.ssl-images-amazon.com/images/I/61YjU3OnPlL._SY450_.jpg)

The car is powered by 5 AA batteries, and the two DC motors controlling steering and throttle are on/off – in other words, there are no degrees of steering or speed. 
## Tools and Parts
- Raspberry Pi 3 Model B
- HC-SR04 Ultrasonic Sensor
- L298N Dual H-Bridge Motor Driver
- 330 Ohm and 470 Ohm resistors
- Picamera module
- Male-male, male-female, and female-female jumper wires
- Small screwdriver for assembly and disassembly
- Wire cutter and wire stripper
- Electrical tape
- Portable charger with 2.5A, 5V output
## Hardware
1. Detach the top casing of the car to reveal the main carriage and enclosed electronics
2. Remove the main circuitboard at the center of the car, but keep all attached wires
3. Using jumper wires and the wires already attached to the car, connect the L298N driver to the driving and steering motors and to the Raspberry Pi in accordance with these intructions: http://www.instructables.com/id/Raspberry-Pi-2-WiFi-RC-Car/. You can disregard the connections for the LEDs. To see which pins I used, examine the code in motor.py
4. If you want to use the RC car's battery module to power the car, simply take the power and ground wires and attach them in the appropriate locations on the L298N board.
5. Attach the Picamera module and install all necessary dependencies
6. Following the instructions found here: https://tutorials-raspberrypi.com/raspberry-pi-ultrasonic-sensor-hc-sr04/, attach the HC-SR04 sensor to the Raspberry Pi. If you have a breadboard small enough to fit in the car, you can follow the instructions as written; otherwise, you will have to use a combination of jumper wires and resistors to make the circuit.
7. To make everything a bit more solidified, saw off the screw wells on top of the battery box (where the original circuit board was attached) to create a flat platform, then tape the Raspberry Pi - preferably in a rectangular case - to said platform.
8. Attach the Picamera to a cardboard strip about 3-4 inches high and tape the cardboard strip to the back of the Raspberry Pi, facing forward. Check some preview images to make sure that the field of view extends from just above the front of the car to the horizon.
9. You are now done the hardware side of things! Time to move on to software.
## Software
