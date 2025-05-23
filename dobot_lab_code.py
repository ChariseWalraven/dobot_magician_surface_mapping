# version: Python3
from DobotEDU import *
import serial.tools.list_ports
import time
import json
import threading
import re

from datetime import datetime

# CONSTANTS
z_sweep = -20
location = "C:\\Users\\Gebruiker\\Desktop\\scanner_data"
coordinates = {
  "bottom_right": (143, -124, z_sweep, -41),
  "top_left": (268, 149, z_sweep, 29),
  "bottom_left": (134, 150, z_sweep, 49),
  "top_right": (273, -124, z_sweep, -24),
  "top_middle": (268, 0, z_sweep, 0),
  "bottom_middle": (126, 6, z_sweep, 3),
  "right_middle": (202, -130, z_sweep, -61),
  "left_middle": (197, 148, z_sweep, 37),
}
test_batch_sweep = True
should_get_user_comment = True


def print_pose():
  """Prints the current coordinates/pose of the Dobot Magician"""
  print(magician.get_pose())


def setup():
  """sets speed and acceleration to 50%"""
  magician.motion_params(50, 50)


def go_home():
  """Go to the home position"""
  magician.ptp(mode=0, x=195, y=3, z=z_sweep, r=1)


def move(x, y, z, r, dest_name: dict, mode=2):
  print("Moving to:", dest_name)
  magician.ptp(mode=mode, x=x, y=y, z=z, r=r)


def parse_data(data):
  # parse data
  re_str = r"(\w*:\d{1,5})"

  kv = re.findall(re_str, data)
  data_obj = {}
  for i, s in enumerate(kv):
    kvp = s.split(":")
    data_obj[str(kvp[0])] = kvp[1]

  return data_obj


def do_initial_sweep_batch(arduino: serial.Serial) -> list:
  file_content = {
    "comment": None,
    "measurements": [],
  }
  # br - tl - bl - tr - tm - bm - rm - lm
  origin = {
    'home': magician.get_pose()
  }

  def measure(dest: dict, origin: dict, arduino: serial.Serial):
    """Measure distance while moving"""
    print('Measuring')
    dest_name = list(dest.keys())[0]
    origin_name = list(origin.keys())[0]
    coords = coordinates[dest_name]

    print(f'Moving to {dest_name} from {origin_name}')
    print('coords:', coords)

    # dest_dict = { str(dest_name):  list(coords)}

    measurements = []

    print('reading lines')
    data = arduino.readlines()
    print('done reading lines')
    print('data:', data)

    print('looping through lines')
    for d in data:
      print('decoding lines')
      decoded_d = d.decode('utf-8').split('\r\n')[0]

      measurement = {
        **parse_data(decoded_d),
        "dest": dest,
        "origin": origin
      }

      measurements.append(measurement)
      print('measurement appended, done with this line of data')

    print('Done measuring')
    return measurements

  for leg_name, coord in coordinates.items():
    dest = {leg_name: coord}
    # Read all lines but don't save them, so we can start moving on an empty slate
    arduino.readlines()
    move(*coord, leg_name)
    # NOTE: I've had to remove timestamps because they work when you're reading the lines one by one, but are harder to
    # manage when reading in bulk. I don't use them anywhere, so it's not a big deal. If I find they're needed in future,
    # it would be a better idea to send timestamps with the measurements from the Arduino.
    measurements = measure(dest, origin, arduino)

    file_content['measurements'].append(measurements)

    origin = {}  # <- not sure why I did this, if the program runs the same without it, then it can be deleted.
    origin = dest
  return file_content


def connect_to_arduino() -> serial.Serial:
  arduino_ports = []
  try_count = 0

  print('Finding arduino port...')
  while len(arduino_ports) <= 0:
    if try_count >= 10:
      raise Exception("Try count exceeded while looking for arduino port")
    print('No ports found yet, try count:', try_count)

    ports = list(serial.tools.list_ports.comports())
    print('ports:', [
      (p.device, p.description)
      for p in serial.tools.list_ports.comports()
    ])

    arduino_ports = [
      p.device
      for p in serial.tools.list_ports.comports()
      # This is apparently different per OS & display language. Can it be set somehow from the arduino? Or can we look at some other information?
      # Like, how does the Arduino IDE know which USB port is connected to the Arduino UNO?
      if 'IOUSBHostDevice' in p.description or 'Serieel USB-apparaat' in p.description
    ]

    try_count += 1
    time.sleep(0.5)

  print('found port, connecting...')
  port = arduino_ports[0]
  arduino = serial.Serial(port=port, baudrate=9600, timeout=0.005)
  print('Connected.')
  return arduino


def write_data(dir_location: str, file_content, should_get_user_comment=False):
  dt_str = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
  filename = f"{dir_location}/data_{dt_str}.json"

  if should_get_user_comment:
    comment = input('Enter comment for top of file:')
    file_content['comment'] = comment

  with open(filename, "w+", encoding="utf-8") as f:
    f.writelines(json.dumps(file_content, indent=2, ensure_ascii=False))


def main():
  setup()
  go_home()
  arduino = connect_to_arduino()
  file_content = do_initial_sweep_batch(arduino)
  go_home()
  write_data(location, file_content, should_get_user_comment=should_get_user_comment)


if __name__ == '__main__':
  main()
