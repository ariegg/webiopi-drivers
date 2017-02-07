
Here the files for additional WebIOPi utilities are located.

This comprises:
- The driverDetector utility in drivers.py. It allows to detect new device drivers 
without editing the \_\_init\_\_.py files in the device subfolders. For this to work properly slightly modified versions 
of the \_\_init\_\_.py files are necessary.

  You have to:

  - Add "from webiopi.utils.drivers import driverDetector" to the imports at the beginning of each \_\_init\_\_.py
  - Add "driverDetector(\_\_file\_\_, DRIVERS)" at the very end of each \_\_init\_\_.py
  - Please look at the comment of drivers.py how to use it.
  - So far it has been developed and tested with Python 2.7.x on Windows 7 OS but it should work with other OS as well.

- More to come ...
