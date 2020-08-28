See Backup System Overview pdf for complete description 
# BackupSensor Project Overview
This repository contains the code and design schematics for a Parking Assist System to be implemented in any standard automobile. The general design consists of a series of distance sensors positioned strategically around the car that provides feedback to the driver of how near the edge of the car is to other objects around. This feedback, allows the driver to make smarter decisions while behind the wheel and provides meaningful assistance while maneuvering in tight spaces, such as parking lots, along with blindspot monitoring in traffic. 

# Design Choices
The final design consists of 10 VL53L0X distance sensors positioned 5 along the front bumper and 5 along the rear.  Each sensor provides a 25 degree Field of View and is accurate up to 2 meters (~6.6 feet).  With this in mind, for each corner of the automobile, 2 sensors are positioned at 65° and 20° with respect to the bisecting line between the driver and passenger side. Likewise, a single sensor is centered along the front and rear of the car in order to gauge the distance between its respective bumper and any object. 
The VL53L0X sensor’s communicate over the I2C procedure and due to the processing performed on the sensor itself, when requested the last read measurement may be shared with the central board thus relieving the processor from unnecessary polling across all 10 sensors. 
	
Responsible for the system’s feedback to the driver, a Raspberry Pi Zero handles reading in each sensor’s latest measurement along with updating the display. On startup, each sensor’s default I2C id is 0x29;  in order to properly setup each device and provide meaningful feedback, a method to modify the same address to each device on startup is necessary. The detailed control logic for this solution is laid out in the Circuit Design and Notes section. 

The general solution for staging each Sensor’s startup is by controlling the Vcc Power to each device. In order to limit the number of GPIO pins used to stage the Sensor start up, a simple series of control logic is used to expand 4 pins to map to each sensor. Transcribing the pins A,B,C,D as the binary representation of 0x0 to 0xA, each of the 10 sensors can be powered up, set up, and have a new I2C address written before the next sensor is enabled. An alternate solution to this would be to set up 10 GPIO pins on the Raspberry Pi Zero thus negating the need for the 4 - 16 Multiplexer setup.  See the Next Steps section for discussion on why this option may end up being implemented. For the sake of cable management, the Vcc control logic may be broken up into 2 sections, 1 section mounted to the front of the car and the other in the rear. This will allow for easier installation and repairs. 

# Circuit Design and Notes
In order to allow for each Sensor to be turned on in stages, a simple series of digital logic may be implemented to provide power to only the first sensor, then the first and next sensor, etc until all sensors have power. 

The sensors will be powered from the 5 Volts pin off the Raspberry Pi. In order to distribute this, the Vcc will be connected to an array of analog switches that are controlled by the Outputs of the digital logic above. A NPN Transistor can be used as a switch to accomplish this.

# Next Steps
Currently the first 5 sensor’s have been built out on a Protoboard and the Staged Sensor Startup will be tested. Once that is set up and the feedback behaves as expected, soldering up the last of the sensors and installation will finish up the project. Before being installed, the housing for the digital logic on both sides of the car and the mounts for the sensors will need to be drawn up and 3D printed. 
Also a final decision on whether to use the Python repository and Tkinter UI feedback or whether Chibi RTOS and a series of LED’s and speakers would be best. As of right now, Chibi RTOS provides the fastest startup time and because of that, the Tkinter UI might be dropped. 

# Bill of Materials 
Raspberry Pi Zero / Raspberry Pi 3b+

2N3904BU NPN Transistor

SN74HC08N AND Gate

SN74HC32N OR Gate

SEN0245 VL53L0X Distance Sensor

