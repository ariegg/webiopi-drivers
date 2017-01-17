# WebIOPi Drivers

This respository provides hardware/chip drivers for WebIOPI / T-H-I-N-X.

They are valid for WebIOPI release 0.7.22-bus-swagger.

In order to use the drivers in the original WebIOPi 0.7.22 you have to comment out the decorators starting with @api, remove the "bus" parameter from the \_\_init\_\_(...) method definitions and \_\_init\_\_(...) calls and remove the device() parameter/calls from the __str__() methods. You also have to copy the Python source files to their correct location in the WebIOPi folders, adapt setup.py to include the new components and also modify manager.py so that the dynamic driver lookup finds the new hardware categories.

#IMPORTANT:

This repository does not contain a 1:1 installable package of WebIOPi that can be installed and run as it is. It is more a library of logical separated components that form the hardware abstraction layer including the gereric REST API mappings and the available chip drivers for WebIOPi based on that abstraction layer.
