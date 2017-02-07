#   Copyright 2017 Andreas Riegg - t-h-i-n-x.net
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
#   1.0    2017-02-03    Initial release.
#
#   Implementation and usage remarks
#
#   Implements SPI device connectivity using the MCP2210 USB <-> SPI chip.
#   This driver does not modify the GPIO/CS dedication of the ports. In order
#   to work correct please set the power-up settings to appropriate values with
#   the MCP 2210 utility tool.
#
#   This version is for SPI MCP2210 WinDLL version 2 usage on Windows OS. Parts of
#   the code have been adapted from the MCP 2210 examples from Microchip.
#   CAUTION: This version does not work on any LINUX OS!!
#
#   A singleton for the opened DLL object named MCPDLL is used here.
#   A singleton for the opened DLL object handle named HANDLE is used here.
#   This driver currently works only for the standard vid/pid device ids and only one
#   chip (index 0).
#

from webiopi.devices.bus import Bus, SPI_Bus
from webiopi.utils.types import toint
from webiopi.utils.logger import debug
from ctypes import *

MCPDLL = None
HANDLE = None
CONNECTED = False

class SPI_MCP2210_WINDLL(SPI_Bus):

    #Standard VID and PID of the MCP2210 devices
    vid = c_ushort(0x4d8)
    pid = c_ushort(0xde)

    def __init__(self, chip=0, mode=0, bits=8, speed=12000000, dev="windll:", dllpath="", dllname="mcp2210_dll_um_x86"):
        self.chip = toint(chip)
        self.mode = toint(mode)
        #self.bits = toint(bits) unused
        self.speed = toint(speed)
        if self.speed > 12000000:
            raise ValueError("Maximum SPI speed for MCP2210 is 12,000,000.0 Hz (%s Hz is given)" % '{:,.1f}'.format(self.speed))
        self.dllpath = dllpath
        self.dllname = dllname
        self.cs_to_data_delay = 0
        self.data_to_cs_delay = 0
        self.between_data_delay = 0

        Bus.__init__(self, "SPI", dev + dllpath + dllname)
        debug("Attached SPI device - %s" % self.__str__())

    def __str__(self):
        return "%s (chip=%d mode=%d speed=%s dev=%s)" % (self.__class__.__name__, self.chip, self.mode, '{:,.1f}'.format(self.speed), self.device)

#---------- BUS open() and close() reimplementation to handle dll file singleton ----------
# TODO: Correct handling of open/close with multiple slaves dynamically

    def open(self):
        global MCPDLL
        global CONNECTED
        
        if MCPDLL is None:
            debug("Opening SPI bus device - %s(dev=%s)"  % (self.__class__.__name__, self.device))
            try:
                MCPDLL = WinDLL(self.dllpath + self.dllname)
            except WindowsError:
                raise Exception("Cannot load library %s" % self.device)

            connectedDevices = MCPDLL.Mcp2210_GetConnectedDevCount(self.vid, self.pid)
            if connectedDevices <= 0:
                raise Exception("Cannot connect to MCP2210 chip via %s" % self.device)
            self.openMCPDevice()

        if not CONNECTED:
            raise Exception("Cannot open MCP2210 chip via %s" % self.device)

    def close(self):
        global MCPDLL
        global HANDLE

        if MCPDLL is not None:
            debug("Closing SPI bus device - %s(dev=%s)"  % (self.__class__.__name__, self.device))
            success = MCPDLL.Mcp2210_Close(HANDLE)
            if success != 0:
                raise Exception("Cannot close MCP2210 chip via %s" % self.device)
            MCPDLL = None
            HANDLE = None
            CONNECTED = False
        SPI_Bus.close(self)


#---------- Helper methods ----------

    def getActiveChipSelectValue(self):
        if self.chip == -1:
            return 0xFF00
        else:
            return (0xFFFF & ~(1 << self.chip))

    def openMCPDevice(self):
        global MCPDLL
        global CONNECTED
        global HANDLE
        
        index0 = c_uint32(0)

        # Do first dummy call to get the needed path size put into pathsize
        path = create_unicode_buffer(1)
        pathsize = c_ulong(1)
        h = c_void_p(MCPDLL.Mcp2210_OpenByIndex(self.vid, self.pid, index0, path, byref(pathsize)));
        success = MCPDLL.Mcp2210_GetLastError()
        if success != -3:
            raise Exception("Cannot connect to MCP2210 chip via %s" % self.device)
        del path

        # Do second call to get the final handle
        path = create_unicode_buffer(int(pathsize.value/sizeof(c_wchar)))
        HANDLE = c_void_p(MCPDLL.Mcp2210_OpenByIndex(self.vid, self.pid, index0, path, byref(pathsize)));
        success = MCPDLL.Mcp2210_GetLastError()
        if success != 0:
            raise Exception("Cannot open MCP2210 chip via %s" % self.device)
        else:
            CONNECTED = True
            debug("Opened SPI device - %s (handle=0x%x)" % (self.__str__(), HANDLE.value))


#---------- Basic read/write communication via MCP2210 DLL API calls ----------

    def xfer(self, data=[]):
        global MCPDLL
        global HANDLE
        
        debug("%s xfer send %s" % (self.__str__(), data))
        size = len(data)
        txbuff           = (c_ubyte * size)(*data)
        rxbuff           = (c_ubyte * size)()
        pSpeed           = c_uint(self.speed)
        pXferSize        = c_uint(size)
        CsMask           = c_uint(0x8000)  # Ignore GP8 error and keep port designation unchanged
        pIdleCsVal       = c_uint(0xFFFF)
        pActiveCsVal     = c_uint(self.getActiveChipSelectValue())
        pCsToDataDelay   = c_uint(self.cs_to_data_delay)
        pDataToDataDelay = c_uint(self.between_data_delay)
        pDataToCsDelay   = c_uint(self.data_to_cs_delay)
        pMode            = c_ubyte(self.mode)

        success = MCPDLL.Mcp2210_xferSpiDataEx(HANDLE, txbuff, rxbuff, byref(pSpeed), byref(pXferSize),
                                               CsMask, byref(pIdleCsVal), byref(pActiveCsVal),
                                               byref(pCsToDataDelay), byref(pDataToCsDelay), byref(pDataToDataDelay),
                                               byref(pMode))
        if success != 0:
            raise Exception("Xfer error %s returncode: %s" % (self.device, success))

        return bytearray(rxbuff)

    def writeBytes(self, data):
        debug("%s writeBytes %s" % (self.__str__(), data))
        #at the bottom line, writeBytes does the same as xfer, so just delegate
        self.xfer(data)
