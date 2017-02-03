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
#   Derived from original WebIOPi SPI class 
#   Implements SPI device connectivity using the MCP2210 USB <-> SPI chip
#   Communicates via raw HID reports using the user space device node /dev/hidrawX
#   This driver has the limitation of supporting max 60 bytes per SPI transfer
#
#   ----------------------------------------------------------------------------
#
#   Changelog
#
#   1.0    2016-05-30    Initial release.
#
#   1.1    2016-06-22    Refactored for bus device indirection.
#
#   Implementation and usage remarks
#
#   Implements SPI device connectivity using the MCP2210 USB <-> SPI chip.
#   Communicates via raw HID reports using the user land device node /dev/hidrawX.
#   The value of X is dependent on the number of HID devices present in the
#   current system and from the time of insertion of the USB device. The number
#   may also change on behalf of the OS and its numbering algorithms between reboots.
#   This driver makes the assumption that the MCP2210 gets recognized automatically
#   by the OS as a HID device and attached to the raw OS HID drivers.
#   This driver has the current limitation of supporting max 60 bytes per single
#   SPI transfer which in most cases does not matter as typically only a few bytes
#   are transferred.
#
#   SPI standard communication methods are secured by mutual locking to avoid concurent
#   SPI communication via the same /dev/hidrawX node when multiple SPI chips are
#   connected to the same MCP2210 and concurrent request occur via the REST API.
#
#   If chip = -1 is used, ALL CS outputs (CS0..CS7) are tied to low, CS8 is omitted.
#

from webiopi.devices.bus import SPI_Bus
from webiopi.utils.logger import debug, info
from threading import Lock
import os

#HID report sizes
MCP_HID_REPORT_SIZE           = 64
MCP_MAX_TRANSFER_BYTES        = 60

#HID report commands
MCP_COMMAND_CANCEL_SPI_TRANSFER = 0x11
MCP_COMMAND_SET_CHIP_SETTINGS   = 0x21
MCP_COMMAND_SET_SPI_SETTINGS    = 0x40
MCP_COMMAND_TRANSFER_SPI_DATA   = 0x42

#HID report subcommands
MCP_COMMAND_OK                = 0x00
MCP_SPI_TRANSFER_STARTING     = 0x20
MCP_SPI_TRANSFER_FINISHED     = 0x10
MCP_SPI_TRANSFER_NOT_FINISHED = 0x30

#HID report byte offsets
MCP_SPI_COMMAND               = 0
MCP_SPI_TX_SIZE               = 1
MCP_SPI_DATA_START            = 4
MCP_SPI_RESULT_ERROR          = 1
MCP_SPI_RECEIVED_BYTES        = 2
MCP_SPI_ENGINE_STATUS         = 3

MCP_SPI_BIT_RATE_BYTE_3       = 4
MCP_SPI_BIT_RATE_BYTE_2       = 5
MCP_SPI_BIT_RATE_BYTE_1       = 6
MCP_SPI_BIT_RATE_BYTE_0       = 7

MCP_SPI_CS_IDLE_LOW           = 8
MCP_SPI_CS_IDLE_HIGH          = 9
MCP_SPI_CS_ACTIVE_LOW         = 10
MCP_SPI_CS_ACTIVE_HIGH        = 11

MCP_SPI_CS_TO_DATA_LOW        = 12
MCP_SPI_CS_TO_DATA_HIGH       = 13
MCP_SPI_LAST_DATA_TO_CS_LOW   = 14
MCP_SPI_LAST_DATA_TO_CS_HIGH  = 15
MCP_SPI_BETWEEN_DATA_LOW      = 16
MCP_SPI_BETWEEN_DATA_HIGH     = 17

MCP_SPI_TRSIZE_LOW            = 18
MCP_SPI_TRSIZE_HIGH           = 19

MCP_SPI_SPI_MODE              = 20

#MCP chip settings
MCP_CS                        = 0x01
    
#Singletons
MCPLOCK = None
FD = 0

class SPI_MCP2210_HIDRAW(SPI_Bus):
    def __init__(self, dev, chip=0, mode=0, bits=8, speed=0):
        Bus.__init__(self, "SPI", "/dev/" + dev)
        
        self.chip = chip
        self.mode = mode
        self.speed = speed
        self.cs_to_data_delay = 0
        self.data_to_cs_delay = 0
        self.between_data_delay = 0

        global MCPLOCK
        if MCPLOCK is None:
            MCPLOCK = Lock()

        debug("Attached SPI device - SPI_MCP2210_HIDRAW(class=%s chip=%d speed=%d dev=%s fd=%d)"  % (self.__class__.__name__, self.chip, self.speed, self.device, self.fd))
        
    def __str__(self):
        return "SPI_MCP2210_HIDRAW(chip=%d)" % self.chip

#---------- BUS open() and close() reimplementation to handle file descriptor singleton ----------

    def open(self):
        global FD
        if FD == 0:
            debug("Opening SPI bus device - SPI_MCP2210_HIDRAW(dev=%s)"  % self.device)
            self.fd = os.open(self.device, self.flag)
            if self.fd < 0:
                raise Exception("Cannot open %s" % self.device)
            FD = self.fd
            #self.setChipSettings() # uncomment when setting the chip settings is necessary at runtime
            self.resetSPITransfer()

        else:
            self.fd = FD

    def close(self):
        global FD
        if FD > 0:
            self.resetSPITransfer()
            debug("Closing SPI bus device - SPI_MCP2210_HIDRAW(dev=%s)"  % self.device)
            os.close(FD)
            FD = 0

#---------- SPI abstraction communication methods secured by mutual locking ----------

    def xfer(self, txbuff=None):
        global MCPLOCK
        size = len(txbuff)
        debug("%s xfer txsize=%d" % (self.__str__(), size))

        with MCPLOCK:
            self.setSPISettings(size)
            response = self.sendXferCommand(txbuff)
            # If not all bytes are received, do re-sending of nothing until needed bytes are received)
            while len(response) < len(txbuff):
                response += self.sendXferCommand()

        return bytearray(response)

    def writeBytes(self, data):
        size = len(data)
        debug("%s write size=%d" % (self.__str__(), size))
        #at the bottom line, writeBytes does the same as xfer, so just delegate
        self.xfer(data)

#---------- Basic read/write communication via HID reports of MCP2210 ----------

    def sendXferCommand(self, data=[]):
        size = len(data)
        if size > MCP_MAX_TRANSFER_BYTES:
            raise Exception("Error: MCP SPI driver can only write max %d bytes." % MCP_MAX_TRANSFER_BYTES)

        debug("%s sendXfer sendsize=%d" % (self.__str__(), size))

        wbuff = bytearray(MCP_HID_REPORT_SIZE)
        wbuff[MCP_SPI_COMMAND] = MCP_COMMAND_TRANSFER_SPI_DATA
        wbuff[MCP_SPI_TX_SIZE] = size
        for i in range(size):
            wbuff[i+MCP_SPI_DATA_START] = data[i]
        self.write(wbuff)

        rbuff = bytearray(self.read(MCP_HID_REPORT_SIZE))

        state = self.calculateState(rbuff[MCP_SPI_ENGINE_STATUS])
        debug("%s transfer_spi_data_received: 0x%02X, 0x%02X, got=%d, %s, [0x%02X, 0x%02X, 0x%02X, 0x%02X]" % (self.__str__(),rbuff[0],rbuff[1],rbuff[2],state,rbuff[4],rbuff[5],rbuff[6],rbuff[7]))

        if (rbuff[MCP_SPI_COMMAND] == MCP_COMMAND_TRANSFER_SPI_DATA) & (rbuff[MCP_SPI_RESULT_ERROR] != MCP_COMMAND_OK):
            raise Exception("Error: MCP SPI driver cannot accept SPI data.")

        rsize = rbuff[MCP_SPI_RECEIVED_BYTES]                 
        return rbuff[MCP_SPI_DATA_START:MCP_SPI_DATA_START+rsize]
                
    def setSPISettings(self, size=0):
        wbuff = bytearray(MCP_HID_REPORT_SIZE)
        wbuff[MCP_SPI_COMMAND] = MCP_COMMAND_SET_SPI_SETTINGS
        
        speedByte3, speedByte2, speedByte1, speedByte0 = self.getBitRate(self.speed)
        wbuff[MCP_SPI_BIT_RATE_BYTE_3]    = speedByte3
        wbuff[MCP_SPI_BIT_RATE_BYTE_2]    = speedByte2
        wbuff[MCP_SPI_BIT_RATE_BYTE_1]    = speedByte1
        wbuff[MCP_SPI_BIT_RATE_BYTE_0]    = speedByte0

        idlelow, idlehigh, activelow, activehigh = self.getChipSelect(self.chip)
        wbuff[MCP_SPI_CS_IDLE_LOW]    = idlelow
        wbuff[MCP_SPI_CS_IDLE_HIGH]   = idlehigh
        wbuff[MCP_SPI_CS_ACTIVE_LOW]  = activelow
        wbuff[MCP_SPI_CS_ACTIVE_HIGH] = activehigh
        
        wbuff[MCP_SPI_CS_TO_DATA_LOW]       = self.cs_to_data_delay & 0xFF         
        wbuff[MCP_SPI_CS_TO_DATA_HIGH]      = (self.cs_to_data_delay >> 8) & 0xFF
        wbuff[MCP_SPI_LAST_DATA_TO_CS_LOW]  = self.data_to_cs_delay & 0xFF
        wbuff[MCP_SPI_LAST_DATA_TO_CS_HIGH] = (self.data_to_cs_delay >> 8) & 0xFF
        wbuff[MCP_SPI_BETWEEN_DATA_LOW]     = self.between_data_delay & 0xFF
        wbuff[MCP_SPI_BETWEEN_DATA_HIGH]    = (self.between_data_delay >> 8) & 0xFF

        wbuff[MCP_SPI_TRSIZE_LOW]  = size & 0xFF
        wbuff[MCP_SPI_TRSIZE_HIGH] = (size >> 8) & 0xFF

        wbuff[MCP_SPI_SPI_MODE] = self.mode

        self.write(wbuff)
        
        rbuff = bytearray(self.read(MCP_HID_REPORT_SIZE))

        bitrate = self.calculateBitRate(rbuff[MCP_SPI_BIT_RATE_BYTE_3],rbuff[MCP_SPI_BIT_RATE_BYTE_2],rbuff[MCP_SPI_BIT_RATE_BYTE_1],rbuff[MCP_SPI_BIT_RATE_BYTE_0])
        idle, active = self.calculateChipSelects(rbuff[MCP_SPI_CS_IDLE_LOW],rbuff[MCP_SPI_CS_IDLE_HIGH],rbuff[MCP_SPI_CS_ACTIVE_LOW],rbuff[MCP_SPI_CS_ACTIVE_HIGH])
        debug("%s set_spi_settings_received: 0x%02X, 0x%02X, speed=%d, idle_cs=%s, active_CS=%s" % (self.__str__(),rbuff[0],rbuff[1],bitrate,idle,active))

        if (rbuff[MCP_SPI_COMMAND] == MCP_COMMAND_SET_SPI_SETTINGS) & (rbuff[MCP_SPI_RESULT_ERROR] != MCP_COMMAND_OK):
            raise Exception("Error: MCP SPI driver cannot accept SPI settings data.")

    def setChipSettings(self):
        wbuff = bytearray(MCP_HID_REPORT_SIZE)
        wbuff[MCP_SPI_COMMAND] = MCP_COMMAND_SET_CHIP_SETTINGS
        
        for i in range(4,12): #Enable CS0 to CS7, don't use CS8
            wbuff[i] = MCP_CS
        wbuff[13]   = 0xFF
        wbuff[17]   = 0x12

        self.write(wbuff)
        
        rbuff = bytearray(self.read(MCP_HID_REPORT_SIZE))

        if (rbuff[MCP_SPI_COMMAND] == MCP_COMMAND_SET_CHIP_SETTINGS) & (rbuff[MCP_SPI_RESULT_ERROR] != MCP_COMMAND_OK):
            raise Exception("Error: MCP SPI driver cannot accept chip settings data.")
        debug("Setted SPI bus device chip settings - SPI_MCP2210_HIDRAW(dev=%s)"  % self.hidChannel)

    def resetSPITransfer(self):
        wbuff = bytearray(MCP_HID_REPORT_SIZE)
        wbuff[MCP_SPI_COMMAND] = MCP_COMMAND_CANCEL_SPI_TRANSFER
        
        self.write(wbuff)
        
        rbuff = bytearray(self.read(MCP_HID_REPORT_SIZE))

        if (rbuff[MCP_SPI_COMMAND] == MCP_COMMAND_SET_CHIP_SETTINGS) & (rbuff[MCP_SPI_RESULT_ERROR] != MCP_COMMAND_OK):
            raise Exception("Error: MCP SPI driver cannot reset SPI transfer.")
        debug("Resetted SPI bus transfer - SPI_MCP2210_HIDRAW(dev=%s)"  % self.device)

#---------- MCP2210 HID communication helper methods ----------

    def getChipSelect(self, chip):
        idlelow = 0xFF
        idlehigh = 0xFF
        if chip == -1:
            activehigh = 0xFF
            activelow = 0x00
        else:       
            active = (0xFFFF & ~(1 << chip))
            activehigh = active >> 8
            activelow = active & 0xFF       
        return (idlelow, idlehigh, activelow, activehigh)
    
    def getBitRate(self, speed):
        speedByte3 = (speed) & 0xFF
        speedByte2 = (speed >> 8) & 0xFF
        speedByte1 = (speed >> 16) & 0xFF
        speedByte0 = (speed >> 24) & 0xFF
        return (speedByte3, speedByte2, speedByte1, speedByte0)

#---------- MCP2210 HID communication debugging helper methods ----------

    def calculateBitRate(self, speedByte3, speedByte2, speedByte1, speedByte0):
        return (speedByte0 << 24) + (speedByte1 << 16) + (speedByte2 << 8) + speedByte3

    def calculateChipSelects(self, idlelow, idlehigh, activelow, activehigh):
        idle = bin ((idlehigh << 8) | idlelow)
        active = bin ((activehigh << 8) | activelow )
        return idle, active

    def calculateState(self, stateByte):
        if stateByte == MCP_SPI_TRANSFER_FINISHED:
            return "finished"
        if stateByte == MCP_SPI_TRANSFER_NOT_FINISHED:
            return "ongoing"
        if stateByte == MCP_SPI_TRANSFER_STARTING:
            return "starting"
        



