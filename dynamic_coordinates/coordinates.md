# Description

Get coordinate differences. How are the positions for my pattern, including the center starting 
position, different from the home position?

Then we can calculate the position based on the home position of the arm (below).

Ignore Z coords, because we'll set those to be constant so we can gather high quality height data. 
As long as the arm doesn't complain about any out of bounds coordinates (forgot the exact error),
then we're good on the constant Z setting.

# Position Data

### Home position:

![img.png](img.png)

### Other positions

See png's for positions with old working area, see dobot_lab_code.py for positions with current working area (the commit on 20-05-2025)
