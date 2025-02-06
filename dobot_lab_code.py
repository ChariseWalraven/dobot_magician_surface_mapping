# version: Python3
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
  "measurements": [],
  "coordinates": []
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
  byte_size = 500

  def measure():
    print('Measuring')
    while moving:
      data = {}
      data['arduino'] = arduino.readline().decode("utf-8")
      data['time'] = str(time.time())
      file_content["measurements"].append(data)
      time.sleep(0.5)

  def move(x,y,z,r, dest):
    print("Moving to:",  dest)
    magician.ptp(mode=mode, x=x, y=y, z=z, r=r)
    moving = False

  
  for key, coord in coordinates.items():
    t = threading.Thread(target=measure)
    moving = True
    t.start()
    file_content["coordinates"].append({ "pose": magician.get_pose(), "time":  str(time.time()) })
    move(*coord, key)
    moving = False
    t.join()

def read_json(data: bytes):
  # print("data: ", data)
  str_data = data.decode('utf-8').split('\r\n')[0]
  return json.loads(str_data) if str_data != '' else {'duration': -1, 'distance_mm': -1}


# main code
setup()
do_initial_sweep()

dt_str = datetime.now().strftime("%d_ %m_%Y_%H_%M_%S")
filename = f"{location}data{dt_str}.json"
with open(filename, "w+") as f:
  f.write(json.dumps(file_content))
