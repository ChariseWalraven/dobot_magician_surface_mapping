# version: Python3
from typing import Tuple
from DobotEDU import *
import serial
import serial.tools.list_ports
import time
import json
import numpy as np
import matplotlib as plt
import threading

from datetime import datetime
# check ports automatically - not needed, we can set it manually to the correct port,
# but it is helpful to check which port is correct
# ports = list(serial.tools.list_ports.comports())

#print([(p.device, p.description) for p in ports])\

z_sweep = -9
file_content = {
    "measurements": []
}

location = "C:\\Users\\Gebruiker\\Desktop\\scanner_data\\"

# set initial position
# scan in steps, saving coordinates and measured distance to a list
# plot list at end of scan
coordinates = {
    "bottom_right": (172, -13, z_sweep, 0),
    "top_left": (146, 292, z_sweep, 0),
    "bottom_left": (19, 192, z_sweep, 88),
    "top_right": (294, 80, z_sweep, 18.9),
    "top_middle": (225, 188, z_sweep, 71),
    "bottom_middle": (98, 88, -10, 46),
    "right_middle": (241, 26, z_sweep, 11),
    "left_middle": (82, 242, z_sweep, 76),
}


arduino = serial.Serial(port='COM4', baudrate=9600, timeout=0.1)


def print_pose():
    print( magician.get_pose())


def setup():
    #set speed and acceleration to 50%
    magician.motion_params(50, 50)


def go_home():
    magician.ptp(mode=0, x=200, y=0, z=100,  r=0)


def do_initial_sweep():
    # br - tl - bl - tr - tm - bm - rm - lm
    mode = 2
    origin = {
        'home': magician.get_pose()
    }

    def measure(key: str, coord: Tuple[int, int, int, int], origin):
        print('Measuring')
        while moving:
            data = {
                'distance_mm': arduino.readline().decode("utf-8"),
                'dest': {[key]: coord},
                'origin': origin,
                'time': str(time.time())
            }
            file_content["measurements"].append(data)
            time.sleep(0.5)
        print('Done measuring')

    def move(x,y,z,r, dest):
        print("Moving to:",  dest)
        magician.ptp(mode=mode, x=x, y=y, z=z, r=r)

    for key, coord in coordinates.items():
        t = threading.Thread(target=measure, args=(key, coord, origin))
        moving = True
        t.start()
        move(*coord, key)
        moving = False
        t.join()

        origin = { [key]: coord }


# main code
setup()
do_initial_sweep()

dt_str = datetime.now().strftime("%d_ %m_%Y_%H_%M_%S")
filename = f"{location}data_{dt_str}.json"
with open(filename, "w+") as f:
    f.write(json.dumps(file_content))
