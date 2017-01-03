# WebIOPi Drivers

This respository provides hardware/chip drivers for WebIOPI / T-H-I-N-X.

They are valid for WebIOPI release 0.7.22-bus-swagger.

In order to use the drivers in the original WebIOPi 0.7.22 you have to comment out the decorators starting with @api and remove the "bus" parameter from the ____init____(...) method definitions and ____init____(...) calls.
