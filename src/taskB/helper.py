# --------------------------------------------------------------
# Define useful functions for taskB
# --------------------------------------------------------------

# imports
import time
import logging

from collections import deque
import ev3dev.ev3 as ev3
import util.robotio as io
from util.control import Controller
from util.observer import Listener, Subject

# global vars
L = io.motA
R = io.motB
gyro = io.gyro
col = io.col


# ====================================================================
def follow_line(v, direction, midpoint, stop_col, history, g=None, c=None):
    """
    :param v - the constant duty_cycle_sp
    :param direction - whether we should hug the inner line by going cw (1) or ccw (-1)
    :param midpoint - The desired col value that the control is set to
    :param stop_col - The col value that will stop this function
    :param history - Number of past color samples to consider
    :param g - a subject that tracks the value of the gyro
    :param c - a subject that tracks the value of the col
    """
    global col, L, R, gyro

    # ev3.Sound.speak('Following line').wait()
    # Control:
    control = Controller(.9 , 0, .4, midpoint, 3)

    while True:

        if col.value() >= stop_col or io.btn.backspace:  # circuit breaker  ``
            L.stop()
            R.stop()
            L.duty_cycle_sp = v
            R.duty_cycle_sp = v
            ev3.Sound.speak('I have reach the end of line').wait()
            return g, c
        else:
            signal, err = control.control_signal(col.value()) # update controller
            if abs(v+signal) >= 100: signal = 0
            # A positive error implies need to hug the line more
            if direction == 1: # inner of left line = going CW
                L.run_direct(duty_cycle_sp = v - signal)
                R.run_direct(duty_cycle_sp = v + signal)
            elif direction == -1: # follow the inner of right line = going CCW
                L.run_direct(duty_cycle_sp = v + signal)
                R.run_direct(duty_cycle_sp = v - signal)

            logging.info('COL = {},\tcontrol = {},\t err={}, \tL = {}, \tR = {}'.format(
                col.value(), signal, err, L.duty_cycle_sp, R.duty_cycle_sp))
            g.set_val(gyro.value())
            c.set_val(col.value())

# ====================================================================

def forward_until_line(v, line_col, desired_heading, direction, g=None, c=None):
    """
    Robot will move forward and then stop once the line_col is detected
    it uses the desired heading to ensure that the robot is moving straight

    :param v - the duty_cycle_sp at which the motor should travel at
    :param line_col - the line_col that should cause the robot to halt
    (usually the MIDPOINT)
    :param desired_heading - the gyro value that the robot should walk in
    (hence moving in a straight)
    """

    global col, L, R, gyro

    ev3.Sound.speak(
        'Moving forward until line is found').wait()

    col_subject = Subject('col_sub')
    gyro_control = Controller(.8, 0, 0.05,
                              desired_heading,
                              history=10)
    halt_ = Listener('halt_',col_subject ,
                     line_col, 'LT')
    previous_col = col.value()

    while True:
        col_subject.set_val(col.value())
        if halt_.get_state() or io.btn.backspace:
            # need to halt since distance have reached
            L.stop(); R.stop()
            # ev3.Sound.speak('Line detcted. hurray!').wait()
            logging.info('STOP! Line detected')
            L.duty_cycle_sp = v
            R.duty_cycle_sp = v
            return g, c

        else:  # when out of range value is not reached yet- keep tracing the object and adjusting to maintain desired_range
            signal, err = gyro_control.control_signal(gyro.value())

            if abs(v+signal) >= 100: signal = 0

            if err > 0: # less than expected
                L.run_direct(duty_cycle_sp=v + signal)
                R.run_direct(duty_cycle_sp=v - signal)
            elif err < 0: # more than expected
                L.run_direct(duty_cycle_sp=v - signal)
                R.run_direct(duty_cycle_sp=v + signal)
            else:
                L.run_direct(duty_cycle_sp=v)
                R.run_direct(duty_cycle_sp=v)

            logging.info('GYRO = {},COL = {},\tcontrol = {},\t err={}, \tL = {}, \tR = {}'.format(
                gyro.value(), col.value(), signal, err, L.duty_cycle_sp, R.duty_cycle_sp))
            g.set_val(gyro.value())
            c.set_val(col.value())


 # ====================================================================


def calibrate_gyro():
    global gyro
    ev3.Sound.speak('Calibrating Gyroscope')
    logging.info('Calibrating Gyroscope')
    gyro.mode = 'GYRO-CAL'
    time.sleep(7)
    robot_forward_heading = gyro.value()
    robot_right = robot_forward_heading + 90
    robot_left = robot_forward_heading - 90
    ev3.Sound.speak('Done').wait()
    logging.info('Done')
    logging.info('reference heading = {}'.format(robot_forward_heading))
    logging.info('robot_left = {}'.format(robot_left))
    logging.info('robot_right = {}'.format(robot_right))
    gyro.mode = 'GYRO-ANG'
    return (robot_forward_heading, robot_left, robot_right)
