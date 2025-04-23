# version: Python3
from typing import Tuple
from DobotEDU import *
import serial.tools.list_ports
import time
import json
import threading

from datetime import datetime
# check ports automatically - not needed, we can set it manually to the correct port,
# but it is helpful to check which port is correct
# ports = list(serial.tools.list_ports.comports())

#print([(p.device, p.description) for p in ports])\

z_sweep = -20
file_content = []

location = "C:\\Users\\Gebruiker\\Desktop\\scanner_data"

# set initial position
# scan in steps, saving coordinates and measured distance to a list
# plot list at end of scan
coordinates = {
    "bottom_right": (141, -126, z_sweep, -42),
    "top_left": (269, 155, z_sweep, 30),
    "bottom_left": (113, 142, z_sweep, 51),
    "top_right": (283, -111, z_sweep, -21),
    "top_middle": (274, 20, z_sweep, 4),
    "bottom_middle": (129, 6, z_sweep, 3), 
    "right_middle": (206, -129, z_sweep, -32),
    "left_middle": (197, 151, z_sweep, 37),
}


arduino = serial.Serial(port='COM4', baudrate=9600, timeout=0.1)


def print_pose():
    """Prints the current coordinates/pose of the Dobot Magician"""
    print(magician.get_pose())


def setup():
    #set speed and acceleration to 50%
    magician.motion_params(50, 50)


def go_home():
    """Go to the home position"""
    magician.ptp(mode=0, x=200, y=0, z=100,  r=0)


def do_initial_sweep():
    # br - tl - bl - tr - tm - bm - rm - lm
    mode = 2
    origin = {
        'home': magician.get_pose()
    }

    def measure(dest, origin):
        """Measure distance while moving"""
        print('Measuring')
        while moving:
            data = {
                'distance_mm': arduino.readline().decode("utf-8"),
                'dest': dest,
                'origin': origin,
                'time': str(time.time())
            }
            file_content.append(data)
            time.sleep(0.5)
        print('Done measuring')

    def move(x,y,z,r, dest):
        print("Moving to:",  dest)
        magician.ptp(mode=mode, x=x, y=y, z=z, r=r)

    for key, coord in coordinates.items():
        dest = {}
        dest[key] = coord
        # Start a thread so we can read sensor data and move at the same time
        t = threading.Thread(target=measure, args=(dest, origin))
        moving = True  # Needed for measure function (above), do not delete
        t.start()
        move(*coord, key)
        moving = False
        t.join()

        origin = {}  # <- not sure why I did this, if the program runs the same without it, then it can be deleted.
        origin = dest


# main code
# TODO: maybe add __name__ == __main__ check? Would follow Python code conventions,
#       but not sure if helpful in current context specifically.
setup()

go_home() 
do_initial_sweep()
go_home()

dt_str = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
filename = f"{location}/data_{dt_str}.json"

# write data to scanner data folder (see location at top of file).
with open(filename, "w+") as f:
    f.write(json.dumps(file_content))
