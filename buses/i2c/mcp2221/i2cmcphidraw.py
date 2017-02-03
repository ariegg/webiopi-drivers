#   Copyright 2016 Andreas Riegg - t-h-i-n-x.net
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
#   1.0    2016-05-27    Initial release.
#
#   1.1    2016-06-13    Rework and added setting of I2C speed.
#
#   1.2    2016-06-22    Refactored for bus device indirection.
#
#   1.3    2016-07-28    Added compatibilty with slave address detect feature from WebIOPi 0.7.22
#
#   Implementation and usage remarks
#
#   Derived from original WebIOPi I2C class.
#   Implements I2C device connectivity using the MCP2221 USB <-> I2C chip.
#   Communicates via raw HID reports using the user land device node /dev/hidrawX.
#   The value of X is dependent on the number of HID devices present in the
#   current system and from the time of insertion of the USB device. The number
#   may also change on behalf of the OS and its numbering algorithms between reboots.
#   This driver makes the assumption that the MCP2221 gets recognized automatically
#   by the OS as a HID device and attached to the raw OS HID drivers.
#   This driver has the current limitation of supporting max 60 bytes per single
#   I2C transfer which in most cases does not matter as typically only a few bytes
#   are transferred.
#
#   I2C standard communication methods are secured by mutual locking to avoid concurent
#   I2C communication via the same /dev/hidrawX node when multiple I2C chips are
#   connected to the same MCP2221 and concurrent request occur via the REST API.
#

from webiopi.devices.bus import Bus, I2C_Bus
from webiopi.utils.logger import debug, info
from threading import Lock
from webiopi.utils.types import toint
import os

#HID report sizes
MCP_HID_REPORT_SIZE           = 64
MCP_MAX_TRANSFER_BYTES        = 60

#HID report commands
MCP_COMMAND_STATUS            = 0x10
MCP_COMMAND_WRITE_I2C         = 0x90
MCP_COMMAND_REQUEST_READ_I2C  = 0x91
MCP_COMMAND_GET_READ_DATA_I2C = 0x40

#HID report subcommands
MCP_SUB_COMMAND_CANCEL_I2C    = 0x10
MCP_SUB_COMMAND_SET_I2C_SPEED = 0x20

#HID report result codes
MCP_COMMAND_OK                = 0x00

#HID report byte offsets
MCP_I2C_COMMAND               = 0
MCP_I2C_READ_SIZE             = 1
MCP_I2C_WRITE_SIZE            = 1
MCP_I2C_SLAVE_ADDR            = 3
MCP_I2C_DATA_START            = 4
MCP_I2C_RESULT_ERROR          = 1
MCP_I2C_RESPONSE_SIZE         = 3
MCP_I2C_CANCEL_SUBCOMMAND     = 2
MCP_I2C_SET_I2C_SPEED         = 3
MCP_I2C_NEW_I2C_CLOCK_DIVIDER = 4

#I2C speed clock dividers examples
# 47 kHz = 255 (12MHz /  47kHz) Slowest Possible Mode of MCP2221
#100 kHz = 120 (12MHz / 100kHz) Standard Mode
#400 kHz =  30 (12MHz / 400kHz) Fast Mode

#Singletons
MCPLOCK = None
FD = 0

class I2C_MCP2221_HIDRAW(I2C_Bus):
    def __init__(self, dev, slave, speed=100000):
        Bus.__init__(self, "I2C", "/dev/" + dev)
        
        self.slave = slave
        self.speed = toint(speed)
        if self.speed > 400000:
            raise ValueError("Maximum I2C speed for MCP2221 is 400,000.0 Hz (%s Hz is given)" % '{:,.1f}'.format(self.speed))
        self.i2cbusdivider = int(12000000 // self.speed)
        I2C_Bus.__init__(self, slave)
        
        global MCPLOCK
        if MCPLOCK is None:
            MCPLOCK = Lock()

        debug("Attached I2C device - %s" % self.__str__())
        
        self.setI2CBusSpeed(self.i2cbusdivider)
        self.getStatus()

    def __str__(self):
        return "%s (slave=0x%02X speed=%s dev=%s)" % (self.__class__.__name__, self.slave, '{:,.1f}'.format(self.speed), self.device)

#---------- BUS open() and close() reimplementation to handle file descriptor singleton ----------
# TODO: Correct handling of open/close with multiple slaves dynamically

    def open(self):
        global FD
        if FD == 0:
            debug("Opening I2C bus device - %s(dev=%s)"  % (self.__class__.__name__, self.device))
            self.fd = os.open(self.device, self.flag)
            if self.fd < 0:
                raise Exception("Cannot open %s" % self.device)
            FD = self.fd
            self.resetI2CTransfer()
        else:
            self.fd = FD

    def close(self):
        global FD
        if FD > 0:
            self.resetI2CTransfer()
            debug("Closing I2C bus device - %s(dev=%s)"  % (self.__class__.__name__, self.device))
            os.close(FD)
            FD = 0
            
        I2C_Bus.close(self)

#---------- I2C Bus abstraction communication methods secured by mutual locking ----------

    def readRegister(self, addr):
        global MCPLOCK
        with MCPLOCK:
            self.writeByte(addr)
            result = self.readByte()
        return result

    def readRegisters(self, addr, count):
        global MCPLOCK
        with MCPLOCK:
            self.writeByte(addr)
            result = self.readBytes(count)
        return result

    def writeRegister(self, addr, byte):
        global MCPLOCK
        with MCPLOCK:
            self.writeBytes([addr, byte])

    def writeRegisters(self, addr, buff):
        global MCPLOCK
        with MCPLOCK:
            d = bytearray(len(buff)+1)
            d[0] = addr
            d[1:] = buff
            self.writeBytes(d)

#---------- Basic read/write communication via HID reports of MCP2221 ----------

    def readBytes(self, size=1):
        if size > MCP_MAX_TRANSFER_BYTES:
            raise Exception("Error: MCP I2C driver can only read max %d bytes." % MCP_MAX_TRANSFER_BYTES)
        debug("%s readBytes size=%d" % (self.__str__(), size))

        wbuff = bytearray(MCP_HID_REPORT_SIZE)
        wbuff[MCP_I2C_COMMAND] = MCP_COMMAND_REQUEST_READ_I2C
        wbuff[MCP_I2C_READ_SIZE] = size
        wbuff[MCP_I2C_SLAVE_ADDR] = (self.slave << 1) + 1
        self.write(wbuff)

        rbuff = bytearray(self.read(MCP_HID_REPORT_SIZE))
        if (rbuff[MCP_I2C_COMMAND] == MCP_COMMAND_REQUEST_READ_I2C) & (rbuff[MCP_I2C_RESULT_ERROR] != MCP_COMMAND_OK):
            raise Exception("Error: MCP I2C driver cannot request read data.")

        response = []
        while len(response) < size:
            wbuff = bytearray(MCP_HID_REPORT_SIZE)
            wbuff[MCP_I2C_COMMAND] = MCP_COMMAND_GET_READ_DATA_I2C
            self.write(wbuff)

            rbuff = bytearray(self.read(MCP_HID_REPORT_SIZE))
            debug("%s get_i2c_data_received: 0x%02X, 0x%02X, 0x%02X, got=%d, [0x%02X, 0x%02X, 0x%02X, 0x%02X]" % (self.__str__(),rbuff[0],rbuff[1],rbuff[2],rbuff[3],rbuff[4],rbuff[5],rbuff[6],rbuff[7]))
            if (rbuff[MCP_I2C_COMMAND] == MCP_COMMAND_GET_READ_DATA_I2C) & (rbuff[MCP_I2C_RESULT_ERROR] != MCP_COMMAND_OK):
                raise Exception("Error: MCP I2C driver cannot read data.")
            else:
                rsize = rbuff[MCP_I2C_RESPONSE_SIZE]
                response += rbuff[MCP_I2C_DATA_START:MCP_I2C_DATA_START+rsize]
        return bytearray(response)

    def writeBytes(self, data):
        size = len(data)
        if size > MCP_MAX_TRANSFER_BYTES:
            raise Exception("Error: MCP I2C driver can only write max %d bytes." % MCP_MAX_TRANSFER_BYTES)
        debug("%s writeBytes size=%d" % (self.__str__(), size))

        wbuff = bytearray(MCP_HID_REPORT_SIZE)
        wbuff[MCP_I2C_COMMAND] = MCP_COMMAND_WRITE_I2C
        wbuff[MCP_I2C_WRITE_SIZE] = size
        wbuff[MCP_I2C_SLAVE_ADDR] = (self.slave << 1)
        for i in range(size):
            wbuff[i+MCP_I2C_DATA_START] = data[i]

        self.write(wbuff)
        rbuff = bytearray(self.read(MCP_HID_REPORT_SIZE))
        if (rbuff[MCP_I2C_COMMAND] == MCP_COMMAND_WRITE_I2C) & (rbuff[MCP_I2C_RESULT_ERROR] != MCP_COMMAND_OK):
            raise Exception("Error: MCP I2C driver cannot write data.")

    def resetI2CTransfer(self):
        wbuff = bytearray(MCP_HID_REPORT_SIZE)
        wbuff[MCP_I2C_COMMAND] = MCP_COMMAND_STATUS
        wbuff[MCP_I2C_CANCEL_SUBCOMMAND] = MCP_SUB_COMMAND_CANCEL_I2C

        self.write(wbuff)

        rbuff = bytearray(self.read(MCP_HID_REPORT_SIZE))

        if (rbuff[MCP_I2C_COMMAND] == MCP_COMMAND_STATUS) & (rbuff[MCP_I2C_RESULT_ERROR] != MCP_COMMAND_OK):
            raise Exception("Error: MCP I2C driver cannot reset I2C transfer.")
        debug("Resetted I2C bus transfer - I2C_MCP2221_HIDRAW(dev=%s)"  % self.device)

    def setI2CBusSpeed(self, divider):
        wbuff = bytearray(MCP_HID_REPORT_SIZE)
        wbuff[MCP_I2C_COMMAND] = MCP_COMMAND_STATUS
        wbuff[MCP_I2C_SET_I2C_SPEED] = MCP_SUB_COMMAND_SET_I2C_SPEED
        wbuff[MCP_I2C_NEW_I2C_CLOCK_DIVIDER] = divider

        self.write(wbuff)

        rbuff = bytearray(self.read(MCP_HID_REPORT_SIZE))
        debug("I2C_MCP2221_HIDRAW(dev=%s) status_received: 0x%02X, 0x%02X, cancel=%d, speedstate=0x%02X, newdiv=%s, currdiv=%s, currto=%s" % (self.device,rbuff[0],rbuff[1],rbuff[2],rbuff[3],rbuff[4],rbuff[14],rbuff[15]))

        if (rbuff[MCP_I2C_COMMAND] == MCP_COMMAND_STATUS) & (rbuff[MCP_I2C_RESULT_ERROR] != MCP_COMMAND_OK):
            raise Exception("Error: MCP I2C driver cannot set I2C speed.")
        debug("Setted I2C bus speed - I2C_MCP2221_HIDRAW(dev=%s)"  % self.device)

#---------- MCP2210 HID communication debugging helper methods ----------

    def getStatus(self):
        wbuff = bytearray(MCP_HID_REPORT_SIZE)
        wbuff[MCP_I2C_COMMAND] = MCP_COMMAND_STATUS

        self.write(wbuff)

        rbuff = bytearray(self.read(MCP_HID_REPORT_SIZE))
        debug("I2C_MCP2221_HIDRAW(dev=%s) status_received: 0x%02X, 0x%02X, cancel=%d, speedst=0x%02X, ndiv=%s, i2cst=0x%02X, lbr=0x%02X, hbr=0x%02X, lbs=0x%02X, hbs=0x%02X, cnt=%d, cdiv=%s, cto=%s, lba=0x%02X, hba=0x%02X, pend=%d"  %
              (self.device,rbuff[0],rbuff[1],rbuff[2],rbuff[3],rbuff[4],rbuff[8],rbuff[9],rbuff[10],rbuff[11],rbuff[12],rbuff[13],rbuff[14],rbuff[15],rbuff[16],rbuff[17],rbuff[25]))


