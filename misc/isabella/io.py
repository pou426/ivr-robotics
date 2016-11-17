# Defines the input and output for use for all packages
import ev3dev.ev3 as ev3
btn = ev3.Button()
col = ev3.ColorSensor(ev3.INPUT_3) 
gyro = ev3.GyroSensor()
sonar = ev3.UltrasonicSensor(ev3.INPUT_4)
motmed = ev3.MediumMotor('outB')
motA = ev3.LargeMotor(ev3.OUTPUT_A) # left motor
motB = ev3.LargeMotor(ev3.OUTPUT_C) # right motor