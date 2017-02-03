#   Copyright 2012-2016 Eric Ptak - trouch.com
#   Partly Copyright 2016 Andreas Riegg - t-h-i-n-x.net
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable la(w or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
#   ----------------------------------------------------------------------------
#
#   Changelog
#
#   1.1    2016-06-28    Patched version for bus selection. Renamed from serial.py
#                        to avoid naming conflicts with new abstract serial device.
#


import os
import fcntl
import struct
import termios

from webiopi.devices.bus import Bus, UART_Bus

TIOCINQ   = hasattr(termios, 'FIONREAD') and termios.FIONREAD or 0x541B
TIOCM_zero_str = struct.pack('I', 0)

class UART_DEV(UART_Bus):
    def __init__(self, dev, baudrate):
        if not dev.startswith("/dev/"):
            dev = "/dev/%s" % dev
        
        aname = "B%d" % baudrate
        if not hasattr(termios, aname):
            raise Exception("Unsupported baudrate")
        self.baudrate = baudrate

        Bus.__init__(self, "UARTDEV", dev, os.O_RDWR | os.O_NOCTTY)
        fcntl.fcntl(self.fd, fcntl.F_SETFL, os.O_NDELAY)
        
        #backup  = termios.tcgetattr(self.fd)
        options = termios.tcgetattr(self.fd)
        # iflag
        options[0] = 0

        # oflag
        options[1] = 0

        # cflag
        options[2] |= (termios.CLOCAL | termios.CREAD)
        options[2] &= ~termios.PARENB
        options[2] &= ~termios.CSTOPB
        options[2] &= ~termios.CSIZE
        options[2] |= termios.CS8

        # lflag
        options[3] = 0

        speed = getattr(termios, aname)
        # input speed
        options[4] = speed
        # output speed
        options[5] = speed
        
        termios.tcsetattr(self.fd, termios.TCSADRAIN, options)
        
    def __str__(self):
        return "UART_DEV(%dbps)" % self.baudrate
        
    def available(self):
        s = fcntl.ioctl(self.fd, TIOCINQ, TIOCM_zero_str)
        return struct.unpack('I',s)[0]
    
