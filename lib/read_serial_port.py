# Importing Libraries
import json
import serial.tools.list_ports
import time
from datetime import datetime
import re

read_data = True
data_dir = '/Users/charise/code/robot-arm/dobot_magician_surface_mapper/test_data'

if __name__ == '__main__':
    log_lines = []
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
        # print('Arduino ports:', arduino_ports)


        time.sleep(0.5)

    print('found port, connecting...')
    port = arduino_ports[0]

    arduino = serial.Serial(port=port, baudrate=9600, timeout=0.1)

    print('Connected.')
    input('Press enter to start reading data')
    try:
        print('Reading data...')
        while read_data:
            data = arduino.readline().decode('utf-8').split('\r\n')[0]

            now = datetime.now()
            timestamp = now.strftime('%H:%M:%S:%f')

            # parse data
            re_str = r"(\w*:\d{1,5})"

            kv = re.findall(re_str, data)
            data_obj = {}
            for i, s in enumerate(kv):
                kvp = s.split(":")
                data_obj[str(kvp[0])] = int(kvp[1])


            print(data, data_obj)

            log = {
                **data_obj,
                "timestamp": timestamp,
            }

            log_lines.append(log)

            print(json.dumps(log, ensure_ascii=False))
            # TODO: sync delay time with arduino via serial comm? maybe that way the
            #       data I'm reading will be formatted better and make more sense?
            time.sleep(0.05) #50ms
    except KeyboardInterrupt:
        print('User interrupted, stopped reading serial port and will write data log...')

    comment = input('Enter comment for top of file:')
    with open(filename, 'w+') as f:
        file_content = {
            "comment": comment,
            "log": log_lines
        }

        f.writelines(json.dumps(file_content, indent=2, ensure_ascii=False))

    print('Wrote data log, program complete.')

