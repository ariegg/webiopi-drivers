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
#   1.0    2017-02-27    Initial release.
#
#   Implementation and usage remarks
#
#   Implements I2C and SPI device connectivity using the Robot Electronics USB-ISS
#   and USB-I2C adapters and the bus extension for WebIOPi.
#
#   Communicates via any standard serial interface. On Linux platforms, this may be
#   any properly configured /dev/tty.... connection. On Windows platform, this may be
#   any COMx interface. This is implemented via an auxiliary bus device which can be
#   any supported serial device of WebIOPi. The communication scheme is like this:
#   HW <-> USB-XXX Adapter <-> Serial <-> AuxiliaryBus <-> XXX_RE_USB_XXX <-> WebIOPi devices.
#
#   In order to work, the auxiliary serial bus device has to be declared in the [BUSES]
#   section BEFORE the declaration of the selected XXX_RE_USB_XXX bus device and
#   has to be provided via the name of that serial device as dev: parameter.
#
#   Example (Linux):
#   [BUSES]
#   auxserial = UART_DEV dev:ttyAMA0 baudrate:115200
#   issi2c = I2C_RE_USB_ISS dev:auxserial
#
#   Example (Windows):
#   [BUSES]
#   auxserial = UART_PYSERIAL dev:COM6 baudrate:115200
#   issi2c = I2C_RE_USB_ISS dev:auxserial
#
#   [DEVICES]
#   mcp = MCP23009 bus:issi2c
#
#   The USB-XXX adapters have the limitation of supporting max 60 bytes per single
#   I2C transfer and max 62 bytes per single SPI transfer. In most cases this does
#   not matter as typically only a few bytes are transferred in typical I2C or SPI
#   communication scenarios.
#
#   Due to the high similarity of the USB-ISS and USB-I2C adapters a lot of code could be
#   abstracted to super classes. However, for the USB-I2C some restrictions apply:
#
#   - it supports only I2C and
#   - only with a fixed frequency of 100 kHz
#   - its serial interface supports a maximum baudrate of 19200 with no parity and
#     2 stopbits.
#
#   The maximum SPI frequency of USB-ISS is 3 Mhz, the maximum I2C frequency is 1 MHz.
#
#   Not all functionalities of USB-ISS and USB-I2C are supported. Only those needed
#   to provide all SPI and I2C methods needed for WebIOPi devices are implemented.
#

import webiopi
from webiopi.devices.bus import Bus, SPI_Bus, I2C_Bus, SLAVES
from webiopi.devices.buses.auxiliary import AuxiliaryBus
from webiopi.utils.types import toint
from webiopi.utils.logger import debug, info
from datetime import datetime

SERIALBUS = None
#Todo: Locking

MAX_I2C_SLAVES_COUNT   = 128
MAX_I2C_TRANSFER_BYTES =  60
MAX_SPI_TRANSFER_BYTES =  62

#---------- USB-ISS device constants ----------
#ISS commands
ISS_COMMAND_ISS_CMD  = 0x5A
#ISS_COMMAND_I2C_SGL  = 0x53
ISS_COMMAND_I2C_AD0  = 0x54
ISS_COMMAND_I2C_AD1  = 0x55
#ISS_COMMAND_I2C_AD2  = 0x56
#ISS_COMMAND_I2C_TEST = 0x58
ISS_COMMAND_SPI      = 0x61

#ISS subcommands
ISS_SUBCOMMAND_ISS_VERSION = 0x01
ISS_SUBCOMMAND_ISS_MODE    = 0x02

#ISS command values
ISS_VALUE_ISS_MODE_I2C_S_20KHZ   = 0x20
ISS_VALUE_ISS_MODE_I2C_S_50KHZ   = 0x30
#ISS_VALUE_ISS_MODE_I2C_S_100KHZ  = 0x40
#ISS_VALUE_ISS_MODE_I2C_S_400KHZ  = 0x50
ISS_VALUE_ISS_MODE_I2C_H_100KHZ  = 0x60
ISS_VALUE_ISS_MODE_I2C_H_400KHZ  = 0x70
ISS_VALUE_ISS_MODE_I2C_H_1000KHZ = 0x80
ISS_VALUE_ISS_MODE_SPI           = 0x90

#---------- USB-I2C device constants ----------
#I2C commands
I2C_COMMAND_I2C_CMD  = 0x5A
#I2C_COMMAND_I2C_SGL  = 0x53
I2C_COMMAND_I2C_MUL  = 0x54 # = ISS_COMMAND_I2C_AD0
I2C_COMMAND_I2C_AD1  = 0x55
#I2C_COMMAND_I2C_AD2  = 0x56

#I2C subcommands
I2C_SUBCOMMAND_I2C_REVISION = 0x01


#---------- USB-XXX abstract class ----------

class XXX_RE_USB_XXX(AuxiliaryBus):
    def __init__(self, dev=""):
        self.serialBusName = dev

        global SERIALBUS
        if SERIALBUS is None:
            SERIALBUS = self.openAuxiliaryBus(dev)

    def __str__(self):
        return "%s (ser=%s)" % (self.__class__.__name__, self.serialBusName)

#---------- Helpers ----------

    def __readResponse__(self, size):
        t1 = datetime.now()
        response = []
        missing = size
        while missing > 0:
            response += SERIALBUS.read(missing)
            missing = size - len(response)
            debug("%s readResponse missing=%d" % (self.__str__(), missing))
            # check for timeout
            t2 = datetime.now()
            elapsed = t2 - t1
            if elapsed.total_seconds() > 0.5:
                debug("%s timeout" % self.__str__())
                return bytearray(size)
        return bytearray(response)


#---------- USB-XXX I2C abstract class ----------

class I2C_RE_USB_XXX(XXX_RE_USB_XXX, I2C_Bus):

#---------- BUS open() and close() reimplementation to handle serial bus singleton ----------

    def open(self):
        debug("Opening I2C bus device - %s" % self.__str__())

    def close(self):
        debug("Closing I2C bus device - %s" % self.__str__())
        I2C_Bus.close(self)
        if SLAVES[self.device].count(None) == MAX_I2C_SLAVES_COUNT: #No more registered slaves
            debug("Closing auxiliary serial bus device - %s (ser=%s)"  % (self.__class__.__name__, self.serialBusName))
            global SERIALBUS
            if SERIALBUS is not None:
                SERIALBUS.close()
                SERIALBUS = None

#---------- Bus and I2C abstraction communication methods redirected to USB-ISS/USB-I2C command sequences ----------

    def readBytes(self, size=1):
        if size > MAX_I2C_TRANSFER_BYTES:
            raise Exception("Error: XXX-I2C driver can only read max %d bytes." % MAX_I2C_TRANSFER_BYTES)
        slaveAddress = (self.slave << 1) + 1
        buff = bytearray(3)
        buff[0] = ISS_COMMAND_I2C_AD0
        buff[1] = slaveAddress
        buff[2] = size
        SERIALBUS.write(buff)
        return self.__readResponse__(size)

    def writeBytes(self, data):
        size = len(data)
        if size > MAX_I2C_TRANSFER_BYTES:
            raise Exception("Error: XXX-I2C driver can only write max %d bytes." % MAX_I2C_TRANSFER_BYTES)
        slaveAddress = self.slave << 1
        buff = bytearray(3 + size)
        buff[0]  = ISS_COMMAND_I2C_AD0
        buff[1]  = slaveAddress
        buff[2]  = size
        buff[3:] = data
        SERIALBUS.write(buff)
        result = self.__readResponse__(1)
        if result[0] == 0:
             raise Exception("Write error %s " % self.device)

    def readRegister(self, addr):
        return self.readRegisters(addr, 1)[0]

    def readRegisters(self, addr, count):
        if count > MAX_I2C_TRANSFER_BYTES:
            raise Exception("Error: XXX-I2C driver can only read max %d bytes." % MAX_I2C_TRANSFER_BYTES)
        slaveAddress = (self.slave << 1) + 1
        buff = bytearray(4)
        buff[0] = ISS_COMMAND_I2C_AD1
        buff[1] = slaveAddress
        buff[2] = addr
        buff[3] = count
        SERIALBUS.write(buff)
        return self.__readResponse__(count)

    def writeRegister(self, addr, byte):
        self.writeRegisters(addr, bytearray([byte]))

    def writeRegisters(self, addr, data):
        size = len(data)
        if size > MAX_I2C_TRANSFER_BYTES:
            raise Exception("Error: XXX-I2C driver can only write max %d bytes." % MAX_I2C_TRANSFER_BYTES)
        slaveAddress = self.slave << 1
        buff = bytearray(4 + size)
        buff[0]  = ISS_COMMAND_I2C_AD1
        buff[1]  = slaveAddress
        buff[2]  = addr
        buff[3]  = size
        buff[4:] = data
        SERIALBUS.write(buff)
        result = self.__readResponse__(1)
        if result[0] == 0:
            raise Exception("Write error %s " % self.device)


#---------- USB-ISS I2C concrete class ----------

class I2C_RE_USB_ISS(I2C_RE_USB_XXX):
    def __init__(self, slave=0x00, speed=100000, dev=""):
        self.slave = slave
        self.speed = toint(speed)

        XXX_RE_USB_XXX.__init__(self, dev)
        Bus.__init__(self, "I2C", "usb-iss:%s" % dev)
        I2C_Bus.__init__(self, slave)

        res = self.__setI2CMode__(self.speed)
        if res[0] == 0x00:
            raise Exception("Cannot set I2C speed %s" % self.__str__())
        debug("Attached I2C bus device - %s" % self.__str__())

        res = self.__getVersion__()
        debug("USB-ISS bus device version - 0x%02X 0x%02X 0x%02X" % (res[0], res[1], res[2]))

#---------- Helpers ----------

    def __getVersion__(self):
        buff = bytearray(2)
        buff[0] = ISS_COMMAND_ISS_CMD
        buff[1] = ISS_SUBCOMMAND_ISS_VERSION
        SERIALBUS.write(buff)
        return self.__readResponse__(3)

    def __setI2CMode__(self, preferredSpeed):
        if self.speed > 1000000:
            debug("Maximum I2C speed for USB-ISS is 1,000,000.0 Hz (%s Hz is given)" % '{:,.1f}'.format(self.speed))
            self.speed = 1000000

        if preferredSpeed < 50000:
            speedmode = ISS_VALUE_ISS_MODE_I2C_S_20KHZ
        elif preferredSpeed < 100000:
            speedmode = ISS_VALUE_ISS_MODE_I2C_S_50KHZ
        elif preferredSpeed < 400000:
            speedmode = ISS_VALUE_ISS_MODE_I2C_H_100KHZ
        elif preferredSpeed <= 1000000:
            speedmode = ISS_VALUE_ISS_MODE_I2C_H_400KHZ
        else:
            speedmode = ISS_VALUE_ISS_MODE_I2C_H_1000KHZ

        buff = bytearray(4)
        buff[0] = ISS_COMMAND_ISS_CMD
        buff[1] = ISS_SUBCOMMAND_ISS_MODE
        buff[2] = speedmode
        buff[3] = 0x00
        SERIALBUS.write(buff)
        return self.__readResponse__(2)


#---------- USB-I2C I2C concrete class ----------

class I2C_RE_USB_I2C(I2C_RE_USB_XXX):
    def __init__(self, slave=0x00, dev=""):
        self.slave = slave

        XXX_RE_USB_XXX.__init__(self, dev)
        Bus.__init__(self, "I2C", "usb-i2c:%s" % dev)
        I2C_Bus.__init__(self, slave)

        debug("Attached I2C bus device - %s" % self.__str__())

        res = self.__getRevision__()
        debug("USB-I2C bus device revision - 0x%02X" % res[0])

#---------- Helpers ----------

    def __getRevision__(self):
        buff = bytearray(4)
        buff[0] = I2C_COMMAND_I2C_CMD
        buff[1] = I2C_SUBCOMMAND_I2C_REVISION
        SERIALBUS.write(buff)
        return self.__readResponse__(1)


#---------- USB-ISS SPI concrete class ----------

class SPI_RE_USB_ISS(XXX_RE_USB_XXX, SPI_Bus):
    def __init__(self, chip=0, mode=0, bits=8, speed=3000000, dev=""):
        #self.chip = toint(chip) unused as USB-ISS has only one CS pin.
        self.mode = toint(mode)
        #self.bits = toint(bits) unused
        self.speed = toint(speed)
        if self.speed > 3000000:
            debug("Maximum SPI speed for USB-ISS is 3,000,000.0 Hz (%s Hz is given)" % '{:,.1f}'.format(self.speed))
            self.speed = 3000000

        XXX_RE_USB_XXX.__init__(self, dev)
        Bus.__init__(self, "SPI", "usb-iss:%s" % dev)

        res = self.__setSPIParameters__(self.mode, self.speed)
        if res[0] == 0x00:
            raise Exception("Cannot set SPI parameters %s" % self.__str__())

        debug("Attached SPI bus device - %s" % self.__str__())

        res = self.__getVersion__()
        debug("USB-ISS bus device version - 0x%02X 0x%02X 0x%02X" % (res[0], res[1], res[2]))

#---------- BUS open() and close() reimplementation to handle serial bus singleton ----------

    def open(self):
        debug("Opening SPI bus device - %s" % self.__str__())

    def close(self):
        debug("Closing SPI bus device - %s" % self.__str__())
        SPI_Bus.close(self)
        global SERIALBUS
        if SERIALBUS is not None:
            SERIALBUS.close()
            SERIALBUS = None

#---------- Bus and SPI abstraction communication methods redirected to USB-ISS command sequences ----------

    def xfer(self, data=[]):
        debug("%s xfer send %s" % (self.__str__(), data))
        size = len(data)
        if size > MAX_SPI_TRANSFER_BYTES:
            raise Exception("Error: ISS-SPI driver can only transfer max %d bytes." % MAX_SPI_TRANSFER_BYTES)
        buff = bytearray(1 + size)
        buff[0]  = ISS_COMMAND_SPI
        buff[1:] = data
        SERIALBUS.write(buff)
        result = self.__readResponse__(len(buff))
        if result[0] == 0:
             raise Exception("Xfer error %s " % self.device)
        return result[1:]

    def writeBytes(self, data):
        debug("%s writeBytes" % self.__str__())
        self.xfer(data)

#---------- Helpers ----------

    def __getVersion__(self):
        buff = bytearray(2)
        buff[0] = ISS_COMMAND_ISS_CMD
        buff[1] = ISS_SUBCOMMAND_ISS_VERSION
        SERIALBUS.write(buff)
        return self.__readResponse__(3)

    def __setSPIParameters__(self, mode, speed):

        clkdiv = (6000000/speed) - 1
        if clkdiv > 255:
            clkdiv = 255

        buff = bytearray(4)
        buff[0] = ISS_COMMAND_ISS_CMD
        buff[1] = ISS_SUBCOMMAND_ISS_MODE
        buff[2] = ISS_VALUE_ISS_MODE_SPI + mode
        buff[3] = clkdiv

        SERIALBUS.write(buff)
        return self.__readResponse__(2)

