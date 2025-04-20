# Importing Libraries
import serial
# import serial.tools.list_ports
import time
import json
# check ports automatically - not needed, we can set it manually to the correct port,
# but it is helpful to check which port is correct
# ports = list(serial.tools.list_ports.comports())

# arduino_ports = [
#     p.device
#     for p in serial.tools.list_ports.comports()
#     if 'IOUSBHostDevice' in p.description
# ]

arduino = serial.Serial(port='/dev/cu.usbmodem13301', baudrate=9600, timeout=0.1)

def read_json(data: bytes):
    str_data = data.decode('utf-8').split('\r\n')[0]
    return json.loads(str_data) if str_data != '' else {'duration': -1, 'distance_mm': -1}

while True:
    data = read_json(arduino.readline())
    print(data['distance_mm'])
    time.sleep(0.5)
