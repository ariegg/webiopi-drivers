# WebIOPi Drivers

This respository provides hardware/chip drivers for WebIOPi / T-H-I-N-X.

They are valid for WebIOPi release 0.7.22-bus-swagger (which is not an official release at the moment).

In order to use the drivers in the original WebIOPi 0.7.22 you have to comment out the decorators starting with @api, remove the "bus" parameter from the \_\_init\_\_(...) method definitions and \_\_init\_\_(...) calls and remove the device() parameter/calls from the \_\_str\_\_() methods. You also have to copy the Python source files to their correct location in the WebIOPi folders, adapt setup.py to include the new components and also modify manager.py so that the dynamic driver lookup finds the new hardware categories. Please keep in mind, this is not a job for WebIOPi beginners, it's something for the professionals.

#IMPORTANT:

This repository does not contain a 1:1 installable package of WebIOPi that can be installed and run as it is. It is more a library of logical separated components that form the hardware abstraction layer including the generic REST API mappings, the different hardware bus implementations and the available chip drivers for WebIOPi based on the abstraction components.

This repository was created to save all extension work for WebIOPi in one place in a consistent way until it is decided how to proceed with the whole package.

#Bus extension

All drivers in this repository use the "bus" extension created by me. This extension allows to select different bus providers for I2C, SPI and UART (aka Serial). The standard bus "drivers" of WebIOPi use the /dev nodes in the userspace. Other variants are provided to
- use USB-based protocol conversion chips for I2C and SPI
- simulate bus communication, partly with the help of simulated memory chips
- use USB-based protocol conversion chips for I2C and SPI on the Windows platform with dll's
- use the PySerial library to provide extended serial support
