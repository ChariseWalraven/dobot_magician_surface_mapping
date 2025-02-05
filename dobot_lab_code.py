# version: Python3
from DobotEDU import *
import serial
import serial.tools.list_ports
import time
import json
import numpy as np
import matplotlib as plt

# check ports automatically - not needed, we can set it manually to the correct port,
# but it is helpful to check which port is correct
# ports = list(serial.tools.list_ports.comports())

#print([(p.device, p.description) for p in ports])\
run_loop = False

r_const = 0
z_home = 100
z_sweep = 50

# set initial position
# scan in steps, saving coordinates and measured distance to a list
# plot list at end of scan
coordinates = {
  "bottom_right": (90, -140),
  "bottom_left": (112, -98),
  "bottom_middle": (130, -20),
  "top_right": (283, -164),
  "top_left": (316, 78),
  "top_middle": (312, -46),
  "right_middle": (179, -156),
  "left_middle": (221, 91),
}

arduino = serial.Serial(port='COM4', baudrate=9600, timeout=0.1)


def print_pose():
  print( magician.get_pose())
 

def go_home():
  magician.ptp(mode=0, x=200, y=0, z=z_home,  r=r_const)

def do_initial_sweep():
  # br - tl - bl - tr - tm - bm - rm - lm
  for c_name, c_vals in coordinates.items():
    print(c_name, c_vals)
    magician.ptp(mode=0, x=c_vals[0], y=c_vals[1], z=z_sweep, r=r_const)
    time.sleep(0.5)

def read_json(data: bytes):
  # print("data: ", data)
  str_data = data.decode('utf-8').split('\r\n')[0]
  return json.loads(str_data) if str_data != '' else {'duration': -1, 'distance_mm': -1}


# main code
go_home()
time.sleep(0.5)
#doinitial_sweep()

while run_loop:
  time.sleep(0.01)
  data = read_json(arduino.readline())
  print("mm: ", data['distance_mm'])
  time.sleep(0.5)
