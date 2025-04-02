# Dobot Magician Surface Mapping
This project uses Python to read distance data sent from an Arduino Uno that's connected to a sensor on the arm of a Dobot Magician robot arm.

## To Do

- [x] Attach sensor to arm
- [x] Move arm in set pattern
- [x] Read data while moving arm
- [x] Write data to file for analysis
- [ ] Analyse data
  - [ ] Verify if ultrasonic sensor is capable of measuring distance correctly
    - [x] Reformat files (`transform_scanner_data.py`) 
    - [ ] Impute x, y and z values based on origin and destination values
    - [ ] Plot height at location and assess variation to see if the sensor detects the object given the current setup and parameters

