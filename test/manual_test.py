# Importing Libraries
import json
import serial.tools.list_ports
import time
from datetime import datetime
import re

data_dir = './test_data/dummy'

z_sweep = -20

coordinates = [
    {"dest": "bottom_right", "coord": (141, -126, z_sweep, -42)},
    {"dest": "top_left", "coord": (269, 155, z_sweep, 30)},
    {"dest": "bottom_left", "coord": (113, 142, z_sweep, 51)},
    {"dest": "top_right", "coord": (283, -111, z_sweep, -21)},
    {"dest": "top_middle", "coord": (274, 20, z_sweep, 4)},
    {"dest": "bottom_middle", "coord": (129, 6, z_sweep, 3)},
    {"dest": "right_middle", "coord": (206, -129, z_sweep, -32)},
    {"dest": "left_middle", "coord": (197, 151, z_sweep, 37)},
]


if __name__ == '__main__':
    measurements = []
    dt_str = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
    filename = f"{data_dir}/data_{dt_str}.json"
    arduino_ports = []

    print('Finding arduino port...')
    while len(arduino_ports) <= 0:
        ports = list(serial.tools.list_ports.comports())

        arduino_ports = [
            p.device
            for p in serial.tools.list_ports.comports()
            if 'IOUSBHostDevice' in p.description
        ]

        time.sleep(0.5)

    print('found port, connecting...')
    port = arduino_ports[0]

    arduino = serial.Serial(port=port, baudrate=9600, timeout=0.1)

    print('Connected.')
    input('Press enter to start reading data')
    print('Reading data...')
    read_data = True
    leg = 0
    # NOTE: jointAngle is bogus, I don't use it. It's just there so the simulation is the same as the real thing
    origin = {'home': {"jointAngle": [71.28, 44.09, 46.12, 4.72], "r": 0.0, "x": 200.0, "y": 0.0, "z": -20.0}}
    # TODO: read all lines after moving one leg to get all data instead of going line per line
    while read_data:
        try:

            if leg > 0:
                prev_leg = leg - 1
                origin = { coordinates[prev_leg]["dest"]:  list(coordinates[prev_leg]["coord"])}

            dest_name = coordinates[leg]["dest"]
            coords = coordinates[leg]["coord"]
            dest = { str(dest_name):  list(coords)}
            print(f'Moving to {dest_name} from {list(origin.keys())[0]}')
            print('coords:', coords)
            data = arduino.readline().decode('utf-8').split('\r\n')[0]

            now = datetime.now()
            timestamp = now.strftime('%H:%M:%S:%f')

            # parse data
            re_str = r"(\w*:\d{1,5})"

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

            measurements.append(measurement)

            print(json.dumps(measurement, ensure_ascii=False))
            # TODO: sync delay time with arduino via serial comm? maybe that way the
            #       data I'm reading will be formatted better and make more sense?
            time.sleep(0.05) #50ms
        except KeyboardInterrupt:
            u_in = input('User interrupted, press return to start the next movement, or interrupt again to exit the program without completing the measurements')
            leg += 1
            if leg > (len(coordinates) - 1):
                break

    comment = input('Enter comment for top of file:')
    with open(filename, 'w+') as f:
        file_content = {
            "comment": comment,
            "measurements": measurements
        }

        f.writelines(json.dumps(file_content, indent=2, ensure_ascii=False))

    print('Wrote data log, program complete.')

