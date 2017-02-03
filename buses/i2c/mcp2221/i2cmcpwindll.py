#   Copyright 2016 Andreas Riegg - t-h-i-n-x.net
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
#   ----------------------------------------------------------------------------
#
#   Changelog
#
#   1.0    2016-06-27    Initial release.
#
#   1.1    2016-07-28    Added compatibilty with slave address detect feature from WebIOPi 0.7.22
#
#   Implementation and usage remarks
#
#   Implements I2C device connectivity using the MCP2221 USB <-> I2C chip.
#
#   This version is for I2C MCP2221 WinDLL usage on Windows OS.
#   CAUTION: This version does not work on any LINUX OS!!
#   The Microchip DLL works with 8 bit slave addresses only, so convert it
#   automatically.
#
#   A singleton for the opened DLL object named MCPDLL is used here.
# 

from webiopi.devices.bus import Bus, I2C_Bus
from webiopi.utils.types import toint
from webiopi.utils.logger import debug
import ctypes
from ctypes import c_ubyte, c_uint

MCPDLL = None

class I2C_MCP2221_WINDLL(I2C_Bus):
    def __init__(self, slave, speed=100000, dev="windll:", dllpath="", dllname="MCP2221DLL-UM_x86"):
        self.slave = slave
        self.speed = toint(speed)
        if self.speed > 400000:
            raise ValueError("Maximum I2C speed for MCP2221 is 400,000.0 Hz (%s Hz is given)" % '{:,.1f}'.format(self.speed))
        self.dllpath = dllpath
        self.dllname = dllname
        Bus.__init__(self, "I2C", dev + dllpath + dllname)
        I2C_Bus.__init__(self, slave)

        debug("Attached I2C device - %s" % self.__str__())
        
    def __str__(self):
        return "%s (slave=0x%02X speed=%s dev=%s)" % (self.__class__.__name__, self.slave, '{:,.1f}'.format(self.speed), self.device)
    
#---------- BUS open() and close() reimplementation to handle dll file singleton ----------
# TODO: Correct handling of open/close with multiple slaves dynamically
    
    def open(self):
        global MCPDLL       
        if MCPDLL is None:
            debug("Opening I2C bus device - %s(dev=%s)"  % (self.__class__.__name__, self.device))
            try:
                MCPDLL = ctypes.WinDLL(self.dllpath + self.dllname)
            except WindowsError:
                raise Exception("Cannot load library %s" % self.device)
            MCPDLL.DllInit()

        isConnected = MCPDLL.GetConnectionStatus()
        if not isConnected:
            raise Exception("Cannot connect to MCP2221 chip via %s" % self.device)

    def close(self):
        global MCPDLL
        if MCPDLL is not None:
            MCPDLL.StopI2cDataTransfer()
            debug("Closing I2C bus device - %s(dev=%s)"  % (self.__class__.__name__, self.device))
            handle = MCPDLL._handle
            ctypes.windll.kernel32.FreeLibrary(handle)
            MCPDLL = None
            
        I2C_Bus.close(self)


#---------- Basic read/write communication via MCP2221 DLL API calls ----------
        
    def readBytes(self, size=1):
        global MCPDLL      
        buff = (c_ubyte * size)(*bytearray(size))
        success = MCPDLL.ReadI2cData(c_ubyte((self.slave << 1) + 1), buff, c_uint(size), c_uint(self.speed))
        if success < 0: #Todo: some returncodes may be worth a retry
            raise Exception("Read error %s returncode: %s" % (self.device, success))
        return bytearray(buff)

    def writeBytes(self, data):
        global MCPDLL
        size = len(data)
        success = MCPDLL.WriteI2cData(c_ubyte(self.slave << 1), (c_ubyte * size)(*data), c_uint(size), c_uint(self.speed))
        if success < 0: #Todo: some returncodes may be worth a retry
            raise Exception("Write error %s returncode: %s" % (self.device, success))




