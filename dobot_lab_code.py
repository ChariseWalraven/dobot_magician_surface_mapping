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
    "bottom_right": (141, -126, z_sweep, -42),
    "top_left": (269, 155, z_sweep, 30),
    "bottom_left": (113, 142, z_sweep, 51),
    "top_right": (283, -111, z_sweep, -21),
    "top_middle": (274, 20, z_sweep, 4),
    "bottom_middle": (129, 6, z_sweep, 3), 
    "right_middle": (206, -129, z_sweep, -32),
    "left_middle": (197, 151, z_sweep, 37),
}


def print_pose():
    """Prints the current coordinates/pose of the Dobot Magician"""
    print(magician.get_pose())


def setup():
    """sets speed and acceleration to 50%"""
    magician.motion_params(50, 50)


def go_home():
    """Go to the home position"""
    magician.ptp(mode=0, x=200, y=0, z=z_sweep,  r=0)


def do_initial_sweep(arduino: serial.Serial) -> list:
    file_content = []
    # br - tl - bl - tr - tm - bm - rm - lm
    mode = 2
    origin = {
        'home': magician.get_pose()
    }

    # TODO: read all lines after moving one leg to get all data instead of going line per line
    def measure(dest: dict, origin: dict, arduino: serial.Serial):
        """Measure distance while moving"""
        print('Measuring')
        while moving:
            now = datetime.now()
            timestamp = now.strftime('%H:%M:%S:%f')
            
            dest_name = list(dest.keys())[0]
            origin_name = list(origin.keys())[0]
            coords = coordinates[dest_name]

            print(f'Moving to {dest_name} from {origin_name}')
            print('coords:', coords)
            
            dest_dict = { str(dest_name):  list(coords)}
            
            # parse data
            re_str = r"(\w*:\d{1,5})"
            
            data = arduino.readline().decode('utf-8').split('\r\n')[0]

            kv = re.findall(re_str, data)
            data_obj = {}
            for i, s in enumerate(kv):
                kvp = s.split(":")
                data_obj[str(kvp[0])] = kvp[1]

            measurement = {
                **data_obj,
                "timestamp": timestamp,
                "dest": dest,
                "origin": origin
            }
            
            file_content.append(measurement)
            # delay for 50ms
            time.sleep(0.05)
        print('Done measuring')

    def move(x, y, z, r, dest: dict):
        print("Moving to:",  dest)
        magician.ptp(mode=mode, x=x, y=y, z=z, r=r)

    for key, coord in coordinates.items():
        dest = {key: coord}
        # Start a thread so we can read sensor data and move at the same time
        t = threading.Thread(target=measure, args=(dest, origin, arduino))
        moving = True  # Needed for measure function (above), do not delete
        t.start()
        move(*coord, key)
        moving = False
        t.join()

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
        print('ports:',  [
           ( p.device, p.description)
            for p in serial.tools.list_ports.comports()
        ])

        arduino_ports = [
            p.device
            for p in serial.tools.list_ports.comports()
            if 'IOUSBHostDevice' in p.description or 'Serieel USB-apparaat' in p.description  # This is apparently different per OS/language. Can it be set?
        ]
        
        try_count += 1
        time.sleep(0.5)

    print('found port, connecting...')
    port = arduino_ports[0]
    arduino = serial.Serial(port=port, baudrate=9600, timeout=0.1)
    print('Connected.')
    return arduino


def write_data(dir_location: str, file_content, should_get_user_comment = False):
    dt_str = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
    filename = f"{dir_location}/data_{dt_str}.json"

    if should_get_user_comment:
        comment = input('Enter comment for top of file:')
        file_content['comment'] = comment

    with open(filename, "w+",  encoding="utf-8") as f:
        f.writelines(json.dumps(file_content, indent=2,  ensure_ascii=False))


def main():
    setup()
    go_home()
    arduino = connect_to_arduino()
    file_content = do_initial_sweep(arduino)
    go_home()
    write_data(location, file_content, should_get_user_comment=False)


if __name__ == '__main__':
    main()
