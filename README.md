# WebIOPi Drivers

This respository provides hardware/chip drivers for WebIOPi / T-H-I-N-X.

They are valid for WebIOPi release 0.7.22-bus-swagger (which is not an official release at the moment).

In order to use the drivers in the original WebIOPi 0.7.22 you have to comment out the decorators starting with @api, remove the "bus" parameter from the \_\_init\_\_(...) method definitions and \_\_init\_\_(...) calls and remove the device() parameter/calls from the \_\_str\_\_() methods. You also have to copy the Python source files to their correct location in the WebIOPi folders, adapt setup.py to include the new components and also modify manager.py so that the dynamic driver lookup finds the new hardware categories. Please keep in mind, this is not a job for WebIOPi beginners, its something for the professionals.

#IMPORTANT:

This repository does not contain a 1:1 installable package of WebIOPi that can be installed and run as it is. It is more a library of logical separated components that form the hardware abstraction layer including the generic REST API mappings, the different hardware bus implementations and the available chip drivers for WebIOPi based on that abstraction layer.

This repository was created to save all extension work for WebIOPi in one place in a consistent way until it is decided how to proceed with the whole package.
