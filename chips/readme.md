
Here you find the code for chip drivers.

The drivers are grouped into subdirectories with the naming scheme ./{abstraction}/{chip-name}. On the lowest level, there is 
- the driver file (*.py)
- a code fragment to add the driver file to the driver class lookup table at 
the end in the corresponding abstraction \_\_init\_\_.py code file (drivers.py)
- the driver detection file (*.drivers)
- sometimes a text file fragment that shows some device parameter options for the config file entry in the [DEVICES] section
- sometimes a full version of the \_\_init\_\_.py code file (but it may be not the latest version)

The drivers for the chip simulations ca be found in the ./{abstraction}/simulation subdirectories (if available).
